require 'rspec-puppet'
require 'puppetlabs_spec_helper/puppet_spec_helper'

RSpec.configure do |c|
    c.manifest = File.expand_path(File.join(__dir__, '..', '..', 'ciimage.pp'))
    c.module_path = File.expand_path(
        File.join(
            __dir__, '../../../../../../operations/puppet/modules'))
end

describe 'ci-jessie-wikimedia' do
    let(:facts) { {
        :initsystem => 'systemd',
        :lsbdistrelease => 'Jessie',
        :lsbdistid => 'Debian',
    } }
    it { should compile }
end
