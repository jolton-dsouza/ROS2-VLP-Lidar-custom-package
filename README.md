# ROS2-VLP-Lidar-custom-package
This repo will help you to create custom ROS messages for VLP-16 and VLP-32 lidars. It will unpack the data stream coming from the sensor and will convert those values to data points(point cloud) and display it on a visualizer, an open source 'vispy' visualizer is used. It also packs the whole data packet as a ROS message which can be recorded as ROS bags. The script will also make a Publisher/Subscriber node.

**NOTE: Check lidar_acq.py file**

## Dependencies
- Ubuntu >= 16.04
- ROS2 - Crystal (see 'ros2CrystalInstall.bash' file)
- Python3

## Python packages 
- vispy (https://github.com/vispy/vispy)
- multiprocessing
- numpy
- matplotlib
- yaml
