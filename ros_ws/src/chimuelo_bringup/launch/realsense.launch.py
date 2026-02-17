import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        # 1. Publicador de estado del robot (Lee el URDF y genera los TFs)
        Node(
            package='realsense2_camera',
            executable='rs_launch.py',
            parameters=[{'align_depth.enable': 'true',
                         'pointcloud.enable' : 'true'}]
        )
    ])
