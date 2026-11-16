#!/usr/bin/python3

import sys
import tty
import termios
import random

import rclpy
from rclpy.node import Node

from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter
from rcl_interfaces.msg import ParameterValue
from std_srvs.srv import Empty
from geometry_msgs.msg import Twist


def getkey():
    """Get one keyboard key without waiting for Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch


class MyTeleop(Node):

    def __init__(self):
        super().__init__('my_teleop')

        # Client to change TurtleSim background color
        self.parameter_client = self.create_client(
            SetParameters,
            '/turtlesim1/sim1/set_parameters'
        )
        self.parameter_client.wait_for_service()

        # Publisher for turtle movement
        # This topic will be remapped in my_launch.py
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Client to clear the path
        self.clear_client = self.create_client(
            Empty,
            '/turtlesim1/clear'
        )
        self.clear_client.wait_for_service()

        self.get_logger().info('Starting the teleop node')
        self.get_logger().info(
            "The commands:\n"
            "        'o' to move forward\n"
            "        'l' to move backward\n"
            "        'k' to turn left\n"
            "        'm' to turn right\n"
            "        'c' to clear the path\n"
            "        'p' to randomly change background color\n"
            "        'q' to quit"
        )


def main(args=None):
    rclpy.init(args=args)

    node = MyTeleop()

    try:
        while rclpy.ok():

            key = getkey()

            msg = Twist()

            # Move forward
            if key == 'o':
                msg.linear.x = 1.0

            # Move backward
            elif key == 'l':
                msg.linear.x = -1.0

            # Turn left
            elif key == 'k':
                msg.angular.z = 1.0

            # Turn right
            elif key == 'm':
                msg.angular.z = -1.0

            # Clear path
            elif key == 'c':
                request = Empty.Request()
                node.clear_client.call_async(request)

            # Change background color randomly
            elif key == 'p':

                params = []

                for name in [
                    'background_r',
                    'background_g',
                    'background_b'
                ]:

                    param = Parameter()
                    param.name = name

                    param.value = ParameterValue(
                        type=2,
                        integer_value=random.randint(0, 255)
                    )

                    params.append(param)

                request = SetParameters.Request()
                request.parameters = params

                node.parameter_client.call_async(request)

            # Quit
            elif key == 'q':
                break

            # Publish movement command
            node.publisher_.publish(msg)

    finally:
        node.get_logger().info('Stopping the node...')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()