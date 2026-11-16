from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess


def generate_launch_description():

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim'
    )

    follow_path_node = Node(
        package='tp1',
        executable='follow_path.py',
        name='path_action_server'
    )

    send_goal = ExecuteProcess(
        cmd=[
            'ros2', 'action', 'send_goal',
            '/path',
            'tp1/action/Path',
            '{path: [{x: 5.0, y: 5.0, z: 0.0}, '
            '{x: 6.0, y: 5.0, z: 0.0}, '
            '{x: 7.0, y: 4.0, z: 0.0}, '
            '{x: 7.0, y: 2.0, z: 0.0}, '
            '{x: 6.0, y: 1.0, z: 0.0}, '
            '{x: 1.0, y: 1.0, z: 0.0}, '
            '{x: 1.0, y: 5.0, z: 0.0}, '
            '{x: 3.0, y: 5.0, z: 0.0}, '
            '{x: 5.0, y: 7.0, z: 0.0}, '
            '{x: 6.0, y: 7.0, z: 0.0}, '
            '{x: 5.0, y: 5.0, z: 0.0}]}',
            '--feedback'
        ],
        output='screen'
    )

    return LaunchDescription([
        turtlesim_node,
        follow_path_node,
        send_goal
    ])