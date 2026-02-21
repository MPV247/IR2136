import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('chimuelo_bringup')
    rviz_config_file = os.path.join(pkg_dir, 'rviz', 'rtabmap-rviz.rviz')

    return LaunchDescription([
        # 1. Lanzar RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file]
        )
    ])
