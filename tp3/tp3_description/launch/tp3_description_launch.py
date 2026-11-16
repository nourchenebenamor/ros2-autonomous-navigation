#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                            SetEnvironmentVariable)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg = get_package_share_directory('tp3_description')
    world = os.path.join(pkg, 'gazebo', 'tp3_world.sdf')
    resources = os.pathsep.join(filter(None, [pkg, os.environ.get('GZ_SIM_RESOURCE_PATH', '')]))
    headless = LaunchConfiguration('headless')
    return LaunchDescription([
        DeclareLaunchArgument('headless', default_value='false',
                              description='true: run Gazebo without its GUI'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resources),
        ExecuteProcess(cmd=['gz', 'sim', '-r', world], output='screen',
                       condition=UnlessCondition(headless)),
        ExecuteProcess(cmd=['gz', 'sim', '-r', '-s', world], output='screen',
                       condition=IfCondition(headless)),
    ])
