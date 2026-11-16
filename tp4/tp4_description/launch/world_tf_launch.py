
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    description_dir = get_package_share_directory('tp4_description')
    nodes_dir = get_package_share_directory('tp4_nodes')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                description_dir,
                'launch',
                'gazebo_and_rviz_launch.py'
            )
        )
    )

    world_tf_broadcaster = Node(
        package='tp4_nodes',
        executable='world_tf_broadcaster.py',
        name='world_tf_broadcaster',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    teleop_node = Node(
        package='turtlesim',
        executable='turtle_teleop_key',
        name='teleop',
        output='screen',
        prefix='xterm -e',
        remappings=[('/turtle1/cmd_vel', '/cmd_vel')],
        parameters=[{'use_sim_time': True}],
        )
    

    return LaunchDescription([
        gazebo_launch,
        world_tf_broadcaster,
        teleop_node
    ])
