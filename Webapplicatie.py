"""

Title: HTML-Python voor webinterface
Beschrijving: Zie titel
Bronnen: Geen
Auteurs: Alex Staritsky en William Sies
Datum: Donderdag 10 mei 2016 - ?
Versie: 1.0
Updates: Zie Github
(c) Copyright

"""

import mysql.connector
from mod_python import apache

def index(req):
	req.content_type = 'text/html'
	req.write(head())
	req.write(bovenmenu())
	req.write(Questionform())

def BLAST_Resultaat(req, check='1', radiobutton='1'):
	req.content_type = 'text/html'
	req.write(head())
	req.write(bovenmenu())
	req.write("""<h1>Hier komen resultaten</h1>""")

def Sequentie_Informatie(req):
	req.content_type = 'text/html'
	req.write(head())
	req.write(bovenmenu())
	Sequentie_Informatie_Table(req)

def BLAST_Informatie(req):
	req.content_type = 'text/html'
	req.write(head())
	req.write(bovenmenu())
	BLAST_Informatie_Table(req)
	
def head():
	return """<html>
    <head>
    <link rel="stylesheet" "type="text/css" href="http://cytosine.nl/~owe4_bi1e_2/Python/Webinterface.css" >
	<title>BLAST results champignon dataset</title>
    </head>"""

def bovenmenu():
	return """<body>
	<div class="menu">
		<ul>
			<li>
				<a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py">Home</a>
			</li>
		</ul>
		<ul>
			<li>
				<a href="#">Resultaat tabellen</a>
				<ul>
					<li><a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Resultaat">BLAST Resultaat</a></li>
					<li><a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/Sequentie_Informatie">Sequentie Informatie</a></li>
					<li><a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Informatie">BLAST Informatie</a></li>
				</ul>
			</li>
		</ul>
		<ul>
			<li>
				<a href="#">Het project</a>
			</li>
		</ul>
	</div>"""
	
def tablelog(query):
	conn = mysql.connector.connect(host="localhost", user="owe4_bi1e_2", db="owe4_bi1e_2", password='blaat1234')
	cursor = conn.cursor()
	cursor.execute (query)
	row = cursor.fetchall()
	cursor.close()
	conn.close()
	return row

def Questionform():
	orgs = ''
	organisme_eiwit = tablelog("SELECT Organisme_eiwit_info FROM BLAST_resultaat__informatie")
	for row in organisme_eiwit:
		orgs += '<option value={0}> {0}</option>'.format(row[0])
	eggs = ''
	for row in organisme_eiwit:
		eggs += '<option value={0}> {0}</option>'.format(row[0])
	return """<form value='information' action='http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Resultaat' id='filter'>
	<p>Organisme:</p>
	<select id='Organisme' name='Organisme'>
		<option value='0'></option>
		"""+orgs+"""
	</select><br>
	or<br>
	<input type='text' name='Organisme'>
	<p>Eiwit:</p>
	<select id='Eiwit' name='Eiwit'>
		<option value='0'></option>
		"""+eggs+"""
	</select><br>
	or<br>
	<input type='text' name='Eiwit'>
	<p>E-Value:</p>
	<input type='text' name='e_value'>
	<p>Gaps:</p>
	<select>
		<option value='Null'></option>
		<option value='0'>0</option>
		<option value='< 10'>< 10</option>
		<option value='< 25'>< 25</option>
		<option value='< 50'>< 50</option>
		<option value='< 100'>< 100</option>
	</select>
	<input type='submit' name='klik' value='Submit'>
	</form>"""
	
def BLAST_Informatie_Table(req):
	conn = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Resultaat r, Parameters p WHERE r.Parameters_ID = p.Parameters_ID ORDER BY Sequentie_identifier ASC LIMIT 1000")
	results = cursor.fetchall()

	cursor.close()
	conn.close()    

	req.write('<table border=1>')
	req.write('<caption>BLAST informatie</caption>')
	req.write('<tr><th>Sequentie ID</th><th>Type BLAST</th><th>Has Results</th><th>Datum</th><th>Tijd</th><th>Matrix</th><th>Database</th><th>Gap Costs</th><th>Low Complexity</th><th>Mask Lookup Only</th></tr>')
	for row in results:
		req.write('<tr>')
		has_results = str(row[6]).replace('1','Yes').replace('0','No')
		matrix = str(row[9]).replace('None','N/A')
		if row[12] != None:
			gap_costs = 'Existence: '+str(row[12]).split(',')[0]+' Extension: '+str(row[12]).split(',')[1]
		else:
			gap_costs = 'N/A'
		low_complexity = str(row[10]).replace('1','Enabled').replace('0','Disabled')
		mask_lookup_only = str(row[11]).replace('1','Enabled').replace('0','Disabled')
		new_row = [row[3],row[7],has_results,row[1],row[2],matrix,row[8],gap_costs,low_complexity,mask_lookup_only]
		for data in new_row:
			new_data = str(data)
			if len(new_data) > 47:
				req.write('<td>'+new_data[:47]+'...'+'</td>')
			else:
				req.write('<td>'+new_data+'</td>')
		req.write('</tr>')
	req.write('</table>')

def Sequentie_Informatie_Table(req):
	conn = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Sequentie_informatie ORDER BY Sequentie_identifier ASC LIMIT 1000")
	results = cursor.fetchall()

	cursor.close()
	conn.close()    

	req.write('<table border=1>')
	req.write('<caption>Sequentie informatie</caption>')
	req.write('<tr><th>Type</th><th>Sequentie ID</th><th>Sequentie</th><th>Kwaliteitsscore</th></tr>')
	for row in results:
		req.write('<tr>')
		new_row = [row[2],row[3],row[1],row[0]]
		firstrow = True
		for data in new_row:
			new_data = str(data)
			if firstrow == True:
				if new_data == '1':
					new_data = 'Forward'
				else:
					new_data = 'Reverse'
				firstrow = False
			if len(new_data) > 47:
				req.write('<td>'+new_data[:47]+'...'+'</td>')
			else:
				req.write('<td>'+new_data+'</td>')
		req.write('</tr>')
	req.write('</table>')
