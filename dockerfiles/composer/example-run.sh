#!/bin/bash

export output=`docker run --rm --tty wmfreleng/composer:latest --version --no-ansi`
echo $output | grep "Composer version"
