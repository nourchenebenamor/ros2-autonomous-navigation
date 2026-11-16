
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # Get the path of the tp4_nodes package
    tp4_nodes_dir = get_package_share_directory('tp4_nodes')

    # Launch the simulation and mapping
    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                tp4_nodes_dir,
                'launch',
                'mapping_launch.py'
            )
        )
    )

    # Start the node that computes the shortest path
    path_node = Node(
        package='tp4_nodes',
        executable='tp4_get_path.py',
        name='tp4_get_path',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        mapping_launch,
        path_node
    ])
