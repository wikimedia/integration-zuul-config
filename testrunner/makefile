# Generic test runner for Wikimedia repositories
#
# Copyright (c) 2015, Antoine "hashar" Musso
# Copyright (c) 2015, Wikimedia Foundation Inc.

ENTRY_POINTS := commitmessage $(wildcard composer.json package.json tox.ini)

COMPOSER := composer --ansi

.PHONY: test composer-validate $(ENTRY_POINTS)


test: $(ENTRY_POINTS)
	@echo Done

commitmessage:
	@echo '** Validating commit message **'
	@echo '> TODO'

composer.json: composer-validate
	@echo '** Found composer.json. Running composer **'
	$(COMPOSER) test

#composer-validate:
#	$(COMPOSER) validate --no-check-publish
#
#composer-update:
#	$(COMPOSER) update --no-progress --prefer-dist --profile -v
#

package.json:
	@echo '** Found package.json. Running npm **'
	npm test

tox.ini:
	@echo '** Found tox.ini. Running tox **'
	@echo Found tox.ini
	tox -v
