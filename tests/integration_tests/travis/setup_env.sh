
apt-get install -y git python3-pip
curl -s https://install.zerotier.com/ | sudo bash
mkdir sal_tests; cd sal_tests
git clone https://github.com/threefoldtech/jumpscale_lib.git  -b ${1}
cd jumpscale_lib
echo "#######${1}#####################${2}##################"
# if [ ${2} = "True" ]; then
#     sudo bash tests/integration_tests/travis/jumspcale_install.sh 
# fi
cd tests/integration_tests/
pip3 install -r requirements.txt
#sudo ln -sf /usr/sbin/zerotier-cli /opt/bin/zerotier-cli
sed -i -e"s/^nodeip=.*/nodeip=${3}/" config.ini
sed -i -e"s/^zt_token=.*/zt_token=${4}/" config.ini
#nosetests -v -s ${5} --tc-file=config.ini 
