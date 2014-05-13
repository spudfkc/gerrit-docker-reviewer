from setuptools import setup

setup(name='gerrit-reviewer',
        version='0.1',
        description='Checks out a change from Gerrit, builds it, deploys it to a docker container',
        url='',
        author='ncc',
        author_email='ncaley@us.ibm.com',
        license='?',
        packages=['reviewer'],
        zip_safe=False)
