#!/usr/bin/env python3
"""Single launch: Gazebo + ROS/Gazebo bridges + TF + RViz + autonomous node."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('tp3_description')
    headless = LaunchConfiguration('headless')

    with open(os.path.join(pkg, 'urdf', 'tp3_robot.urdf'), encoding='utf-8') as f:
        description = f.read()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'tp3_description_launch.py')),
        launch_arguments={'headless': headless}.items())

    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/model/tp3_robot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ], output='screen')

    publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        parameters=[{'use_sim_time': True, 'robot_description': description}],
        output='screen')

    joints = Node(
        package='joint_state_publisher', executable='joint_state_publisher',
        parameters=[{'use_sim_time': True}], output='screen')

    rviz = Node(
        package='rviz2', executable='rviz2',
        arguments=['-d', os.path.join(pkg, 'rviz', 'tp3.rviz')],
        parameters=[{'use_sim_time': True}], output='screen')

    escape = Node(
        package='tp3_nodes', executable='escape_room',
        parameters=[{'use_sim_time': True}], output='screen')

    return LaunchDescription([
        DeclareLaunchArgument('headless', default_value='false'),
        gazebo, bridge, publisher, joints, rviz, escape,
    ])
