from setuptools import setup

setup(
	name='fizzyblog',
	version='1.0',
	packages=['fizzyblog'],
	url='https://github.com/TheElectronWill/fizzyblog',
	license='GPLv3',
	author='TheElectronWill',
	description='Blog engine in python',
	install_requires=['markdown', 'toml', 'python-markdown-math']
)
