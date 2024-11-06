# Database
For this app, it is assumed that a mariadb or mysql database server has already been created (localhost or remote).

This server must have the following conditions met:
  - A database called "Home_IMS".
  - A user called "Home_IMS_app".
  - The "Home_IMS_app" user been given full permissions to the "Home_IMS" database.

This database server can either be installed independently or via the provided docker compose file.


## Docker Compose
If one would like, a docker compose file is provided that will create a mariadb server with 
the required conditions already in place.

In addition, a ".env" file is required with the variables for the passwords for the root and "Home_IMS_app" users in the same directory 
as the docker-compose.yaml file. A "template.env" file has been provided. Please fill it in with the appropriate values and rename 
it to ".env".

