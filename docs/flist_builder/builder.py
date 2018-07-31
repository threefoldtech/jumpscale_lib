#!/usr/bin/python3

"""
This script is used to quickly deploy a ubuntu container on a 0-OS node and allow you to ssh into it

This container is used to build flist, it contains already preinstalled tools like git, mc, build-essential.

"""


from jumpscale import j
import click


@click.command()
@click.argument('ip')
def main(ip):
    client = j.clients.zos.get('builder', data={'host': ip})
    node = j.sal_zos.node.get(client)
    print('creating builder container...')
    container = node.containers.create(name='buidler',
                                       flist='https://hub.gig.tech/gig-official-apps/ubuntu-bionic-build.flist',
                                       nics=[{'type': 'default'}],
                                       ports={2222: 22})
    print('builder container deployed')
    print("to connect to it do: 'ssh root@%s -p 2222' (password: rooter)" % node.addr)


if __name__ == '__main__':
    main()
