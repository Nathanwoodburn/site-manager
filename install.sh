#!/bin/bash

# Make sure script is running as root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Install nginx
sudo apt update
sudo apt install nginx -y

cd /root
git clone https://git.woodburn.au/nathanwoodburn/site-manager.git
cd site-manager
chmod +x *.sh


# Install python script as a service
sudo cp ./nginx-traffic-monitor.service /etc/systemd/system/nginx-traffic-monitor.service
sudo systemctl start nginx-traffic-monitor]
sudo systemctl enable nginx-traffic-monitor
