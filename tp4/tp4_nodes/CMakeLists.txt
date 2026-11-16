cmake_minimum_required(VERSION 3.5)
project(tp4_nodes)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

install(PROGRAMS
  src/world_tf_broadcaster.py
  src/tp4_mapping.py
  src/tp4_get_path.py
  src/tp4_follow_path.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch rviz src
  DESTINATION share/${PROJECT_NAME}
)

ament_package()