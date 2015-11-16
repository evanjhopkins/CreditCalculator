######################################
# -*- mode: ruby -*-
# vi: set ft=ruby :
######################################
# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

## Start of file (connects to last "end")
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

#######################################
 ## Box and OS #####NEEDED#####
  config.vm.box = "hashicorp/precise64"
 # config.vm.box = "precise64"
 # config.vm.box_url = "http://files.vagrantup.com/precise64.box"

#######################################
  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

#######################################
 ## Forwarding/Mapping ports from Guest(VM) to Host(computer)
  # Connecting flask port 5000 from guest to port 8080 of host
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 80, host: 8080

#######################################
  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

#######################################
 ## Connecting Dir from Host(computer) to Guest(VM)
  config.vm.synced_folder "../CreditCalculator", "/home/vagrant/CreditCalculator"
  #config.vm.synced_folder ".", "/home/vagrant/CreditCalculator", type: "nfs"

#######################################
 ## Setting up the VM "hardware"
  config.vm.provider "virtualbox" do |vb|
  # Amount of memory for the VM:
    vb.memory = "1024"
  # Amount of cpus for the VM:
    vb.cpus = "2"
  # Name of the VM:
    vb.name = "CreditCalculatorMain"
  # Setting HDD size
  #  vb.customize ["modifyhd", 05d56fa6-7abf-4fc8-8e52-6a2a94a59f83, "--resize", "30"]
  end

#######################################
  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

#######################################
 ## Connecting to the VM shell at startup, the following commands are run as
  # script
  config.vm.provision "shell", inline: <<-SHELL
     # Updating
     sudo apt-get update
     # install vim text editor
     sudo apt-get install -y vim
     # install python package
     sudo apt-get install -y python
     # debconf allows us to have more control over shell commands
     apt-get install debconf-utils -y > /dev/null
     # use debconf to preset the mysql root pass for the mysql install
     debconf-set-selections <<< "mysql-server mysql-server/root_password password bbemt"
     debconf-set-selections <<< "mysql-server mysql-server/root_password_again password bbemt"
     # install mysql client + server packages
     apt-get install mysql-server -y > /dev/null
     sudo apt-get install -y python-dev libmysqlclient-dev
     # install pip
     sudo apt-get install -y python-pip
     # install mysql for python
     pip install MySQL-python
     # install Flask
     pip install Flask
     # install Flask Session for server side connection
     pip install Flask-Sessions
     # install requests for python
     pip install requests
     #pygal graphs
     pip install pygal
     # create and populate database
     mysql -u root -pbbemt < /home/vagrant/CreditCalculator/credit_calculator_create.sql
     mysql -u root -pbbemt creditcalc < /home/vagrant/CreditCalculator/build_db.sql
  SHELL

#######################################
 ## End of File, this end connect back to the top command
end
