<div style="text-align: center">
    <h1>TP4 - Map the maze</h1>
    <b>Polytech Angers</b> - Mobile Robotics
</div>

---
- [Assumption](#assumption)
- [Tools](#tools)
  - [Occupancy grid map](#occupancy-grid-map)
  - [Advices](#advices)

---

At this step you should be able to move the robot in the maze and to get its position in the `world` frame.

As the robot is equipped with a LiDAR sensor, the idea will be to build a map of the maze. Usually, the position of the robot is processed via a localization algorithm, but to ease the work here, you are going to use the *ground truth* provided by gazebo : the pose of the robot is assumed to be known.

As you have the pose of the robot and the LiDAR data you will be able to build a map of the maze, that is a grid, and each cell of the grid you will note if this corresponds to an obstacle or a free space in the maze (world).

Objective: create a node named `tp4_mapping` that will provide every **two seconds** the current map of the maze. It will be considered that:
- The value 0 means there is no obstacle in this space in the world (will be displayed in white with rviz);
- The value 50 means an unknown space of the environment (will be displayed in grey with rviz);
- The value 100 means there is an obstacle (will be displayed in black with rviz);
- The value 120 means that this is an unknown space that can be reached via an empty cell (will be useful to generate a target position later, will be displayed in green with rviz).

You also need to write a `mapping_launch.py` launch file that will start the simulation, the rviz display (a new configuration, do not overwrite the one done for the world tf broadcaster), the mapping node and a way to move the robot (with the keyboard for instance).

Here are the expected nodes and topics:
```
docker@ros2:~/wdir/src/tp4/tp4_nodes/src$ ros2 topic list
[...]
/cmd_vel
/joint_states
/lidar
/map
/pose
docker@ros2:~/wdir/src/tp4/tp4_nodes/src$ ros2 node list
/robot_state_publisher
/ros_gz_bridge
/rviz2
/tf_broadcaster
/tp4_mapping
/transform_listener_impl_557878eae300
/turtle_teleop_key
```

And the result should be something like (moving the robot using the teleop key node):

![mapping](images/mapping.gif)

## Assumption

- To ease the mapping it can be assumed the LiDAR measurements are done at the last known pose of the robot;
- There are no outliers in the data set, each time an obstacle is detected it can directly be marked down in the map.
- A *green cell* is a frontier between a free cell (white) and an unknown cell (gray).

## Tools

### Occupancy grid map

To store a map, classically occupancy grids are considered (each value of the grid cell corresponds to the probability to represent an obstacle in the environment). In ros2 it exists standard structures for occupancy grid : https://docs.ros2.org/foxy/api/nav_msgs/msg/OccupancyGrid.html.

The characteristics of the map built in the example are:
- resolution = 0.25 (the size of a cell in m)
- width = 40 (number of x cells)
- height = 40 (number of y cells)
- frame_id = "world"

Use the data value indicated previously to be able to have a correct display with rviz.

### Advices

Your node should: listen and store the current pose of the robot, listen for LiDAR data, when LiDAR data are available, update the map by:
- Writing down all the detected obstacles;
- Free the path between the detected obstacles and the robot.

**Do it step by step!**
- [1] Publish a dumb map every two second and display it on rviz;
- [2] Write down the detected obstacles on the map;
- [3] Free the path between the robot and the obstacles;
- [4] Add the frontier cells (unknown cell that can be reach via empty cells);

To write down the detected obstacles on the map you may need to be able to convert quaternions from the pose to a robot orientation (euler):

```py
def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = atan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = asin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = atan2(t3, t4)
    
    return roll_x, pitch_y, yaw_z # in radians
```

To free the path from the robot to the detected obstacle, you may need to test the intersection between two segments:

Be four distinct points of $R^2$, $a = (a_1; a_2)$, $b = (b_1; b_2)$, $c= (c_1; c_2)$ and $d = (d_1; d_2)$. We have

$$Seg(a,b) \cap Seg(c,d) = \emptyset \Leftrightarrow \\ det(a-c|d-c) \times det(b-c|d-c) > 0 \vee \\ det(c-a|b-a) \times det(d-a|b-a) > 0 \vee \\ \left[a \cup b\right] \cap \left[c \cup d\right] = \emptyset$$

and 

$$Seg(a,b) \cap Seg(c,d) \neq \emptyset \Leftrightarrow \\ det(a-c|d-c) \times det(b-c|d-c) \leq 0 \land  \\ det(c-a|b-a) \times det(d-a|b-a) \leq 0 \land \\ \left[a \cup b\right] \cap \left[c \cup d\right] \neq \emptyset$$

with 

$$det(a-b|c-b) = (a_1-b_1)(c_2-b_2)-(a_2-b_2)(c_1-b_1)$$ 

Note that $\vee$ means OR and $\land$ means AND.

One can be inspired by the mapping part of https://gitlab.u-angers.fr/cours/mobile_robotic_student/-/blob/master/documents/EXPLORATION/EXPLORATION.pdf (only the mapping approach, you do not have a cost map here!).


<!-- TO handle Latex in the pdf-->
<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
<script type="text/x-mathjax-config">
        MathJax.Hub.Config({ tex2jax: {inlineMath: [['$', '$']]}, messageStyle: "none" });
</script>