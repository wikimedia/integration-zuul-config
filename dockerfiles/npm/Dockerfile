FROM wmfreleng/ci-jessie:latest

# Install nodejs-legacy to provide /usr/bin/node alias
RUN apt-get update && \
    apt-get install --yes \
        nodejs-legacy npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# DO NOT CHANGE VERSION WITHOUT INVOLVING Krinkle OR hashar
RUN npm install -g npm@3.8.3

USER nobody

ENTRYPOINT ["npm"]
CMD ["--help"]
