<div style="text-align: center">
    <h1>TP4 - Follow path</h1>
    <b>Polytech Angers</b> - Mobile Robotics
</div>

---
- [Advices](#advices)

---

At this step you should be able to map the maze, and generate a path to move to the closest frontier.

Now the idea it to follow a path when receiving one.

Create a new node named `tp4_follow_path.py` and a new launch file named `get_out_launch.py` that starts everything.

The node `tp4_follow_path.py` should publish the command according to the path processed in the previous step. The general idea:
- Explore all the frontiers until the exit has been found...

Once out of the maze, the node should publish a `True` value over a `/tp4/out` topic (`std_msgs/Bool` message) and stop the robot.

Here is an example of what is expected at the end:

![out](images/out.gif)

![out speedx5](images/out_x5.webm)

## Advices

- The size of the maze is known, use that to identify when the robot is out of the maze...
- You already did a similar work in the TP2, you may reuse some of your code...
- **Make it simple, you do not need thread or execution group...**