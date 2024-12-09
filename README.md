# Group Project
This is a group project for the CPSC 471 Fall 2024 course at the University of Calgary.

# Project Description
Inventory Managment System for you, your home and your family, to help manage your daily needs, keep track of your consumable items and record waste.

# Install 
## Prerequsites
### MariaDB (or MySQL)
It is assumed that you already have a MariaDB or MySQL database setup and have the following parameters:
- The **host IP address or URL** of the database.
- The **port** number of the database.
- The name of the **user** which has full access to a database called **Home_IMS** inside your database.
- The **password** for that user.

If you do not have a database there is a simple docker compose file that will help you create a database [here](mariadb/).
(Of course, this requires that you have [docker](https://docs.docker.com/engine/install/) and [docker compose](https://docs.docker.com/compose/install/) set up on the machine that will host the database)

### Python
This app runs on [python 3.12](https://www.python.org/downloads/).
It should run on any version of python 3.12.x but specifically it was developed on python 3.12.7.
While other versions of python may work, it is known that python 3.13+ does not work and version below 3.12 are untested.

### Qt
This app requires **Qt6**.

## <a name="linux-install"></a> Linux Install
1. Download the install script
   ```
   wget https://raw.githubusercontent.com/isaac-ucalgary/CPSC471_Fall2024_GroupProject/refs/heads/main/install.sh
   ```
2. Run the install script
   ```
   sh install.sh
   ```

This script will clone the git repo to your home directory under *~/Home_IMS*, ask you about the details for connecting to [your database](#MariaDB (or MySQL)), and create 
the appropriate config files using this information.

While you should always read a script before you run it, for those of you that are particularly lazy, just run:
```
wget -O- https://raw.githubusercontent.com/isaac-ucalgary/CPSC471_Fall2024_GroupProject/refs/heads/main/install.sh | bash
```

Assuming all went well you should now be able to run it using:
```
cd ~/Home_IMS && sh run.sh
```


## Windows Install
Good luck.

## MacOS Install
Even more good luck and pray to the apple gods.



# Group Members
- Dane Beliveau
- Daniel Bogorad
- Isaac Shiells Thomas
