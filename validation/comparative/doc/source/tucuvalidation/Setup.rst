.. _Setup:

===========
Setup-Linux
===========

Install Prerequisites
---------------------

All the prereqs for the tests (not including those for tucuxi or nonmem programs) can be installed with the following command from the 'dev/test/global' directory: ::

	~$ sudo ./install


If you used the above command and it works, you can skip to installing Tucuxi and nonmem now. If you didn't, you can install python, pip, freetype and the python modules as shown below.

* **Python 3.5**

  * Debian/Ubuntu: ::

         ~$ sudo apt-get install python3.5
         ~$ sudo apt-get install python-tk

  * Redhat/Fedora/centOS: ::

	~$ su

	~$ yum install python3.5

* **Python Modules**

  * To install the modules with python pip, first install the following packages: ::

	~$ sudo apt-get install python-pip
	~$ sudo apt-get install libfreetype6-dev

    Or use yum or brew (mac) or choco (windows) to install them if your on another OS.
    Then install the following python modules (if windows get numpy and scipy from here
    http://www.lfd.uci.edu/~gohlke/pythonlibs/ because its a mess): ::

	~$ sudo pip3 install numpy
	~$ sudo pip3 install beautifulsoup4
	~$ sudo pip3 install matplotlib
	~$ sudo pip3 install scipy
	~$ sudo pip3 install colorama
	~$ sudo pip3 install lxml

  * To install with easy_install: ::

	~$ easy_install numpy matplotlib beautifulsoup4 scipy colorama lxml

..   There is a file, 'requirements' in the 'src/test/global' directory that can be used to install the required python modules using pip. Of course, pip is required for that (see below on how to install pip). So to install just the python modules: ::

..	~$ sudo pip install -r requirements


* **NONMEM 7.20**

    The tests have been used with NONMEM version 7.20. It may work for newer versions, but there is no guaranties it will. For installing NONMEM, please follow the procedure corresponding to your NONMEM version.

* **tucucli**

    If tucucli is available as is, the tests will work. If tucucli is placed somewhere not on the PATH, then simply use the -t option to specify the path to the executable.
