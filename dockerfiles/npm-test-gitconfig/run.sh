#!/usr/bin/env bash

umask 002

cd /src

npm install git-lint
git-lint project.config
