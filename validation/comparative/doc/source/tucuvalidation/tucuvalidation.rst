.. _crosscomparison:

Tucuxi-NONMEM cross comparison
==============================


.. toctree::
   :maxdepth: 2
   :includehidden:

   Setup
   Usage
   NONMEMfiles
   Sources



Summary
-------
This is a python application for running **automated tests of tucuxi** from the users point of view using the **command line interface**.

The idea is to automate user interaction with Tucuxi and with other softwares (which provide overlapping functionality (e.g.NONMEM, Pmetrix)) to compare their results for the same inputs and benchmark Tucuxi. Currently NONMEM is the only other TDM software used for testing.

The program can accept input as Tucuxi drugfiles (tdd) and Tucuxi query files (tqf), which are parsed by the Beautiful Soup `Link bs4` and fed into each program for calculation. Query files contain data for user-defined patients.

.. comments Random samples and random patients can also be used instead or as well as dataset files.

Percentiles and apriori/aposteriori calculations can be tested. At one point the suggestions for dosage adaptations (reverse engine) could be tested too.

The results from both softwares can be graphed together to take a look.

Prerequisites
-------------
**Python 3.5**

    *Modules: matplotlib, numpy, colorama, lxml, BeautifulSoup4*

**NONMEM 7.2**

**tucucli**

Usage
-----

To get the help : ::

    ./tucuvalidation.py -h
