#! /bin/bash

# This script installs ROS1 Melodic and ROS2 Crystal on Ubuntu 18.04 Bionic
# using available apt packages


# Stop on any command error
set -e

# Set locale
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8


# Install general dependencies and good things
sudo apt update

sudo apt install -y git g++ cmake qt5-default
sudo apt install -y wireshark


# Install general python stuff
sudo apt install -y python-docutils
sudo apt install -y python3-pyqt5
sudo apt install -y pyqt5-dev-tools
sudo apt install -y python3-pip
sudo -H pip3 install opencv-python dpkt



## Install ROS 1

## Setup package sources
#sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
#sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116
#sudo apt-get update

## Install
#sudo apt-get install -y ros-melodic-desktop

## Initialize rosdep
#sudo rosdep init
#rosdep update


# Install ROS 2

# Setup package sources
sudo apt update && sudo apt install -y curl gnupg2 lsb-release
curl http://repo.ros2.org/repos.key | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64,arm64] http://packages.ros.org/ros2/ubuntu `lsb_release -cs` main" > /etc/apt/sources.list.d/ros2-latest.list'
sudo apt update

# Install
export CHOOSE_ROS_DISTRO=crystal
sudo apt install -y ros-$CHOOSE_ROS_DISTRO-desktop
sudo -H pip3 install argcomplete

# source and add to .bashrc
echo "source /opt/ros/$CHOOSE_ROS_DISTRO/setup.bash" >> ~/.bashrc
source ~/.bashrc


# Install ROS 2 Add-Ons
sudo apt install -y ros-$CHOOSE_ROS_DISTRO-ros1-bridge
sudo apt-get install -y ros-$CHOOSE_ROS_DISTRO-ros2bag* ros-$CHOOSE_ROS_DISTRO-rosbag2*


sudo apt install -y python3-colcon-common-extensions

# Give feedback that the script completed correctly
echo "Installation successfully completed."
