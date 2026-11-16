#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node

from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from rclpy.action import ActionServer
from tp1.action import Path

class FollowPath(Node):

    def __init__(self):
        super().__init__('path_action_server')

        self.get_logger().info(
            'Beginning path_action_server, shut down with CTRL-C'
        )
        self.pose_group = MutuallyExclusiveCallbackGroup()
        self.action_group = MutuallyExclusiveCallbackGroup()

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.path_in_progress = False

        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.pose_group
        )

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.action_server = ActionServer(
            self,
            Path,
            '/path',
            self.execute_callback,
            callback_group=self.action_group
        )




    def pose_callback(self, msg):
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta

    def go_to_point(self, target_x, target_y):

        while True:

            dx = target_x - self.x
            dy = target_y - self.y

            distance = math.sqrt(dx**2 + dy**2)

            if distance < 0.1:
                break

            target_angle = math.atan2(dy, dx)

            angle_error = target_angle - self.theta

            angle_error = math.atan2(
                math.sin(angle_error),
                math.cos(angle_error)
            )

            cmd = Twist()

            if abs(angle_error) > 0.1:
                cmd.linear.x = 0.0
                cmd.angular.z = angle_error
            else:
                cmd.linear.x = 1.0
                cmd.angular.z = 0.0

            self.cmd_vel_publisher.publish(cmd)

            time.sleep(0.05)

        # Arrêter la tortue
        cmd = Twist()
        self.cmd_vel_publisher.publish(cmd)

    def execute_callback(self, goal_handle):

        if self.path_in_progress:
            self.get_logger().warn(
                "A path is already being followed"
            )

            goal_handle.abort()

            result = Path.Result()
            result.final_point.x = self.x
            result.final_point.y = self.y
            result.final_point.z = 0.0

            return result

        self.path_in_progress = True

        self.get_logger().info("Executing goal...")

        path = goal_handle.request.path

        for point in path:

            self.get_logger().info(
                f"Going to point ({point.x}, {point.y})"
            )

            self.go_to_point(point.x, point.y)

            feedback = Path.Feedback()

            feedback.reached_point.x = self.x
            feedback.reached_point.y = self.y
            feedback.reached_point.z = 0.0

            goal_handle.publish_feedback(feedback)

        result = Path.Result()

        result.final_point.x = self.x
        result.final_point.y = self.y
        result.final_point.z = 0.0

        goal_handle.succeed()

        self.path_in_progress = False

        self.get_logger().info("...Finished")

        return result


def main(args=None):
    rclpy.init(args=args)

    node = FollowPath()

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()