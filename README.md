# UAV - ROS2 Bringup & SLAM Architecture
[![ROS2](https://img.shields.io/badge/ROS2-Humble-34a853.svg?logo=ros)](https://docs.ros.org/en/humble/index.html)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420.svg?logo=ubuntu)](https://ubuntu.com/blog/tag/22-04-lts)
[![Hardware](https://img.shields.io/badge/Hardware-Jetson_Orin_Nano-76B900.svg?logo=nvidia)](https://docs.px4.io/main/en/companion_computer/holybro_pixhawk_jetson_baseboard)

This repository contains the core software architecture for the **"Chimuelo"** platform, a custom multirotor UAV designed for autonomous navigation and 3D mapping in GPS-denied environments. 

The system integrates a PX4-based flight controller with an NVIDIA Jetson Orin Nano companion computer, leveraging an Intel RealSense D435 for visual odometry and dense 3D mapping via RTAB-Map.

## Table of Contents
- [System Requirements](#system-requirements)
- [Hardware Setup](#hardware-setup)
- [Repository Structure](#repository-structure)
- [Installation & Build](#installation--build)
- [Usage & Launch Instructions](#usage--launch-instructions)
- [Sensor Fusion (Future Work)](#sensor-fusion-future-work)
- [Authors & Acknowledgments](#authors--acknowledgments)

## System Requirements

- **OS:** Ubuntu 22.04 LTS (Jammy Jellyfish)
- **Middleware:** ROS2 Humble Hawksbill, 
- **Core Dependencies:**
  ```bash
  sudo apt install ros-humble-mavros ros-humble-mavros-extras
  sudo apt install ros-humble-rtabmap-ros
  sudo apt install ros-humble-realsense2-camera
  sudo apt install ros-humble-robot-localization
  sudo apt install ros-humble-xacro ros-humble-joint-state-publisher
 
## Hardware Setup

  Flight Controller: Holybro 500x Frame with Pixhawk (running PX4 Autopilot).

  Companion Computer: NVIDIA Jetson Orin Nano (handles heavy SLAM computation and hardware interfacing).

  Sensors: Intel RealSense D435 (RGB-D depth camera).

## Repository Structure

The workspace is modularized within the `chimuelo_bringup` package to facilitate maintenance and scalability:

```text
chimuelo_bringup/
├── config/          # EKF parameters for future sensor fusion (robot_localization)
├── launch/          # Modular Python launch scripts (bringup, transforms, rviz)
├── meshes/          # 3D STL model for visualization
├── rviz/            # Pre-configured RViz profiles for mapping and TF debugging
├── urdf/            # Kinematic description linking base_link and optical frames
├── CMakeLists.txt   # Build configuration
└── package.xml      # Package metadata and dependencies
```

## Installation & Build

    ```bash
    
    #Clone this repository into your ROS2 workspace src folder:
    cd ~/ros2_ws/src
    git clone [https://github.com/MPV247/chimuelo_bringup.git](https://github.com/MPV247/chimuelo_bringup.git)

    #Install remaining dependencies using rosdep:
    
    cd ~/ros2_ws
    rosdep install --from-paths src --ignore-src -r -y

    #Build the package:

    colcon build --packages-select chimuelo_bringup --symlink-install

    #Source the workspace:

    source install/setup.bash
    ```
    
## Usage & Launch Instructions

The core logic is encapsulated in chimuelo_bringup.launch.py, which uses conditional execution logic (Launch Arguments) to toggle specific subsystems.
1. **Main Bringup:** To launch the full system (URDF + RealSense + RTAB-Map SLAM):

```bash
ros2 launch chimuelo_bringup chimuelo_bringup.launch.py
```

2. **Modular Execution (Flags):** You can enable/disable specific modules depending on your testing needs (e.g., when playing back a rosbag):

```bash
ros2 launch chimuelo_bringup chimuelo_bringup.launch.py enable_description:=true enable_realsense:=false enable_mapping:=true
```

    enable_description: Launches robot_state_publisher and broadcasts the URDF TF tree.

    enable_realsense: Initializes the D435 camera with GPU acceleration.

    enable_mapping: Activates RTAB-Map for visual odometry and mapping.

3. **Visualization:** To visualize the real-time TF tree, point cloud, and 2D occupancy grid:

```bash
ros2 launch chimuelo_bringup rviz_config.launch.py
```

## Sensor Fusion (Future Work)

Currently, IMU-Visual fusion is handled internally by the RTAB-Map node via low-latency synchronization with the **/mavros/imu/data topic**. However, a fully configured **Extended Kalman Filter (EKF)** using robot_localization is available in the config/ekf_params.yaml file to support future integrations (e.g., external LiDAR, UWB).

## Authors & Acknowledgments

    Miguel Porcar:  Kinematic modeling, URDF design, TF tree logic, and EKF configuration.

    David Ballester: Jetson Orin OS configuration, perception drivers (RealSense), and RTAB-Map SLAM tuning.

*Special thanks to the UJI Robotics Team for providing the high-fidelity .STL 3D model used in the URDF visualization.*


