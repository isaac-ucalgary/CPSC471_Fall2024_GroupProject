#! /bin/bash

# Clone the project
git clone https://github.com/isaac-ucalgary/CPSC471_Fall2024_GroupProject.git ~/Home_IMS

# Navigate to the source
cd "$HOME/Home_IMS/home_ims/src" || { printf "Failed to locate project... Aborting..."; exit 1; }

db_host
db_port
db_user
db_password

data_confirmed=false
while [[ ! $data_confirmed ]]; do
  # Get database parameters from the user
  printf "Enter Database Information:\n"
  read -pr "Host: " db_host
  read -pr "Port: " db_port
  read -pr "User: " db_user
  read -prs "Password: " db_password

  # Check inputs
  if [[ $db_port -lt 1 || $db_port -gt 65535 ]] ; then 
    printf "%d is not a valid port number, try again.\n\n" db_port

  # If inputs are good, ask for confirmation on the data
  else
    # Confirm data
    printf "Confirm Information:\n"
    printf "\tHost: %s\n" db_host  
    printf "\tPort: %d\n" db_port
    printf "\tUser: %s\n" db_user
    read -pr "Confirm (y/N): " confirm_input 

    case $confirm_input in
      "y" | "Y" | "yes")
        data_confirmed=true
        ;;
      "quit")
        printf "Aborting..."
        exit 1
        ;;
      *)
        printf "Data rejected... Trying agin...\n"
        ;;
    esac
  fi
done

printf "Data confirmed\n\n"



# Populate the files
cat > ./env.py << EOL
MARIADB_HOST:str = \"${db_host}\"
MARIADB_PORT:int = \"${db_port}\"
MARIADB_DATABASE_NAME:str = \"Home_IMS\"
MARIADB_USER:str = \"${db_user}\"
EOL

echo "MARIADB_PASSWORD:str = \"${db_password}\"" > secrets.py

