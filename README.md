# CreditCalculator
Evan Hopkins, Bryan Keller, Mason Crane, Tom Morse, Brad Huntington
Calculates the amount of credits that will transfer from DCCC to Marist College

## Vagrant Setup and use:

1. clone git repository
2. Make sure the repository dir is labeled "CreditCalculator" and it must be
   located directly under the users home folder
3. cd into the dir
4. run the command "vagrant up" this starts the VM (may take a few minutes to
   start first time)
5. All coding can be done inside the working dir on the host machine
   ~/CreditCalculator

## Mysql:
 - Root credentials
    Username: root
    Password: bbemt (clearly these should be changed if deployed to a live server)

## Notes:
 - To access the VM directly run the command "vagrant ssh"
 - To nicely stop the VM "vagrant halt"
 - If your VM gets messed up run "vagrant destroy" to obliterate your VM and run
   "vagrant up" to create a fresh new one
