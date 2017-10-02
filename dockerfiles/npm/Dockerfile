FROM wmfreleng/slave-scripts:latest AS slave-scripts

FROM wmfreleng/ci-jessie:latest

# Install nodejs-legacy to provide /usr/bin/node alias
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        nodejs-legacy npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# DO NOT CHANGE VERSION WITHOUT INVOLVING Krinkle OR hashar
RUN npm install -g npm@3.8.3

COPY --from=slave-scripts /srv/deployment/integration/slave-scripts /srv/deployment/integration/slave-scripts

USER nobody

RUN /srv/deployment/integration/slave-scripts/bin/npm-setup.sh

ENTRYPOINT ["npm"]
CMD ["--help"]
