from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    tp4_description_launch_prefix = get_package_share_directory(
        'tp4_description'
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                tp4_description_launch_prefix,
                '/launch/gazebo_and_rviz_launch.py'
            ]
        ),
        launch_arguments={}.items()
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

    my_pkg_dir = get_package_share_directory('tp4_nodes')

    tf_broadcaster = Node(
        package='tp4_nodes',
        executable='world_tf_broadcaster.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        gazebo_launch,
        teleop_node,
        tf_broadcaster
    ])