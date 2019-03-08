# Makefile help based on
# https://github.com/ianstormtaylor/makefile-help
.PHONY: help
# Show this help prompt.
help:
	@ echo
	@ echo '  Usage:'
	@ echo ''
	@ echo '    make <target> [flags...]'
	@ echo ''
	@ echo '  Targets:'
	@ echo ''
	@ awk '/^#/{ comment = substr($$0,3) } comment			\
		 && /^[a-zA-Z][a-zA-Z0-9_-]+ ?: *[^=]*$$/ {		\
			 print "   ", $$1, comment			\
		}' $(MAKEFILE_LIST) | column -t -s ':' | sort
	@ echo ''
	@ echo '  Flags:'
	@ echo ''
	@ awk '/^#/{ comment = substr($$0,3) } comment			\
		 && /^[a-zA-Z][a-zA-Z0-9_-]+ ?\?= *([^=].*)$$/ {	\
			print "   ", $$1, $$2, comment, 		\
			"(Default: " ENVIRON[$$1] ")"			\
		}' $(MAKEFILE_LIST) | column -t -s '?=' | sort
	@ echo ''
