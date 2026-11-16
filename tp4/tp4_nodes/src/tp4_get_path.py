#!/usr/bin/env python3


import heapq
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid, Path


class TP4GetPath(Node):
    def __init__(self):
        super().__init__('tp4_get_path')
        self.map_msg = None
        self.robot_pose = None
        self.blocked_frontiers = set()

        self.create_subscription(OccupancyGrid, '/map', self.map_callback, 10)
        self.create_subscription(PoseStamped, '/pose', self.pose_callback, 10)
        self.create_subscription(PoseStamped, '/tp4/blocked', self.blocked_callback, 10)
        self.path_pub = self.create_publisher(Path, '/tp4/path', 10)
        self.get_logger().info('TP4 get path started')

    def map_callback(self, msg):
        self.map_msg = msg
        self.compute_path()

    def pose_callback(self, msg):
        if msg.header.frame_id == 'my_world':
            self.robot_pose = msg.pose

    def blocked_callback(self, msg):
        if self.map_msg is None:
            return
        pos = msg.pose.position
        cell = self.world_to_cell(pos.x, pos.y, self.map_msg.info)
        if cell is not None:
            self.blocked_frontiers.add(cell)
            self.compute_path()

    def world_to_cell(self, x, y, info):
        col = math.floor((x - info.origin.position.x) / info.resolution)
        row = math.floor((y - info.origin.position.y) / info.resolution)
        if 0 <= row < info.height and 0 <= col < info.width:
            return row, col
        return None

    def cell_to_world(self, row, col, info):
        x = info.origin.position.x + (col + 0.5) * info.resolution
        y = info.origin.position.y + (row + 0.5) * info.resolution
        return x, y

    def neighbors(self, row, col, width, height):
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = row + dr, col + dc
            if 0 <= nr < height and 0 <= nc < width:
                yield nr, nc

    def near_wall(self, row, col, width, height, data):
        """Retourne le nombre de cases occupées autour d'une case."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r, c = row + dr, col + dc
                if 0 <= r < height and 0 <= c < width:
                    if data[r * width + c] == 100:
                        count += 1
        return count

    def compute_path(self):
        if self.map_msg is None or self.robot_pose is None:
            return

        msg = self.map_msg
        info = msg.info
        width, height = info.width, info.height
        data = msg.data

        start = self.world_to_cell(
            self.robot_pose.position.x, self.robot_pose.position.y, info
        )
        if start is None or len(data) != width * height:
            self.publish_empty_path()
            return

        if data[start[0] * width + start[1]] != 0:
            self.get_logger().warn(
                'Robot not on a free cell; waiting for an updated map.',
                throttle_duration_sec=2.0
            )
            self.publish_empty_path()
            return

        distances = {start: 0.0}
        previous = {}
        queue = [(0.0, start)]
        target = None

        while queue:
            distance, current = heapq.heappop(queue)
            if distance > distances[current]:
                continue

            row, col = current
            if data[row * width + col] == 120:
                target = current
                break

            for nr, nc in self.neighbors(row, col, width, height):
                value = data[nr * width + nc]
                if value not in (0, 120):
                    continue
                if value == 120 and (nr, nc) in self.blocked_frontiers:
                    continue

                # Les murs proches coûtent plus cher, mais ne bloquent pas le couloir.
                cost = 1.0
                if value == 0:
                    cost += self.near_wall(nr, nc, width, height, data)

                nxt = (nr, nc)
                new_distance = distance + cost
                if new_distance < distances.get(nxt, float('inf')):
                    distances[nxt] = new_distance
                    previous[nxt] = current
                    heapq.heappush(queue, (new_distance, nxt))

        if target is None:
            self.get_logger().warn(
                'No reachable frontier found.', throttle_duration_sec=2.0
            )
            self.publish_empty_path()
            return

        cells = [target]
        while cells[-1] != start:
            cells.append(previous[cells[-1]])
        cells.reverse()

        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'world'
        for row, col in cells:
            x, y = self.cell_to_world(row, col, info)
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = 0.05
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)

        self.path_pub.publish(path)

    def publish_empty_path(self):
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'world'
        self.path_pub.publish(path)


def main(args=None):
    rclpy.init(args=args)
    node = TP4GetPath()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
