# coding: utf8
# python

from get_save import HtmlParser, FromHtmlToCsv
import csv, argparse, os.path

def set_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--directory", type=str, help="Directory of the CSV file (default: csv/)", default="csv/")
	parser.add_argument("-o", "--csv_filename", type=str, help="Name you want to give to the CSV file (default: ing_checkaccount_YYYYMM.csv)", default="ing_checkaccount_YYYYMM.csv")
	parser.add_argument("-i", "--html_file", type=str, help="HTML file you want to import data from (default: html/ing.html)", default="html/ing.html")
	args = parser.parse_args()
	directory = args.directory
	csv_filename = args.csv_filename
	html_file = args.html_file

	check_args(directory, csv_filename, html_file)

	return directory, csv_filename, html_file

def check_args(directory, csv_filename, html_file):
	# Check if directory exists
	if os.path.isdir(directory) != True:
		print(u"[Error]: Directory not found")
		exit(0)
	# Check if CSV filename ends with .csv and don't already exists
	if csv_filename[-4:] != ".csv":
		print(u"[Error]: CSV file name must end with .csv")
		exit(0)
	if os.path.exists(directory + csv_filename):
		print(u"[Error]: CSV file already exists")
		exit(0)
	# Check if html filename ends with .html
	if html_file[-5:] != ".html":
		print(u"[Error]: HTML file name must end with .html")
		exit(0)
	# Check if html file exists
	if os.path.exists(html_file) != True:
		print(u"[Error]: HTML file not found")
		exit(0)

if __name__ == "__main__":
	directory, csv_filename, html_file = set_args()
	html_parser = HtmlParser(html_file)
	html_data, html_encoding = html_parser.parse()
	html_to_csv = FromHtmlToCsv(directory, csv_filename, html_data, html_encoding)
	try:	
		html_to_csv.insert()
		print(u"[Success]: Data successfully imported")
	except Exception:
		print(u"[Error]: Something went wrong during data import")
		raise
