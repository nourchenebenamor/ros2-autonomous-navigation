<div style="text-align: center">
    <h1>TP4 - Path to closest frontier</h1>
    <b>Polytech Angers</b> - Mobile Robotics
</div>

---
- [Work to do](#work-to-do)
- [Dijkstra](#dijkstra)
- [Advices - Instructions](#advices---instructions)

---

At this step you should be able to map the maze.

Now the idea it to generate a path from the current position to the closest frontier each time you received a map.

Here is an example of the path displayed with rviz:

![frontier](images/frontier_path.png)

## Work to do

Create a new node named `tp4_get_path.py` that publishes a `/tp4/path` topic. You should have:
```
ros2 topic list -t
[...]
/tp4/path [nav_msgs/msg/Path]
[...]
```
Create a new launch file named `path_launch.py` that allows to test this new node (should start everything to be able to test the node and display the path with a new configuration of `rviz` that displays the computed path).


## Dijkstra

To find a path in a grid cell we can use the Dijkstra algorithm (thus we will also have the shortest path). You can have some information about Dijkstra algorithm here : https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm, and you can also run the script https://gitlab.u-angers.fr/cours/mobile_robotic_student/-/blob/master/tp_a_star/shortest_path_ui.py to have a user interface that explains how the Dijkstra can be implemented on a grid.


## Advices - Instructions

- **The path should be from the robot to the frontier**
- You can use the markers to display objects in `rviz`
- Be careful with the frames of the pose
- You can create a new grid from the map
- You can create a new `Cell` class to store everything you need in a grid cell
- Do it step by step, test your algorithm with a known grid for instance
- Make it simple, you do not need thread or execution group...
