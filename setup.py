from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os


# zlib1g-dev/zesty
# libjpeg-dev/zesty

def _post_install(libname, libpath):
    from js9 import j
    # add this plugin to the config
    c = j.core.state.configGet('plugins', defval={})
    c[libname] = "%s/github/jumpscale/lib9/JumpScale9Lib" % j.dirs.CODEDIR
    # c[libname] = libpath
    j.core.state.configSet('plugins', c)
    j.sal.process.execute(
        "pip3 install 'git+https://github.com/spesmilo/electrum.git@3.2.2'")
    j.tools.jsloader.generate()


class install(_install):

    def run(self):
        _install.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath),
                     msg="Running post install task")


class develop(_develop):

    def run(self):
        _develop.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath),
                     msg="Running post install task")


long_description = ""
try:
    from pypandoc import convert
    long_description = convert('README.md', 'rst')
except ImportError:
    long_description = ""


setup(
    name='JumpScale9Lib',
    version='9.4.0-rc4',
    description='Automation framework for cloud workloads library',
    long_description=long_description,
    url='https://github.com/Jumpscale/lib9',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=find_packages(),
    install_requires=[
        'Brotli>=0.6.0',
        'Jinja2>=2.9.6',
        'JumpScale9>=9.4.0-rc4',
        'Pillow>=4.1.1',
        'PyGithub>=1.34',
        'SQLAlchemy>=1.1.9',
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
        'ovh>=0.4.7',
        'paramiko>=2.2.3',  # for parallel-ssh
        'path.py>=10.3.1',
        'peewee>=2.9.2',
        'psycopg2>=2.7.1',
        'pudb>=2017.1.2',
        'cryptography>=2.2.0',
        'pyOpenSSL>=17.0.0',
        'pyblake2>=0.9.3',
        'pycapnp>=0.5.12',
        'pymux>=0.13',
        'redis>=2.10.5',
        'requests>=2.13.0',
        'toml>=0.9.2',
        'uvloop>=0.8.0',
        'watchdog>=0.8.3',
        'dnspython>=1.15.0',
        'etcd3>=0.7.0',
        'zerotier>=1.1.2',
        'packet-python>=1.37',
        'blosc>=1.5.1',
        'pynacl>=1.1.2',
        'ipcalc>=1.99.0',
        'ed25519>=1.4',
        'python-jose>=1.3.2',
    ],
    cmdclass={
        'install': install,
        'develop': develop,
        'developement': develop,
    },
)
