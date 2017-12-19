require 'rspec-puppet'
require 'rspec-puppet-facts'
require 'puppetlabs_spec_helper/puppet_spec_helper'
include RspecPuppetFacts

RSpec.configure do |c|
    c.manifest = File.expand_path(File.join(__dir__, '..', '..', 'ciimage.pp'))
    if ENV['PUPPET_DIR']
        c.module_path = File.expand_path(
            File.join( ENV['PUPPET_DIR'], 'modules'))
    else
        c.module_path = File.expand_path(
            File.join(
                __dir__, '../../../../../../operations/puppet/modules'))
    end
end

if ENV['PUPPET_DEBUG']
    Puppet::Util::Log.level = :debug
    Puppet::Util::Log.newdestination(:console)
end

describe 'ci-jessie-wikimedia' do
    test_on = {
        supported_os: [
            {
                'operatingsystem' => 'Debian',
                'operatingsystemrelease' => ['8'],
            }
        ],
    }
    on_supported_os(test_on).each do |os, facts|
        context "on #{os}" do
            let(:facts) do
                facts.merge({initsystem: 'systemd'})
            end
            it { should compile }
        end
    end
end
