
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    description_dir = get_package_share_directory('tp4_description')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                description_dir,
                'launch',
                'gazebo_and_rviz_launch.py'
            )
        )
    )

    nodes = [
        'world_tf_broadcaster.py',
        'tp4_mapping.py',
        'tp4_get_path.py',
        'tp4_follow_path.py'
    ]

    launch_nodes = []

    for executable in nodes:
        launch_nodes.append(
            Node(
                package='tp4_nodes',
                executable=executable,
                output='screen',
                parameters=[{'use_sim_time': True}]
            )
        )

    return LaunchDescription([gazebo] + launch_nodes)
