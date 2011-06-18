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


def main():
    """Run sample data on empty DB.

    The updated DB displays inserted records when used with FST and
    Django admin. We must verify all necessary related tables are created.
    """

    db_path = "fst_no_docs.db"
    db_connection = sqlite3.connect(db_path)
    db_connection.text_factory = str  # bugger 8-bit bytestrings

    try:
        # Hardcoded data below - replace with data from '/tools/import.py'
        data = {'fs_doc_fsdokument':
                [
                    {'id': '1',  # id is created when loading docs
                     'arsutgava': '2011',
                     'lopnummer': '1',
                     'is_published': '0',  # False (nothing is published yet)
                     'titel': u'Föreskrifter om ersättningssystem i kreditinstitut, värdepappersbolag och fondbolag med tillstånd för diskretionär portföljförvaltning',
                     'sammanfattning': u'Finansinspektionen har beslutat ... utan av FFFS 2011:2',
                     'forfattningssamling_id': '1',  # ID handled by import
                     'beslutsdatum': '2011-02-17',  # Use string not datetime
                     'ikrafttradandedatum': '2011-03-01',
                     'utkom_fran_tryck': '2011-02-24',
                     'omtryck': '0',  # Use '0' or '1' for boolean!
                     'content_md5': ''  # Should be calculated somewhere...
                     },
                    {'id': '2',  # id is created when loading docs
                     'arsutgava': '2011',
                     'lopnummer': '2',
                     'is_published': '0',  # False (nothing is published yet)
                     'titel': u'Föreskrifter om ändring i föreskrifter 2009:1 om administration hos statliga myndigheter',
                     'sammanfattning': u'Finansinspektionen har beslutat ... utan av FFFS 2011:2',
                     'forfattningssamling_id': '1',  # ID handled by import
                     'beslutsdatum': '2011-04-01',  # Use string not datetime
                     'ikrafttradandedatum': '2011-05-01',
                     'utkom_fran_tryck': '2011-04-20',
                     'omtryck': '0',  # Use '0' or '1' for boolean!
                     'content_md5': ''  # Should be calculated somewhere...
                     }
                    ],
                'fs_doc_allmannarad':
                [
                    {'fsdokument_ptr_id': '2',  # id is created when loading docs
                     'content': u'/allmannarad/fs1102.pdf',
                     'beslutad_av_id': '',  # Always empty (we don't handle this yet)
                     'utgivare_id': ''  # Always empty (we don't handle this yet)
                     }
                    ],
                'fs_doc_myndighetsforeskrift':
                [
                    {'fsdokument_ptr_id': '1',  # id is created when loading docs
                     'content': u'/foreskrift/fs1101.pdf',
                     'beslutad_av_id': '',  # Always empty (we don't handle this yet)
                     'utgivare_id': ''  # Always empty (we don't handle this yet)
                     }
                    ],
                'fs_doc_Myndighet':
                [
                    {'id': '1',  # Default. Sometimes there is only one.
                     'namn': u'Finansinspektionen',
                     }
                    ],
                'fs_doc_Forfattningssamling':
                [
                    {'id': '1',  # Default. Sometimes there is only one.
                     'titel': u'Finansinspektionens författningssamling',
                     'kortnamn': u'FFFS',
                     'slug': u'fffs'
                     }
                ]
                }

        fill_table('fs_doc_fsdokument', data, db_connection)
        fill_table('fs_doc_allmannarad', data, db_connection)
        fill_table('fs_doc_myndighetsforeskrift', data, db_connection)
        fill_table('fs_doc_Myndighet', data, db_connection)
        fill_table('fs_doc_Forfattningssamling', data, db_connection)

    except:
        exc_type, exc_value = sys.exc_info()
        print exc_type, exc_value
        traceback.print_stack()

if __name__ == '__main__':
    main()