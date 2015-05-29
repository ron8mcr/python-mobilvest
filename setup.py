import os
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='python-mobilvest',
    version="0.0.1",
    description='Application for working with API of mobilvest.ru',
    long_description=readme,
    author="Roman Gorbil",
    author_email='rons_mail@mail.ru',
    url='https://github.com/ron8mcr/python-mobilvest',
    packages=['mobilvest'],
    include_package_data=True,
    install_requires=['setuptools', 'requests'],
    test_requires=['responses'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
