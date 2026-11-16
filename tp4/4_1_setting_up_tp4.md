<div style="text-align: center">
    <h1>TP4 - Set up</h1>
    <b>Polytech Angers</b> - Mobile Robotics
</div>

---

For this work you will need the package `tp4_description` that handles the simulation and robot descriptions. Have a look to the files and check the code that is inside (you have a `readme.md` file that presents the different files and directories).

## Set-up TP4 meta-package

For large ROS2 project, it is a good practice to organize your workspace into meta-packages (packages that will contain packages). We are not doing that as I did not managed to make it work with colcon and python nodes... But you must do *as if* you had a metapackage: create a new directory named `tp4` and get the `tp4_description` archive and put the source code in the tp4 package. You should have something like:

```
tp4
└── tp4_description
    ├── CMakeLists.txt
    ├── package.xml
    └── ...
```

Build the `tp4_description` package and you should be able to start the `gazebo_and_rviz_launch.py` launch file.

You should have a `rviz` window with the robot and LiDAR data.

![tp4_setup_rviz.png](images/tp4_setup_rviz.png)

When listing the running node you should have (among others):
```
/robot_state_publisher
/ros_gz_bridge
/rviz2
[...]
```

and for the topics
```
/clock
/cmd_vel
/joint_states
/lidar
/robot_pose_array
[...]
```

Note that the launch file starts gazebo in server mode (without graphic user interface), but gazebo is indeed started to simulate the robot (and working correctly since you have the LiDAR data that is simulated by gazebo). You can do a `ps -aux | grep gz` command to be sure that gazebo is running.

When the given `tp4_description` package runs correctly, you can go to the next step.

## Create a new package

Create a new package named `tp4_nodes` inside the `tp4` meta-package. You will code your nodes into that package.

In that package, create a `launch` directory to put your launch file, and an `rviz` directory to put your rviz2 configurations. 

### Adding launch file `teleop_launch.py`

In your launch directory, create a launch file named `teleop_launch.py`. 

In that launch file, call the launch file of the `tp4_description` package:

```py
tp4_description_launch_prefix = get_package_share_directory('tp4_description')
    
gazebo_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource([tp4_description_launch_prefix,
                                    '/launch/gazebo_and_rviz_launch.py']),
    launch_arguments={}.items()
)
```

Compile and install your package, you should be able to start the simulation by doing :

```bash
ros2 launch tp4_nodes teleop_launch.py
```

### Tele-operating the robot

In your launch file, add a node that is able to control the robot using the `turtle_teleop_key` node of the `turtlesim` package. Now, running the launch file, you should be able to move your robot in the maze.

![tp4_teleop.gif](images/tp4_teleop.gif)

Remark: as we are using the simulator, do not forget to set the `use_sim_time` option with your node:

```py
parameters=[{
    'use_sim_time': True,
}],
```

From now, the objective will be to create a control node that will make the robot to move out of the maze. To do that, you are going to follow several steps...

> **Disclaimer:** the proposed approach does not pretend to be the best approach to get out of a maze, it is a step by step approach designed to introduce robotic and ROS2 notions and tools. **You have to follow those steps** at first, **then** if you want to code a better node, be my guest :-)