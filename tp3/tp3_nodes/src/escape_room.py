#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from visualization_msgs.msg import Marker
from tf2_ros import TransformBroadcaster

from escape_geometry import (clamp, wrap_angle, lidar_hits, enclosed_from_center,
                             find_door, local_to_odom, normal_to_odom,
                             wall_progress, wall_lateral)


class EscapeRoom(Node):
    STAGING_DISTANCE = 1.8       
    EXIT_CLEARANCE = 1.70        
    TIMEOUT = 2.5                

    def __init__(self):
        super().__init__('escape_room')
        self.state = 'IDLE'
        self.start_requested = False
        self.scan = None
        self.pose = None         
        self.scan_time = None
        self.odom_time = None
        self.door = None         
        self.outward = None      
        self.stage = None       
        self.last_message = 0.0
        self.last_markers = 0.0

        self.create_subscription(Bool, '/tp3/start', self.on_start, 10)
        self.create_subscription(LaserScan, '/lidar', self.on_scan, 10)
        self.create_subscription(
            Odometry, '/model/tp3_robot/odometry', self.on_odom, 10)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.done_pub = self.create_publisher(Bool, '/tp3/finish', 10)
        marker_qos = QoSProfile(depth=10,
                                durability=DurabilityPolicy.TRANSIENT_LOCAL,
                                reliability=ReliabilityPolicy.RELIABLE)
        self.marker_pub = self.create_publisher(
            Marker, '/tp3/debug_marker', marker_qos)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.create_timer(0.1, self.step)
        self.get_logger().info('READY: wait for /lidar and odometry; then send /tp3/start=True')

    def on_start(self, message):
        if not message.data:
            return
        if self.state != 'IDLE':
            self.get_logger().warn(f'START ignored: state={self.state}; relaunch for a new run')
            return
        self.start_requested = True
        self.get_logger().info('START received; searching for the 2m door')

    def on_scan(self, message):
        self.scan = message
        self.scan_time = time.monotonic()

    def on_odom(self, message):
        p = message.pose.pose.position
        q = message.pose.pose.orientation
        yaw = math.atan2(2 * (q.w * q.z + q.x * q.y),
                         1 - 2 * (q.y * q.y + q.z * q.z))
        self.pose = (p.x, p.y, yaw)
        self.odom_time = time.monotonic()

        
        transform = TransformStamped()
        transform.header.stamp = message.header.stamp
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_link'
        transform.transform.translation.x = p.x
        transform.transform.translation.y = p.y
        transform.transform.translation.z = 0.0
        transform.transform.rotation = q
        self.tf_broadcaster.sendTransform(transform)

    def move(self, linear=0.0, angular=0.0):
        cmd = Twist()
        cmd.linear.x = float(linear)
        cmd.angular.z = float(angular)
        self.cmd_pub.publish(cmd)

    def warn_once(self, text):
        t = time.monotonic()
        if t - self.last_message > 2.0:
            self.get_logger().warn(text)
            self.last_message = t

    def marker(self, xy, number, rgb):
        m = Marker()
        m.header.frame_id = 'odom'
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = 'detected_door'
        m.id = number
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        m.pose.position.x = float(xy[0])
        m.pose.position.y = float(xy[1])
        m.pose.position.z = 0.2
        m.pose.orientation.w = 1.0
        m.scale.x = m.scale.y = m.scale.z = 0.23
        m.color.r, m.color.g, m.color.b = rgb
        m.color.a = 1.0
        self.marker_pub.publish(m)

    def show_door(self, detection):
        if self.pose is None:
            return
        p1, p2, centre, _, _ = detection
        self.marker(local_to_odom(p1, self.pose), 1, (1.0, 0.9, 0.0))
        self.marker(local_to_odom(p2, self.pose), 2, (1.0, 0.9, 0.0))
        self.marker(local_to_odom(centre, self.pose), 3, (0.0, 1.0, 0.1))

    def valid_data(self):
        now = time.monotonic()
        return (self.scan is not None and self.pose is not None and
                self.scan_time is not None and self.odom_time is not None and
                now - self.scan_time < self.TIMEOUT and
                now - self.odom_time < self.TIMEOUT)

    def finish(self):
        self.move()
        self.state = 'DONE'
        self.done_pub.publish(Bool(data=True))
        self.get_logger().info('DONE: whole robot is outside; /tp3/finish=True')

    def step(self):
        if self.state == 'DONE':
            self.move()  # keep commanded speed at zero
            return

        if self.state == 'IDLE':
            if not self.start_requested:
                self.move()
                if self.valid_data() and time.monotonic() - self.last_markers > 2.0:
                    self.last_markers = time.monotonic()
                    detection = find_door(self.scan)
                    if detection:
                        self.show_door(detection)
                return

            if not self.valid_data():
                self.move()
                self.warn_once('Waiting for valid /lidar and odometry')
                return

            hits = lidar_hits(self.scan)
            percentage = 100.0 * sum(hits) / max(1, len(hits))
            if not enclosed_from_center(self.scan):
                self.move()
                # No incorrect "finished" claim for a misconfigured LiDAR.
                self.state = 'NOT_INSIDE'
                self.get_logger().warn(
                    f'No surrounding walls detected ({percentage:.1f}% valid rays). '
                    'Robot may already be outside OR LiDAR/world is incorrect. '
                    'NO MOVEMENT. Check /lidar and room in Gazebo.')
                return

            detection = find_door(self.scan)
            if detection is None:
                self.move()
                self.warn_once(f'Walls detected ({percentage:.1f}% rays), '
                               'but no 2m door found. Robot remains stopped.')
                return

            self.show_door(detection)
            _, _, centre, local_normal, width = detection
            self.door = local_to_odom(centre, self.pose)
            self.outward = normal_to_odom(local_normal, self.pose[2])
            nx, ny = self.outward
            self.stage = (self.door[0] - self.STAGING_DISTANCE * nx,
                          self.door[1] - self.STAGING_DISTANCE * ny)
            self.state = 'APPROACH'
            self.start_requested = False
            self.get_logger().info(
                f'DOOR: width={width:.2f} m; centre={self.door}; '
                f'staging_point={self.stage}; state=APPROACH')
            return

        if self.state == 'NOT_INSIDE':
            self.move()
            return

        if not self.valid_data():
            self.move()
            self.warn_once('Lost /lidar or odometry: safety STOP')
            return

        x, y, yaw = self.pose
        if self.state == 'APPROACH':
            dx, dy = self.stage[0] - x, self.stage[1] - y
            distance = math.hypot(dx, dy)
            if distance < 0.12:
                self.move()
                self.state = 'ALIGN'
                self.get_logger().info('Staging point reached; state=ALIGN')
                return
            error = wrap_angle(math.atan2(dy, dx) - yaw)
            turn = clamp(1.2 * error, -0.5, 0.5)
            speed = 0.0 if abs(error) > 0.3 else clamp(0.7 * distance, 0.1, 0.3)
            self.move(speed, turn)
            return

        if self.state == 'ALIGN':
            desired_yaw = math.atan2(self.outward[1], self.outward[0])
            error = wrap_angle(desired_yaw - yaw)
            if abs(error) < 0.035:
                self.move()
                self.state = 'CROSS'
                self.get_logger().info('Robot aligned with door; state=CROSS')
            else:
                self.move(0.0, clamp(1.1 * error, -0.4, 0.4))
            return

        if self.state == 'CROSS':
            progress = wall_progress((x, y), self.door, self.outward)
            if progress >= self.EXIT_CLEARANCE:
                self.finish()
                return
            lateral = wall_lateral((x, y), self.door, self.outward)
            desired_yaw = math.atan2(self.outward[1], self.outward[0])
            heading_error = wrap_angle(desired_yaw - yaw)
            turn = clamp(1.3 * heading_error - 0.5 * lateral, -0.24, 0.24)
            self.move(0.23, turn)
            return


def main(args=None):
    rclpy.init(args=args)
    node = EscapeRoom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.move()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
