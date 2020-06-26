#!/bin/bash
set -eu -o pipefail
mkdir log/

# Fetch VM
# See <https://www.mediawiki.org/wiki/Continuous_integration/Qemu#Snapshots>
cp /srv/vm-images/qemu-debian10buster-2020_05_04b.img vm.img
install -m 600 /srv/vm-images/sshkey_qemu_root_v1 root.key

# Start VM
# - Make the VM's ssh port visible to the Jenkins agent (22 -> 4293)
# - Run qemu in the background so we can run ssh meanwhile.
qemu-system-x86_64 -device virtio-net,netdev=user.0 -netdev user,id=user.0,hostfwd=tcp::4293-:22 -m 4096 -nographic vm.img >/dev/null 2>log/qemu_err &
VM_PID="$!"
kill_vm() {
  kill -9 $VM_PID
}
trap kill_vm EXIT

# - '-F'
#   Don't inherit any /etc/ssh or ~/.ssh settings.
# - 'BatchMode=yes'
#   Avoid the SSH command from hanging indefinitely on a password prompt
#   if the ssh key is rejected for some reason.
#   Avoid failing with "ssh_askpass: exec(/usr/bin/ssh-askpass): No such file"
#   Similar to "PasswordAuthentication=no", except that this actually works.
# - 'UserKnownHostsFile=/dev/null StrictHostKeyChecking=no'
#   Avoid interactive prompt for adding the VM to a ssh/known_hosts file.
VM_TARGET='root@localhost'
SSH_OPTS='-p 4293 -i ./root.key -F /dev/null -o BatchMode=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -E log/ssh_err'
SCP_OPTS='-P 4293 -i ./root.key -F /dev/null -o BatchMode=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

# Wait for VM to initialise
while ! ssh $SSH_OPTS $VM_TARGET 'true'; do
  echo "... waiting for Qemu VM"
  sleep 2
done
echo 'Connected!'

# Define run command for wikimedia/fresh Jenkins job
# TODO: Set this as Jenkins build parameter.
# See https://phabricator.wikimedia.org/T250808#6117684
QEMU_RUN_COMMAND='./test'

# Copy run command to VM
printf '
set -eux -o pipefail

mkdir -p src/
cd src/
git init --quiet
git fetch --depth 2 --quiet %q %q
git checkout --quiet -b %q FETCH_HEAD
git submodule --quiet update --init --recursive

%q
' "${ZUUL_URL}/${ZUUL_PROJECT}" "+${ZUUL_REF}:${ZUUL_REF}" "${ZUUL_BRANCH}" "${QEMU_RUN_COMMAND}" > test_command.sh
scp $SCP_OPTS test_command.sh $VM_TARGET:/tmp/test_command.sh 2>log/scp_err

# Run test command
ssh $SSH_OPTS $VM_TARGET 'bash /tmp/test_command.sh'
VM_CMD_EXIT="$?"

# End
exit $VM_CMD_EXIT
