#! /bin/bash

# Clone the project
printf "\033[34mDownloading repo:\033[0m\n"
git clone https://github.com/isaac-ucalgary/CPSC471_Fall2024_GroupProject.git ~/Home_IMS || { printf "\"~/Home_IMS\" already exitst... Aborting"; exit 1; }

# Navigate to the source
cd "$HOME/Home_IMS/home_ims/src" || { printf "Failed to locate project... Aborting..."; exit 1; }

data_confirmed=false
while [[ $data_confirmed == false ]]; do
  # Get database parameters from the user
  printf "\n\n\033[34mEnter Database Information:\033[0m\n"
  read -rp "Host: " db_host
  read -rp "Port: " db_port
  read -rp "User: " db_user
  read -srp "Password: " db_password

  # Check inputs
  if [[ $db_port -lt 1 ]] || [[ $db_port -gt 65535 ]] ; then 
    printf "%s is not a valid port number, try again.\n\n" "${db_port}"

  # If inputs are good, ask for confirmation on the data
  else
    # Confirm data
    printf "\nConfirm Information:\n"
    printf "\tHost: %s\n" "${db_host}"  
    printf "\tPort: %s\n" "${db_port}"
    printf "\tUser: %s\n" "${db_user}"
    read -rp "Confirm (y/N): " confirm_input 

    case $confirm_input in
      "y" | "Y" | "yes")
        data_confirmed=true
        ;;
      "quit")
        printf "Aborting..."
        exit 1
        ;;
      *)
        printf "Data rejected... Trying again...\n"
        ;;
    esac
  fi
done

printf "\033[32mData confirmed\033[0m\n"

printf "\033[34mWriting config files...\033[0m\n"


# Populate the files
cat > ./env.py << EOL
MARIADB_HOST:str = "${db_host}"
MARIADB_PORT:int = ${db_port}
MARIADB_USER:str = "${db_user}"
EOL

echo "MARIADB_PASSWORD:str = \"${db_password}\"" > secrets.py


printf "\033[32mInstall successful\033[0m\n"
