# -*- coding: utf-8 -*-
import sys
import sqlite3
import traceback

def fill_table(conn,cursor, table_name, data):
	insert_sql = 'INSERT INTO %s VALUES (?,?,?,?,?,?,?,?,?,?,?,?)' % table_name
	cursor.execute(insert_sql, data)
	conn.commit()
	
def fill_table2(conn,cursor, table_name, data):
	print data
	insert_sql = 'INSERT INTO %s VALUES (?,?,?,?)' % table_name
	cursor.execute(insert_sql, data)
	conn.commit()

def main():
	db_path = "fst_no_docs.db"
	conn = sqlite3.connect(db_path)
	conn.text_factory = str  #bugger 8-bit bytestrings
	cursor = conn.cursor()
	
	try:
		#docs = parse_fsdocs("scraped_docs.data")
		data = {'FSDokument':[
		            [('id','1'), #'FFFS 2011:1' ???!? How to handle this?
		             ('arsutgava','2011'),
		             ('lopnummer','1'),
					 ('is_published',0), # Always null
		             ('titel', 'Föreskrifter om ersättningssystem i kreditinstitut, värdepappersbolag och fondbolag med tillstånd för diskretionär portföljförvaltning'),
		             ('sammanfattning', 'Finansinspektionen har beslutat ... utan av FFFS 2011:2'),
		             ('forfattningssamling','1'), # How to use 'EXFS' here ??!?
					 ('beslutsdatum','2011-02-17'), # Use string not datetime
		             ('ikrafttradandedatum','2011-03-01'),
		             ('utkom_fran_tryck','2011-02-24'),	
					 ('omtryck', '0'), # Sqlite uses string '0' or '1', not Python boolean False
					 ('content_md5','') # Always empty (unless we calculate this before loading)			
					]
				],
				'AllmannaRad':[
					[('id','1'), #'FFFS 2011:1' ???!? How to handle this?
		             ('content','/allmannarad/fffs2011.pdf'),
		             ('beslutad_av',''),
					 ('utgivar_id',''),
					]
				],
		        'KonsolideradForeskrift':[
		            ],
		        
				'Bilaga':[],
				'Andringar_fsdokument':[]
				}
		params = []
		for tup in data['FSDokument'][0]:
			params.append(tup[1])
		#fill_table(conn, cursor, "fs_doc_fsdokument",params	)
		params = []
		for tup in data['AllmannaRad'][0]:
			params.append(tup[1])
		fill_table2(conn, cursor, "fs_doc_allmannarad",params	)
	
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		print exc_type, exc_value
		traceback.print_stack()

if __name__ == '__main__':
	main()
		
		