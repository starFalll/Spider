#!/bin/bash
#https://github.com/starFalll/Spider
#author:ACool
vir=$(pip3 list | grep  virtualenv |awk '{print $1}')
echo $vir

if [ "$vir" != virtualenv"" ];then
    sudo pip3 install -i https://pypi.douban.com/simple/ virtualenv
fi

PROJ_DIR=`pwd`
VENV=${PROJ_DIR}/.env
PROJ_NAME=WeiboSpider

if [ ! -d ${VENV} ];then
    virtualenv --prompt "(${PROJ_NAME})" ${VENV} -p  python3
fi

source ${VENV}/bin/activate
export PYTHONPATH=${PROJ_DIR}/../
export PROJ_DIR
export PATH=${PATH}:${VENV}/bin
pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt
