require 'puppet-syntax/tasks/puppet-syntax'

task :default => [:help]

desc 'Run all build/tests commands (CI entry point)'
task test: [:syntax]

desc 'Show the help'
task :help do
	system 'rake -T'
end
