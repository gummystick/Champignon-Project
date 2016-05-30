"""
Title: HTML-Python voor webinterface
Beschrijving: Zie titel
Bronnen: http://www.w3schools.com/
Auteurs: Alex Staritsky en William Sies
Datum: Donderdag 10 mei 2016 - ?
Versie:	2.0
Updates: Zie Github
@ Copyright
"""
#importeert de library's voor mysql en apache.
import mysql.connector
from mod_python import apache
#De index functie is de homepage van de webapplicatie.
#Hierin worden als standaard de head, title en bovenmenu functies opgeroepen voor het standaard uiterlijk.
#Als laatst word de questionform functie aangeroepen waarin de filters ingesteld kunnen worden voor de blast resultaten pagina.
def index(req):
	titel = 'BLAST results from Champignondataset'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	req.write(Questionform())

#Op deze pagina is de tabel met alle sequentie informatie te zien.
#Deze pagina heeft weer de vaste functies voor de head, titel en bovenmenu.
#De tabel wordt gecreerd door een query generator functie en de sequentie_informatie_tabel.

def Sequentie_Informatie(req, sequentie='', sequentieid='', type=''):
	titel = 'Sequentie informatie tabel'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	queryline = queryseqi(sequentie, sequentieid, type)
	Sequentie_Informatie_Table(req, queryline)

#Deze pagina bevat de tabel met alle BLAST resultaten.
#Net als de sequentie_informatie pagina worden de vaste functie gebruikt.
#De tabel wordt ook met een query generator en de BLAST_Resultaten_Table gemaakt.
def BLAST_Resultaten(req, sequentieid='', typeblast='', e_value='', bit_score='', gaps='', ident_perc='', posit_perc='', accessiecode='', org_eiwit='', show_unicode=''):
	titel = 'BLAST Resultaten tabel'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	queryline = queryblastr(sequentieid, typeblast, e_value, bit_score, gaps, ident_perc, posit_perc, accessiecode, org_eiwit, show_unicode)
	BLAST_Resultaten_Table(req, queryline)

#De opbouw van deze pagina is gelijk aan de BLAST_resultaten alleen bevat de tabel andere informatie.
def BLAST_Informatie(req, sequentieid='', typeblast='', hasresults='', datum='', masklookup=''):
	titel = 'BLAST Informatie tabel'
	req.content_type = 'text/html'
	req.write(head())
	req.write(title(titel))
	req.write(bovenmenu())
	queryline = queryblasti(sequentieid, typeblast, hasresults, datum, masklookup)
	BLAST_Informatie_Table(req, queryline)
#Dit is de laatste pagina die gecreerd wordt.
#Het bevat de standaard head, titel en bovenmenu functies en verder wordt er informatie gegeven over het project.
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
#Deze functie maakt de standaard verbinding met de stylessheet. De functie wordt apart in elke functie opgeroepen als deze nodig is.	
def head():
	return """<html>
    <head>
    <link rel="stylesheet" "type="text/css" href="http://cytosine.nl/~owe4_bi1e_2/Python/Webinterface.css" >
	<title>BLAST results champignon dataset</title>
    </head>"""

#Deze functie genereerd de bovenmenu.
#Deze kan op elke pagina apart aangeroepen worden. Het bovenmenu bevat een dropdownmenu met de links naar elke pagina.
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
#Deze functie returnt per pagina een aparte titel. De naam wordt in de pagina functie apart aangegeven.
def title(titel):
	return """<div class='title'><h1>"""+titel+"""</h1></div>"""	
#Deze functie bevat de inloggegevens voor de database en bevat de methode om de informatie uit de database op te halen.
#De query die uitgevoerd wordt is voor elke functie apart gegenereerd of aangegeven.
def tablelog(query):
	conn = mysql.connector.connect(host="localhost", user="owe4_bi1e_2", db="owe4_bi1e_2", password='blaat1234')
	cursor = conn.cursor()
	cursor.execute (query)
	row = cursor.fetchall()
	cursor.close()
	conn.close()
	return row

#Deze functie genereerd het filterformulier voor de blast resultaten pagina.
#Per filter die word ingevuld veranderd de query die gestuurd word naar de database.
#Er kan gefilterd worden op sequentie_id hierbij wordt elk sequentie id in een andere functie opgehaald 
#en op de juiste manier gereturnt zodat de alle sequentie id's geselecteerd kunnen worden.
#Ook kan er op type blast gefilterd worden dit zijn er maar drie.
#De e-value filter wordt ook gegenereerd met een aparte functie die alle opties returnt.
#De bit score wordt gefilterd op vast gestelde hoeveelheden dus alles boven een bepaalde waarde.
#Identity_percentage wordt gefilterd op alles boven een specifiek opgegeven waarde.
#Er kan ook een enkele accessiecode geselecteerd worden die in een aparte functie opgehaald worden.
#Als laatste kan er een specifiek organisme/eiwit geselecteerd worden die ook in een aparte functie opgehaald en gereturnt worden.

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
	<div class='formset'>
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
	<option value='5'>5 ></option>
	<option value='10'>10 ></option>
	<option value='15'>15 ></option>
	<option value='25'>25 ></option>
	<option value='100'>100 ></option>
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
	<input type='submit' name='klik' value='Search'>
	</div>
	</form>"""
#De blast_resultaten_table functie returnt een volledige tabel naar de pagina blast resultaten.
#Hiervoor wordt eerst een query opgegeven die gegenereerd is aan de hand van filter instellingen.	
#Er wordt geconnecteerd aan de database en de gegevens worden opgehaald.
#Hierna wordt de tabel gemaakt en wordt voor bepaalde rijen filters gemaakt zodat de query aangepast kan worden.
#Gefilterd kan worden op:
#- Sequentie ID: Een specifiek sequetie id kan geselecteerd worden voor generatie: zie 'ids' functie.
#- Type BLAST: blastn, blastx of tblastx.
#- E-value: Er kunnen verschillende opties geselecteerd worden waarbij de resultaten kleiner dan de opgegeven waar weergeven worden,
#zie 'options' functie.
#- Bitscore: Alleen resultaten groter dan de input van de gebruiker worden weergeven.
#- Gaps: Alles kleiner dan een bepaalde invoer. De opties waaruit gekozen kan worden zijn aangegeven.
#- Indentity percentage/ Positive percentage: Alles groter dan de input van de gebruiker wordt in de tabel weergeven.
#- Accessiecode: Een specifieke accessiecode kan geselecteerd worden zie functie codes.
#- Organisme/Eiwit: Een specifiek organisme/eiwit kan geselecteerd worden zie functie 'orgs'.
#De tabel word gegenereerd in een for loop. 
#Hierin wordt elke rij gegenereerd en in een tweede for loop wordt de tabel data in elke rij toegevoegd.
def BLAST_Resultaten_Table(req, queryline):
	conn = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = conn.cursor()

	cursor.execute(queryline)
	results = cursor.fetchall()

	cursor.close()
	conn.close()
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
#De blast informatie tabel returnt een tabel met alle blast informatie. 
#Deze wordt net als bij de blast resultaten tabel gegenereerd door te connecteren aan de database,
#waarbij een query uitgevoerd word die gegenereerd is aan de hand van de filter behorende bij deze tabel.
#De data uit de query wordt verwerkt in een geneste for loop. de eerste for loop creert de rijen de tweede zorgt voor de data in de rijen.
#De filters voor deze tabel zijn:
#- Sequentie ID: Een specifiek sequetie id kan geselecteerd worden voor generatie: zie 'ids' functie.
#- Type BLAST: blastn, blastx of tblastx.
#- Has Results: Yes/No. Laat zien of een blast resultaat heeft.
#- Datum: De opties worden gegenereerd in de 'dates' functie. Alle resultaten op een specifieke dag weergeven.
#- Mask lookup only: Enabled/Disabled. Laat zien of deze parameter bij de blast ingesteld is.
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
#De sequentie informatie tabel wordt ook gegenereerd door een query afhankelijk van filters en een for loop die de tabel genereerd.
#De filters voor deze tabel zijn:
#- Type: Forward/Revers. Laat alleen resultaten van de geselecteerde optie zien.
#- Sequentie ID: Een specifiek sequetie id kan geselecteerd worden voor generatie: zie 'ids' functie.
#- Sequentie: Een specifiek deel uit de sequentie kan ingevoerd worden waarop gefilterd wordt.
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
#De functie ids returnt de sequentie identifiers.
#De functie dates returnt de dates waarop een blast is uitgevoerd.
#De functie codes returnt alle accessiecodes.
#Bij alle functies word elke optie wordt in een html option tag gezet zodat deze in de dropdownmenu als keuze naarvoren komt. 
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
#De orgs functie haalt alle organisme/eiwit namen op en zorgt ervoor dat ze een maximale lengte van 60 tekens hebben.
#Elke optie wordt in een option tag gereturnt voor het dropdownmenu.	
def orgs():
	orgs = ''
	for row in tablelog("""SELECT `Organisme_eiwit_info` FROM `BLAST_resultaat__informatie` GROUP BY Organisme_eiwit_info"""):
		if len(row[0]) > 60:
			orgs += '<option value={0}> {0}</option>'.format(row[0][:60]+'.....')
		else:
			orgs += '<option value={0}> {0}</option>'.format(row[0])
		
	return orgs
#De options functie zorgt ervoor dat er e-value opties worden aangemaakt voor elke stap van honderd kleiner.(1*10^-3 tot 1*10^-30)
#Elke optie wordt in een option tag gereturnt zodat alle opties in het dropdown geselecteerd kunnen worden.
def options():	
	options = ''
	for i in range(3, 30):
		options += '<option value='+str(float(10)**-i)+'>< *10^-'+str(i)+'</option>'
	return options
#De functies queryseqi, queryblasti en queryblastr zorgen ervoor dat de query's gegenereerd worden,
#die ervoor zorgen dat er gefilterd kan worden op parameters.
#Voor elke parameter die doorgegeven worden komt er een stukje query aan de gehele query.
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
