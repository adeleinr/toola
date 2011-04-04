# These are the steps for deploying
# the project and adjusting misc configs

# This step installs everything from a clean
# Ubuntu setup and copies/deploys the projects

1) fab environment setup > deploy.log

# If it is the fist time deploying this project
# then need to create a DB, Django does not create 
# the DB
2) mysql -u root -p
3) create database webme;

# Copy all the private (outside of Git)  files
# to the remote host
4) run.sh
   -> calls private_local.sh

# This loads all the init data in the DB
# and preprocess JavaScript Files
5) private_remote.sh
