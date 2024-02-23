#!/bin/bash

# Make sure script is running as root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Install nginx
sudo apt update
sudo apt install nginx python3-pip -y

cd /root
git clone https://git.woodburn.au/nathanwoodburn/site-manager.git
cd site-manager
chmod +x *.sh
python3 -m pip install -r requirements.txt

# Install python script as a service
sudo cp ./nginx-manager.service /etc/systemd/system/nginx-manager.service
sudo systemctl start nginx-manager
sudo systemctl enable nginx-manager

# Install certbot
sudo snap install core; sudo snap refresh core
sudo apt remove certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot