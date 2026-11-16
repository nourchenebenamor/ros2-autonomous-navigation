# These import statements pull in some Python launch modules.
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import FindExecutable
from launch.actions import ExecuteProcess

# The launch description itself begins here:
def generate_launch_description():
    ld = LaunchDescription()
    
    # creating the node
    turtle_node = Node( package='turtlesim',
                        namespace='turtlesim1',
                        executable='turtlesim_node',
                        name='sim1'
                    )

    teleop = Node(package='tp1',
                        namespace='turtlesim1',
                        executable='my_teleop.py',
                        name='teleop',
                        prefix=["xterm -e"],
                        remappings=[ # rename /turtle1/cmd_vel to /turtlesim1/caroline/cmd_vel
                        ('/turtle1/cmd_vel', '/turtlesim1/caroline/cmd_vel')]
                )

    # creating a process to execute after starting the node
    ep = ExecuteProcess(
            cmd = [[
                FindExecutable(name="ros2"),
                " service call ",
                "/turtlesim1/spawn ",
                "turtlesim/srv/Spawn ",
                '"{x: 2, y: 2, theta: 0.2, name: \'caroline\'}"',
            ]],
            shell = True
        )
    # add the node
    ld.add_action(turtle_node)
    # add the process
    ld.add_action(ep)
    ld.add_action(teleop)

    return ld