ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUILD_DIR := ${ROOT_DIR}/build
OUTPUT_DIR := ${BUILD_DIR}/output
OUTPUT_PREV_DIR := ${BUILD_DIR}/output-prev

.PHONY: test install clean clean-diff clean-output clean-prev changed

test: jjb/*.yaml clean-output clean-diff .tox/jjb/bin/jenkins-jobs
	tox -e jjb -- test jjb/ -o "${OUTPUT_DIR}"
	test -d ${OUTPUT_PREV_DIR} && colordiff -u -r "${OUTPUT_PREV_DIR}" "${OUTPUT_DIR}" | tee ${BUILD_DIR}/diff.txt ; \
	test ! -d ${OUTPUT_PREV_DIR} && cp -r "${OUTPUT_DIR}" "${OUTPUT_PREV_DIR}"

install: .tox/jjb/bin/jenkins-jobs

.tox/jjb/bin/jenkins-jobs: tox.ini test-requirements.txt
	tox -r -e jjb --notest

clean: clean-diff clean-output clean-prev

clean-diff:
	rm -f ${BUILD_DIR}/diff.txt

clean-output:
	rm -fR "${OUTPUT_DIR}"

clean-prev:
	rm -fR "${OUTPUT_PREV_DIR}"

changed:
	diff -q "${OUTPUT_PREV_DIR}" "${OUTPUT_DIR}"|cut -d\  -f4 |cut -d\/ -f2-
