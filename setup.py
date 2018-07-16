from setuptools import setup

setup(
    name='alchemy',
    version='0.2.7',
    author='Sudeep Jathar',
    author_email='sudeep.jathar@gmail.com',
    url='https://github.com/sudeep9/alchemy',
    description='Simple and general puprose automation framework',
    license='MIT',
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Operating System :: POSIX :: Linux'
    ],
    entry_points = {
        'console_scripts': ['alch=alchemy.alch:run'],
    },
    packages=['alchemy'],
    install_requires=['PyYaml', 'docopt'],
    package_data = {
        'alchemy': ["*.yml"]
    }
)
