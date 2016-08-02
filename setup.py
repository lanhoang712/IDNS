from setuptools import setup

APP = ['MainProg.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True,
 #'iconfile': 'bell.icns',
 'includes': ['sip', 'PyQt4','pandas','sqlite3']}

setup(
app=APP,
data_files=DATA_FILES,
options={'py2app': OPTIONS},
setup_requires=['py2app'],
)