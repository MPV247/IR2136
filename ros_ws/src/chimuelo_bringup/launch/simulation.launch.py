import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_chimuelo = get_package_share_directory('chimuelo_bringup')
    pkg_mavros = get_package_share_directory('mavros')

    # RUTAS
    urdf_file = os.path.join(pkg_chimuelo, 'urdf', 'prueba_chimuelo.urdf')
    ekf_config_file = os.path.join(pkg_chimuelo, 'config', 'ekf_params_simple.yaml')

    # LEER URDF
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # ====================================================
    # 1. MAVROS (Conexión UDP con SITL)
    # ====================================================
    # En simulación, PX4 habla por el puerto UDP 14540
    mavros_node = Node(
        package='mavros',
        executable='mavros_node',
        output='screen',
        parameters=[{
            'fcu_url': 'udp://:14540@127.0.0.1:14557',
            'gcs_url': '',
            'target_system_id': 1,
            'target_component_id': 1,
            'fcu_protocol': 'v2.0',
            'use_sim_time': True  # <--- VITAL EN SIMULACIÓN
        }]
    )

    # ====================================================
    # 2. STATE PUBLISHER (Tu URDF)
    # ====================================================
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc, 
            'use_sim_time': True # <--- VITAL
        }]
    )

    # ====================================================
    # 3. STATIC TRANSFORMS (Parches para Simulación)
    # ====================================================
    # A veces la cámara en Gazebo tiene nombres de frame distintos.
    # Esto une tu URDF (camera_link) con la cámara de Gazebo (camera_link_optical)
    # Si ves que la nube de puntos apunta mal, ajusta estos números.
    tf_camera_sim = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments = ['0', '0', '0', '-1.57', '0', '-1.57', 'camera_link', 'camera_depth_optical_frame']
    )

    # ====================================================
    # 4. EKF (Tu configuración)
    # ====================================================
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_file, {'use_sim_time': True}], # <--- VITAL
        remappings=[('odometry/filtered', '/odometry/filtered')]
    )

    # ====================================================
    # 5. RTAB-MAP ODOMETRY
    # ====================================================
    rtabmap_odom = Node(
        package='rtabmap_odom',
        executable='rgbd_odometry',
        name='rgbd_odometry',
        output='screen',
        parameters=[{
            'frame_id': 'base_link',
            'publish_tf': False,
            'wait_imu_to_init': False,
            'use_sim_time': True # <--- VITAL
        }],
        remappings=[
            # Mapeamos los tópicos que escupe Gazebo a los que espera RTAB
            ('rgb/image', '/camera/rgb/image_raw'),
            ('depth/image', '/camera/depth/image_raw'),
            ('rgb/camera_info', '/camera/rgb/camera_info'),
            ('odom', '/rtabmap/odom')
        ]
    )

    # ====================================================
    # 6. RVIZ
    # ====================================================
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_chimuelo, 'rviz', 'chimuelo.rviz')],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        mavros_node,
        robot_state_publisher,
        tf_camera_sim,
        ekf_node,
        rtabmap_odom,
        rviz_node
    ])