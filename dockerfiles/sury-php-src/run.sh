#!/bin/bash
pushd /usr/src
apt-get update
apt-get source $php_packages
