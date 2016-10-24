# coding: utf8
# python

from get_save import HtmlParser, FromHtmlToSqlite
import sqlite3, argparse, os.path

def set_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--db_file", type=str, help="SQLite file (default: db/bank.db)", default="db/bank.db")
	parser.add_argument("-o", "--table_dest", type=str, help="Table you want to update (default: ing_checkaccount)", default="ing_checkaccount")
	parser.add_argument("-i", "--html_file", type=str, help="HTML file you want to import data from (default: html/ing.html)", default="html/ing.html")
	args = parser.parse_args()
	database_file = args.db_file
	table_dest = args.table_dest
	html_file = args.html_file

	check_args(database_file, table_dest, html_file)

	return database_file, table_dest, html_file

def check_args(database_file, table_dest, html_file):
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
	# Check html file type
	if html_file[-5:] != ".html":
		print(u"[Error]: HTML file name must end with .html")
		exit(0)
	# Check if html file exists
	if os.path.exists(html_file) != True:
		print(u"[Error]: HTML file not found")
		exit(0)


if __name__ == "__main__":
	database_file, table_dest, html_file = set_args()
	html_parser = HtmlParser(html_file)
	html_data, html_encoding = html_parser.parse()
	table_tmp = "bankdata_import"
	html_to_sqlite = FromHtmlToSqlite(database_file, table_tmp, table_dest, html_data, html_encoding)
	try:	
		html_to_sqlite.insert()
		print(u"[Success]: Data successfully imported")
	except Exception:
		print(u"[Error]: Something went wrong during data import")
		raise
