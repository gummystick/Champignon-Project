"""
Title: Online BLAST en sequentie toevoegen aan database
Beschrijving: Zie titel
Bronnen: http://www.w3schools.com/
Auteurs: William Sies en Alex Staritsky
Datum: Donderdag 9 juni 2016
Versie:	1.0
Updates: Zie Github
@ Copyright
"""

# Mod_python voor de apache server
from mod_python import apache
# Bio.Blast NCBI.WWW voor de BLAST
from Bio.Blast import NCBIWWW
# Bio.Blast NCBIXML voor het parsen van de XML
from Bio.Blast import NCBIXML
# MySQL connector voor de connectie met de database.
import mysql.connector

# Verwijst je door naar juiste pagina

def index(req, username='', token=''):
	req.content_type = 'text/html'
	# Als je een username en wachtwoord hebt verstuurd, stuur door naar blast_form.
	if username != '' and token != '':
		blast_form(req, username, token)
	else:
	# Anders wordt je naar de login gestuurd.
		login(req, '0')
		
# Login om bij de BLAST pagina te komen.
		
def login(req, status='0'):
	req.content_type = 'text/html'
	title = 'Login'
	# Bovenkant van de pagina
	req.write(head(title))
	req.write(titel(title))
	req.write(bovenmenu())
	# Script voor het versleutelen van het wachtwoord in SHA256 met een salt.
	req.write("""
					<script type='text/javascript' src='http://cytosine.nl/~owe4_bi1e_2/Python/sha256.js'></script>
					<script type='text/javascript'>
						function send() {
							document.getElementById('token').value = SHA256(SHA256(document.getElementById('password').value)+'25cc0490077a3fc37452ea7c2b457ab8d167da3b58f799b8ebe55277470c2025');
					}
					</script>
					<br>
					<div class='login'>
					""")
	# Als deze pagina met een status '1' is geladen, geef weer dat er een verkeerde login gegevens zijn ingevoerd.
	if status == '1':
		req.write("<p><font color='red'>You didn't enter the correct details!</font><p>")
	# Het formulier voor het invullen van de gebruikersnaam en wachtwoord.
	req.write("""<form action='http://cytosine.nl/~owe4_bi1e_2/Python/blast.py' method='POST' onsubmit='send()'>
					<input placeholder='Username' id='username', name='username'>
					<input type='password' placeholder='Password' id='password'>
					<input type='hidden' id='token' name='token'>
					<br>
					<input type='submit' value='Login'>
				 </form>
				 </div>
				 </body>
				 </html>
				 """)

# Hier worden de gegevens voor de BLAST ingevoerd.
				 
def blast_form(req, username='', token='', status='', sequentie_id='', type_blast='', type_sequentie='', sequentie='', kwaliteitsscore=''):
	req.content_type = 'text/html'
	# Het wachtwoord + salt in SHA256
	encryption = 'fc2f89450e7c878998ebd6cb2b99298ab8f4defd140582f62967094bbd19ddb6'
	# Check de login gegevens
	if username == 'admin' and token == encryption:
		# Bovenkant van de pagina
		title = 'BLAST Form'
		req.write(head(title))
		req.write(titel(title))
		req.write(bovenmenu())
		req.write("""
				 <br>
				 <div class='blast_form'>
				 """)
		# Als deze pagina met een status '1' is geladen, geef weer dat niet alles ingevuld is.
		if status == '1':
			req.write("<p><font color='red'>Niet alle waarden zijn ingevuld!</font></p>")
		# Formulier voor de BLAST.
		req.write("""<form action=http://cytosine.nl/~owe4_bi1e_2/Python/blast.py/blast method='POST'>
					 <p>Type sequentie</p>
					 <select name='type_sequentie'>""")
		# De if statements zijn voor het automatisch selecteren van de vorige optie die ingevuld was als de BLAST terugverwijst naar deze pagina.
		if type_sequentie == 'reverse':
			req.write("""<option value='1'>Forward</option>""")
			req.write("""<option value='2' selected='selected'>Reverse</option>""")
		else:
			req.write("""<option value='1' selected='selected'>Forward</option>""")
			req.write("""<option value='2'>Reverse</option>""")
		req.write("""</select>
				 <br>
				 <p>Type BLAST:</p>
				 <select name='type_blast'>""")
		if type_blast == 'blastn':
			req.write("""<option value='blastn' selected='selected'>blastn</option>
						 <option value='blastx'>blastx</option>
						 <option value='tblastx'>tblastx</option>""")
		elif type_blast == 'blastx':
			req.write("""<option value='blastn'>blastn</option>
						 <option value='blastx' selected='selected'>blastx</option>
						 <option value='tblastx'>tblastx</option>""")
		elif type_blast == 'tblastx':
			req.write("""<option value='blastn'>blastn</option>
						 <option value='blastx'>blastx</option>
						 <option value='tblastx' selected='selected'>tblastx</option>""")
		else:
			req.write("""<option value='blastn'>blastn</option>
						 <option value='blastx'>blastx</option>
						 <option value='tblastx'>tblastx</option>""")
		# De rest van het formulier.
		req.write("""
				 </select>
				 <br>
				 <p>Sequentie ID:</p>
				 <input type='text' id='sequentie_id' name='sequentie_id' value={0}>
				 <br>
				 <p>Sequentie:</p>
				 <textarea rows="4" cols="50" name='sequentie'>{1}</textarea>
				 <p>Kwaliteitsscore:</p>
				 <textarea rows="4" cols="50" name='kwaliteitsscore'>{2}</textarea>
				 <br><br>
				 <input type='submit' value='BLAST'>
				 <input type='hidden' name='username' value='{3}'>
				 <input type='hidden' name='token' value='{4}'>
				 </form
				 </div>
				 </form>
				 </body>
				 </html>
				 """.format(sequentie_id, sequentie, kwaliteitsscore, username, token))
	else:
		# Als de authenticatie niet goed is, ga naar de loginpagina met status '1'.
		login(req, '1')

# Hier wordt de BLAST uitgevoerd en de resultaten worden opgeslagen.
		
def blast(req, username='', token='', sequentie_id='', type_blast='', type_sequentie='', sequentie='', kwaliteitsscore=''):
	req.content_type = 'text/html'
	# Het wachtwoord + salt in SHA256
	encryption = 'fc2f89450e7c878998ebd6cb2b99298ab8f4defd140582f62967094bbd19ddb6'
	# Check de login gegevens
	if username == 'admin' and token == encryption:
		# Check of het formulier volledig ingevuld is.
		if sequentie_id != '' and type_blast != '' and sequentie != '' and kwaliteitsscore != '':
			try:
				# Bovenkant van de pagina
				title = 'BLAST'
				req.write(head(title))
				req.write(titel(title))
				req.write(bovenmenu())
				# Tekst voor de pagina
				req.write("""
						 <br>
						 <div class='blast'>
						 <h1>BLAST wordt verwerkt, sluit de pagina niet!</h1>
						 <p>De BLAST kan een tijdje duren, afhankelijk van hoe druk de server is...</p>
						 </div>
						 <br><div class='blast'>""")
				# Blast de sequentie
				blast_record = do_blast(sequentie, type_blast)
				# Sla de informatie van de sequentie op in de database
				sequentie_informatie(req, sequentie_id, sequentie, type_sequentie, kwaliteitsscore)
				# Sla de BLAST resultaten op in de database
				save_blast(sequentie_id, blast_record, type_blast)
				# Stuur naar de webpagina dat de BLAST gelukt is.
				req.write("<p><font color='green'>BLAST gelukt en opgeslagen!</font></p>")
			except Exception as error:
				# Stuur naar de webpagina dat bij de BLAST een error heeft opgetreden.
				req.write("<p><font color='red'>Een error heeft opgetreden!</font></p><p>{0}</p>".format(str(error)))
			# Sluit het HTML document.
			req.write("""
						 </div>
						 </body>
						 </html>
						 """)
		else:
			# Als het formulier niet volledig is ingevuld stuur de gebruiker terug naar het formulier met zijn ingevulde gegevens.
			blast_form(req, username, token, '1', sequentie_id, type_blast, type_sequentie, sequentie, kwaliteitsscore)
	else:
		# Als de authenticatie niet goed is, ga naar de loginpagina met status '1'.
		login(req, '1')
		
def titel(title):
	# De titel van de pagina.
	return """<div class='title'><h1>"""+title+"""</h1></div>"""

def head(title):
	# De head van de pagina.
	return """<html>
    <head>
    <link rel="stylesheet" "type="text/css" href="http://cytosine.nl/~owe4_bi1e_2/Python/Webinterface.css" >
	<title>"""+title+"""</title>
    </head>
	<body>"""
	
def bovenmenu():
	# Het menu van de pagina.
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
		<ul>
			<li>
				<a href="http://cytosine.nl/~owe4_bi1e_2/Python/blast">Resultaten toevoegen</a>
			</li>
		<ul>
	</div>"""

def sequentie_informatie(req, sequentie_id, sequentie, type_sequentie, kwaliteitsscore):
	# Anti SQL injection gedeeltelijk
	sequentie_id = sql(sequentie_id)
	sequentie = sql(sequentie)
	type_sequentie = sql(type_sequentie)
	kwaliteitsscore = sql(kwaliteitsscore)
	
	connection = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = connection.cursor()
	# Check of deze sequentie al in de database staat
	cursor.execute("SELECT Sequentie_identifier FROM Sequentie WHERE Sequentie_identifier = '{0}'".format(sequentie_id))
	results = cursor.fetchall()
	cursor.close()
	connection.close()
	# Maak een nieuwe cursor aan om gegevens aan de database toe te voegen.
	connection = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = connection.cursor()
	try:
		results[0]
	except IndexError:
		# Als de sequentie er niet in staat, voeg het toe aan de database.
		cursor.execute("INSERT INTO Sequentie VALUES ('{0}');".format(sql(sequentie_id)))
	# Sla de sequentiegegevens op in de database.
	cursor.execute("INSERT INTO Sequentie_informatie VALUES ('{0}', '{1}', {2}, '{3}');".format(kwaliteitsscore, sequentie, type_sequentie, sequentie_id))
	# Commit de data en sluit de verbinding
	connection.commit()
	cursor.close()
	connection.close()
	
def do_blast(sequentie, type_blast):
	sequentie = sql(sequentie)
	type_blast = sql(type_blast)
	
	if type_blast == 'blastn':
		record_handle = NCBIWWW.qblast(type_blast, 'nr', sequentie, expect='1', filter='LM')
	# Als de type blast 'blastx' is, voer een 'blastx' uit met de parameters voor 'blastx'.
	elif type_blast == 'blastx':
		record_handle = NCBIWWW.qblast(type_blast, 'nr', sequentie, expect='1', filter='L', matrix_name='BLOSUM62', gapcosts='11 1')
	# Als de type blast 'blastx' is, voer een 'blastx' uit met de parameters voor 'tblastx'.
	elif type_blast == 'tblastx':
		record_handle = NCBIWWW.qblast(type_blast, 'nr', sequentie, expect='1', filter='L', matrix_name='BLOSUM62')
	# Parse het XML bestand dat uit de 'BLAST' komt en haal de 'BLAST_record' er uit en zet het in 'self.blast_record'
	blast_results = NCBIXML.parse(record_handle)
	blast_record = next(blast_results)
	return blast_record
	
def save_blast(sequentie_id, blast_record, type_blast):
	# Anti SQL injection gedeeltelijk
	sequentie_id = sql(sequentie_id)
	type_blast = sql(type_blast)
	
	# Kijk wat de hoogste ID in de database is.
	connection = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = connection.cursor()
	cursor.execute("SELECT max(Parameters_ID) FROM Resultaat")
	results = cursor.fetchall()
	cursor.close()
	connection.close()
	# Als het nog niet bestaat begin dan bij 1.
	if results[0][0] == None:
		parameters_id = 1
	# Voeg anders 1 toe aan het ID
	else:
		parameters_id = int(results[0][0])+1
	# In onze database zijn de query_id, resultaat_id en parameters_id gelijk aan elkaar (op het type variabele na).
	query_id = str(parameters_id)
	resultaat_id = parameters_id

	# Kijk of het 'BLAST_record' object resultaten heeft.
	has_results = 1
	for alignment in blast_record.alignments:
		for hsp in alignment.hsps:
			if hsp.num_alignments == 'None':
				has_results = 0
	
	# Maak een cursor aan om de gegevens naar de database te versturen.
	connection = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = connection.cursor()
	# Als het type blast 'blastn' is, vul dan de resultaten en parameters voor een 'blastn' specifiek in (niet alle blasts hebben dezelfde typen parameters).
	if type_blast == 'blastn':
		cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', NULL, {2}, {3}, NULL, {4}, {5});""".format(type_blast, 'nr', '1', '1', parameters_id, resultaat_id))
	# Als het type blast 'blastx' is, vul dan de resultaten en parameters voor een 'blastn' specifiek in (niet alle blasts hebben dezelfde typen parameters).
	if type_blast == 'blastx':
		cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', '{2}', {3}, {4}, '{5}', {6}, {7});""".format(type_blast, 'nr', 'BLOSUM62', '1', '0', '11,1', parameters_id, resultaat_id))
	# Als het type blast 'tblastx' is, vul dan de resultaten en parameters voor een 'blastn' specifiek in (niet alle blasts hebben dezelfde typen parameters).
	if type_blast == 'tblastx':
		cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', '{2}', {3}, {4}, NULL, {5}, {6});""".format(type_blast, 'nr', 'BLOSUM62', '1', '0', parameters_id, resultaat_id))
	cursor.execute("""INSERT INTO Resultaat VALUES ('{0}', CURRENT_DATE(), CURRENT_TIME(), '{1}', {2}, {3}, {4});""".format(query_id, sequentie_id, resultaat_id , parameters_id, has_results))
	connection.commit()
	cursor.close()
	connection.close()
	
	connection = mysql.connector.connect(host='localhost', user='owe4_bi1e_2', db='owe4_bi1e_2', password='blaat1234')
	cursor = connection.cursor()
	for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
				try:
					if hsp.expect < float(0.1):
						# Haal de total aligned op.
						total_aligned = hsp.align_length
						# Bereken het identity percentage.
						identity_perc = float(float(hsp.identities)/float(total_aligned))*100
						# Bereken het positive percentage.
						positives_perc = float(float(hsp.positives)/float(total_aligned))*100
						# Probeer de informatie van het eiwit op te halen.
						try:
							organisme_eiwit_info = str(alignment.hit_def.encode('utf-8'))
						except AttributeError:
							# Lukt het ophalen van de informatie niet, door een AttributeError (op een of andere manier komt er een Unicodeobject?) -> negeer het dan en maak er een 'NULL' van en schijf het op in het logbestand.
							organisme_eiwit_info = 'NULL'
						# Probeer de informatie over het organisme en/of eiwit id te halen.
						try:
							organisme_eiwit_ID = str(alignment.hit_id.encode('utf-8'))
						except AttributeError:
							# Lukt het ophalen van de informatie niet, door een AttributeError (op een of andere manier komt er een Unicodeobject?) -> negeer het dan en maak er een 'NULL' van en schijf het op in het logbestand.
							organisme_eiwit_ID = 'NULL'
						# Probeer de titel van het organisme en/of eiwit te halen.
						try:
							organisme_eiwit_title = str(alignment.title.encode('utf-8'))
						except AttributeError:
							# Lukt het ophalen van de informatie niet, door een AttributeError (op een of andere manier komt er een Unicodeobject?) -> negeer het dan en maak er een 'NULL' van en schijf het op in het logbestand.
							organisme_eiwit_title = 'NULL'
						# Maak een 'alignment' door de 'query' sequentie, de 'matches' en 'subject' sequentie.
						alignment = hsp.query+'\n'+hsp.match+'\n'+hsp.sbjct
						# Als het type blast 'blastn' is, vul informatie de database in die bekend is over een 'blastn'.
						if type_blast == 'blastn':
							cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, NULL, '{9}', '{10}', '{11}', '{12}', {13});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
						# Als het type blast 'blastx' is, vul informatie de database in die bekend is over een 'blastx'.
						if type_blast == 'blastx':
							cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, '{9}', '{10}', '{11}', '{12}', '{13}', {14});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, hsp.frame, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
						# Als het type blast 'tblastx' is, vul informatie de database in die bekend is over een 'tblastx'.                    
						if type_blast == 'tblastx':
							cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, '{9}', '{10}', '{11}', '{12}', '{13}', {14});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, hsp.frame, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
				except:
					continue
        # Commit de data en sluit de verbinding met de database.
        connection.commit()
        cursor.close()
        connection.close()
		
def sql(string):
	# Haal rare tekens uit de string
	new_string = string.replace(' ','').replace('\\','').replace('/','').replace("'",'').replace('"','').replace('\n','').replace('\t','').replace('\r','')
	return new_string
