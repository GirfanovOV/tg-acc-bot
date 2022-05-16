.. Accountant-Bot documentation master file, created by
   sphinx-quickstart on Tue May 10 14:39:34 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Accountant-Bot's documentation!
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   bot
   util
   test_data

**************
Accountant-Bot
**************

Cost accounting module written in Python 3.

The telegram bot acts as an interface, the API to which is written in python `python-telegram-bot <https://github.com/python-telegram-bot/python-telegram-bot>`_. Therefore, for deployment, you must first obtain a token from `Bot-father <https://t.me/botfather>`_.

Expenses vary by category and by time.

Available categories (total 6) :
 - entertainment
 - restaurants
 - transportation
 - pharmacy
 - supermarkets
 - others

Each spending entry is distinguished by the exact time it was recorded.

The user interface consists of a simple set of commands:

 - ``/add`` - add an expense entry. After the command is entered, it is proposed to select a category of spending, after determining the category, it is necessary to indicate how much money was spent. If successful, a message will appear stating that the category has been successfully updated.
 - ``/set_limit`` - add a weekly limit for a certain category. After entering the command, as in the case of ``/add`` , you must first select a category, then specify a limit for it. If successful, a message will appear stating that the limit for the category has been updated. Initially, all categories have no limit. If a category limit is set, then adding expenses to it automatically checks if the limit is exceeded and warns the user about it.
 - ``/week`` - display last week's expenses by category. The last week starts exactly 7 days ago from the introduction of the ``/week`` command. In addition, the total amount of money spent per week is calculated.
 - ``/weeks`` - display the total amount of money spent by week. Statistics will be collected for all recorded in the database.
 - ``/help`` - help for the user.

Commands for testing:

 - ``/load_test_1`` - loads specially prepared data about 100 spendings for the last week.
 - ``/load_test_2`` - loads specially prepared data about 1000 spending evenly distributed over 8 weeks.

Testing of functional elements:

 - ``doit`` utility:
    - ``doit test`` - to run the test module.
    - ``doit coverage`` - to generate test coverage.

Building :

 - ``doit html`` - build sphinx documentation.
 - ``doit check`` - check pydocstyle, flake8 and tests.
 - ``doit wheel`` - build the wheel module.
 - ``doit sdist`` - build sources.

 Installation : ``pip install acc_bot``

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
