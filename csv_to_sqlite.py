# coding: utf8
# python

from get_save import HtmlParser, FromCsvToSqlite
import sqlite3, csv, argparse, os.path

def set_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--db_file", type=str, help="SQLite file (default: db/bank.db)", default="db/bank.db")
	parser.add_argument("-o", "--table_dest", type=str, help="Table you want to update (default: ing_checkaccount)", default="ing_checkaccount")
	parser.add_argument("-i", "--csv_file", type=str, help="CSV file you want to import data from")
	args = parser.parse_args()
	database_file = args.db_file
	table_dest = args.table_dest
	csv_file = args.csv_file

	check_args(database_file, table_dest, csv_file)

	return database_file, table_dest, csv_file

def check_args(database_file, table_dest, csv_file):
	# Check if SQLite file exists
	if os.path.exists(database_file) != True:
		print(u"[Error]: SQLite file not found")
		exit(0)
	# Check if table exists
	try:
		conn = sqlite3.connect(database_file)
		conn.execute("SELECT * FROM {0}".format(table_dest))
		conn.close()
	except:
		print(u"[Error]: Table not found")
		exit(0)
	# Check csv file type
	if csv_file[-4:] != ".csv":
		print(u"[Error]: CSV file name must end with .csv")
		exit(0)
	# Check if csv file exists
	if os.path.exists(csv_file) != True:
		print(u"[Error]: CSV file not found")
		exit(0)

if __name__ == "__main__":
	database_file, table_dest, csv_file = set_args()
	table_tmp = "bankdata_import"
	csv_to_sqlite = FromCsvToSqlite(database_file, table_tmp, table_dest, csv_file)
	try:	
		csv_to_sqlite.insert()
		print(u"[Success]: Data successfully imported")
	except Exception:
		print(u"[Error]: Something went wrong during data import")
		raise
