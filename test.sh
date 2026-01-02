#!/bin/sh

# Execute unittests inside docker
sudo docker build --progress=plain -t nut-base-server-tests -f Dockerfile.test .
