include help.mk
include config.mk

# Checkout, tag, and build a tarball
tarball: tag doTarball

# Just build tarball with already checkedout code
doTarball: verifyReleaseGiven verifyPreviousVersion getMakeRelease getPreviousTarball
	test -f ${mwDir}/.git/config || (				\
		echo "Check out repo first: make tarball"; 		\
		echo; exit 1						\
	)

	mkdir -p ${targetDir}
	${makeRelease} --previous ${prevReleaseVer} --sign		\
		--output_dir ${targetDir} ${mwDir} ${releaseVer}

#
showPreviousRelease:
	echo ${prevReleaseVer}

# Retreive all artifacts from the release server before releaseVer.
getAllTarballs:
	${MAKE} getPreviousTarball releaseVer=${prevReleaseVer} &&	\
		${MAKE} getAllTarballs releaseVer=${prevReleaseVer}
#
getPreviousTarball:
	# Fork another, or we get recursiveness
	${MAKE} downloadTarball releaseVer=${prevReleaseVer}		\
		majorReleaseVer=${prevMajorVer}

# Download all artifacts for a release.
downloadTarball:
	test -n "${thisMinorVer}" || (					\
		echo "Minor version not found in '${releaseVer}'!";	\
		echo; exit 1						\
	)

	${MAKE} downloadAndVerifyFile 					\
		targetFile=mediawiki-core-${releaseVer}.tar.gz || ${doNotFail}
	${MAKE} downloadAndVerifyFile 					\
		targetFile=mediawiki-${releaseVer}.tar.gz || ${doNotFail}
	${MAKE} downloadAndVerifyFile					\
		targetFile=mediawiki-${releaseVer}.patch.gz || ${doNotFail}
	${MAKE} downloadAndVerifyFile 					\
		targetFile=mediawiki-i18n-${releaseVer}.patch.gz || ${doNotFail}

#
downloadAndVerifyFile:
	${MAKE} downloadFile targetFile=${targetFile} || true
	test ! -f ${targetDir}/${targetFile} ||				\
		${MAKE} downloadFile targetFile=${targetFile}.sig ||	\
		${continueWithoutSignature}
	test ! -f ${targetDir}/${targetFile} -o				\
		! -f ${targetDir}/${targetFile}.sig ||			\
		${MAKE} verifyFile targetFile=${targetFile}

downloadFile:
	mkdir -p ${targetDir}

	test -f ${targetDir}/${targetFile} || (				\
		echo -n Downloading ${targetFile}...;			\
		${CURL} ${releasesUrl}${majorReleaseVer}/${targetFile}	\
			-o ${targetDir}/${targetFile} || (		\
			echo; echo Could not download ${targetFile}; 	\
			echo; exit 1					\
		) || exit 1;						\
		echo							\
	)


verifyFile:
	gpg --batch --verify ${targetDir}/${targetFile}.sig		\
		${targetDir}/${targetFile} || (				\
		echo Could not verify ${targetFile};			\
		echo; exit 1						\
	)
	echo Successfully verified ${targetFile}
	echo

getMakeRelease: ${releaseDir}/.git
${releaseDir}/.git: installGitArchiveAll
	test -d $@ || git clone ${gerritHead}/mediawiki/tools/release	\
		${releaseDir}

installGitArchiveAll:
	pip list --format=legacy | grep git-archive-all > /dev/null ||	\
		pip install git-archive-all

# Tag the checkout with the releaseVer.
tag: verifyReleaseGiven verifyTagNotExist verifyPrivateKeyExists checkoutRelBranch
	# Without the cd, this fails with "fatal: $program_name cannot
	# be used without a working tree." on git v2.11.0
	echo "Ensuring submodules are up to date ..."
	(								\
		cd ${mwDir};						\
		${GIT} submodule -q foreach				\
			'git fetch && git checkout -q ${relBranch}'	\
	)

	(								\
		export modules=`${GIT} status -s extensions skins |	\
			awk '{print $$2}'`;				\
		test -z "$$modules" || (				\
			echo "Committing submodules: $$modules";	\
			cd ${mwDir};					\
			${GIT} add $$modules;				\
			${GIT} commit -m				\
				"Updating submodules for ${releaseVer}"	\
				$$modules				\
		)							\
	)

	test `${GIT} status -s | wc -l` -eq 0 || (			\
		echo "There is uncommitted work!";			\
		echo; exit 1						\
	)

	echo Tagging submodules...
	(								\
		cd ${mwDir};						\
		${GIT} submodule -q					\
			foreach git tag -sa ${releaseVer}		\
			-m ${releaseTagMsg};				\
	)

	echo Tagging core...
	${GIT} tag -sa ${releaseVer} -m ${releaseTagMsg}

# Remove the tag specified in releaseVer.
removeTag: verifyReleaseGiven
	${GIT} fetch $(if $(filter-out false,${fetchSubmodules}),	\
				--recurse-submodules=yes)
	(								\
		cd ${mwDir};						\
		${GIT} submodule foreach				\
			'git tag -d ${releaseVer} ${force}';		\
	)
	${GIT} tag -d ${releaseVer}


clone:
	test -f ${mwDir}/.git/config && (				\
		echo "Fetching the latest code ...";			\
		${GIT} fetch 						\
		$(if $(filter-out false,${fetchSubmodules}),		\
			--recurse-submodules=yes)			\
	) || (								\
		echo "Cloning repository ...";				\
		git clone						\
		$(if $(filter-out false,${fetchSubmodules}),		\
			--recurse-submodules)				\
			${mwGit} ${mwDir}				\
	)

# Checkout relBranch
checkoutRelBranch: clone
	test "${relBranch}" != "---" || (				\
		echo "No release branch given";				\
		echo; exit 1						\
	)

	echo "Checking out release branch (${relBranch})..."
	${GIT} checkout -q ${relBranch}
  ifneq	"false" "${fetchSubmodules}"
	(								\
		cd ${mwDir};						\
		git submodule update --init;				\
	)
  endif

# Show revision matching HEAD.
showHeadRev: fetchSubmodules=false
showHeadRev: clone checkoutRelBranch
	${GIT} log -1 --oneline

# Show information about the key used for signing.
showKeyInfo:
	gpg --list-key ${keyId}

# Make sure the releaseVer tag is signed correctly.
verifyTag: verifyReleaseGiven checkoutRelBranch
	echo "Checking core"
	${GIT} verify-tag ${releaseVer} || (				\
		echo "Cannot verify signature on tag '${releaseVer}'";	\
		echo; exit 1						\
	)
	test "${revision}" = "HEAD" || (				\
		test "`${GIT} log -1 ${releaseVer} --format=%H`" = 	\
			"${revision}" || (				\
				echo "Wrong revision tagged.";		\
				echo; exit 1				\
		)							\
	)
	(								\
		cd ${mwDir};						\
		${GIT} submodule foreach 'git fetch &&			\
			git verify-tag ${releaseVer} || (		\
				echo -n Could not verify signature on;	\
				echo " ${releaseVer} for $$name";	\
				echo; exit 1				\
			)';						\
	)

#
verifyReleaseGiven:
	test "${releaseVer}" != "---" || (				\
		echo "Please specify releaseVer!";			\
		echo; exit 1						\
	)

verifyPrivateKeyExists:
	gpg --list-secret-keys ${keyId} > /dev/null 2>&1 || (		\
		echo "No private key matching '${keyId}'"; 		\
		echo; exit 1						\
	)


verifyRevisionExists: clone
	$(if $(filter-out 0,$(shell 					\
			${GIT} ls-tree ${revision} | wc -l		\
		)),							\
		exit 0,							\
		exit 1							\
	)

verifyTagNotExist: verifyReleaseGiven clone
	test -z "`cd ${mwDir};						\
			${GIT} log -1 --oneline ${releaseVer} 2>	\
				/dev/null`" || (			\
		echo "Release tag already set!";			\
		echo; exit 1						\
	)

verifyPreviousVersion:
