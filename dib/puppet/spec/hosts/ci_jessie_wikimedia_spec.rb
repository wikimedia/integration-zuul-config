require 'rspec-puppet'
require 'puppetlabs_spec_helper/puppet_spec_helper'

def get_module_path
    if ENV['PUPPET_DIR']
        File.expand_path(
            File.join( ENV['PUPPET_DIR'], 'modules'))
    else
        File.expand_path(
            File.join(
                __dir__, '../../../../../../operations/puppet/modules'))
    end
end

RSpec.configure do |c|
    c.manifest = File.expand_path(File.join(__dir__, '..', '..', 'ciimage.pp'))
    c.module_path = get_module_path
end


describe 'ci-jessie-wikimedia' do
    let(:facts) { {
        :initsystem => 'systemd',
        :lsbdistrelease => 'Jessie',
        :lsbdistid => 'Debian',
    } }
    before(:each) {
        # Poor hiera() mock
        Puppet::Parser::Functions.newfunction(:hiera, :type => :rvalue) do |args|
            case args[0]
            when 'jenkins_agent_username'
                'jenkins'
            else
                return args[1]
            end
        end
    }
    it { should compile }
end
