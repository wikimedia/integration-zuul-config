#!/usr/bin/env bash

umask 002

cd /src

npm install git-lint@1.0.0
git-lint project.config
