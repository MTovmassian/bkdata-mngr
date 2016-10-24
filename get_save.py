# coding: utf8
# python

from bs4 import BeautifulSoup
import sqlite3, argparse, os.path, re, csv

class HtmlParser(object):
	"""
	Provides methods to parse ING html webpage and retrieve elements containing bank data
	"""
	def __init__(self, html_file):
		self.html_file = html_file

	def parse(self):
		# Parse and retrieve html elements containing bank data
		soup = BeautifulSoup(open(self.html_file), "html.parser")
		html_encoding = soup.original_encoding
		# Reach bank data general container
		html_data_container = soup.find("div", attrs={"class":"ccinc_content"})
		# Get all table elements into general html container
		html_data = html_data_container.find_all("table")
		# Sort table elements in descending order
		html_data.reverse()

		return html_data, html_encoding


class ExtractFromHTML(object):
	"""
	Provides methods to extract bank data from an html element
	"""
	def __init__(self, html_data_elmt, html_encoding):
		self.html_data_elmt = html_data_elmt
		self.html_encoding = html_encoding

	def extract_date(self):
		# Extract the date data from its html element
		date_extracted = self.html_data_elmt.find("td", attrs={"class":"date"}).text
		# Split date data in 3 parts (year, month, day)
		date_extracted = date_extracted.split(" ")
		year = date_extracted[2]
		month = date_extracted[1]
		# ING literal month format and their digital correspondence
		months = {u"janv.":u"01", u"févr.":u"02", u"mars":u"03", u"avr.":u"04", u"mai":u"05", u"juin":u"06", 
		u"juil.":u"07", u"août":u"08", u"sept.":u"09", u"oct.":u"10", u"nov.":u"11", u"déc.":u"12"}
		# Compare ING literal month format and recover its digital format
		match_status = False
		for key in months.keys():
			if month.encode(self.html_encoding) == key.encode("utf8"):
				month = months[key]
				match_status = True
		if match_status == False:
			print(u"/!\ Unsuccessful match whith the ING literal month format")
			exit(0)
		day = date_extracted[0]
		date = year + "-" + month + "-" + day

		return date.encode('utf8')

	def extract_label(self):
		# Extract label data from its html element
		label = self.html_data_elmt.find("td", attrs={"class":"lbl"}).text.encode("utf8")
		# Check label data to delete apostrophes if there are
		if re.search(r"\'", label) != None:
			label = label.replace("\'", "")
		
		#return label.encode('utf8')
		return label

	def extract_amount(self):
		# Extract amount data from its html element
		amount_extracted = self.html_data_elmt.find("td", attrs={"class":"amount"}).text.encode("utf8")
		# Check amount data to delete non-breaking spaces if there are
		if re.search(r"\xc2\xa0", amount_extracted) != None:
			amount_extracted = amount_extracted.replace("\xc2\xa0", "")
		# Split amount data in 2 parts (integer, decimal) to avoid encoding issues with euro sign
		amount_extracted = amount_extracted.split(",")
		amount_int = amount_extracted[0]
		amount_dec = amount_extracted[1][:2]
		amount = amount_int + "." + amount_dec
		
		return amount.encode('utf8')

class FromHtmlToCsv(object):
	"""
	Provides methods to iterate html extraction and data insertion in a csv file 
	"""
	def __init__(self, directory, csv_filename, html_data, html_encoding):
		self.directory = directory
		self.csv_filename = csv_filename
		self.html_data = html_data
		self.html_encoding = html_encoding

	def assign_filename(self):
		# Assign filename to output csv file
		# When filename not provided it retrieves date in html data and make a defautl filename with it 
		if self.csv_filename == "ing_checkaccount_YYYYMM.csv":
			extract_from_html =  ExtractFromHTML(self.html_data[0], self.html_encoding)
			date = extract_from_html.extract_date()
			month = date[5:7]
			year = date[:4]
			self.csv_filename = "ing_checkaccount_" + year + month + ".csv"

		csv_filepath = self.directory + self.csv_filename

		return csv_filepath

	def insert(self):
		# For each html element containing bank data it extracts date, label, and amount values
		csv_filepath = self.assign_filename()
		for index, value in enumerate(self.html_data):
			extract_from_html =  ExtractFromHTML(self.html_data[index], self.html_encoding)
			date = extract_from_html.extract_date()
			label = extract_from_html.extract_label()
			amount = extract_from_html.extract_amount()
			# Writes values in csv file
			with open(csv_filepath, "a") as csvfile:
				fieldnames = ['date', 'label', 'type', 'amount']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writerow({'date':date, 'label':label, 'type':"",'amount':amount})

class FromHtmlToSqlite(object):
	"""
	Provides methods to iterate html extraction and data insertion in a SQLite db 
	"""
	def __init__(self, database_file, table_tmp, table_dest, html_data, html_encoding):
		self.database_file = database_file
		self.table_tmp = table_tmp
		self.table_dest = table_dest
		self.html_data = html_data
		self.html_encoding = html_encoding

	def insert(self):
		# Open connection with database
		conn = sqlite3.connect(self.database_file)
		# Clear temporary table
		conn.execute("DELETE FROM {0}".format(self.table_tmp))
		# For each html element containing bank data it extracts date, label, and amount values
		# Set SQL query with values
		# Run SQL query and insert new values in temporary table
		for index, value in enumerate(self.html_data):
			extract_from_html =  ExtractFromHTML(self.html_data[index], self.html_encoding)
			date = extract_from_html.extract_date()
			label = extract_from_html.extract_label()
			amount = extract_from_html.extract_amount()
			sql_query = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', {4});".format(self.table_tmp, date, label, "", amount)
			conn.execute(sql_query)
		# Copy data from temporary table to structured table with primary key
		conn.execute("INSERT INTO {0}(trsc_date, trsc_label, trsc_type, trsc_amount) SELECT * FROM {1};".format(self.table_dest, self.table_tmp))
		# Commit changes into the database
		conn.commit()
		# Close the connection with the database
		conn.close()

class FromCsvToSqlite(object):
	"""
	Provides methods to iterate csv extraction and data insertion in a SQLite db 
	"""
	def __init__(self, database_file, table_tmp, table_dest, csv_file):
		self.database_file = database_file
		self.table_tmp = table_tmp
		self.table_dest = table_dest
		self.csv_file = csv_file

	def insert(self):
		# Open connection with database
		conn = sqlite3.connect(self.database_file)
		# Clear temporary table
		conn.execute("DELETE FROM {0}".format(self.table_tmp))
		# Read and insert data in temporary table
		with open(self.csv_file, 'r') as csv_file:
			data_reader = csv.reader(csv_file, delimiter = ',')
			for row in data_reader:
				sql_query = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', {4});".format(self.table_tmp, row[0], row[1], row[2], row[3])
				conn.execute(sql_query)
		# Copy data from temporary table to structured table with primary key
		conn.execute("INSERT INTO {0}(trsc_date, trsc_label, trsc_type, trsc_amount) SELECT * FROM {1};".format(self.table_dest, self.table_tmp))
		# Commit changes into the database
		conn.commit()
		# Close the connection with the database
		conn.close()
