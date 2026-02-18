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
    # 2. MAVROS
    # ====================================================
    '''
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
            'timesync_rate': 0.0,
            'use_sim_time': True,
            # ESTOS SON LOS PARÁMETROS QUE UNEN LAS ISLAS:
            'local_position.tf.send': True,
            'local_position.tf.frame_id': 'odom',
            'local_position.tf.child_frame_id': 'base_link',
        }]
    )
    '''
    # ====================================================
    # 7. RVIZ
    # ====================================================
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_chimuelo, 'rviz', 'chimuelo.rviz')],
        parameters=[{'use_sim_time': True}]
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # ====================================================
    # 8. GZ ROS BRIDGE (Comunicación Gazebo <-> ROS 2)
    # ====================================================
    bridge_config_file = os.path.join(pkg_chimuelo, 'config', 'bridge_camera_sim.yaml')

    # ====================================================
    # 8. GZ ROS BRIDGE (Usando YAML)
    # ====================================================
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': bridge_config_file,
            'use_sim_time': True
        }],
        remappings=[
            # Reloj
            ('/world/default/clock', '/clock'),
            
            # RGB
            ('/world/default/model/x500_depth_0/link/camera_link/sensor/IMX214/image', '/camera/image_raw'),
            ('/world/default/model/x500_depth_0/link/camera_link/sensor/IMX214/camera_info', '/camera/camera_info'),
            
            # Depth
            ('/depth_camera', '/camera/depth/image_raw'),
            ('/camera_info', '/camera/depth/camera_info')
        ]
    )

    return LaunchDescription([
        #mavros_node,
        rviz_node,
        robot_state_publisher,
        bridge_node
    ])