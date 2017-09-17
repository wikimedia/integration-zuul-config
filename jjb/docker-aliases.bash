alias git='docker run --rm -it -v "/$PWD://src" wmfreleng/git:latest'
alias composer='docker run --rm -it -v "/$PWD://src" wmfreleng/composer:latest'
alias mw-phan='docker run --rm -it -v "/$PWD://src" wmfreleng/mediawiki-phan:latest'
alias zuul-cloner='docker run --rm -it -v "/$PWD://src" wmfreleng/zuul-cloner:latest'