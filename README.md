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


## Django config
  - Database: SQLite3
  - Project module: SA3
  - App module: qa_web
  - Settings found under `SA3/SA3/settings.py`

## Superuser credentials:

Username|Password
--------|---------
admin   |SA3qa_web
