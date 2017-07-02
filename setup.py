from setuptools import setup
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os


# zlib1g-dev/zesty
# libjpeg-dev/zesty

def _post_install(libname, libpath):
    from js9 import j

    # add this plugin to the config
    c = j.core.state.configGet('plugins', defval={})
    c[libname] = libpath
    j.core.state.configSet('plugins', c)
    j.do.execute("pip3 install 'git+https://github.com/zero-os/0-core#egg=0-core-client&subdirectory=client/py-client'")
    j.tools.jsloader.generateJumpscalePlugins()


class install(_install):

    def run(self):
        _install.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath), msg="Running post install task")


class develop(_develop):

    def run(self):
        _develop.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath), msg="Running post install task")


setup(
    name='JumpScale9Lib',
    version='9.0.3',
    description='Automation framework for cloud workloads library',
    url='https://github.com/Jumpscale/lib9',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=['JumpScale9Lib'],
    install_requires=[
        'Brotli>=0.6.0',
        'Cython>=0.25.2',
        'Jinja2>=2.9.6',
        'JumpScale9>=9.0.3',
        'Pillow>=4.1.1',
        'PyGithub>=1.34',
        'PyYAML>=3.12',
        'SQLAlchemy>=1.1.9',
        'asyncssh>=1.9.0',
        'colored-traceback>=0.2.2',
        'colorlog>=2.10.0',
        'cson>=0.7',
        'docker>=2.2.1',
        'gevent>=1.2.1',
        'grequests>=0.3.0',
        'influxdb>=4.1.0',
        'msgpack-python>=0.4.8',
        'netaddr>=0.7.19',
        'netifaces>=0.10.5',
        'numpy>=1.12.1',
        'ovh>=0.4.7',
        'paramiko>=2.1.2',
        'path.py>=10.3.1',
        'peewee>=2.9.2',
        'psutil>=5.2.2 ',
        'psycopg2>=2.7.1',
        'pudb>=2017.1.2',
        'pyOpenSSL>=17.0.0',
        'pyblake2>=0.9.3',
        'pycapnp>=0.5.12',
        'pymux>=0.13',
        'redis>=2.10.5',
        'requests>=2.13.0',
        'tarantool>=0.5.4',
        'toml>=0.9.2',
        'uvloop>=0.8.0',
        'watchdog>=0.8.3',
        'xonsh>=0.5.9',
        'dnspython>=1.15.0',
        'libvirt-python>=3.3.0',
        'apache_libcloud>=2.0.0',
        'python-etcd>=0.4.5',
        'zerotier>=1.1.2',
        'packet-python>=1.33'
    ],
    cmdclass={
        'install': install,
        'develop': develop,
        'developement': develop
    },
)
