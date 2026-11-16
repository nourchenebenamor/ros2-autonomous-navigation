import math


def wrap_angle(a):
    return math.atan2(math.sin(a), math.cos(a))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def lidar_hits(scan):
    return [math.isfinite(r) and scan.range_min <= r < scan.range_max - 0.02
            for r in scan.ranges]


def scan_point(scan, index):
    r = scan.ranges[index]
    theta = scan.angle_min + index * scan.angle_increment
    return (r * math.cos(theta), r * math.sin(theta))


def enclosed_from_center(scan):
   
    points = [scan_point(scan, i) for i, hit in enumerate(lidar_hits(scan)) if hit]
    if len(points) < 30:
        return False
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    return min_x < -2.0 and max_x > 2.0 and min_y < -2.0 and max_y > 2.0


def opening_edges(scan):
    
    hit = lidar_hits(scan)
    n = len(hit)
    if n < 10 or not any(hit):
        return []
    openings = []
    for i in range(n):
        if hit[(i - 1) % n] and not hit[i]:
            j = i
            while not hit[j]:
                j = (j + 1) % n
            count = (j - i) % n
            if count >= 5:
                openings.append(((i - 1) % n, j, count))
    return openings


def find_door(scan):
    
    candidates = []
    for i, j, _ in opening_edges(scan):
        p1 = scan_point(scan, i)
        p2 = scan_point(scan, j)
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        width = math.hypot(dx, dy)
        if not (1.45 <= width <= 2.70):
            continue
        cx = (p1[0] + p2[0]) / 2
        cy = (p1[1] + p2[1]) / 2
        
        nx, ny = -dy / width, dx / width
        if nx * cx + ny * cy < 0:
            nx, ny = -nx, -ny
        score = abs(width - 2.0) + 0.02 * math.hypot(cx, cy)
        candidates.append((score, p1, p2, (cx, cy), (nx, ny), width))
    if not candidates:
        return None
    _, p1, p2, center, normal, width = min(candidates, key=lambda t: t[0])
    return p1, p2, center, normal, width


def local_to_odom(local_point, pose):
    x, y, yaw = pose
    c, s = math.cos(yaw), math.sin(yaw)
    lx, ly = local_point
    return x + c * lx - s * ly, y + s * lx + c * ly


def normal_to_odom(local_normal, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    nx, ny = local_normal
    return c * nx - s * ny, s * nx + c * ny


def wall_progress(position, center, outward):
    return ((position[0] - center[0]) * outward[0] +
            (position[1] - center[1]) * outward[1])


def wall_lateral(position, center, outward):
    return (-(position[0] - center[0]) * outward[1] +
            (position[1] - center[1]) * outward[0])
