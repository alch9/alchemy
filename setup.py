from distutils.core import setup

setup(
    name='Alchemy',
    version='0.1.0',
    author='Sudeep Jathar',
    author_email='sudeep.jathar@gmail.com',
    url='https://github.com/sudeep9/alchemy',
    description='Alchemy',

    packages=['alchemy'],
    install_requires=['PyYaml'],
    scripts=['alch'],
    package_data = {
        'alchemy': ["*.yml"]
    }
)
