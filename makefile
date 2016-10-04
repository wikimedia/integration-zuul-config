ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUILD_DIR := ${ROOT_DIR}/build
OUTPUT_DIR := ${BUILD_DIR}/output
OUTPUT_PREV_DIR := ${BUILD_DIR}/output-prev

HAS_PREV_DIR := $(wildcard ${OUTPUT_PREV_DIR})

.PHONY: diff install clean clean-output clean-prev changed

diff: ${OUTPUT_DIR}
ifdef HAS_PREV_DIR
	colordiff -u -r "${OUTPUT_PREV_DIR}" "${OUTPUT_DIR}" \
		&& { echo "No difference." ; } \
		|| { \
			[ $$? -eq 1 ] \
				&& { echo "\nPlease review difference!" >&2 ; } \
				|| { echo "Failure in diff" >&2 ; exit $$? ; } \
			} ; \
		}
else
	@echo "No reference to compare against. Saving current as reference:"
	cp -r "${OUTPUT_DIR}" "${OUTPUT_PREV_DIR}"
endif

${OUTPUT_DIR}: jjb/*.yaml .tox/jjb/bin/jenkins-jobs
	tox -e jjb -- test jjb/ -o "${OUTPUT_DIR}"
	@touch ${OUTPUT_DIR}

install: .tox/jjb/bin/jenkins-jobs

.tox/jjb/bin/jenkins-jobs: tox.ini test-requirements.txt
	tox -r -e jjb --notest

clean: clean-output clean-prev

clean-output:
	rm -fR "${OUTPUT_DIR}"

clean-prev:
	rm -fR "${OUTPUT_PREV_DIR}"

changed: ${OUTPUT_PREV_DIR} ${OUTPUT_DIR}
	diff -q "${OUTPUT_PREV_DIR}" "${OUTPUT_DIR}"|cut -d\  -f4 |cut -d\/ -f2-
