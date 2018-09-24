# set -ex
# apt-get install libvirt-bin libvirt-dev qemu-system-x86 qemu-system-common genisoimage -y

if [ "$(uname)" == "Darwin" ]; then
    echo 'darwin'
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    apt-get install python3-pip libffi-dev libpython3-dev libssh-dev libsnappy-dev build-essential python3-dev pkg-config libvirt-dev libsqlite3-dev ipmitool -y
fi



pip3 install -U cryptography
#for development mode
pip3 install -e .

js_init generate
