.. Qiskift documentation master file, created by
   sphinx-quickstart on Sat May  8 12:35:13 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to QiskiFT!
===================================
QiskiFT is a package for implementing Quantum Error Correction and Quantum Fault Tolerance in Python using `Qiskit <https://qiskit.org/>`_. It automates much of the process of implementing fault tolerant computation, allowing users to create fault-tolerant circuits in only a few more lines of code than non-fault-tolerant circuits. For example, Deutsch's Algorithm can be implemented fault-tolerantly in 15 lines of code.

.. list-table::

       * - .. figure:: Images/Deutsch.png
              :height: 800

              A non-fault-tolerant implementation of Deutsch's Algorithm.
         - .. figure:: Images/DeutschFT.png
              :height: 800

              A fault-tolerant implementation of Deutsch's Algorithm.

Below are links to documentation for each of QiskiFT's modules.

.. toctree::
   :maxdepth: 2

   API
   Demos

This documentation is available as both a `website <https://druidowm.github.io/qiskift/>`_ and a :download:`pdf download<../docs_creation/_build/latex/qiskift.pdf>`. The code for this repository can be found `here <https://github.com/druidowm/qiskift>`_.
