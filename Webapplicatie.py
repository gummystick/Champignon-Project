"""
Title: HTML-Python voor webinterface
Beschrijving: Zie title
Bronnen:-
Auteurs: Alex Staritsky en William Sies
Datum: Donderdag 19 mei 2016 - ?
Versie:1
Updates:-
Copyright
"""

import mysql.connector
from mod_python import apache

def index(req):
	req.content_type = 'text/html'
	req.write("""<html>
    <head>
    <link rel="stylesheet" "type="text/css" href="Webinterface.css" >
	<title>Blast results champignon dataset</title>
    </head>
    <body>
	<div class="global">
	<h1>Blast results champignon dataset</h1>
	<div class="introtext">
	<h3>Fill in this form to filter the BLAST results of the champignon dataset.</h3>
	<p>The dataset visualised by this webtool is derived from the genetic data in champignon fertilizer.
	This tool contains information about sequence alignments made with BLAST to look proteins and organisms that live in the fertilize.
	Fill in this form to show the results.</p>
	</div>
	<hr>
	<form value='information' action='http://cytosine.nl/~owe4_bi1e_2/Python/HTMLwebTest.py/infofunc'>
	<input type='text' name='check'>
	<div class='radiobuttons'>
	<p>Radiobuttons:<p><input type='radio' name='radiobutton' value='optie1'>Optie1<br>
	<input type='radio' name='radiobutton' value='optie2'>Optie2<br>
	<input type='radio' name='radiobutton' value='optie3'>Optie3<br>
	</div>
	<input type='submit' name='klik' value='submit'>
	</form>
	</div>
	</body>
    </html>""")

	
def infofunc(req, check, radiobutton):
	req.content_type = 'text/html'
	req.write("""<html>
    <head>
    <link rel="stylesheet" "type="text/css" href="http://cytosine.nl/~owe4_bi1e_2/Python/Webinterface.css" >
    </head>
    <body>
	<div class="global">
	<h1>Should be blue</h1>
	<div class="textarea">
	<textarea disabled>Your input in the textfield was:"""+check+"""
Your radiobutton choice was: """+radiobutton+"""</textarea>
	</div>
	</div>
	</body>
	</html>""")
