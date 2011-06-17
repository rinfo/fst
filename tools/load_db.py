# -*- coding: utf-8 -*-
import sys
import sqlite3
import traceback

def questionsmarks(count):
	if count == 1:
		return "(?)"
	else:
		return "(?," + (count -2) * "?," + "?)"
	
def fill_record(conn,cursor, table_name, fieldnames, values):
	insert_sql1 = "INSERT INTO %s VALUES "  % table_name
	insert_sql2 = questionsmarks(len(fieldnames))
	sql = insert_sql1 + insert_sql2
	cursor.execute(sql, values)
	conn.commit()

def extract_fieldnames(doc):
	fieldnames = []
	for tup in doc:
		fieldnames.append(tup[0])
	return fieldnames
	
def extract_values(doc):
	values = []
	for tup in doc:
		values.append(tup[1])
	return values

def main():
	db_path = "fst_no_docs.db"
	conn = sqlite3.connect(db_path)
	conn.text_factory = str  #bugger 8-bit bytestrings
	cursor = conn.cursor()
	
	try:
		#docs = parse_fsdocs("scraped_docs.data")
		data = {'FSDokument':[
		            [('id','1'), ##'FFFS 2011:1' Created by import
		             ('arsutgava', '2011'),
		             ('lopnummer', '1'),
					 ('is_published', '0'), # Always null (nothing is published)
		             ('titel', 'Föreskrifter om ersättningssystem i kreditinstitut, värdepappersbolag och fondbolag med tillstånd för diskretionär portföljförvaltning'),
		             ('sammanfattning', 'Finansinspektionen har beslutat ... utan av FFFS 2011:2'),
		             ('forfattningssamling', '1'), # ID handled by import 
					 ('beslutsdatum', '2011-02-17'), # Use string not datetime
		             ('ikrafttradandedatum', '2011-03-01'),
		             ('utkom_fran_tryck', '2011-02-24'),
					 ('omtryck', '0'), # Sqlite uses string '0' or '1', not Python boolean False
					 ('content_md5', '') # Always empty (unless we calculate this before loading)
					]
				],
				'AllmannaRad':[
					[('fsdokument_ptr_id', '1'), #'FFFS 2011:1' Created by import
		             ('content', '/allmannarad/fffs2011.pdf'),
		             ('beslutad_av', ''), 
					 ('utgivar_id', ''),
					]
				]
		}
		
		for doc in data['FSDokument']:	
			fieldnames = extract_fieldnames(doc)
			values = extract_values(doc)					
			fill_record(conn, cursor, "fs_doc_fsdokument",fieldnames, values)
		
		for doc in data['AllmannaRad']:	
			fieldnames = extract_fieldnames(doc)
			print fieldnames
			values = extract_values(doc)
			print values					
			fill_record(conn, cursor, "fs_doc_allmannarad",fieldnames, values)
		
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		print exc_type, exc_value
		traceback.print_stack()

if __name__ == '__main__':
	main()
		
		