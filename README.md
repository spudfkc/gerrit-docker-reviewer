
###Prerequisites
 - Docker version 0.7.5, build c348c04[3]
 - Python 2.7.4
 - git version 1.8.1.2[2]
 - 'docker' and 'git' must be avaible on PATH
 - docker able to be run without sudo[1]
 - symlink to your ucd/dist/install dir in current directory[4]

 [1] Run Docker without sudo - https://gist.github.com/spudfkc/8649919
 [2] `sudo apt-get install git`
 [3] Docker Installation - http://docs.docker.io/en/latest/installation/ubuntulinux/
 [4] `ln -s /home/${USER}/workspace/urban-deploy/dist/install/ibm-ucd-install ibm-ucd-install`

###Running
chmod +x gerrit-get-changes.py
./gerrit-get-changes.py

###Your directory structure should look like this
.
├── config
├── Dockerfile
├── ibm-ucd-install -> /home/ncc/workspace/urban-deploy/dist/install/ibm-ucd-install
├── install.properties
├── README.md
├── reviewer.py
└── TODO.md

