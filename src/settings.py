#!/usr/bin/env python
#coding=utf-8

#
# Copyright (c) 2017 Maurizio Montel.
#
# This file is part of the pg-data-loader distribution.
#   (https://github.com/dr-prodigy/pg-data-loader)
#
# pg-data-loader is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, version 3.
#
# pg-data-loader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# doc/info/contacts: https://github.com/dr-prodigy
#

import os

DB_USER = 'my_user'
DB_PASSWORD = 'my_pwd'
DB_NAME = 'my_db'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_COLLATION = 'UTF-8'

INPUT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "input_files/")
BAK_FOLDER = INPUT_FOLDER + 'bak/'


IMPORT_CONFIGS = {
                'CSV_LOADER_SAMPLE':
                {
                    'file_name'      : '*csv_loader_sample.csv',
                    'table_name'     : 'csv_loader_sample',
                    'rebuild_table'  : True,
                    'skip_rows_until': None,
                    'skip_rows'      : 1,
                    'delimiter': ';',
                    'quotes': '',
                    'db_columns'     :
                        ['col1', 'col2', 'col3'],
                    'csv_columns'    :
                        [0, 1, 2],
                    'values'         :
                        ['numeric,', 'string8859-1', 'string8859-1'],
                    'table_create'   :
                        """create table {}
                        (
                        col1 numeric,
                        col2 varchar(50),
                        col3 varchar(50)
                        );"""
                },
                'XLS_LOADER_SAMPLE':
                {
                    'file_name': '*xls_loader_sample.xls',
                    'table_name': 'xls_loader_sample',
                    'rebuild_table': True,
                    'skip_rows_until': None,
                    'skip_rows': 0,
                    'delimiter': ',',
                    'quotes': '',
                    'db_columns':
                        ['dates1', 'numerics', 'dates2', 'ints', 'strings'],
                    'csv_columns':
                        [0, 1, 2, 3, 4],
                    'values':
                        ['xldate', 'numeric,', 'xldate', 'numeric,', 'string8859-1'],
                    'table_create':
                        """create table {}
                        (
                        dates1 date,
                        numerics numeric,
                        dates2 date,
                        ints integer,
                        strings text
                        );"""
                },
                'XLSX_LOADER_SAMPLE':
                {
                    'file_name': '*xlsx_loader_sample.xlsx',
                    'table_name': 'xlsx_loader_sample',
                    'rebuild_table': True,
                    'skip_rows_until': None,
                    'skip_rows': 0,
                    'delimiter': ',',
                    'quotes': '',
                    'db_columns':
                        ['dates1', 'numerics', 'dates2', 'ints', 'strings'],
                    'csv_columns':
                        [0, 1, 2, 3, 4],
                    'values':
                        ['xldate', 'numeric,', 'xldate', 'numeric,', 'string8859-1'],
                    'table_create':
                        """create table {}
                        (
                        dates1 date,
                        numerics numeric,
                        dates2 date,
                        ints integer,
                        strings text
                        );"""
                },
}
# un-comment to manage specific settings
# from settings_local import *