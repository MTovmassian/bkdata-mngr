# coding: utf8
# python3

import os, csv, re, argparse

def format_date(date_extracted):
	months = {"janv.":"01", "févr.":"02", "mars":"03", "avr.":"04", "mai":"05", "juin":"06", 
		"juil.":"07", "août":"08", "sept.":"09", "oct.":"10", "nov.":"11", "déc.":"12"}
	day, month, year = date_extracted.split()
	if month in months:
		month = months[month]
	else:
		print("/!\ Unsuccessful match whith the RBC literal month format")
		exit(0)
	date = "{0}-{1}-{2}".format(year, month, day)
	return date

def format_label(label_extracted):
	label = label_extracted
	nline_pattern = r"\n"
	apostr_pattern = r"\'"
	if re.search(nline_pattern, label) != None:
		label = label.replace("\n", "")
	if re.search(apostr_pattern, label) != None:
		label = label.replace("\'", " ")
	return label

def format_amount(amount_extracted):
	amount = amount_extracted
	dollar_pattern = r"\s\$"
	comma_pattern = r"\,"
	space_pattern = r"\s"
	if re.search(dollar_pattern, amount) != None:
		amount = re.sub(dollar_pattern, "", amount)
	if re.search(comma_pattern, amount) !=None:
		amount = re.sub(comma_pattern, ".", amount)
	if re.search(space_pattern, amount) != None:
		amount = re.sub(space_pattern, "", amount)
	return amount

def insert(date, label, amount, void):
	with open(directory + output_csv_file, 'a') as csv_file:
		fieldnames = ['date', 'label', 'void', 'amount']
		data_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		data_writer.writerow({'date':date, 'label':label, 'void':void, 'amount':amount})

def check_args(directory, input_csv_file, output_csv_file):
	# Check if directory exists
	if os.path.isdir(directory) != True:
		print("[Error]: Directory not found")
		exit(0)
	# Check if input_csv_file ends with .csv and exists
	if input_csv_file[-4:] != ".csv":
		print("[Error]: Input CSV file must end with .csv")
		exit(0)
	if os.path.exists(directory + input_csv_file) != True:
		print("[Error]: Input CSV file not found")
		exit(0)
	# Check if output_csv_file ends with .csv and if already exists
	if output_csv_file[-4:] != ".csv":
		print("[Error]: Output CSV file must end with .csv")
		exit(0)
	if os.path.exists(directory + output_csv_file) == True:
		print("[Error]: Output CSV file already exists")
		exit(0)

def name_output_file(directory, input_csv_file):
	with open(directory + input_csv_file, 'r') as csv_file:
		data_reader = csv.reader(csv_file, delimiter=',')
		date = format_date(list(data_reader)[0][0])
		year, month, day = date.split('-')
		output_csv_file = "rbc_checkaccount_{0}{1}.csv".format(year, month)
		return output_csv_file

def set_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--directory", type=str, 
		help="Directory of the CSV files (default: csv/)", default="csv/")
	parser.add_argument("-i", "--input_csv_file", type=str, 
		help="CSV file you want to format data (default: csv/raw_bank_data.csv)", 
		default="raw_bank_data.csv")
	parser.add_argument("-o", "--output_csv_file", type=str, 
		help="CSV file where you want to save formated data (default: rbc_checkaccount_[YYYYMM].csv)", 
		default="default.csv")
	args = parser.parse_args()
	directory = args.directory
	input_csv_file = args.input_csv_file
	output_csv_file = args.output_csv_file

	check_args(directory, input_csv_file, output_csv_file)
	if output_csv_file == "default.csv":
		output_csv_file = name_output_file(directory, input_csv_file)

	return directory, input_csv_file, output_csv_file

def extract_data_rbc(row):
	date_extracted = row[0] 
	label_extracted = row[1]
	if row[2]:
		amount_extracted = row[2]
	else:
		amount_extracted = row[3]
	return date_extracted, label_extracted, amount_extracted

def format_raw_data():
	with open(directory + input_csv_file, 'r') as csv_file:
		data_reader = csv.reader(csv_file, delimiter=',')
		for row in data_reader:
			date_extracted, label_extracted, amount_extracted = extract_data_rbc(row)
			date = format_date(date_extracted)
			label = format_label(label_extracted)
			amount = format_amount(amount_extracted)
			void = ""
			insert(date, label, amount, void)

if __name__ == "__main__":
	directory, input_csv_file, output_csv_file = set_args()
	format_raw_data()