# -*- coding: utf-8 -*-
import sys
import sqlite3
import traceback

def get_insert_string(row):
	fields = "("
	values = " VALUES("
	
	for key, val in row.items():
		fields = fields + key + ", "
		values = values + "'" + val + "'" + ", "
	
	fields = fields[:-2] + ")"
	values = values[:-2] + ")"
	return fields + values

def fill_table(table_name, data, db_connection):
	for row in data[table_name]:
		fill_record(table_name, row, db_connection)

def fill_record(table_name, row, db_connection):
	cursor = db_connection.cursor()
	insert_statement = "INSERT INTO %s "  % table_name
	insert_data = get_insert_string(row)
	sql = insert_statement + insert_data
	print sql
	cursor.execute(sql)
	db_connection.commit()

def main():
	
	db_path = "fst_no_docs.db"
	db_connection = sqlite3.connect(db_path)
	db_connection.text_factory = str  #bugger 8-bit bytestrings
	
	try:
		# Hardcoded sample data below - replace with data from '/tools/import.py'
		data = {'fs_doc_fsdokument':
				[
					{'id': '1', # id for 'FFFS 2011:1' created when loading docs
		            'arsutgava': '2011',
		             'lopnummer': '1',
					 'is_published': '0', # False (initally nothing is published)
		             'titel': u'Föreskrifter om ersättningssystem i kreditinstitut, värdepappersbolag och fondbolag med tillstånd för diskretionär portföljförvaltning',
		             'sammanfattning': u'Finansinspektionen har beslutat ... utan av FFFS 2011:2',
		             'forfattningssamling_id': '1', # ID handled by import
					 'beslutsdatum': '2011-02-17', # Use string not datetime
		             'ikrafttradandedatum': '2011-03-01',
		             'utkom_fran_tryck': '2011-02-24',
					  'omtryck': '0', # Sqlite uses string '0' or '1': not Python boolean False
					  'content_md5': '' # Must be calculated somewhere
					}
				],
				'fs_doc_allmannarad':
				[
					{'fsdokument_ptr_id': '1', # id for 'FFFS 2011:1' created when loading docs
		             'content': u'/allmannarad/fffs2011.pdf',
		             'beslutad_av_id': '',  # Always empty (we don't handle this yet)
					 'utgivare_id': ''  # Always empty (we don't handle this yet)
					}
				],
				'fs_doc_Myndighet':
				[
					{'id': '1', # Default. Sometimes there is only one.
		             'namn': u'Finansinspektionen',
					}
				],
				'fs_doc_Forfattningssamling':
				[
					{'id': '1', # Default. Sometimes there is only one.
		             'titel': u'Finansinspektionens författningssamling',
		             'kortnamn': u'FFFS',
					'slug': u'fffs'
					}
				]
		}
		
		fill_table('fs_doc_fsdokument', data, db_connection)
		fill_table('fs_doc_allmannarad', data, db_connection)
		fill_table('fs_doc_Myndighet', data, db_connection)
		fill_table('fs_doc_Forfattningssamling', data, db_connection)
	
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		print exc_type, exc_value
		traceback.print_stack()

if __name__ == '__main__':
	main()
		
		