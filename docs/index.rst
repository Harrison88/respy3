Respy3
======

.. toctree::
   :hidden:
   :maxdepth: 1

Respy3 is an implementation of the RESP3 protocol in Python.


Installation
------------

To install respy3,
run this command in your terminal:

.. code-block:: console

   $ pip install respy3


Usage
-----

Respy3's usage looks like:

.. code-block:: python

   >>> import respy3
   >>> reader = respy3.Resp3Reader()
   >>> reader.feed(b"+PONG\r\n")
   >>> reader.parse()
   b'PONG'
   >>> respy3.write_command(b"HELLO", b"3")
   b'*2\r\n$5\r\nHELLO\r\n$1\r\n3\r\n'