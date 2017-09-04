FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

RUN apt-get update && \
	apt-get install --yes --no-install-recommends \
		zuul \
		# Well duh, zuul needs to clone things
		git \
		# pin python-pbr https://phabricator.wikimedia.org/T153877
		python-pbr=0.8.2-1 && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

ENTRYPOINT /bin/bash zuul-cloner --workspace=/root $ZUUL_URL $ZUUL_PROJECT
