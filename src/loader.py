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

from cStringIO import StringIO
from datetime import datetime, timedelta

import os
import sys
import shutil
import psycopg2
import csv
import re
import glob
import ast
import xlrd

from settings import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT, DB_COLLATION
from settings import INPUT_FOLDER, BAK_FOLDER, IMPORT_CONFIGS

req_import_type = ''

if len(sys.argv) < 2:
    print "Usage: {} [import type]".format(sys.argv[0])
    newlist = list()
    for i in IMPORT_CONFIGS.keys():
        newlist.append(i)
    newlist.append('ALL')
    print "Import types: {}".format('\n'.join(newlist))
else:
    req_import_type = sys.argv[1]
    print "Requested {} execution".format(req_import_type)

def main():
    error_count = line_counter = col_counter = 0
    database = None
    for import_type in IMPORT_CONFIGS:
        if import_type == req_import_type or req_import_type == 'ALL':
            filename = os.path.join(INPUT_FOLDER, IMPORT_CONFIGS[import_type]['file_name'])
            tablename = IMPORT_CONFIGS[import_type]['table_name']
            rebuild_table = IMPORT_CONFIGS[import_type]['rebuild_table']
            skip_rows_until = IMPORT_CONFIGS[import_type]['skip_rows_until']
            skip_rows = IMPORT_CONFIGS[import_type]['skip_rows']
            delimiter = IMPORT_CONFIGS[import_type]['delimiter']
            quotes = IMPORT_CONFIGS[import_type]['quotes']
            db_columns = IMPORT_CONFIGS[import_type]['db_columns']
            csv_columns = IMPORT_CONFIGS[import_type]['csv_columns']
            values = IMPORT_CONFIGS[import_type]['values']
            table_create = IMPORT_CONFIGS[import_type]['table_create']

            if len(glob.glob(filename)) > 0:
                database = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST,
                                            port=DB_PORT)
                cursor = database.cursor()

                if rebuild_table and table_create != '':
                    # table rebuild
                    drop = 'drop table if exists {}'.format(tablename)
                    print (drop)
                    cursor.execute(drop)

                    create = table_create.format(tablename)
                    print (create)
                    cursor.execute(create)

                    print("Table {} created successfully".format(tablename))
                else:
                    # table truncate
                    truncate = 'truncate table {}'.format(tablename)
                    print (truncate)

                    cursor.execute(truncate)
                    print("Table {} truncated successfully".format(tablename))

                if cursor:
                    cursor.close()

                if database:
                    database.commit()
                    database.close()

            for _file in sorted(glob.glob(filename)):
                #with open(_file, 'rb') as csvfile:
                #    dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=";,")
                try:
                    last_format_processed = last_value_processed = ''

                    print("Loading file %s..." % os.path.basename(_file))

                    tmp_filename = _file
                    if (_file.lower().endswith('.xls') or _file.lower().endswith('.xlsx')):
                        print("Converting file %s to .csv..." % os.path.basename(_file))
                        tmp_filename = csv_from_excel(_file)

                    # reset skip rows data
                    skip_rows_until = IMPORT_CONFIGS[import_type]['skip_rows_until']

                    with open(tmp_filename, 'rU') as _fileobj:
                        reader = csv.reader(_fileobj, delimiter=delimiter)

                        database = psycopg2.connect (database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

                        cursor = database.cursor()

                        # table load
                        lines_skipped = line_counter = col_counter = 0
                        db_column_list = ','.join(map(str, db_columns))

                        for row in reader:
                            last_format_processed = last_value_processed = ''

                            if skip_rows_until:
                                lines_skipped += 1
                                if delimiter.join(row) == skip_rows_until:
                                    skip_rows_until = None
                                continue

                            line_counter += 1
                            if line_counter <= skip_rows:
                                lines_skipped += 1
                                continue

                            new_row = []
                            values_format = ''
                            col_counter = 0
                            if len(csv_columns) > len(row):
                                raise Exception('ERROR: insufficient columns in input: wrong delimiter?')

                            empty_row = True
                            for col in csv_columns:
                                last_value_processed = row[col]
                                last_format_processed = values[col_counter]

                                current_value = row[col]
                                if quotes != '':
                                    current_value = current_value.strip(quotes)
                                if current_value.strip() == '' or current_value.strip() == '-':
                                    new_row.append(None)
                                elif values[col_counter] == 'string8859-1':
                                    new_row.append(current_value.decode('iso-8859-1').strip().encode(DB_COLLATION))
                                    empty_row = False
                                elif values[col_counter] == 'stringUTF-8':
                                    new_row.append(current_value.decode('UTF-8').strip().encode(DB_COLLATION))
                                    empty_row = False
                                elif values[col_counter] == 'numeric,':
                                    if current_value != '0':
                                        current_value = current_value.lstrip('0')
                                        if current_value == '': current_value = '0'
                                    new_row.append(ast.literal_eval(current_value.replace('.','').replace(',','.')))
                                    empty_row = False
                                elif values[col_counter] == 'numeric.':
                                    if current_value != '0':
                                        current_value = current_value.lstrip('0')
                                        if current_value == '': current_value = '0'
                                    new_row.append(ast.literal_eval(current_value.replace(',','')))
                                    empty_row = False
                                elif values[col_counter] == 'dateDMY':
                                    # "09/10/2012"
                                    new_row.append(datetime.strptime(current_value.replace('-','/'), "%d/%m/%Y"))
                                    empty_row = False
                                elif values[col_counter] == 'dateMDY':
                                    # "10/09/2012"
                                    new_row.append(datetime.strptime(current_value.replace('-', '/'), "%m/%d/%Y"))
                                    empty_row = False
                                elif values[col_counter] == 'dateYMD':
                                    # "2012-10-09"
                                    new_row.append(datetime.strptime(current_value.replace('-','/'), "%Y/%m/%d"))
                                    empty_row = False
                                elif values[col_counter] == 'timeHMS':
                                    # "08:27:45"
                                    new_row.append(datetime.strptime(current_value.replace('.',':'), "%H:%M:%S"))
                                    empty_row = False
                                elif values[col_counter] == 'dateYMD HMS':
                                    # "2012-10-09"
                                    new_row.append(datetime.strptime(current_value.replace('-','/').replace('.',':'), "%Y/%m/%d %H:%M:%S"))
                                    empty_row = False
                                elif values[col_counter] == 'boolean':
                                    # "0"|"1"
                                    new_row.append(bool(ast.literal_eval(current_value.replace(',',''))))
                                    empty_row = False
                                elif values[col_counter] == 'booleanSN':
                                    # "S"|"N"
                                    new_row.append(True if current_value == 'S' else False)
                                    empty_row = False
                                elif values[col_counter] == 'xldate':
                                    new_row.append(xldate_to_datetime(ast.literal_eval(current_value.replace(',',''))))
                                    empty_row = False
                                else:
                                    raise Exception('ERROR: Unmanaged \'{}\' datatype'.format(values[col_counter]))
                                values_format += '%s,'
                                col_counter += 1
                            values_format = values_format[:-1]

                            if not empty_row:
                                cursor.execute("""insert into {}({}) 
                                           values ({})""".format(tablename, db_column_list, values_format),
                                           new_row)
                            if line_counter % 1000 == 0:
                                database.commit()
                            if line_counter % 5000 == 0:
                                print('{} rows loaded..'.format(line_counter))
                        print( 'TOTAL: {} rows loaded ({} rows skipped)'.format(line_counter, lines_skipped))

                        cursor.close()
                        database.commit()
                        if tmp_filename != _file:
                            try:
                                os.remove(tmp_filename)
                            except:
                                pass
                        move_and_rename(_file)
                except Exception, e:
                    print('########## File ERROR ############')
                    print(e)
                    print('{}: {} (col # {})'.format(os.path.basename(_file), line_counter, col_counter))
                    print "Value: *{}* format: {}".format(last_value_processed, last_format_processed)
                    if database and not database.closed:
                        database.rollback()
                        print('Rolled back.')
                    print('##################################')
                    error_count += 1
                finally:
                    if tmp_filename != _file:
                        try:
                            os.remove(tmp_filename)
                        except:
                            pass
                    if database:
                        database.close()
                    if error_count > 0:
                        print 'COMPLETED WITH {} ERRORS: PLEASE CHECK!'.format(error_count)
                        sys.exit(-1)

def sorted(l):
    l.sort()
    return l


def move_and_rename(filename):
    today__strftime = datetime.today().strftime('%Y%m%d_')
    if re.match(r'^\d{8}', os.path.basename(filename)):
        # date in name: move with no name changes
        shutil.move(filename, os.path.join(BAK_FOLDER, os.path.basename(filename)))
    else:
        shutil.move(filename, os.path.join(BAK_FOLDER, today__strftime + os.path.basename(filename)))
    print('########## File %s loaded ############' % os.path.basename(filename))


def robust_decode(file_name):
    f = open(file_name, 'rU')
    content = "\n".join(f.readlines())
    f.close()
    try:
        content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = content.decode('utf-16')
        except UnicodeDecodeError:
            content = content.decode('latin1')
    return StringIO(content.encode('utf-8'))


def csv_from_excel(file_name):
    csv_file_name = os.path.join(os.path.dirname(file_name), '_tmp.csv')

    workbook = xlrd.open_workbook(file_name, encoding_override='cp1252')
    all_worksheets = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(all_worksheets[0])
    try:
        os.remove(csv_file_name)
    except:
        pass
    csv_output_file = open(csv_file_name, 'wb')
    wr = csv.writer(csv_output_file, quoting=csv.QUOTE_ALL)

    for rownum in xrange(worksheet.nrows):
        wr.writerow([unicode(entry).encode("utf-8") for entry in worksheet.row_values(rownum)])
    csv_output_file.close()

    return csv_file_name

def xldate_to_datetime(xldate, datemode=0):
    # datemode: 0 for 1900-based, 1 for 1904-based
    return (datetime(1899, 12, 30) + timedelta(days=xldate + 1462 * datemode))

if __name__ == "__main__": main()
