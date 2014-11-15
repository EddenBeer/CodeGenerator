#from distutils.core import setup
from cx_Freeze import setup, Executable

setup(
    name='CodeGenerator',
    version='0.1',
    packages=['/home/ed/PycharmProjects/CodeGenerator/CodeGenerator/'],
    url='',
    license='',
    author='Ed den Beer',
    author_email='eddenbeer@gmail.com',
    description="Generate copy logic out of a 1 or 2 column csv file."
)
