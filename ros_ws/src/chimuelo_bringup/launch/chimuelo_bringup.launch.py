import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. LOCALIZAR DIRECTORIOS
    pkg_chimuelo = get_package_share_directory('chimuelo_bringup')
    pkg_realsense = get_package_share_directory('realsense2_camera')

    # 2. RUTAS DE ARCHIVOS
    urdf_file = os.path.join(pkg_chimuelo, 'urdf', 'prueba_chimuelo.urdf')
    ekf_config_file = os.path.join(pkg_chimuelo, 'config', 'ekf_params_simple.yaml')

    # 3. LEER EL URDF (Necesario para robot_state_publisher)
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # ========================================================================
    # DEFINICIÓN DE NODOS
    # ========================================================================

    # A. PUBLICAR EL ROBOT (URDF)S
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}],
        arguments=[urdf_file]
    )

    # B. CÁMARA REALSENSE
    # TODO --> Preguntarle a David el launch que utiliza el.
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_realsense, 'launch', 'rs_launch.py')
        ),
        launch_arguments={
            'align_depth.enable': 'true',  # Sintaxis ROS2 para realsense
            'pointcloud.enable': 'true',
        }.items()
    )

    # C. ODOMETRÍA VISUAL (RTAB-MAP RGBD)
    rtabmap_odom_node = Node(
        package='rtabmap_odom',
        executable='rgbd_odometry',
        name='rgbd_odometry',
        output='screen',
        parameters=[{
            'frame_id': 'base_link',
            'publish_tf': False,       # Ya lo hace EKF
            'wait_imu_to_init': False
        }],
        remappings=[
            ('rgb/image', '/camera/camera/color/image_raw'),
            ('depth/image', '/camera/camera/aligned_depth_to_color/image_raw'),
            ('rgb/camera_info', '/camera/camera/color/camera_info'),
            ('odom', '/rtabmap/odom') # Salida de odometría
        ]
    )

    # D. FUSIÓN DE SENSORES (EKF - ROBOT LOCALIZATION)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_file], # Carga el YAML corregido
        remappings=[('odometry/filtered', '/odometry/filtered')]
    )

    # E. VISUALIZACIÓN (RVIZ2)
    rviz_config = os.path.join(pkg_chimuelo, 'rviz', 'chimuelo.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config]
    )

    # Descripcion
    return LaunchDescription([
        robot_state_publisher_node,
        realsense_launch,
        rtabmap_odom_node,
        ekf_node,
        rviz_node
    ])
