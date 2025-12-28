#!/bin/bash

# build the new image, the new image will replace the old one
sudo docker build -t downloadblocks -f Dockerfile ..

# tag the image of its version, with the name of docker account
sudo docker tag downloadblocks hkustelric/downloadblocks:latest

# login the docker account (automatically)
sudo docker login

# push the new image to the depository
sudo docker push hkustelric/downloadblocks:latest