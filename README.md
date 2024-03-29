# Site Manager
A simple web server manager for managing multiple websites on a single server.
It is designed to be simple and easy to use, supporting HNS domains out of the box.

[YouTube Tutorial](https://youtu.be/a_QVf6NpKZk)

Installation
------------

```bash
wget https://git.woodburn.au/nathanwoodburn/site-manager/raw/branch/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

Create account
--------------
Accounts can only be created by the root user
```bash
sudo -i
cd /root/site-manager
python3 account.py
exit
```


Updating
--------
```bash
sudo -i
cd /root/site-manager
git pull
exit
```


## Screenshots
![Dashboard](assets/dash.png)
![Management page](assets/mg1.png)
![Plain Content](assets/plain.png)
![Git Content](assets/git.png)