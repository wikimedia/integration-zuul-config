require 'puppetlabs_spec_helper/rake_tasks'

task :default => [:help]

Rake::Task[:lint].clear
PuppetLint::RakeTask.new :lint do |config|
    config.fail_on_warnings = true  # be strict
    config.log_format = '%{path}:%{line} %{KIND} %{message} (%{check})'
end

desc 'Run spec for dib/puppet'
task :dib_spec do
    Dir.chdir 'dib/puppet' do
        fail unless system('rake spec')
    end
end

desc 'Run all build/tests commands (CI entry point)'
task test: [:syntax, :lint, :dib_spec]

desc 'Show the help'
task :help do
    system 'rake -T'
end
