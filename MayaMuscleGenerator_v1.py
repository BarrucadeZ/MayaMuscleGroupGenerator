import maya.cmds as mc
import maya.OpenMaya as om
import math


# MuscleJointGroup class definition 
# -----------------------------------
# MuscleJointGroup Class and createJnt Function
# -----------------------------------
def createJnt(jointName, parent=None, radius=1.0, **kwargs): #**kwargs allows you to add other joint attributes may needed by cmds.joint while using this function 
    mc.select(clear=True)
    jnt=mc.joint(name=jointName, **kwargs)
    mc.setAttr("{0}.radius".format(jnt), radius)
    #if set a parent, put the child's translation to parent's automatically
    if parent:
        mc.parent(jnt,parent)
        mc.setAttr("{0}.translate".format(jnt), 0, 0, 0)
        mc.setAttr("{0}.rotate".format(jnt), 0, 0, 0)
        #mc.setAttr("{0}.scale".format(jnt), 0, 0, 0)
        mc.setAttr("{0}.jo".format(jnt), 0, 0, 0)
    return jnt


class MuscleJointGroup:
    def __init__(self, muscleName, muscleLength, compressionFactor, stretchFactor,
                 stretchOffset=None,
                 compressionOffset=None):
        self.muscleName = muscleName
        self.muscleLength = muscleLength
        self.compressionFactor = compressionFactor
        self.stretchFactor = stretchFactor
        self.stretchOffset = stretchOffset
        self.compressionOffset = compressionOffset

        self.muscleOrigin = None
        self.muscleBase = None
        self.muscleInsertion = None
        self.muscleTip = None
        self.muscleDriver = None
        self.muscleOffset = None
        self.JOmuscle = None

        self.allJoints = []

        #classmethod parameters
        self.originAttachObj = None
        self.insertionAttachObj = None

        #Use create function to create all the joints
        self.create()
        self.edit()
        
        

    def create(self):
        self.muscleOrigin = createJnt("{0}_muscleOrigin".format(self.muscleName))

        self.muscleInsertion = createJnt("{0}_muscleInsertion".format(self.muscleName))

        # move self.muscleInsertion to the end of the muscle
        mc.setAttr("{0}.tx".format(self.muscleInsertion), self.muscleLength)

        #this may not be necessary, it's used for modify the orientation muscleInsertion
        mc.delete(mc.aimConstraint(self.muscleInsertion, self.muscleOrigin, 
                                   aimVector = [1, 0, 0], upVector=[0, 1, 0],
                                   worldUpType = 'scene', offset = [0, 0, 0], weight = 1))
        #Create muscleBase and make its radius a little smaller
        self.muscleBase = createJnt("{0}_muscleBase".format(self.muscleName), radius=0.5)
        mc.pointConstraint(self.muscleOrigin, self.muscleBase, mo=False, weight=1)
        self.mainAimConstraint = mc.aimConstraint(self.muscleInsertion, self.muscleBase, 
                         aimVector = [1, 0, 0], upVector = [0, 1, 0],
                         worldUpType = 'objectrotation', worldUpObject = self.muscleOrigin,
                         worldUpVector = [0, 1, 0], weight = 1)
        
        #Create a joint muscleTip, it's the child of muscleBase;
        #its location's the same as muscleInsertion. And use muscleInsertion to pointCOnstraint it 
        self.muscleTip = createJnt("{0}_muscleTip".format(self.muscleName), parent = self.muscleBase)
        mc.pointConstraint(self.muscleInsertion, self.muscleTip, mo=False, weight=1)

        self.muscleDriver = createJnt("{0}_muscleDriver".format(self.muscleName), radius=0.5, parent=self.muscleBase)
        self.mainPointConstraint = mc.pointConstraint(self.muscleBase, self.muscleTip, self.muscleDriver, mo=False, weight=1)


        mc.parent(self.muscleBase, self.muscleOrigin)

        #Create muscleOffset, its translate should be the same as the muscle driver, and it should be the child of muscleDriver
        #The createJnt has a feature that if the parent is set, the child's translate will be the same as the parent
        self.muscleOffset = createJnt("{0}_muscleOffset".format(self.muscleName), radius=0.75, parent=self.muscleDriver)

        self.JOmuscle = createJnt("{0}_JOmuscle".format(self.muscleName), radius=1.0, parent=self.muscleOffset)
        #if segmentScaleCompensate is off, the child joint will scale along with the parent joint
        mc.setAttr("{0}.segmentScaleCompensate".format(self.JOmuscle), 0)

        self.allJoints.extend(
            [self.muscleOrigin, self.muscleBase, self.muscleInsertion, self.muscleTip,
            self.muscleDriver, self.muscleOffset,
            self.JOmuscle]
        )


        #self.muscleNodes = []
        self.addSetDrivenKey()

        

    
    def edit(self):

        def createSpaceLocator(scaleValue, **kwargs):
            loc = mc.spaceLocator(**kwargs)[0]
            for axis in 'XYZ':
                mc.setAttr('{0}.localScale{1}'.format(loc, axis), scaleValue)
            return loc
        
        mc.setAttr('{0}.overrideEnabled'.format(self.muscleOrigin), 1)
        mc.setAttr('{0}.overrideDisplayType'.format(self.muscleOrigin), 1)
        mc.setAttr('{0}.overrideEnabled'.format(self.muscleInsertion), 1)
        mc.setAttr('{0}.overrideDisplayType'.format(self.muscleInsertion), 1)

        self.ptConstraints_tmp = []
        self.originLoc = createSpaceLocator(5.0, name='{0}_muscleOrigin_loc'.format(self.muscleName))
        # 开启 overrideEnabled 属性
        mc.setAttr("{}.overrideEnabled".format(self.originLoc), 1)
        # 设置 overrideColor 属性为 13（红色）
        mc.setAttr("{}.overrideColor".format(self.originLoc), 13)
        
        if self.originAttachObj:
            mc.parent(self.originLoc, self.originAttachObj)
        #Move origin locator to the place
        mc.delete(mc.pointConstraint(self.muscleOrigin, self.originLoc, maintainOffset = False, weight = 1))
        self.ptConstraints_tmp.append(mc.pointConstraint(self.originLoc, self.muscleOrigin, maintainOffset = False, weight = 1)[0])


        self.insertionLoc = createSpaceLocator(5.0, name="{0}_muscleInsertion_loc".format(self.muscleName))
        # 开启 overrideEnabled 属性
        mc.setAttr("{}.overrideEnabled".format(self.insertionLoc), 1)
        # 设置 overrideColor 属性为 21 (light blue)
        mc.setAttr("{}.overrideColor".format(self.insertionLoc), 5)

        if self.insertionAttachObj:
            mc.parent(self.insertionLoc, self.insertionAttachObj)

        # use X axis as the main axis and make aim constraint
        # By using this, the 2 locators will rotate and point to each other when they're moved
        mc.aimConstraint(self.insertionLoc, self.originLoc, aimVector=[1,0,0], upVector=[0,1,0],
                         worldUpType='scene', offset=[0,0,0],weight=1)
        mc.aimConstraint(self.originLoc, self.insertionLoc, aimVector=[-1,0,0], upVector=[0,1,0],
                         worldUpType='scene', offset=[0,0,0],weight=1)
        
        mc.delete(mc.pointConstraint(self.muscleInsertion, self.insertionLoc, maintainOffset=False, weight=1))
        self.ptConstraints_tmp.append(mc.pointConstraint(self.insertionLoc, self.muscleInsertion, maintainOffset=False, weight=True)[0])

        driverGrp = mc.group(name="{0}_muscleCenter_loc".format(self.muscleName), empty=True)
        self.centerLoc = createSpaceLocator(5.0, name="{0}_muscleCenterLoc".format(self.muscleName))
        # 开启 overrideEnabled 属性
        mc.setAttr("{}.overrideEnabled".format(self.centerLoc), 1)
        # 设置 overrideColor 属性为 14 (purple)
        mc.setAttr("{}.overrideColor".format(self.centerLoc), 9)

        mc.parent(self.centerLoc, driverGrp)
        mc.delete(mc.pointConstraint(self.muscleDriver, driverGrp, maintainOffset=False, weight=True))
        mc.parent(driverGrp,self.originLoc)
        mc.pointConstraint(self.originLoc, self.insertionLoc, driverGrp, maintainOffset = True, weight = True)
        mc.setAttr("{0}.rotate".format(driverGrp), 0,0,0)
        mc.delete(self.mainPointConstraint)
        self.ptConstraints_tmp.append(mc.pointConstraint(self.centerLoc, self.muscleDriver, maintainOffset=False, weight=True)[0])



    def update(self):
        #"""apply the edits"""#
        # remove control
        for ptConstraint_tmp in self.ptConstraints_tmp:
            if mc.objExists(ptConstraint_tmp):
                mc.delete(ptConstraint_tmp)

        for loc in [self.originLoc, self.insertionLoc, self.centerLoc]:
            if mc.objExists(loc):
                mc.delete(loc)

        mc.setAttr("{0}.overrideEnabled".format(self.muscleOrigin), 0)
        mc.setAttr("{0}.overrideDisplayType".format(self.muscleOrigin), 0)
        mc.setAttr("{0}.overrideEnabled".format(self.muscleInsertion), 0)
        mc.setAttr("{0}.overrideDisplayType".format(self.muscleInsertion), 0)

        mc.delete(self.mainAimConstraint)

        self.mainPointConstraint = mc.pointConstraint(self.muscleBase, self.muscleTip, self.muscleDriver,
                                                    maintainOffset=True, weight=1)
            
        # use X axis as aim axis, make muscleOrigin point to the end of muscle
        mc.delete(mc.aimConstraint(self.muscleInsertion, self.muscleOrigin, aimVector=[1,0,0], upVector=[0,1,0],
                                    worldUpType='scene', offset=[0,0,0],weight=1))
            
        self.mainAimConstraint = mc.aimConstraint(self.muscleInsertion, self.muscleBase, aimVector=[1,0,0], upVector=[0,1,0],
                                                    worldUpType='objectrotation', worldUpObject= self.muscleOrigin,
                                                    worldUpVector=[0,1,0])
                                                      
        # remove existing sdk nodes
        animCurveNodes = mc.ls(mc.listConnections(self.JOmuscle, source=True, destination=False), type=('animCurveUU','animCurveUL'))
        mc.delete(animCurveNodes)

        #After Updating, set driven key again
        self.addSetDrivenKey()

        self.createDataNode()


    def addSetDrivenKey(self):
        yzSquashScale = math.sqrt(1.0/self.compressionFactor)
        yzStretchScale = math.sqrt(1.0/self.stretchFactor)

        #Set a default offset value
        if not self.stretchOffset:
            self.stretchOffset = [0.0, 0.0, 0.0]
        if not self.compressionOffset:
            self.compressionOffset = [0.0, 0.0, 0.0]
            
        #Tip is the child of muscleBase put in the origin location of muscle
        #So its translateX is the muscleLength
        restLength = mc.getAttr("{0}.translateX".format(self.muscleTip))


        #Set the driven key. Driver: MuscleTip, Driven: JOmuscle
            
            
        for index, axis in enumerate('XYZ'):
            #Default position
            #First Set the attribute of driver and driven, then set driven key
            ##mc.setAttr("{0}.translateX".format(self.muscleTip), restLength)

            mc.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), 1.0)
            mc.setAttr("{0}.translate{1}".format(self.JOmuscle, axis), 0.0)

            #attribute and currentDriver are necssary parmeters
            mc.setDrivenKeyframe("{0}.scale{1}".format(self.JOmuscle, axis),
                                 currentDriver = "{0}.translateX".format(self.muscleTip))
            mc.setDrivenKeyframe("{0}.translate{1}".format(self.JOmuscle, axis), 
                                 currentDriver = "{0}.translateX".format(self.muscleTip))
                
                

            #Stretch position
            mc.setAttr("{0}.translateX".format(self.muscleTip), restLength*self.stretchFactor)
            if axis == 'X':
                mc.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), self.stretchFactor)
            else:
                mc.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), yzStretchScale)
                #stretch offset is a [x,y,z] list
                mc.setAttr("{0}.translate{1}".format(self.JOmuscle, axis), self.stretchOffset[index])

            mc.setDrivenKeyframe("{0}.scale{1}".format(self.JOmuscle, axis),
                                     currentDriver = "{0}.translateX".format(self.muscleTip))
            mc.setDrivenKeyframe("{0}.translate{1}".format(self.JOmuscle, axis),
                                     currentDriver = "{0}.translateX".format(self.muscleTip))

            #Compression position
            mc.setAttr("{0}.translateX".format(self.muscleTip), restLength*self.compressionFactor)
            if axis == 'X':
                mc.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), self.compressionFactor)
            else:
                mc.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), yzSquashScale)
                #stretch offset is a [x,y,z] list
                mc.setAttr("{0}.translate{1}".format(self.JOmuscle, axis), self.compressionOffset[index])

            mc.setDrivenKeyframe("{0}.scale{1}".format(self.JOmuscle, axis),
                                     currentDriver = "{0}.translateX".format(self.muscleTip), inTangentType = "linear")
            mc.setDrivenKeyframe("{0}.translate{1}".format(self.JOmuscle, axis),
                                     currentDriver = "{0}.translateX".format(self.muscleTip), inTangentType = "linear")
                

            #Back to default position
            mc.setAttr("{0}.translateX".format(self.muscleTip), restLength)

    def createDataNode(self):
        dataNodeName = self.muscle + "_dataNode"
        if mc.ls(dataNodeName):
            mc.delete(dataNodeName)

        dataNode = mc.createNode("network", name=dataNodeName)
        # create attributes
        mc.addAttr(dataNode, longName = "name", niceName = "Name", dataType="string")
        mc.addAttr(dataNode, longName = "type", niceName = "Type", dataType="string")
        mc.addAttr(dataNode, longName = "restLength", niceName = "Muscle Length", dataType="double")
        mc.addAttr(dataNode, longName = "compressionFactor", niceName = "Compression Factor", dataType="double")
        mc.addAttr(dataNode, longName = "stretchFactor", niceName = "Stretch Factor", dataType="double")
        mc.addAttr(dataNode, longName = "compressionOffset", niceName = "Compression Offset", dataType="float3")
        mc.addAttr(dataNode, longName = "compressionOffsetX", dataType="float", parent = "compressionOffset")
        mc.addAttr(dataNode, longName = "compressionOffsetY", dataType="float", parent = "compressionOffset")
        mc.addAttr(dataNode, longName = "compressionOffsetZ", dataType="float", parent = "compressionOffset")
        mc.addAttr(dataNode, longName = "stretchOffset", niceName = "Stretch Offset", dataType="float3")
        mc.addAttr(dataNode, longName = "stretchOffsetX", dataType="float", parent = "stretchOffset")
        mc.addAttr(dataNode, longName = "stretchOffsetY", dataType="float", parent = "stretchOffset")
        mc.addAttr(dataNode, longName = "stretchOffsetZ", dataType="float", parent = "stretchOffset")
        # Assign Attributes
        mc.setAttr(f"{dataNode}.name", self.muscleName, type="string")
        mc.setAttr(f"{dataNode}.type", "muscleJointGroup", type="string")
        mc.setAttr(f"{dataNode}.restLength", self.muscleLength)
        mc.setAttr(f"{dataNode}.compressionFactor", self.compressionFactor)
        mc.setAttr(f"{dataNode}.stretchFactor", self.stretchFactor)
        if self.compressionOffset is None:
            compressionOffset = [0,0,0]
        else:
            compressionOffset = self.compressionOffset
        mc.setAttr(f"{dataNode}.compressionOffset", *compressionOffset)

        if self.stretchOffset is None:
            stretchOffset = [0,0,0]
        else:
            stretchOffset = self.stretchOffset
        mc.setAttr(f"{dataNode}.stretchOffset", *stretchOffset)

        # muscle attach obj
        mc.addAttr(dataNode, longName = "originAttachObj", niceName = "Origin Attach Obj", attributeType = "message")
        mc.addAttr(dataNode, longName = "insertionAttachObj", niceName = "Insertion Attach Obj", attributeType = "message")

        # muscle origin
        mc.addAttr(dataNode, longName = "muscleOrigin", niceName = "Muscle Origin", attributeType = "message")

        mc.addAttr(dataNode, longName = "muscleInsertion", niceName = "Muscle Insertion", attributeType = "message")

        mc.addAttr(dataNode, longName = "muscleDriver", niceName = "Muscle Driver", attributeType = "message")

        mc.addAttr(dataNode, longName = "muscleBase", niceName = "Muscle Base", attributeType = "message")

        mc.addAttr(dataNode, longName = "muscleTip", niceName = "Muscle Tip", attributeType = "message")

        mc.addAttr(dataNode, longName = "JOMuscle", niceName = "JOMuscle", attributeType = "message")

        mc.addAttr(dataNode, longName = "mainPtConst", niceName = "Main PointConstraint", attributeType = "message")

        mc.addAttr(dataNode, longName = "mainAimConst", niceName = "Main AimConstraint", attributeType = "message")

        dataParentAttr = f"{self.muscleName}_dataParent"

        #connect
        if not mc.attributeQuery(dataParentAttr, node=self.originAttachObj, exists=True):
            mc.addAttr(self.originAttachObj, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.originAttachObj", f"{self.originAttachObj}.{dataParentAttr}")

        if not mc.attributeQuery(dataParentAttr, node=self.insertionAttachObj, exists=True):
            mc.addAttr(self.insertionAttachObj, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.insertionAttachObj", f"{self.insertionAttachObj}.{dataParentAttr}")

        if not mc.attributeQuery(dataParentAttr, node=self.muscleOrigin, exists=True):
            mc.addAttr(self.muscleOrigin, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.muscleOrigin", f"{self.muscleOrigin}.{dataParentAttr}")

        if not mc.attributeQuery(dataParentAttr, node=self.muscleInsertion, exists=True):
            mc.addAttr(self.muscleInsertion, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.muscleInsertion", f"{self.muscleInsertion}.{dataParentAttr}")

        if not mc.attributeQuery(dataParentAttr, node=self.muscleDriver, exists=True):
            mc.addAttr(self.muscleDriver, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.muscleDriver", f"{self.muscleDriver}.{dataParentAttr}")

        #muscleBase
        if not mc.attributeQuery(dataParentAttr, node=self.muscleBase, exists=True):
            mc.addAttr(self.muscleBase, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")       
        mc.connectAttr(f"{dataNode}.muscleBase", f"{self.muscleBase}.{dataParentAttr}")

        #muscleTip
        if not mc.attributeQuery(dataParentAttr, node=self.muscleTip, exists=True):
            mc.addAttr(self.muscleTip, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")    
        mc.connectAttr(f"{dataNode}.muscleTip", f"{self.muscleTip}.{dataParentAttr}")

        #JOmuscle
        if not mc.attributeQuery(dataParentAttr, node=self.JOmuscle, exists=True):
            mc.addAttr(self.JOmuscle, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.JOMuscle", f"{self.JOmuscle}.{dataParentAttr}")

        #mainPointConstraint
        if not mc.attributeQuery(dataParentAttr, node=self.mainPointConstraint, exists=True):
            mc.addAttr(self.mainPointConstraint, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.mainPtConst", f"{self.mainPointConstraint}.{dataParentAttr}")

        #mainAimConstraint
        if not mc.attributeQuery(dataParentAttr, node=self.mainAimConstraint, exists=True):
            mc.addAttr(self.mainAimConstraint, longName = dataParentAttr, niceName= dataParentAttr, attributeType="message")
        mc.connectAttr(f"{dataNode}.mainAimConst", f"{self.mainAimConstraint}.{dataParentAttr}")


            

        


    @classmethod
    def createFromAttachObjects(cls, muscleName, originAttachObj, insertionAttachObj, compressionFactor=1.0,
                               stretchFactor=1.0, stretchOffset=None, compressionOffset=None):
        #The maya debug log says the xform return data need to be unpacked
        originAttachPos = om.MVector(*mc.xform(originAttachObj, translation=True, worldSpace=True, query=True))
        insertionAttachPos = om.MVector(*mc.xform(insertionAttachObj, translation=True, worldSpace=True, query=True))
        muscleLength = om.MVector(insertionAttachPos - originAttachPos).length()

        #create a muscleJointGroup class
        muscleJointGroup = cls(muscleName, muscleLength, compressionFactor, stretchFactor, compressionOffset, stretchOffset)
        muscleJointGroup.originAttachObj = originAttachObj
        muscleJointGroup.insertionAttachObj = insertionAttachObj

        #Match transform and parent joints to the attachObj
        mc.matchTransform(muscleJointGroup.originLoc, originAttachObj)
        mc.matchTransform(muscleJointGroup.insertionLoc, insertionAttachObj)

        mc.parent(muscleJointGroup.muscleOrigin, originAttachObj)
        mc.parent(muscleJointGroup.muscleInsertion, insertionAttachObj)

        mc.parent(muscleJointGroup.originLoc, originAttachObj)
        mc.parent(muscleJointGroup.insertionLoc, insertionAttachObj)

        return muscleJointGroup
    
    @classmethod
    def getMuscleObjFromDataNode(cls, dataNode):
        muscleName = mc.getAttr(f"{dataNode}.name")
        muscleLength = mc.getAttr(f"{dataNode}.restLength")
        compressionFactor = mc.getAttr(f"{dataNode}.compressionFactor")
        stretchFactor = mc.getAttr(f"{dataNode}.stretchFactor")
        compressionOffset = mc.getAttr(f"{dataNode}.compressionOffset")[0]
        stretchOffset = mc.getAttr(f"{dataNode}.stretchOffset")[0]
        muscleOrigin = mc.listConnections(f"{dataNode}.muscleOrigin", destination=True, source=False)[0]
        muscleInsertion = mc.listConnections(f"{dataNode}.muscleInsertion", destination=True, source=False)[0]
        muscleDriver = mc.listConnections(f"{dataNode}.muscleDriver", destination=True, source=False)[0]
        muscleBase = mc.listConnections(f"{dataNode}.muscleBase", destination=True, source=False)[0]
        muscleTip = mc.listConnections(f"{dataNode}.muscleTip", destination=True, source=False)[0]
        JOmuscle = mc.listConnections(f"{dataNode}.JOMuscle", destination=True, source=False)[0]

        originAttachObj = mc.listConnections(f"{dataNode}.originAttachObj", destination=True, source=False)[0]
        insertionAttachObj = mc.listConnections(f"{dataNode}.insertionAttachObj", destination=True, source=False)[0]

        mainPtConst = mc.listConnections(f"{dataNode}.mainPtConst", destination=True, source=False)[0]
        mainAimConst = mc.listConnections(f"{dataNode}.mainAimConst", destination=True, source=False)[0]

        muscleObj = cls(muscleName, muscleLength, compressionFactor, stretchFactor, stretchOffset, compressionOffset)
        muscleObj.muscleOrigin = muscleOrigin
        muscleObj.muscleInsertion = muscleInsertion
        muscleObj.originAttachObj = originAttachObj
        muscleObj.insertionAttachObj = insertionAttachObj
        muscleObj.muscleDriver = muscleDriver
        muscleObj.muscleBase = muscleBase
        muscleObj.muscleTip = muscleTip
        muscleObj.JOmuscle = JOmuscle

        muscleObj.mainPointConstraint = mainPtConst
        muscleObj.mainAimConstraint = mainAimConst
        return muscleObj


#Mirror Function
# Mirror Function with corrections
def mirror(muscleJointGroup, muscleOriginAttachObj, muscleInsertionAttachObj, mirrorAxis='x'):
    # Get original positions
    originPos = om.MVector(*mc.xform(muscleJointGroup.muscleOrigin, translation=True, worldSpace=True, query=True))
    insertionPos = om.MVector(*mc.xform(muscleJointGroup.muscleInsertion, translation=True, worldSpace=True, query=True))
    centerPos = om.MVector(*mc.xform(muscleJointGroup.muscleDriver, translation=True, worldSpace=True, query=True))

    # Mirror the positions based on the specified axis
    if mirrorAxis == 'x':
        mirrorOriginPos = om.MVector(-originPos.x, originPos.y, originPos.z)
        mirrorInsertionPos = om.MVector(-insertionPos.x, insertionPos.y, insertionPos.z)
        mirrorCenterPos = om.MVector(-centerPos.x, centerPos.y, centerPos.z)
    elif mirrorAxis == 'y':
        mirrorOriginPos = om.MVector(originPos.x, -originPos.y, originPos.z)
        mirrorInsertionPos = om.MVector(insertionPos.x, -insertionPos.y, insertionPos.z)
        mirrorCenterPos = om.MVector(centerPos.x, -centerPos.y, centerPos.z)
    elif mirrorAxis == 'z':
        mirrorOriginPos = om.MVector(originPos.x, originPos.y, -originPos.z)
        mirrorInsertionPos = om.MVector(insertionPos.x, insertionPos.y, -insertionPos.z)
        mirrorCenterPos = om.MVector(centerPos.x, centerPos.y, -centerPos.z)
    else:
        raise RuntimeError("Invalid Mirror Axis")

    # Determine mirrored muscle name
    if "Left" in muscleJointGroup.muscleName:
        newMuscleName = muscleJointGroup.muscleName.replace('Left', 'Right')
    elif "Right" in muscleJointGroup.muscleName:
        newMuscleName = muscleJointGroup.muscleName.replace('Right', 'Left')
    else:
        raise RuntimeError("Invalid Side Information, muscle joint name should contain 'Left' or 'Right'")

    # Create mirrored MuscleJointGroup using original attach objects and factors
    mirrorMuscleGroup = MuscleJointGroup.createFromAttachObjects(
        newMuscleName, muscleOriginAttachObj, muscleInsertionAttachObj, 
        compressionFactor=muscleJointGroup.compressionFactor,
        stretchFactor=muscleJointGroup.stretchFactor,
        stretchOffset=muscleJointGroup.stretchOffset,
        compressionOffset=muscleJointGroup.compressionOffset
    )

    # Set the mirrored joint positions
    mc.xform(mirrorMuscleGroup.originLoc, translation=(mirrorOriginPos.x, mirrorOriginPos.y, mirrorOriginPos.z), worldSpace=True)
    mc.xform(mirrorMuscleGroup.insertionLoc, translation=(mirrorInsertionPos.x, mirrorInsertionPos.y, mirrorInsertionPos.z), worldSpace=True)
    mc.xform(mirrorMuscleGroup.centerLoc, translation=(mirrorCenterPos.x, mirrorCenterPos.y, mirrorCenterPos.z), worldSpace=True)

    # Re-parent mirrored joints to attach objects if they are not already children
    def safeParent(child, parent):
        current_parent = mc.listRelatives(child, parent=True)
        if current_parent is None or current_parent[0] != parent:
            mc.parent(child, parent)

    safeParent(mirrorMuscleGroup.muscleOrigin, muscleOriginAttachObj)
    safeParent(mirrorMuscleGroup.originLoc, muscleOriginAttachObj)
    safeParent(mirrorMuscleGroup.muscleInsertion, muscleInsertionAttachObj)
    safeParent(mirrorMuscleGroup.insertionLoc, muscleInsertionAttachObj)


    mirrorMuscleGroup.update()
    return mirrorMuscleGroup
    
# Create UI Window
def create_muscle_ui():
    # Check existed window
    if mc.window("muscleUI", exists=True):
        mc.deleteUI("muscleUI", window=True)
    
    # Create window
    window = mc.window("muscleUI", title="Muscle Control Panel", widthHeight=(300, 200))
    mc.columnLayout(adjustableColumn=True)
    
    # Pt1：Input box and slider for muscle name and deform factor
    mc.text(label="Muscle Name:")
    muscle_name_field = mc.textField()

    mc.text(label="Origin Attach Object:")
    origin_attach_obj_field = mc.textField()

    mc.text(label="Insertion Attach Object:")
    insertion_attach_obj_field = mc.textField()

    mc.text(label="Compression Factor (0-1):")
    compression_slider = mc.floatSlider(min=0.0, max=1.0, value=0.5, step=0.01)

    mc.text(label="Stretch Factor (1-3):")
    stretch_slider = mc.floatSlider(min=1.0, max=3.0, value=1.5, step=0.01)

    # Create Button
    def create_muscle():
        muscleName = mc.textField(muscle_name_field, query=True, text=True)
        originAttachObj = mc.textField(origin_attach_obj_field, query=True, text=True)
        insertionAttachObj = mc.textField(insertion_attach_obj_field, query=True, text=True)
        compressionFactor = mc.floatSlider(compression_slider, query=True, value=True)
        stretchFactor = mc.floatSlider(stretch_slider, query=True, value=True)
        
        # Call createFromAttachObjects to create muscleGroup
        global muscleGroup
        muscleGroup = MuscleJointGroup.createFromAttachObjects(
            muscleName, originAttachObj, insertionAttachObj, compressionFactor, stretchFactor)

    mc.button(label="Create", command=lambda _: create_muscle())

    

    # Pt2: Update Button
    def update_muscle():
        if 'muscleGroup' in globals():
            muscleGroup.update()
        else:
            mc.warning("No muscle group created yet. Please create a muscle first.")

    mc.button(label="Update", command=lambda _: update_muscle())

    # Pt3: ReEdit Button 
    def edit_muscle():
        if 'muscleGroup' in globals():
            muscleGroup.edit()
        else:
            mc.warning("No muscle group created yet. Please create a muscle first.")

    mc.button(label="ReEdit", command=lambda _: edit_muscle())

    #Mirror
    # Input attach obj in Mirror
    mc.text(label="Mirror Origin Attach Object:")
    mirror_origin_attach_obj_field = mc.textField()

    mc.text(label="Mirror Insertion Attach Object:")
    mirror_insertion_attach_obj_field = mc.textField()

    # Mirror
    def mirror_muscle():
        if 'muscleGroup' in globals():
            mirror_origin_attach_obj = mc.textField(mirror_origin_attach_obj_field, query=True, text=True)
            mirror_insertion_attach_obj = mc.textField(mirror_insertion_attach_obj_field, query=True, text=True)
            mirror(muscleGroup, mirror_origin_attach_obj, mirror_insertion_attach_obj, mirrorAxis='x')

        else:
            mc.warning("No muscle group created yet. Please create a muscle first.")

    mc.button(label="Mirror", command=lambda _: mirror_muscle())

    
    mc.showWindow(window)

# Call UI
create_muscle_ui()







        



#createJnt("jointA")
#createJnt("jointA", position=(1,0,0))

##muscleGroup = MuscleJointGroup("bicep", 10, 0.5, 1.5)

#New creat group methods: create the class(including muscle creation functions) from classmethod
##muscleGroup = MuscleJointGroup.createFromAttachObjects("bicep", 
                                                       ##"L_UpperArm_01_Twist_1",
                                                       ##"L_LowerArm_01_Twist_0",
                                                       ##0.5, 1.5) 
##muscleGroup.update()