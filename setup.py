from setuptools import setup

setup(
    name='Alchemy',
    version='0.2.0',
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

    packages=['alchemy'],
    install_requires=['PyYaml', 'docopt'],
    scripts=['alch'],
    package_data = {
        'alchemy': ["*.yml"]
    }
)
