
apt-get install -y git 
curl -s https://install.zerotier.com/ | sudo bash
mkdir sal_tests; cd sal_tests
git clone https://github.com/threefoldtech/jumpscale_lib.git  -b ${1}
cd jumpscale_lib
if [ ${1} = "True" ]; then
    print("################################################")
    sudo bash tests/integration_tests/travis/jumspcale_install.sh 
fi
cd tests/integration_tests/
pip3 install -r requirements.txt
#sudo ln -sf /usr/sbin/zerotier-cli /opt/bin/zerotier-cli
sed -i -e"s/^nodeip=.*/nodeip=${2}/" config.ini
sed -i -e"s/^zt_token=.*/zt_token=${3}/" config.ini
#nosetests -v -s ${5} --tc-file=config.ini 
