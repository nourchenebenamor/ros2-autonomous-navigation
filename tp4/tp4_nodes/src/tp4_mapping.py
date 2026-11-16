#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan

def euler_from_quaternion(x, y, z, w):
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = 2.0 * (w * y - z * x)
    t2 = max(-1.0, min(1.0, t2))
    pitch_y = math.asin(t2)

    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z


class TP4Mapping(Node):

    def __init__(self):
        super().__init__('tp4_mapping')

        self.resolution = 0.25
        self.width = 56
        self.height = 56

        self.origin_x = -7.0
        self.origin_y = -7.0

        self.robot_pose = None
        self.lidar_scan = None

        self.grid = [50] * (self.width * self.height)

        self.map_publisher = self.create_publisher(
            OccupancyGrid, '/map', 10
        )

        self.pose_subscription = self.create_subscription(
            PoseStamped, '/pose', self.pose_callback, 10
        )

        self.lidar_subscription = self.create_subscription(
            LaserScan, '/lidar', self.lidar_callback, 10
        )

        self.map_msg = OccupancyGrid()
        self.map_msg.header.frame_id = 'world'
        self.map_msg.info.resolution = self.resolution
        self.map_msg.info.width = self.width
        self.map_msg.info.height = self.height

        self.map_msg.info.origin.position.x = self.origin_x
        self.map_msg.info.origin.position.y = self.origin_y
        self.map_msg.info.origin.orientation.w = 1.0

        self.timer = self.create_timer(2.0, self.publish_map)

        self.get_logger().info('TP4 mapping started')

    def pose_callback(self, msg):
        if msg.header.frame_id != 'my_world':
            return
        self.robot_pose = msg.pose

    def lidar_callback(self, msg):
        self.lidar_scan = msg
        self.update_obstacles()

    def world_to_cell(self, x, y):
        col = math.floor((x - self.origin_x) / self.resolution)
        row = math.floor((y - self.origin_y) / self.resolution)

        if 0 <= col < self.width and 0 <= row < self.height:
            return row * self.width + col

        return None

    
    def mark_free_path(self, x0, y0, x1, y1):
        # Parcourir le rayon LiDAR, même si son extrémité est hors carte.
        longueur = math.hypot(x1 - x0, y1 - y0)
        nb = max(1, math.ceil(longueur / (self.resolution / 2)))

        for i in range(nb):
            t = i / nb
            x = x0 + t * (x1 - x0)
            y = y0 + t * (y1 - y0)
            index = self.world_to_cell(x, y)

            if index is None:
                break
            if self.grid[index] != 100:
                self.grid[index] = 0

    def update_obstacles(self):
        if self.robot_pose is None or self.lidar_scan is None:
            return

        p = self.robot_pose.position
        q = self.robot_pose.orientation
        _, _, yaw = euler_from_quaternion(q.x, q.y, q.z, q.w)
        scan = self.lidar_scan
        robot_index = self.world_to_cell(p.x, p.y)

        for i, distance in enumerate(scan.ranges):
            if math.isnan(distance) or distance == -math.inf:
                continue
            if distance < scan.range_min:
                continue

            obstacle = math.isfinite(distance) and distance < scan.range_max
            d = distance if obstacle else scan.range_max
            if not math.isfinite(d) or d <= 0:
                continue

            angle = yaw + scan.angle_min + i * scan.angle_increment
            end_x = p.x + d * math.cos(angle)
            end_y = p.y + d * math.sin(angle)

            # Le rayon traverse un espace libre jusqu'à l'obstacle.
            self.mark_free_path(p.x, p.y, end_x, end_y)

            if obstacle:
                index = self.world_to_cell(end_x, end_y)
                if index is not None and index != robot_index:
                    self.grid[index] = 100

        # Le centre du robot doit rester sur une case libre.
        if robot_index is not None:
            self.grid[robot_index] = 0

    def update_frontiers(self):
        # Réinitialiser les anciennes frontières
        for i in range(len(self.grid)):
            if self.grid[i] == 120:
                self.grid[i] = 50

        # Chercher les cellules inconnues voisines d'une cellule libre
        for row in range(self.height):
            for col in range(self.width):
                index = row * self.width + col

                if self.grid[index] != 50:
                    continue

                neighbors = []

                if row > 0:
                    neighbors.append(index - self.width)
                if row < self.height - 1:
                    neighbors.append(index + self.width)
                if col > 0:
                    neighbors.append(index - 1)
                if col < self.width - 1:
                    neighbors.append(index + 1)

                for neighbor in neighbors:
                    if self.grid[neighbor] == 0:
                        self.grid[index] = 120
                        break

    def publish_map(self):
        self.update_frontiers()
        self.map_msg.header.stamp = self.get_clock().now().to_msg()
        self.map_msg.data = list(self.grid)
        self.map_publisher.publish(self.map_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TP4Mapping()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
