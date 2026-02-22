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
    pkg_mavros = get_package_share_directory('mavros')

    # --- 1. ARGUMENTOS DE CONTROL (FLAGS) ---
    # Permiten al usuario decidir qué activar desde la terminal
    args = [
        DeclareLaunchArgument('enable_description', default_value='true', description='Activar robot_state_publisher'),
        DeclareLaunchArgument('enable_mavros', default_value='true', description='Activar conexión con PX4 via MAVROS'),
        DeclareLaunchArgument('enable_realsense', default_value='true', description='Activar RealSense'),
        DeclareLaunchArgument('enable_mapping', default_value='true', description='Activar RTAB-Map'),
    ]

    # --- 2. INCLUIR LOS SUB-LAUNCHES CON CONDICIONES ---
   
    # A. Descripción (URDF)
    description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_chimuelo, 'launch', 'transformadas.launch.py')),
        condition=IfCondition(LaunchConfiguration('enable_description'))
    )

    # B. MAVROS
    mavros_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_mavros, 'launch', 'px4.launch')),
        condition=IfCondition(LaunchConfiguration('enable_mavros')),
        launch_arguments={
            'fcu_url': '/dev/ttyTHS1:921600',
        }.items()
    )

    # C. Sensores (Cámara)
    sensors_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_realsense, 'launch', 'rs_launch.py')),
        condition=IfCondition(LaunchConfiguration('enable_realsense')),
        launch_arguments={
            'align_depth.enable': 'true',  # Alinea el mapa de profundidad al frame de color
            'pointcloud.enable': 'true',   # Habilita la publicación de PointCloud2
        }.items()
    )

    # D. Mapeo 
    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_rtabmap_launch, 'launch', 'rtabmap.launch.py')),
        condition=IfCondition(LaunchConfiguration('enable_mapping')),
        launch_arguments={
            'frame_id': 'base_link',
            'args': '--delete_db_on_start',
            
            # --- APAGAR GUIs ---
            'rtabmap_viz': 'false', 
            'rviz': 'false',        

            # --- OPTIMIZACIÓN: DECIMACIÓN DE IMÁGENES ---
            'Grid/DepthDecimation': '4',       # Reduce la resolución del mapa 3D (1 de cada 4 píxeles)
            'Mem/ImagePreDecimation': '2',     # Reduce la imagen RGB+Depth general a la mitad antes de procesarla
            
            # --- TOPICOS ---
            'depth_topic' : '/camera/camera/aligned_depth_to_color/image_raw',
            'rgb_topic' : '/camera/camera/color/image_raw',
            'camera_info_topic' : '/camera/camera/color/camera_info'
            
        }.items()
    )

    
    # Construir la lista final
    ld = LaunchDescription(args)
    ld.add_action(description_launch)
    ld.add_action(mavros_launch)
    ld.add_action(sensors_launch)
    ld.add_action(mapping_launch)

    return ld
