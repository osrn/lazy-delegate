#!/bin/bash

APPPATH="$HOME/lazy-delegate"
VENV="$HOME/lazy-delegate/.venv"
GITREPO="https://github.com/osrn/lazy-delegate.git"

clear

echo
echo installing system dependencies
echo ==============================
sudo apt -qq install python3 python3-dev python3-venv
python3 -m pip install --user --upgrade pip
python3 -m pip install --user virtualenv
echo done

echo
echo downloading package
echo ===================

cd ~
if [ -d $APPPATH ]; then
    read -p "existing installation found, shall I wipe it? [y/N]> " r
    case $r in
    y) rm -rf $APPPATH;;
    Y) rm -rf $APPPATH;;
    *) echo -e "did not wipe existing installation";;
    esac
fi
if (git clone $GITREPO) then
    echo "package retrieved."
    cd ~/lazy-delegate
else
    echo "local repo found! resetting to remote..."
    cd ~/lazy-delegate
    git reset --hard
    git fetch --all
    git checkout main
    git pull
fi

echo done

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
echo done

# install python dependencies
echo
echo installing python dependencies
echo ==============================
. $VENV/bin/activate
cd ~/lazy-delegate
pip install -r requirements.txt -q
deactivate
echo done

echo ================
echo 
echo install finished
echo
echo ================
echo
echo
echo '>>> next steps'
echo -------------------------------
cat ~/lazy-delegate/POST_INSTALL.txt
