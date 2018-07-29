#!/bin/bash
echo args: $@

echo "Branch in use: $1" > /tmp/HelloWorld

mkdir -p /tmp/archives
tar -czvf /tmp/archives/jumpscale-sandbox.tar.gz /tmp/HelloWorld
