#!/bin/bash

# Install saltstack
add-apt-repository ppa:saltstack/salt -y
apt-get update -y
apt-get install salt-minion -y
apt-get upgrade -y

# Set salt master location and start minion
sed -i 's/#master: salt/master: salt.coherentclothes.com/' /etc/salt/minion

# Explicitly set the id
sed -i 's/#id:/id: %s/' /etc/salt/minion

# Set the keys
read -d '' PEM <<_EOF_
%s
_EOF_

read -d '' PUB <<_EOF_
%s
_EOF_

echo "${PEM}" > /etc/salt/pki/minion/minion.pem
echo "${PUB}" > /etc/salt/pki/minion/minion.pub

service salt-minion restart
