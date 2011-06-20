# -*- coding: utf-8 -*-
""" Load custom Python data structure based on dictionaries into Sqlite

    Use '/tools/import.py' to get data.
    Currently contains hardcoded sample data for testing.
"""

import sys
import sqlite3
import traceback


def get_insert_string(row):
    """ Build SQL string for fieldnames and values.

    Parameter 'row' is a dictionary, so we must keep key/value combinations
    together when constructing the string.
    """
    fields = "("
    values = " VALUES("
    for key, val in row.items():
        fields = fields + key + ", "
        values = values + "'" + val + "'" + ", "
    fields = fields[:-2] + ")"
    values = values[:-2] + ")"
    return fields + values


def fill_table(table_name, data, db_connection):
    """Insert records in SQlite using a list of dictionaries """
    for row in data[table_name]:
        fill_record(table_name, row, db_connection)


def fill_record(table_name, row, db_connection):
    """Insert record in SQlite using a Python dictionary """
    cursor = db_connection.cursor()
    insert_statement = "INSERT INTO %s " % table_name
    insert_data = get_insert_string(row)
    sql = insert_statement + insert_data
    print sql
    cursor.execute(sql)
    db_connection.commit()


def main(indatafile,db_path):
    """Run sample data on empty DB.

    The updated DB displays inserted records when used with FST and
    Django admin. We must verify all necessary related tables are created.
    """

    # db_path = "fst_no_docs.db"
    print "copying fst_no_docs.db to %s" % db_path
    import shutil
    shutil.copy2("fst_no_docs.db", db_path)
    db_connection = sqlite3.connect(db_path)
    db_connection.text_factory = str  # bugger 8-bit bytestrings

    try:
        data = eval(open(indatafile).read())
        print "loaded indata, %s top-level keys" % len(data)

        # With all ID:s in place, we can fill the table in any order
        for table in data.keys():
            fill_table(table,data,db_connection)
        
        #fill_table('fs_doc_fsdokument', data, db_connection)
        #fill_table('fs_doc_allmannarad', data, db_connection)
        #fill_table('fs_doc_myndighetsforeskrift', data, db_connection)
        #fill_table('fs_doc_Myndighet', data, db_connection)
        #fill_table('fs_doc_Forfattningssamling', data, db_connection)

    except:
        #exc_type, exc_value, ex_tb = sys.exc_info()
        #print exc_type, exc_value
        #traceback.print_stack()
        raise

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: %s <indatafile> <dbpath>")
    else:
        indata = sys.argv[1]
        sqllite_file = sys.argv[2]
        main(indata, sqllite_file)
