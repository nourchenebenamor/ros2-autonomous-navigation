cmake_minimum_required(VERSION 3.5)
project(tp1)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
    rosidl_generate_interfaces(${PROJECT_NAME}
    "action/Path.action"
    DEPENDENCIES geometry_msgs
)
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

install(PROGRAMS
  src/my_teleop.py
  src/test_path.py
  src/follow_path.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()