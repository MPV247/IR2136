import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_chimuelo = get_package_share_directory('chimuelo_bringup')
    
    # RUTAS
    urdf_file = os.path.join(pkg_chimuelo, 'urdf', 'prueba_chimuelo.urdf')
    ekf_config_file = os.path.join(pkg_chimuelo, 'config', 'ekf_params_sim.yaml')

    # LEER URDF
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # ====================================================
    # 1. GAZEBO BRIDGE (Vital para ver y para el tiempo)
    # ====================================================
    # Incluimos /clock para sincronizar tiempos y las cámaras
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/rgb/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/rgb/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/camera/depth/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'  # <--- CRÍTICO
        ],
        output='screen'
    )

    # ====================================================
    # 2. MAVROS
    # ====================================================
    mavros_node = Node(
        package='mavros',
        executable='mavros_node',
        output='screen',
        parameters=[{
            'fcu_url': 'udp://:14540@127.0.0.1:14540',
            'gcs_url': '',
            'target_system_id': 1,
            'target_component_id': 1,
            'fcu_protocol': 'v2.0',
            'timesync_rate': 0.0, # Silencia el error de RTT
            'use_sim_time': True
        }]
    )

    # ====================================================
    # 3. STATE PUBLISHER
    # ====================================================
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # ====================================================
    # 4. STATIC TF (Ajuste Cámara)
    # ====================================================
    # Une la cámara del URDF con la óptica de Gazebo
    tf_camera_sim = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments = ['0', '0', '0', '-1.57', '0', '-1.57', 'camera_link', 'camera_depth_optical_frame']
    )

    # ====================================================
    # 5. EKF
    # ====================================================
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_file, {'use_sim_time': True}],
        remappings=[('odometry/filtered', '/odometry/filtered')]
    )

    # ====================================================
    # 6. RTAB-MAP ODOMETRY (CORREGIDO)
    # ====================================================
    rtabmap_odom = Node(
        package='rtabmap_odom',
        executable='rgbd_odometry',
        name='rgbd_odometry',
        output='screen',
        parameters=[{
            'frame_id': 'base_link',
            'publish_tf': False, # EKF se encarga de publicar odom->base_link
            'wait_imu_to_init': False,
            'use_sim_time': True,
            'qos': 2,               # <--- SOLUCIÓN: Acepta "Best Effort" de Gazebo
            'qos_camera_info': 2,   # <--- SOLUCIÓN: También para la info de cámara
            'approx_sync': True,
            'queue_size': 10
        }],
        remappings=[
            ('rgb/image', '/camera/rgb/image_raw'),
            ('depth/image', '/camera/depth/image_raw'),
            ('rgb/camera_info', '/camera/rgb/camera_info'),
            ('odom', '/rtabmap/odom')
        ]
    )

    # ====================================================
    # 7. RVIZ
    # ====================================================
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_chimuelo, 'rviz', 'chimuelo.rviz')],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        bridge,
        mavros_node,
        robot_state_publisher,
        tf_camera_sim,
        ekf_node,
        rtabmap_odom,
        rviz_node
    ])