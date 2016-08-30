import sys
import argparse
import subprocess
import os
from subprocess import Popen, PIPE

buildDir = '/tmp/dockerBuild'

def buildDocker(imageName):
  if os.path.exists(buildDir):
    os.system("rm -rf " + buildDir)
    os.system("mkdir " + buildDir)
  else:
    os.system("mkdir " + buildDir)

  #Creating the Docker build file in /tmp/dockerBuild
  buildFile = open(buildDir + "/Dockerfile",'w')
  buildFile.write('############################################################\n')
  buildFile.write('# Dockerfile to build container image for mounting volumes\n')
  buildFile.write('# Based on Ubuntu\n')
  buildFile.write('############################################################\n')
  buildFile.write('FROM thiruvkram/pubip_docker\n')
  buildFile.write('RUN apt-get -y update\n')
  buildFile.close()
  deployDocker = 'docker build -t "' + imageName + '" ' + buildDir + '/'
  proc = subprocess.Popen(deployDocker,shell=True)
  proc.wait()

def installProcess(installSteps):
  for installStep in installSteps:
    proc = subprocess.Popen(installStep,shell=True)
    proc.wait()

def installDocker(installType,imageName):
  if installType == "CentOS":
   repoFile = open('/etc/yum.repos.d/docker.repo','w')
   repoFile.write('[dockerrepo]\n')
   repoFile.write('name=Docker Repository\n')
   repoFile.write('baseurl=https://yum.dockerproject.org/repo/main/centos/7\n')
   repoFile.write('enabled=1\n')
   repoFile.write('gpgcheck=1\n')
   repoFile.write('gpgkey=https://yum.dockerproject.org/gpg')
   repoFile.close()
   installSteps = ['yum -y update','yum -y install docker','service docker start','docker run hello-world']
  else:
   installSteps = ['apt-get -y update','curl -sSL https://get.docker.com/ | sh','service docker start','docker run hello-world']
  installProcess(installSteps)

  print "Starting the creation of docker image: " + imageName
  buildDocker(imageName)
  print "Successfully deployed docker Image"

def startContainer(dockerImageName,containerName,nicName,containerIpAddress,containerGateway):
  startDockerContainer = ' docker run --privileged=true -d --cap-add=ALL --device /dev/fuse -v  /dev:/dev  -v  /lib/modules:/lib/modules --name ' + containerName
  startDockerContainer = startDockerContainer + ' --net=none ' + dockerImageName + ' sh -c "tail -f /dev/null"'
  proc = subprocess.Popen(startDockerContainer,shell=True)
  proc.wait()
  createVirNic = "ip link add name veth_" + containerName + " link " + nicName + " type macvlan"
  proc = subprocess.Popen(createVirNic,shell=True)
  proc.wait()
  nicName = "veth_" + containerName
  getProcId = "docker inspect -f '{{.State.Pid}}' " + containerName
  proc = subprocess.Popen(getProcId,shell=True,stdin=PIPE, stdout=PIPE, stderr=PIPE)
  (out, err) = proc.communicate()
  procId = out.strip(' \t\r\n')
  attachNic = ['ip addr add ' + containerIpAddress + ' dev '+ nicName,'mkdir -p /var/run/netns','ln -s /proc/' + procId + '/ns/net /var/run/netns/' + procId]
  attachNic.append('ip link set ' + nicName + '  netns ' + procId + ' name eth1')
  attachNic.append('ip netns exec ' + procId + ' ip addr add ' + containerIpAddress +' dev eth1')
  attachNic.append('ip netns exec ' + procId + ' ip route add default via ' + containerGateway +' dev eth1')
  attachNic.append('ip netns exec ' + procId +' ip link set eth1 up')
  attachNic.append('docker exec ' + containerName + ' ping -q -w3 ' + containerGateway)
  attachNic.append('rm /var/run/netns/' + procId)
  installProcess(attachNic)
  print "Successfully started the docker container :" + containerName + " with attaching the NIC : " + nicName

if __name__ == "__main__":
  try:
    parser = argparse.ArgumentParser(description='################# Docker Options ###############')
    parser.add_argument('-i','--Install',help='Host machine type to Install the docker (Ubuntu,CentOS)')
    parser.add_argument('-d','--DockerImage',help='Name of the new Docker image needs to be created')
    parser.add_argument('-r','--Run',help='Name of the Docker container image to run (eg.test_docker:latest)')
    parser.add_argument('-n','--Name',help='Name of the Docker Container')
    parser.add_argument('-e','--Ethernet',help='Name of the NIC interface needs to be attached inside the docker container')
    parser.add_argument('-p','--ContainerIp',help='IP address needs to be added to interface attached to the docker container')
    parser.add_argument('-g','--ContainerGateway',help='Gateway that needs to added to the interface inside the docker container')
    args = parser.parse_args()
    installType = args.Install
    imageName   = args.DockerImage
    dockerImageName = args.Run
    containerName = args.Name
    nicName = args.Ethernet
    containerIpAddress = args.ContainerIp
    containerGateway = args.ContainerGateway
    if not installType:
      if not dockerImageName:
        print "Invalid Option Provided. Expected -i or -r"
        sys.exit(0)
      else:
        print "Starting the docker Container : " + containerName
        startContainer(dockerImageName,containerName,nicName,containerIpAddress,containerGateway)
    else:
      print "Installing the docker engine for host type : " + installType
      installDocker(installType,imageName)
  except Exception as ex:
    print ex
