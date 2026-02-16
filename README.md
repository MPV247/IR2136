🐉 Chimuelo Bringup (PX4 + ROS 2 Humble)

Paquete de inicio y configuración para la simulación del dron "Chimuelo" utilizando PX4 Autopilot (SITL), Gazebo Sim y ROS 2 Humble.

Este paquete orquesta la conexión entre:

    MAVROS: Para comunicación MAVLink (Comandos de vuelo, IMU, GPS).

    RTAB-Map: Para Odometría Visual y SLAM.

    Robot Localization (EKF): Para fusión de sensores.

    ROS-GZ-Bridge: Para traer las imágenes de la cámara de Gazebo a ROS.

📋 Requisitos del Sistema

    OS: Ubuntu 22.04 LTS (Jammy Jellyfish)

    ROS 2: Humble Hawksbill

    Simulador: Gazebo Sim (Garden o Harmony - incluido con PX4 moderno)

    Firmware: PX4-Autopilot (v1.14 o main)

🛠️ Instalación de Dependencias
1. Paquetes de ROS 2

Instala los paquetes necesarios para la odometría, el puente de simulación y MAVROS:
Bash

sudo apt update
sudo apt install -y \
    ros-humble-desktop \
    ros-humble-mavros \
    ros-humble-mavros-extras \
    ros-humble-robot-localization \
    ros-humble-rtabmap-ros \
    ros-humble-ros-gz \
    ros-humble-tf-transformations

2. Dependencias de Python

Necesarias para transformaciones y scripts de control:
Bash

sudo apt install -y python3-pip
pip3 install transforms3d

3. Configuración de GeographicLib (Crítico para MAVROS)

MAVROS requiere el modelo geoidal egm96 para convertir coordenadas GPS. Si este paso falla, MAVROS se cerrará automáticamente.
Bash

sudo apt install -y geographiclib-tools libgeographic-dev
sudo geographiclib-get-geoids egm96-5


SITL - PX4: Repo para clonar la conrtroladora de vuelo y tener Gazebo. 

```bash
git clone https://github.com/PX4/PX4-Autopilot.git --recursive

cd PX4-Autopilot/

#Lanza mundo de gazebo con dron
PX4_GZ_WORLD=default make px4_sitl gz_x500_depth
```bash


