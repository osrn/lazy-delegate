#!/bin/bash

VENV="$HOME/lazy-delegate/.venv"
GITREPO="https://github.com/osrn/lazy-delegate.git"

clear

echo
echo installing system dependencies
echo ==============================
sudo apt -qq install python3 python3-dev python3-venv
python3 -m pip install --user --upgrade pip
python3 -m pip install --user virtualenv
echo "done"

echo
echo downloading package
echo ===================

cd ~
if (git clone $GITREPO) then
    echo "package retrieved."
    cd ~/lazy-delegate
else
    echo "local repo found! resetting to remote..."
    cd ~/lazy-delegate
    git reset --hard
    git fetch --all
    git checkout master
    git pull
fi

echo "done"

echo
echo creating virtual environment
echo ============================

if [ -d $VENV ]; then
    read -p "remove existing virtual environment ? [y/N]> " r
    case $r in
    y) rm -rf $VENV;;
    Y) rm -rf $VENV;;
    *) echo -e "existing virtual environment preserved";;
    esac
fi

python3 -m venv .venv
echo "done"

# install python dependencies
echo
echo installing python dependencies
echo ==============================
. $VENV/bin/activate
cd ~/lazy-delegate
pip install -r requirements.txt -q
deactivate
echo "done"

echo
echo "setup finished"
echo
echo next steps
echo ==========
echo "1/ make sure pm2 is installed:"
echo "npm install pm2@latest -g"
echo "or"
echo "yarn global add pm2"
echo
echo "2/ copy config example and modify"
echo "cd ~/lazy-delegate"
echo "cp src/config/config.example src/config/config"
echo "vi src/config/config"
echo
echo "3/ start the app"
echo "pm2 start apps.json"
echo
echo "4/ check status and logs"
echo "pm2 status"
echo "pm2 logs"
echo
echo "5/ save pm2 environment to start with pm2 at boot"
echo "cd && pm2 save"
