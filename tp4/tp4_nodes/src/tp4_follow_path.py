#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import OccupancyGrid, Path
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


class TP4FollowPath(Node):
    def __init__(self):
        super().__init__('tp4_follow_path')
        self.path = []
        self.index = 0
        self.robot_pose = None
        self.map_msg = None
        self.scan = None
        self.finished = False
        self.exit_count = 0
        self.best_distance = None
        self.last_progress = None

        self.create_subscription(Path, '/tp4/path', self.path_callback, 10)
        self.create_subscription(PoseStamped, '/pose', self.pose_callback, 10)
        self.create_subscription(OccupancyGrid, '/map', self.map_callback, 10)
        self.create_subscription(LaserScan, '/lidar', self.lidar_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.out_pub = self.create_publisher(Bool, '/tp4/out', 10)
        self.blocked_pub = self.create_publisher(PoseStamped, '/tp4/blocked', 10)
        self.create_timer(0.1, self.move_robot)
        self.get_logger().info('TP4 follow path started')

    def path_callback(self, msg):
        if self.finished:
            return
        if not msg.poses:
            if self.index >= len(self.path):
                self.path = []
                self.index = 0
            return
        # Garder le chemin actuel, tant qu'il est encore utilisable.
        if self.index < len(self.path) and not self.path_blocked():
            return
        self.path = msg.poses
        self.index = 1 if len(self.path) > 1 else 0
        self.best_distance = None
        self.last_progress = None

    def pose_callback(self, msg):
        if msg.header.frame_id == 'my_world':
            self.robot_pose = msg.pose

    def map_callback(self, msg):
        self.map_msg = msg
        if self.path and self.index < len(self.path) and self.path_blocked():
            self.cancel_path('Obstacle discovered on the path')

    def lidar_callback(self, msg):
        self.scan = msg

    def path_blocked(self):
        if self.map_msg is None or not self.path:
            return False
        info = self.map_msg.info
        data = self.map_msg.data
        if len(data) != info.width * info.height:
            return False
        # Examiner seulement les prochains points. Le dernier peut être inconnu.
        for i in range(self.index, min(self.index + 3, len(self.path))):
            p = self.path[i].pose.position
            col = math.floor((p.x - info.origin.position.x) / info.resolution)
            row = math.floor((p.y - info.origin.position.y) / info.resolution)
            if not (0 <= row < info.height and 0 <= col < info.width):
                return True
            value = data[row * info.width + col]
            if value == 100 or (value != 0 and i != len(self.path) - 1):
                return True
        return False

    def obstacle_ahead(self):
        if self.scan is None:
            return False
        for i, dist in enumerate(self.scan.ranges):
            angle = self.scan.angle_min + i * self.scan.angle_increment
            if abs(angle) < 0.35 and math.isfinite(dist):
                if self.scan.range_min <= dist < 0.32:
                    return True
        return False

    def cancel_path(self, reason):
        goal = None
        if self.path:
            goal = PoseStamped()
            goal.header.frame_id = 'world'
            goal.header.stamp = self.get_clock().now().to_msg()
            goal.pose.position = self.path[-1].pose.position
            goal.pose.orientation.w = 1.0
            self.get_logger().warn(reason)
        self.path = []
        self.index = 0
        self.best_distance = None
        self.last_progress = None
        self.cmd_pub.publish(Twist())
        if goal is not None:
            self.blocked_pub.publish(goal)

    def move_robot(self):
        cmd = Twist()
        if self.robot_pose is None:
            self.cmd_pub.publish(cmd)
            return

        x = self.robot_pose.position.x
        y = self.robot_pose.position.y

        # Bords du labyrinthe : [-5.5, 4.5] sur les deux axes.
        # Attendre que le centre du robot les depasse de 30 cm.
        dehors = x < -5.8 or x > 4.8 or y < -5.8 or y > 4.8
        self.exit_count = self.exit_count + 1 if dehors else 0
        if self.exit_count >= 5 and not self.finished:
            self.finished = True
            self.get_logger().info('Robot out of the maze!')

        if self.finished:
            self.cmd_pub.publish(cmd)
            self.out_pub.publish(Bool(data=True))
            return

        if not self.path:
            self.cmd_pub.publish(cmd)
            return

        while self.index < len(self.path):
            target = self.path[self.index].pose.position
            dx = target.x - x
            dy = target.y - y
            distance = math.hypot(dx, dy)
            if distance < 0.12:
                self.index += 1
                self.best_distance = None
                self.last_progress = None
            else:
                break

        if self.index >= len(self.path):
            self.cmd_pub.publish(cmd)
            return

        q = self.robot_pose.orientation
        yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z)
        )
        angle = math.atan2(dy, dx)
        error = math.atan2(math.sin(angle - yaw), math.cos(angle - yaw))
        now = self.get_clock().now().nanoseconds / 1e9

        if abs(error) > 0.2:
            cmd.angular.z = 0.5 if error > 0 else -0.5
            self.last_progress = now  # Ne pas compter le temps passé à tourner.
        else:
            if self.scan is None:
                self.cmd_pub.publish(Twist())
                return
            if self.obstacle_ahead():
                self.cancel_path('Obstacle too close in front of the robot')
                return

            if self.best_distance is None or distance < self.best_distance - 0.02:
                self.best_distance = distance
                self.last_progress = now
            if self.last_progress is not None and now - self.last_progress > 4.0:
                self.cancel_path('Robot not moving: requesting another path')
                return
            cmd.linear.x = 0.1

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = TP4FollowPath()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
