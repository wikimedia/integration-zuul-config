#!/usr/bin/env python3

from collections import OrderedDict
import json
import os
import subprocess
import sys

import lib

if os.path.exists('package.json'):
    print('package.json already exists')
    sys.exit(0)

ext = os.getcwd().split('/')[-1]
print('Configuring banana checker for %s extension...' % ext)

grunt_file_for_ext_json = """/*jshint node:true */
module.exports = function ( grunt ) {
	grunt.loadNpmTasks( 'grunt-banana-checker' );
	grunt.loadNpmTasks( 'grunt-jsonlint' );

	var conf = grunt.file.readJSON( 'extension.json' );
	grunt.initConfig( {
		banana: conf.MessagesDirs,
		jsonlint: {
			all: [
				'**/*.json',
				'!node_modules/**'
			]
		}
	} );

	grunt.registerTask( 'test', [ 'jsonlint', 'banana' ] );
	grunt.registerTask( 'default', 'test' );
};
"""  # noqa

grunt_file_for_php_eww = """/*jshint node:true */
module.exports = function ( grunt ) {
	grunt.loadNpmTasks( 'grunt-banana-checker' );
	grunt.loadNpmTasks( 'grunt-jsonlint' );

	grunt.initConfig( {
		banana: {
			all: 'i18n/'
		},
		jsonlint: {
			all: [
				'**/*.json',
				'!node_modules/**'
			]
		}
	} );

	grunt.registerTask( 'test', [ 'jsonlint', 'banana' ] );
	grunt.registerTask( 'default', 'test' );
};
"""  # noqa

if os.path.exists('extension.json'):
    grunt_file = grunt_file_for_ext_json
else:
    grunt_file = grunt_file_for_php_eww

if os.path.exists('extension.json'):
    with open('extension.json') as f:
        data = json.load(f)
        if 'MessagesDirs' not in data:
            print('No MessagesDirs set.')
            sys.exit(1)
else:
    if not os.path.isdir('i18n'):
        print('i18n directory does not exist')
        sys.exit(0)
with open('Gruntfile.js', 'w') as f:
    f.write(grunt_file)

package_data = OrderedDict([
    ('private', True),
    ('scripts', {'test': 'grunt test'}),
    ('devDependencies', OrderedDict())
])
for i in ['grunt', 'grunt-cli', 'grunt-banana-checker', 'grunt-jsonlint']:
    package_data['devDependencies'][i] = lib.get_npm_version(i)
with open('package.json', 'w') as f:
    f.write(json.dumps(package_data, indent='  ') + '\n')
subprocess.call(['npm', 'install'])
res = subprocess.call(['npm', 'test'])
if res != 0:
    print('Error: npm test failed.')
    sys.exit(0)
else:
    print('Yay, npm test passed!')
# Add node_modules to gitignore...
if os.path.exists('.gitignore'):
    add = True
    with open('.gitignore') as f:
        for line in f.read().splitlines():
            if line.strip().startswith('node_modules'):
                add = False
                break
        if add:
            with open('.gitignore', 'a') as f:
                f.write('node_modules/\n')
            print('Added "node_modules/" to .gitignore')
else:
    with open('.gitignore', 'w') as f:
        f.write('node_modules/\n')
        print('Created .gitignore with "node_modules/"')
msg = 'build: Configure banana-checker and jsonlint'
if len(sys.argv) > 1:
    msg += '\n\nChange-Id: %s' % sys.argv[1]
lib.commit_and_push(files=['package.json', 'Gruntfile.js', '.gitignore'],
                    msg=msg, branch='master', topic='banana')
log1 = subprocess.check_output(['git', 'log', '--oneline', '-n', '1'])
sha1 = log1.decode().split(' ', 1)[0]
subprocess.call(['ssh', '-p', '29418', 'gerrit.wikimedia.org',
                 'gerrit', 'review', '-m', '"check experimental"', sha1])
sys.exit(0)
