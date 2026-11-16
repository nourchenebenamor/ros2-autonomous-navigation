from launch import LaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import FindExecutable
from launch.actions import ExecuteProcess
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node
from launch.substitutions import FindExecutable, PathJoinSubstitution
import os

def generate_launch_description():

    # name of the urdf file for the robot
    urdf_name = "tp4_robot"

    # get the path of the tp4_description package (regarding the installation)
    pkg_share = FindPackageShare(package='tp4_description').find('tp4_description')

    # get the path to the rviz config file
    rviz_config_path = os.path.join(pkg_share, 'rviz/base.rviz')
    
    # get the path to the urdf file
    urdf_path = os.path.join(
        pkg_share,
       f'urdf/{urdf_name}.urdf'
    )
    
    # get the content of the urdf file into a string variable
    robot_desc:str = ""
    with open(urdf_path, 'r') as urdf_file:
        robot_desc = urdf_file.read()
        
    
    # get the path to the gazebo world
    gazebo_world_path = PathJoinSubstitution(
        [FindPackageShare('tp4_description'), 'gazebo', 'tp4_world.sdf']
    )

    # start gazebo sim
    gazebo_cmd = ExecuteProcess(
        cmd = [[
            FindExecutable(name="gz"),
            " sim ",
            gazebo_world_path,
            " -r", # run the simulation at start
        ]],
        shell = True
    )
    
    # start the sate publisher node (needed to display the robot with rviz)
    state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,  # to use gazebo time
            'robot_description': robot_desc,  # the content of the urdf file
        }]
    )

    # start rviz
    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{
            'use_sim_time': True,  # to use gazebo time
        }],
        arguments=['-d', rviz_config_path]  # to use the rviz configuration of the package
    )

    # start the ros2 <-> gazebo bridge
    # use the configuration yaml file to setup the bridge
    ros_gz_bridge_cmd = ExecuteProcess(
        cmd=[FindExecutable(name='ros2'),
            f"run ros_gz_bridge parameter_bridge  --ros-args -p config_file:={os.path.join(pkg_share, 'gazebo/ros_gz_bridge.yaml')}"
            ],
        output='screen',
        shell=True
    )
    

    commands = [
        # set the environment variable for gazebo to be able to find the models
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=FindPackageShare('tp4_description')),
        state_publisher_cmd,
        start_rviz_cmd,
        gazebo_cmd,
        ros_gz_bridge_cmd,
    ]

    return LaunchDescription(commands)