# Docker with public ip-address

The ultimate goal of this script is to assign the public ip (ip which can be accessed by other nodes in the network ) to the docker instances which are forked from the base image.
By attaching the virutal interfaces to the newly created docker instances, the instances can able to talk to other nodes with its own network namespace.

# Hands-on
Before running the script make sure that host machine passes following criteria

## Pre-requisites
* Host machine can either be Ubuntu or CentOS.
* Python should be installed in it.

## Steps to be followed
* Run ```python dockerOpt.py -h``` for more information about the script.
* Install the docker in the host machine by mentioning the type of linux ( Ubuntu or CentOS).Here option for ```-d``` can be of any image name which you want to create locally.
```Python
python dockerOpt.py -i CentOS -d pubip_docker:latest
```
* Once the docker / docker image is created will start running the docker with following options
```Python
python dockerOpt.py -r pubip_docker -n jail1 -e ens160 -p 20.10.48.26/8 -g 20.10.1.1
```
* In order to start the ssh service inside the newly created docker instance run ..
```Python
docker exec -it jail1 bash
service ssh start
service rpcbind start
service open-iscsi start
```
* Now the newly created docker instance can be accessed across the nodes in the same network.

## Other Stuffs
In case of using your private/public docker image with above mentioned feature, change the image name in the script while installing the docker and insttall neccessary packages according to your choice.
```Python
  buildFile.write('FROM thiruvkram/pubip_docker\n')
  buildFile.write('RUN apt-get -y update\n')
```

## Note
This is the initial version of the script hence issues during the network connectivity may rarely occur .
