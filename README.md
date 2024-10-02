# Group Project
This is a group project for the CPSC 471 Fall 2024 course at the University of Calgary.

# Project Description
Inventory Managment System for small to medium sized contractors.

# Install 
## Prerequsites
The following are assumed to already be installed:
- Docker (https://docs.docker.com/engine/install/)
- Docker Compose (https://docs.docker.com/compose/install/)

## <a name="linux-install"></a> Linux Install
1. Clone the git repo onto your computer.
   ```bash
   git clone 
   ```
2. In the project root directory, create a file called ".env" and add to it "MARIADB_ROOT_PASSWORD=MySecretPassword" and change "MySecretPassword" to a password of your choosing.
   ```bash
   echo "MARIADB_ROOT_PASSWORD=MySecretPassword" >> .env
   ```
3. In the project root directory, create a directory called "data" and then in data create a directory called "mariadb". This will be the directory to keep the database data persistant upon updating or shuting down the container.
   ```bash
   mkdir -p data/mariadb
   ```
4. Then run initiate docker containers.
   ```bash
   sudo docker compose up -d
   ```
5. Check that the containers are running with
   ```bash
   sudo docker ps -a
   ```
6. If "mariadb-CPSC471_Fall2024_GroupProject" is exited, bootlooping, or otherwise failing to run then its likely because the database data directory we created in step 3 does not have the correct permission for the mariadb docker container to be able to access it. To fix this run the following:
   ```bash
   sudo chmod 777 ./data/mariadb
   ```
   And reload the docker compose file with
   ```bash
   sudo docker compose restart
   ```
   or
   ```bash
   sudo docker compose down && sudo docker compose up -d
   ```
7. Now if everything has gone correctly we should now be able to access the database by using (insure you are in the root project directory):
   ```bash
   source .env; sudo docker exec -it mariadb-CPSC471_Fall2024_GroupProject mariadb -u root --password=$MARIADB_ROOT_PASSWORD -P 3306 -D Project_Database
   ```
   It may prompt for a password, this is (assuming everything has gone right) your user password for the "sudo" command and not the password for the database.
8. If you already have mariadb, mysql or another database tool (GUI or CLI) then to connect to the database use the following values:
   - Port: 49152
   - Host: 127.0.0.1 (Assuming you are connecting from the same machine the docker container is installed on)
   - Password: <The password you set in the .env file>
   - User: root
   - Database: Project_Database
  


## Windows Install
It should be enough to just follow the descriptions of the [Linux Install](#linux-install) but the cli commands may not work.
Maybe try WSL?

## MacOS Install
It should be enough to just follow the descriptions of the [Linux Install](#linux-install) but the cli commands may not work.



# Group Members
- Dane Beliveau
- Daniel Bogorad
- Isaac Shiells Thomas
