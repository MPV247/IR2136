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
        package='rtabmap_launch',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        arguments=['--delete_db_on_start'] if LaunchConfiguration('delete_db') == 'true' else [],
        parameters=[{
            'frame_id': 'base_link',          # Robot

            'approx_sync': 'false',              # Realsense --> Sincronización suave
            'queue_size': 20,

            # --- AJUSTES DE RENDIMIENTO (TFM) ---
            # Si la Jetson se ahoga, baja esto a 1.0 o 0.5 Hz
            'Rtabmap/DetectionRate': '2.0',


            # --- MEMORIA ---
            # Guardar el mapa en disco para verlo luego (rtabmap-databaseViewer)
            'Mem/IncrementalMemory': 'true',
            'Mem/InitWMWithAllNodes': 'true',
            'depth_topic' : '/camera/camera/aligned_depth_to_color/image_raw',
            'rgb_topic' : '/camera/camera/color/image_raw',
            'camera_info_topic' : '/camera/camera/color/camera_info'
            
        }],

    )

    return LaunchDescription([
        delete_db_arg,
        rtabmap_slam_node,
    ])
