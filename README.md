# python_what-package-provides-module

Without getting confused, there are tons of questions online about installing python packages, how to import the resulting modules, and listing what packages are available. But there doesn't seem to be the equivalent of a "--what-provides" option for pip, if you don't have a requirements.txt or pipenv. This question is similar to previous forum questions, but asks for the parent package, and not additional metadata. That said, these other questions do not get a lot of attention or many accepted answers - eg. How do you find python package metadata information given a module on StackOverflow. So forging ahead... I came up with a rough-and-ready method, based on input from sinoroc. The method proposed by sinoroc is included in the "getDistribution" function, but it doesn't work as suggested. As such I moved to a more brute-force approach of using a (Bash CLI) find command.

By way of example, there are two packages (to name a few) that will install a module called "serial" - namely "pyserial" and "serial". So assuming that one of the packages was installed, we might find it by using pip list:

`python3 -m pip list | grep serial`

However, the problem comes in if the name of the package does not match the name of the module, or if you just want to find out what package to install, working on a legacy server or dev machine.

You can check the path of the imported module - which can give you a clue. But continuing the example...
```
>>> import serial
>>> print(serial.__file__)
/usr/lib/python3.6/site-packages/serial/__init__.py
```
It is in a "serial" directory, but only pyserial is in fact installed, not serial:
```
> python3 -m pip list | grep serial
pyserial                 3.4
```
The closest I could initially get to for a solution, was to generate a requirements.txt via "pipreqs ./" which may fail on a dependent child file (as it did with me), or to reverse check dependencies via pipenv (which brings a whole set of new issues along, to get it all setup):
```
> pipenv graph --reverse
cymysql==0.9.15
ftptool==0.7.1
netifaces==0.10.9
pip==20.2.2
PyQt5-sip==12.8.1
    - PyQt5==5.15.0 [requires: PyQt5-sip>=12.8,<13]
setuptools==50.3.0
wheel==0.35.1
```
So I designed a simple solution to find what pip package provides a particular module.

## The BFG Solution

I first use a metadata query to locate the base file for the requested module. Then I find "site-packages" in the returned path, and extract the base directory. From that base directory I find all references to that base file, in the RECORD files of any modules, recursively entering all sub-directories. This uniquely identifies the package that installed the base file in question. That allows one to identify the parent package of the module.

There is also error handling for system packages and other such modules. These return any located base file, and then error out.

The attempt at using the metadata to further locate the parent package did not work out. Hence the use of a brute-force search. It would be nice to get that working if possible (may only work for system packages etc. I'm not sure).

## Run as follows:

- "-m/--module" for the module name you wish to find the package for
- "-d/--debug" for debug

```
> ./python_what-package-provides-module.py -m subprocess -d
[DEBUG] Got these arguments:
Namespace(debug=True, module='subprocess')
[DEBUG] self.location: /usr/lib64/python3.6/subprocess.py
[ERROR] location does not contain "site-packages/" substring!
Found location: /usr/lib64/python3.6/subprocess.py
[ERROR] Parsing module "subprocess"!
location: /usr/lib64/python3.6/subprocess.py
Exiting.

> ./python_what-package-provides-module.py -m serial
pyserial-3.4.dist-info

> ./python_what-package-provides-module.py -m usb
pyusb-1.0.2.dist-info
```
