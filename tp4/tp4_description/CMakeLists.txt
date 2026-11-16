cmake_minimum_required(VERSION 3.5)

project(tp4_description) # The name of the package

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED) # as we are doing python nodes

install(DIRECTORY gazebo launch rviz urdf meshes DESTINATION share/${PROJECT_NAME})

ament_package()