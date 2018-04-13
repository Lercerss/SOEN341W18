[![Build Status](https://travis-ci.org/Lercerss/SOEN341W18.svg?branch=master)](https://travis-ci.org/Lercerss/SOEN341W18)
[![codecov](https://codecov.io/gh/Lercerss/SOEN341W18/branch/master/graph/badge.svg)](https://codecov.io/gh/Lercerss/SOEN341W18)
# SOEN341W18
Software Process Winter 2018 Group Project - SA3.
This is a simple Q&A website built using the Python [django web framework](djangoproject.com).

## Installation
This project uses Python 3.X. To install requirements simply `pip install -r requirements.txt`.

## Quickstart
Since this project is built using django, all commands must go through the `manage.py` entrypoint.
  - Tests: `python SA3/manage.py test SA3/qa_web`
  - Starting the server: `python SA3/manage.py runserver`
  - Build search index: `python SA3/manage.py rebuild_index`
  - Update search index: `python SA3/manage.py update_index`

User can enable search index automatically updated by setting `HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'` in `qa_web/settings.py`.  

## Django config
  - Database: SQLite3
  - App module: qa_web
  - Settings found under `SA3/qa_web/settings.py`

## Superuser credentials:

Username|Password
--------|---------
admin   |SA3qa_web

## Static analysis
This project uses a tool called **Pylint** to check the code quality of the Python source files. Pylint will use a plugin called `pylint-django` that adapts the bug/quality checker to Django-specific commands.

To run this Python quality checker on our web application, run the following command:

`pylint --load-plugins pylint_django SA3/qa_web`

