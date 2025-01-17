# Muscle Rigging Tool

## Features

### 1. Muscle Name
- Users can specify a **name** for the muscle joint group.
- This name will serve as the **prefix** for the generated joints and constraints.

### 2. Origin Attach Object
- Users can assign the skeletal joint where the **origin** of the muscle attaches.
- The origin placement is based on the muscle's anatomical structure.

### 3. Insertion Attach Object
- Users can assign the skeletal joint where the **insertion** of the muscle attaches.

### 4. Stretch Factor
- Users can input the **maximum stretch factor** for the muscle.

### 5. Compress Factor
- Users can input the **maximum compression factor** for the muscle.

### 6. Create
- Generates a **complete muscle joint group** based on the provided parameters.
- After creation, users can adjust the following locators to refine the muscle's anatomical positioning:
  - **MuscleOriginLoc**: Adjusts the starting point of the muscle.
  - **MuscleInsertionLoc**: Adjusts the endpoint of the muscle.
  - **JOMuscleLoc**: Adjusts the bind joint's position.

### 7. Update
- The plugin applies user-defined transformations to the muscle joints based on the adjusted positions of the three locators.

### 8. Mirror
- Users can select objects attached to the **symmetric side** of the joint group.
- The plugin will quickly generate a mirrored joint group with identical properties.

---

## Usage
1. Input the **muscle name** to define the joint group prefix.
2. Assign the **origin** and **insertion attach objects** to specify the muscle's anatomical endpoints.
3. Configure the **stretch** and **compress factors** based on muscle behavior requirements.
4. Click **Create** to generate the muscle joint group and adjust the locators as needed.
5. Use **Update** to apply changes based on locator positions.
6. Use **Mirror** to replicate the joint group on the opposite side.

---
