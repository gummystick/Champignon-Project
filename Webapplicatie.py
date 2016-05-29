"""
Title: HTML-Python voor webinterface
Beschrijving: Zie titel
Bronnen: Geen
Auteurs: Alex Staritsky en William Sies
Datum: Donderdag 10 mei 2016 - ?
Versie:	2.0
Updates: Zie Github
@ Copyright
"""

import mysql.connector
from mod_python import apache

def index(req):
	titel = 'BLAST results from Champignondataset'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	req.write(Questionform())

def Sequentie_Informatie(req, sequentie='', sequentieid='', type=''):
	titel = 'Sequentie informatie tabel'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	queryline = queryseqi(sequentie, sequentieid, type)
	Sequentie_Informatie_Table(req, queryline)
	
def BLAST_Resultaten(req, sequentieid='', typeblast='', e_value='', bit_score='', gaps='', ident_perc='', posit_perc='', accessiecode='', org_eiwit='', show_unicode=''):
	titel = 'BLAST Resultaten tabel'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	queryline = queryblastr(sequentieid, typeblast, e_value, bit_score, gaps, ident_perc, posit_perc, accessiecode, org_eiwit, show_unicode)
	BLAST_Resultaten_Table(req, queryline)

def BLAST_Informatie(req, sequentieid='', typeblast='', hasresults='', datum='', masklookup=''):
	titel = 'BLAST Informatie tabel'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	queryline = queryblasti(sequentieid, typeblast, hasresults, datum, masklookup)
	BLAST_Informatie_Table(req, queryline)

def Het_Project(req):
	titel = 'Het project'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	req.write("""
	<h2> Wat is er tevinden?</h2>
	<h2> Wat is het champignon project?</h2>
	<h2> Bronnen:</h2>""")
	
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
					<li><a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Resultaten">BLAST Resultaat</a></li>
					<li><a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/Sequentie_Informatie">Sequentie Informatie</a></li>
					<li><a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Informatie">BLAST Informatie</a></li>
				</ul>
			</li>
		</ul>
		<ul>
			<li>
				<a href="http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface/Het_Project">Het project</a>
			</li>
		</ul>
	</div>"""
def title(titel):
	return """<div class='title'><h1>"""+titel+"""</h1></div>"""	

def tablelog(query):
	conn = mysql.connector.connect(host="localhost", user="owe4_bi1e_2", db="owe4_bi1e_2", password='blaat1234')
	cursor = conn.cursor()
	cursor.execute (query)
	row = cursor.fetchall()
	cursor.close()
	conn.close()
	return row



def Questionform():
	return """<form value='information' action='http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Resultaten' id='filter'>
	<div class='info'>
	<h3>Info</h3>
	<p>Op deze website kunt u resultaten terug vinden van BLAST gemaakt met nucleotide sequenties uit de dataset van het Champignon-project.<br>
	Voor specifieke resultaten kunt u het onderstaande formulier invullen en hierna wordt u door verwezen naar de bijbehorende 'BLAST Resultaten tabel' met ingevulde filteropties.<br>
	Naast een 'BLAST Resultaten tabel' kunt u ook per BLAST de gebruikte parameters en andere informatie vinden in de 'BLAST Informatie tabel'.<br>
	In de 'Sequentie Informatie tabel' kunt u de sequenties terugvinden die gebruikt zijn en de kwaliteitsscore staat hier ook in vermeld.<br>
	Verder kunt u op deze website nog informatie vinden over het project zelf onder het kopje 'Het project'.</p>
	</div>
	<h3>Filter Formulier BLAST resultaten.</h3>
	<h4>Sequentie_ID:</h4>
	<select name='sequentieid' id='sequentieid'>
	<option value=''></option>
	"""+ids()+"""
	</select>
	<h4>Type BLAST:</h4>
	<select name='typeblast' id='typeblast'>
	<option value=''></option>
	<option value='blastn'>blastn</option>
	<option value='blastx'>blastx</option>
	<option value='tblastx'>tblastx</option>
	</select>
	<h4>E-Value:</h4>
	<select name='e_value' id='e_value'>
	<option value=''></option>
	"""+options()+"""
	</select>
	<h4>Bit-Score:</h4>
	<input type='text' name='bit_score' value=''>
	<h4>Gaps:</h4>
	<select name='gaps' id='gaps'>
	<option value=''></option>
	<option value='0'>0</option>
	<option value='5'>< 5</option>
	<option value='10'>< 10</option>
	<option value='15'>< 15</option>
	<option value='25'>< 25</option>
	<option value='100'>< 100</option>
	</select>
	<h4>Identity Percentage:</h4>
	<input type='text' name='ident_perc' value=''>
	<h4>Positive Percentage:</h4>
	<input type='text' name='posit_perc' value=''>
	<h4>Accessiecode:</h4>
	<select name='accessiecode' id='accessiecode'>
	<option value=''></option>
	"""+codes()+"""
	</select>
	<h4>Organisme/Eiwit:</h4> <select name='org_eiwit' id='org_eiwit'>
	<option value=''></option>
	"""+orgs()+"""
	</select><br><br>
	<div class='button'>
	<input type='submit' name='klik' value='Search'>
	</div>
	</form>"""
	
def BLAST_Resultaten_Table(req, queryline):
	conn = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = conn.cursor()

	cursor.execute(queryline)
	results = cursor.fetchall()

	cursor.close()
	conn.close()
	req.write(queryline)
	req.write('<div class="table_options">')
	req.write("""<table><form value='filter' action='http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Resultaten' id='filter'>
	<th align='left'><input type='submit' name='Filter' value='Filter'></th><th>Show Unicode:<input type='checkbox' name='show_unicode' value='1'></table></div>
	<div class="table">
	<table>
	<tr><th>Sequentie ID:<br><select name='sequentieid' id='sequentieid'>
	<option value=''></option>
	"""+ids()+"""
	</select></th>
	<th>Type BLAST:<br><select name='typeblast' id='typeblast'>
	<option value=''></option>
	<option value='blastn'>blastn</option>
	<option value='blastx'>blastx</option>
	<option value='tblastx'>tblastx</option>
	</select></th>
	<th>E-Value:<select name='e_value' id='e_value'>
	<option value=''></option>
	"""+options()+"""
	</select>
	</th>
	<th>Bit-Score:
	<input type='text' name='bit_score' value=''>
	</th>
	<th>Score</th>
	<th>Identities</th>
	<th>Positives</th>
	<th>Gaps:<select name='gaps' id='gaps'>
	<option value=''></option>
	<option value='0'>0</option>
	<option value='5'>< 5</option>
	<option value='10'>< 10</option>
	<option value='15'>< 15</option>
	<option value='25'>< 25</option>
	<option value='100'>< 100</option>
	</select>
	</th>
	<th>Identity Percentage: <input type='text' name='ident_perc' value=''>
	</th>
	<th>Positive Percentage: <input type='text' name='posit_perc' value=''></th>
	<th>Total Aligned</th>
	<th>Frame</th>
	<th>Accessiecode: <select name='accessiecode' id='accessiecode'>
	<option value=''></option>
	"""+codes()+"""</select></th>
	<th>Organisme/Eiwit: <select name='org_eiwit' id='org_eiwit'>
	<option value=''></option>
	"""+orgs()+"""</select></th>
	<th>Alignment</th></tr>""")
	for row in results:
		req.write('<tr>')
		if row[10] == None:
			frame = 'N/A'
		else:
			frame = str(row[10]).replace('(','').replace(')','')
		if row[11] == 'NULL':
			accessiecode = 'Unicode Error'
		else:
			accessiecode = row[11]
		if row[12] == 'NULL':
			eiwit = 'Unicode Error'
		else:
			eiwit = row[12]
		alignment_data = row[13].split('\n')
		alignment = alignment_data[0][:20]+'...\n'+alignment_data[1][:20]+'...\n'+alignment_data[2][:20]+'...\n'
		new_row = [row[0],row[14],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],frame,accessiecode,eiwit,alignment]
		count = -1
		for data in new_row:
			count += 1
			str_data = str(data)
			if count == 14:
				req.write('<td><pre>'+str_data+'</pre></td>')
			else:
				if len(str_data) > 47:
					req.write('<td>'+str_data[:47]+'...'+'</td>')
				else:
					req.write('<td>'+str_data+'</td>')
	req.write('</tr>')
	req.write('</div></table>')
	
def BLAST_Informatie_Table(req, queryline):
	conn = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = conn.cursor()

	cursor.execute(queryline)
	results = cursor.fetchall()

	cursor.close()
	conn.close()
	
	req.write('<div class="table_options">')
	req.write("<table><form value='filter' action='http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/BLAST_Informatie' id='filter'><th align='left'><input type='submit' name='Filter' value='Filter'></th></table></div>")
	req.write('<div class="table">')
	req.write('<table border=1>')
	req.write("""<th>Sequentie ID:<br><select name='sequentieid' id='sequentieid'>
	<option value=''></option>
	"""+ids()+"""
	</select></th>
	<th>Type BLAST:<br><select name='typeblast' id='typeblast'>
	<option value=''></option>
	<option value='blastn'>blastn</option>
	<option value='blastx'>blastx</option>
	<option value='tblastx'>tblastx</option>
	</select></th>
	<th>Has Results:<br><select name='hasresults' id='hasresults'>
	<option value=''></option>
	<option value='1'>Yes</option>
	<option value='0'>No</option>
	</select></th>
	<th>Datum:<br><select name='datum' id='datum'>
	<option value=''></option>
	"""+dates()+"""
	</select>
	</th>
	<th>Tijd</th>
	<th>Matrix</th>
	<th>Database</th>
	<th>Gap Costs</th>
	<th>Low Complexity</th>
	<th>Mask Lookup Only:<br><select name='masklookup' id='masklookup'>
	<option value=''></option>
	<option value='1'>Enabled</option>
	<option value='0'>Disabled</option>
	</select></th>
	</form>""")
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
	req.write('</div>')
	return

def Sequentie_Informatie_Table(req, queryline):
	conn = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = conn.cursor()

	cursor.execute(queryline)
	results = cursor.fetchall()

	cursor.close()
	conn.close()
	
	req.write('<div class="table_options">')
	req.write("<table><form value='filter' action='http://cytosine.nl/~owe4_bi1e_2/Python/HTMLWebinterface.py/Sequentie_Informatie' id='filter'><th	align='left'><input type='submit' name='Filter' value='Filter'></th></table></div>")
	req.write('<div class="table">')
	req.write('<table border=1>')
	req.write("""<th>Type:<br><select name='type' id='type'>
	<option value=''></option>
	<option value='1'>Forward</option>
	<option value='2'>Reverse</option>
	</select>
	</th>
	<th>Sequentie ID:<br><select name='sequentieid' id='sequentieid'>
	<option value=''></option>
	"""+ids()+"""
	</select></th>
	<th>Sequentie:<br><input type='text' name='sequentie'>
	</th>
	<th>Kwaliteitsscore:</th>
	</tr></form>""")
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
	req.write('</div>')
	return

def ids():
	opties = ''
	for id in tablelog("""SELECT Sequentie_identifier FROM Sequentie_informatie GROUP BY Sequentie_identifier""" ):
		opties += '<option value={0}> {0}</option>'.format(id[0])
	return opties

def dates():
	opties = ''
	for date in tablelog("""SELECT Date_of_BLAST FROM Resultaat GROUP BY Date_of_BLAST"""):
		opties += '<option value={0}> {0}</option>'.format(date[0])
	return opties
	
def codes():
	codes = ''
	for code in tablelog("""SELECT Organisme_eiwit_ID FROM BLAST_resultaat__informatie GROUP BY Organisme_eiwit_ID"""):
		codes += '<option value={0}> {0}</option>'.format(code[0])
	return codes
	
def orgs():
#Org_egg deel naam upper/lower?
	orgs = ''
	for row in tablelog("""SELECT `Organisme_eiwit_info` FROM `BLAST_resultaat__informatie` GROUP BY Organisme_eiwit_info"""):
		orgs += '<option value={0}> {0}</option>'.format(row[0])
	return orgs

def options():	
	options = ''
	for i in range(3, 30):
		options += '<option value='+str(float(10)**-i)+'>< *10^-'+str(i)+'</option>'
	return options
	
def queryseqi(sequentie, sequentieid, type):
	query = 'SELECT * FROM Sequentie_informatie WHERE 1'
	if sequentie != '':
		query += " AND Sequentie like '%{0}%'".format(sequentie.upper())
	if sequentieid != '':
		query += " AND Sequentie_identifier = '{0}'".format(sequentieid)
	if type != '':
		query += " AND Type = {0}".format(type)
	query += ' ORDER BY Sequentie_identifier asc LIMIT 1000'
	return query
	
def queryblasti(sequentieid, typeblast, hasresults, datum, masklookup):
    query = 'SELECT * FROM Resultaat r, Parameters p WHERE r.Parameters_ID = p.Parameters_ID'
    if sequentieid != '':
        query += " AND r.Sequentie_identifier = '{0}'".format(sequentieid)
    if typeblast != '':
        query += " AND p.Type_BLAST = '{0}'".format(typeblast)
    if hasresults != '':
        query += " AND r.Has_Result = {0}".format(hasresults)
    if datum != '':
        query += " AND r.Date_of_BLAST = STR_TO_DATE(  '{0}',  '%Y-%m-%d' )".format(datum)
    if masklookup != '':
        query += " AND p.Mask_lookup_only = {0}".format(masklookup)
    query += ' ORDER BY Sequentie_identifier asc LIMIT 1000'
    return query
	
def queryblastr(sequentieid='', typeblast='', e_value='', bit_score='', gaps='', ident_perc='', posit_perc='', accessiecode='', org_eiwit='', show_unicode=''):
    query = """SELECT r.Sequentie_identifier, i.E_value, i.Bit_score, i.Score, i.Identities, i.Positives, i.Gaps, i.Identity_percentage, i.Positive_percentage, i.Total_Aligned, i.Frame, i.Organisme_eiwit_ID, i.Organisme_eiwit_info, i.Alignment, p.Type_BLAST
			  FROM Resultaat r, BLAST_resultaat__informatie i, Parameters p
			  WHERE r.Resultaat_ID = i.Resultaat_ID
			  AND r.Parameters_ID = p.Parameters_ID"""
    if sequentieid != '':
        query += " AND r.Sequentie_identifier = '{0}'".format(sequentieid)
    if typeblast != '':
        query += " AND p.Type_BLAST = '{0}'".format(typeblast)
    if e_value != '':
        query += " AND convert(i.E_value, decimal(30,30)) <= {0}".format(e_value)
    if bit_score != '':
        query += " AND i.Bit_score >= {0}".format(bit_score)
    if gaps != '':
        if gaps == '0':
            query += " AND i.Gaps = 0"
        else:
            query += " AND i.Gaps <= {0}".format(gaps)
    if ident_perc != '':
        query += " AND i.Identity_percentage >= {0}".format(ident_perc)
    if posit_perc != '':
        query += " AND i.Positive_percentage >= {0}".format(posit_perc)
    if accessiecode != '':
        query += " AND i.Organisme_eiwit_ID = '{0}'".format(accessiecode)
    if org_eiwit != '':
        query += " AND i.Organisme_eiwit_info = '{0}'".format(org_eiwit)
    if show_unicode != '1':
		query += " AND i.Organisme_eiwit_ID != 'NULL'"
		query += " AND i.Organisme_eiwit_info != 'NULL'"
    query += ' ORDER BY r.Sequentie_identifier asc LIMIT 1000'
    return query
