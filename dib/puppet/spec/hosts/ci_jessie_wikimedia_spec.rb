require 'rspec-puppet'
require 'puppetlabs_spec_helper/puppet_spec_helper'

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

describe 'ci-jessie-wikimedia' do
    let(:facts) { {
        :initsystem => 'systemd',
        :lsbdistrelease => '8.9',
        :lsbdistid => 'Debian',
    } }
    it { should compile }
end
