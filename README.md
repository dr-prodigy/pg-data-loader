# pg-data-loader
Small quick &amp; fast tool for CSV and XLS data loading on postgreSQL databases

## Info/wiki
I wrote this tiny tool to simplify data loading of data files on postgreSQL databases.
Nothing really complex / complete: I use it to implement simple ETL procedures (ie: import files in DB table) requiring only few settings (see *settings.py* for examples).
It can read CSV and XLS(X) files, and interpret a number of different data formats.
No particular bells & whistles, but it does what it should, and it does it fast... that's what it's meant to.
Enjoy ;-)

## Technical info
Written in Python2, set up for virtualenv

#### Running pg-data-loader

Steps for running:

- create a virtualenv under venv directory running
```
..../pg-data-loader $ virtualenv venv
```
- activate virtualenv
```
..../pg-data-loader $ . venv/bin/activate
```
- install requirements
```
..../pg-data-loader $ pip install requirements/requirements.txt
```
- create postgreSQL user / db with given params (my_user, my_db ...)
- copy sample files into ..../pg-data-loader/src/input_files
- run ..../pg-data_loader/scripts/load_all.sh

## Licensing
Copyright (C) 2017 Maurizio Montel

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this program. If not, see http://www.gnu.org/licenses/.