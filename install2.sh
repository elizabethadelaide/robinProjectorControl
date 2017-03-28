#!/bin/bash
#install homebrew as a package manager
command -v brew >/dev/null 2>&1 || ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

#add homebrew to path variable
command -v brew >/dev/null 2>&1 || export PATH=/usr/local/bin:/usr/local/sbin:$PATH

#install python3
command -v python3 >/dev/null 2>&1 || brew install python3

#install py2app
pip3 install -U git+https://github.com/metachris/py2app.git@master

#install tkinter (double check)
brew install python3-tk

pip3 install pyserial

#install 
py2applet --make-setup projectorControl.py
python3 setup.py py2app

ln -s dist/projectorControl.app projectorControl.app

chmod 777 projectorControl.app
