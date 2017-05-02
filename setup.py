from distutils.core import setup

setup(
    name='JumpScale9Lib',
    version='9.0.0a1',
    description='Automation framework for cloud workloads library',
    url='https://github.com/Jumpscale/lib9',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=['JumpScale9Lib'],
    install_requires=[
        'redis',
        'colorlog',
        'pytoml',
        'ipython',
        'colored_traceback',
        'pystache',
        'libtmux',
        'httplib2',
        'netaddr',
        'peewee'
    ]
)
