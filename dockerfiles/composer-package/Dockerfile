FROM wmfreleng/composer:latest

USER root
# Enable xdebug for PHPUnit coverage reports
RUN phpenmod xdebug

USER nobody
COPY run.sh /run.sh
ENTRYPOINT /bin/bash /run.sh
