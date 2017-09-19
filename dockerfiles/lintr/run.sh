#!/bin/bash

#TODO loop over all *.R files and lint them

cd /tmp
echo "library(httr)" > test.R
Rscript -e 'lintr::lint("test.R")'

# TODO fix the following error!!!:
# TODO alos this run.sh doesnt appear to be working anyway...
# $ docker run --rm -it wmfreleng/lintr:v2017.09.19.02.19
# root@7bf6c24566ac:/# cd /tmp
# root@7bf6c24566ac:/tmp# echo "library(httr)" > test.R
# root@7bf6c24566ac:/tmp# Rscript -e 'lintr::lint("test.R")'
# Error in dyn.load(file, DLLpath = DLLpath, ...) :
#   unable to load shared object '/usr/local/lib/R/site-library/igraph/libs/igraph.so':
#   libxml2.so.2: cannot open shared object file: No such file or directory
# Calls: <Anonymous> ... tryCatch -> tryCatchList -> tryCatchOne -> <Anonymous>
# Execution halted


# Could do something like the below?
#find ./ -type f -name \*.R -exec Rscript -e 'lintr::lint("{}")' \;
#
##Flip the exit code
#if [ $? -ne 0 ]
#then
#	exit 0
#else
#	exit 1
#fi

# https://github.com/jimhester/lintr/blob/master/README.md makes me feel like there is actually a better way to do this