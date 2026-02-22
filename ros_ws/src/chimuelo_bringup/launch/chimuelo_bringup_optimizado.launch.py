import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition

def generate_launch_description():
    pkg_chimuelo = get_package_share_directory('chimuelo_bringup')
    pkg_realsense = get_package_share_directory('realsense2_camera')
    pkg_rtabmap_launch = get_package_share_directory('rtabmap_launch')

    # --- 1. ARGUMENTOS DE CONTROL (FLAGS) ---
 
    args = [
        DeclareLaunchArgument('enable_description', default_value='true', description='Activar robot_state_publisher'),
        DeclareLaunchArgument('enable_realsense', default_value='true', description='Activar RealSense'),
        DeclareLaunchArgument('enable_mapping', default_value='true', description='Activar RTAB-Map'),
    ]

    # --- 2. INCLUIR LOS SUB-LAUNCHES CON CONDICIONES ---
   
    # A. Descripción (URDF)
    description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_chimuelo, 'launch', 'transformadas.launch.py')),
        condition=IfCondition(LaunchConfiguration('enable_description'))
    )

    # B. Sensores (Cámara)
    sensors_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_realsense, 'launch', 'rs_launch.py')),
        condition=IfCondition(LaunchConfiguration('enable_realsense')),
        launch_arguments={
            'align_depth.enable': 'true',  # Alinea el mapa de profundidad al frame de color
            'pointcloud.enable': 'false',   # Habilita la publicación de PointCloud2
            'accelerate_gpu_with_glsl': 'true'
        }.items()
    )

    # C. Localización 
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_rtabmap_launch, 'launch', 'rtabmap.launch.py')),
        condition=IfCondition(LaunchConfiguration('enable_mapping')),
        launch_arguments={
            'frame_id': 'base_link',          # Robot
            'args': '--delete_db_on_start', 

            'approx_sync': 'false',              # Realsense --> Sincronización suave

            #IMU PX4-Mav/ROS: 
            'imu_topic': '/mavros/imu/data',      
            'wait_imu_to_init': 'true',           
            
            #Camara Realsense D435: 
            'depth_topic' : '/camera/camera/aligned_depth_to_color/image_raw',
            'rgb_topic' : '/camera/camera/color/image_raw',
            'camera_info_topic' : '/camera/camera/color/camera_info',

           # --------- Optimización ----------
           'Rtabmap/DetectionRate': '1.0',
           'Grid/DepthDecimation': '4'
            
        }.items()
    )

    
    # Construir la lista final
    ld = LaunchDescription(args)
    ld.add_action(description_launch)
    ld.add_action(sensors_launch)
    ld.add_action(localization_launch)


    return ld
