from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # Get the path of the tp4_nodes package
    tp4_nodes_dir = get_package_share_directory('tp4_nodes')

    # Launch the simulation, RViz, teleoperation and TF broadcaster
    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                tp4_nodes_dir,
                'launch',
                'teleop_launch.py'
            )
        )
    )

    # Start the mapping node
    mapping_node = Node(
        package='tp4_nodes',
        executable='tp4_mapping.py',
        name='tp4_mapping',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        simulation_launch,
        mapping_node
    ])
