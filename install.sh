#!/bin/bash

AUTHOR="osrn"
APPNAME="lazy-delegate"
APPHOME="$HOME/$APPNAME"
VENV="$APPHOME/.venv"
GITREPO="https://github.com/$AUTHOR/$APPNAME.git"
GITBRANCH="main"

# Regular Colors
CBlack='\033[0;30m'  # Black
CRed='\033[0;31m'    # Red
CGreen='\033[0;32m'  # Green
CYellow='\033[0;33m' # Yellow
CBlue='\033[0;34m'   # Blue
CPurple='\033[0;35m' # Purple
CCyan='\033[0;36m'   # Cyan
CWhite='\033[0;37m'  # White
NC='\033[0m'         # Text Reset


clear

SUDO_USER=$1
if [ -z "$SUDO_USER" ]
  then
    echo -e "${CRed}Error: this script must be called with a sudo user as argument${NC}"
    echo usage: $0 user
    exit 1
fi

if  ! id -u $SUDO_USER &>/dev/null
  then
    echo -e "${CRed}Error: user $SUDO_USER does not exist${NC}"
    exit 1
fi

if [ -z "$(id -Gn $SUDO_USER | grep sudo)" ]
  then
    echo -e "${CRed}Error: $SUDO_USER must have sudo privilage${NC}"
    exit 1
fi

echo
echo installing system dependencies
echo ==============================
echo -e "${CRed}You will be asked for the SUDOER's password twice; first time for su, and second time for sudo in su environment${NC}"
echo Please enter the password for $SUDO_USER
su - $SUDO_USER -c "echo Please enter the password for $SUDO_USER again
sudo -S echo 'installing...'
sudo apt-get -y install python3 python3-pip python3-dev python3-venv
echo '...done'
"

exit_code=$?
if [ "$exit_code" -ne 0 ]; then
    echo -e "${CRed}Error: incorrect password or user $SUDO_USER has no password${NC}"
    exit 1
fi


echo installing latest pip and venv for user
echo =======================================
python3 -m pip install --user --upgrade pip
python3 -m pip install --user virtualenv
echo '...done'


echo
echo downloading package from git repo
echo =================================
cd ~
if [ -d $APPHOME ]; then
    read -p "$(echo -e "${CRed}existing installation found, shall I wipe it? [y/N]>${NC}") " r
    case $r in
    y|Y)
        echo 'stopping jobs...'
        pm2 stop $APPNAME 
        echo 'unregistering jobs with pm2...'
        pm2 delete $APPNAME 
        echo 'removing package...'
        rm -rf $APPHOME
        ;;
    *) echo -e "did not wipe existing installation";;
    esac
fi
if (git clone -b $GITBRANCH $GITREPO) then
    echo "package retrieved from GIT"
    cd $APPHOME
else
    echo "local repo found! resetting to remote..."
    cd $APPHOME
    git reset --hard
    git fetch --all
    git checkout $GITBRANCH
    git pull
fi
echo '...done'


echo
echo creating virtual environment
echo ============================
if [ -d $VENV ]; then
    read -p "remove existing virtual environment ? [y/N]> " r
    case $r in
    y|Y) 
        rm -rf $VENV
        python3 -m venv .venv
        ;;
    *) echo -e "existing virtual environment preserved";;
    esac
else
    python3 -m venv .venv
fi
echo '...done'


echo
echo installing python dependencies
echo ==============================
. $VENV/bin/activate
if [ -n "$CPATH" ]; then
# Workaround for Solar vers > 3.2.0-next.0 setting CPATH 
# causing psycopg2 compilation error for missing header files
    OLDCPATH=$CPATH
    export CPATH="/usr/include"
fi
cd $APPHOME
# wheel and psycopg2 needs to be installed seperately
pip3 install wheel
pip3 install -r requirements.txt
deactivate
echo '...done'
if [ -n "$SAVEDCPATH" ]; then
    export CPATH=$OLDCPATH
fi


echo -e ${CGreen}
echo '====================='
echo 'installation complete'
echo '====================='
echo -e ${NC}
echo '>>> next steps:'
echo '==============='
echo 'This script requires pm2, which is possibly already installed;'
echo 'but otherwise you can install it with:'
echo -e ${CBlue}'  npm install pm2@latest [-g]'
echo -e ${NC}'  or'${CBlue}
echo '  yarn [global] add pm2'
echo -e ${NC}
echo 'First, clone the sample config provided and modify as you see fit'
echo -e ${CBlue}'  cd '$APPHOME 
echo '  cp src/config/config.example src/config/config'
echo '  (editor) src/config/config'
echo -e ${NC}'All config parameters are explained in README.md'
echo 
echo 'Next do;' 
echo -e ${CBlue}'  cd '$APPHOME 
echo '  pm2 start package.json && pm2 logs '$APPNAME
echo -e ${NC} 
echo 'to start the app at boot with pm2;'
echo -e ${CBlue}'  cd && pm2 save'
echo -e ${NC}
echo 'to start pm2 at boot, you have two options:'
echo 'opt 1/ user with sudo privilege'
echo -e ${CBlue}'  pm2 startup'
echo -e ${NC}'and follow the instructions'
echo
echo 'opt 2/ user like solar with no sudo privilege'
echo -e ${CBlue}'  (crontab -l; echo "@reboot /bin/bash -lc \"source /home/solar/.solarrc; pm2 resurrect\"") | sort -u - | crontab -'
echo -e ${NC}
