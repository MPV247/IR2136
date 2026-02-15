import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    # Por defecto 'true' para empezar un mapa limpio en cada prueba.
    delete_db_arg = DeclareLaunchArgument(
        'delete_db',
        default_value='true',
        description='Delete the previous database (reset map)?'
    )

    # 1. NODO DE MAPEO (SLAM)
    rtabmap_slam_node = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        arguments=['--delete_db_on_start'] if LaunchConfiguration('delete_db') == 'true' else [],
        parameters=[{
            'frame_id': 'base_link',          # Robot
            'map_frame_id': 'map',            # Mapa global --> RTABMap
            'odom_frame_id': 'odom',          # EKF

            'subscribe_depth': True,
            'subscribe_odom': True,
            'subscribe_rgb': True,
            'subscribe_scan': False,

            'approx_sync': True,              # Realsense --> Sincronización suave
            'queue_size': 20,

            # --- AJUSTES DE RENDIMIENTO (TFM) ---
            # Si la Jetson se ahoga, baja esto a 1.0 o 0.5 Hz
            'Rtabmap/DetectionRate': '2.0',

            # --- TF ---
            # map --> odom
            'publish_tf': True,

            # --- MEMORIA ---
            # Guardar el mapa en disco para verlo luego (rtabmap-databaseViewer)
            'Mem/IncrementalMemory': 'true',
            'Mem/InitWMWithAllNodes': 'true'
        }],
        remappings=[
            # ENTRADAS DE CÁMARA
            ('rgb/image',       '/camera/camera/color/image_raw'),
            ('depth/image',     '/camera/camera/aligned_depth_to_color/image_raw'),
            ('rgb/camera_info', '/camera/camera/color/camera_info'),

            # ENTRADA DE ODOMETRÍA - EKF
            ('odom', '/odometry/filtered')
        ]
    )

    return LaunchDescription([
        delete_db_arg,
        rtabmap_slam_node,
    ])
