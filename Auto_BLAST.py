"""

 Titel: Auto BLAST
 Beschijving: Automatisch BLASTen
 Bronnen: Geen
 Auteurs: William Sies en Alex Staritsky
 Datum: Thu May 12 12:36:07 2016
 Versie: 4.0
 Updates: Zie Github
 (c) Copyright
 
"""

# Import NCBIWWW voor de BLAS, NCBIXML voor het parsen van het BLAST XML bestand, time voor het ophalen van de tijd en sleep() functie en MySQL connector voor de link met de database.
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import time
import mysql.connector

"""

 Naam: settings
 Functie: Openen van een .settings bestand, settings uitwisselen en opslaan in een object.
 Parameters: Bij de creatie van het object moet er een bestandnaam van settings opgegeven worden om te openen.
 Methoden: get(setting) -> vul een index van de setting in -> geeft een setting (waarde) terug met die index.
           set_progress(proces_number, functie, sequentie_id) -> heeft een proces nummer, functie en sequentie id nodig -> slaat deze gegevens op in het settingsbestand op een vaste plek

"""
class settings: 
    def __init__(self, bestandnaam):
        self.settings = []
        self.bestandnaam = bestandnaam
        try:
            # Open het settingsbestand.
            with open(self.bestandnaam, 'r') as bestand:
                # Haal de settings uit het bestand en sla ze op in de lijst 'self.settings'.
                for regel in bestand:
                    if regel[0] != '#' and regel.replace('\n','').replace('\t','').replace('\r\n','').replace('\n\r','').replace('\r','').replace(' ','') != '':
                        self.settings.append(regel[regel.find(': ')+1:].replace('\n','').replace('\t','').replace('\r\n','').replace('\n\r','').replace('\r','').replace(' ','')) 
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Settingsbestand niet gevonden, of kan het bestand niet lezen!')

    def get(self, setting):
        try:
            # Geef de waarde terug die bij de index hoort.
            return self.settings[setting]
        except IndexError:
            raise Exception('Deze setting bestaat niet of is niet in het bestand opgenomen!')
    
    def set_progress(self, proces_number, function, sequentie_id):
        try:
            # Open het bestand en leest de data -> slaat het op in 'settings'; 'settings' wordt zometeen aangepast en opgeslagen.
            with open(self.bestandnaam, 'r') as bestand:
                settings = bestand.readlines()
                bestand.close()
            # Wijzigt het proces nummer, functie en sequentie id.
            settings[7] = 'proces_number: {0}\n'.format(str(proces_number))
            settings[8] = 'function: {0}\n'.format(str(function))
            settings[9] = 'sequence_id: {0}\n'.format(str(sequentie_id))
            # Opent het bestand en slaat de nieuwe settings op.
            with open(self.bestandnaam, 'w') as bestand:
                bestand.writelines(settings)
                bestand.close()
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Settingsbestand niet gevonden, of kan het bestand niet lezen!')

"""

 Naam: log
 Functie: Maakt of opent een .txt bestand om bij te houden wat er gebeurt in het programma.
 Parameters: Bij de creatie een bestandnaam waarin het logboek bijgehouden kan worden.
 Methode: write(info) -> vul informatie in dat in het logboek opgeslagen moet worden -> het wordt in het logbestand opgeslagen samen met de huidige datum en tijd.

"""
class log:
    def __init__(self, bestandnaam):
        self.bestandnaam = bestandnaam
        try:
            # Dit is om te kijken of het logbestand al bestaat, zo niet, gaat het naar de except.
            bestand = open(self.bestandnaam, 'r')
            bestand.close()
        except IOError or FileNotFoundError or UnicodeDecodeError:
            # Als het bestand niet bestaat, maak een 'leeg' (er worden wel headers toegevoegd) logbestand.
            bestand = open(self.bestandnaam, 'w')
            bestand.write('-'*125+'\nDatum:     | Tijd:    | Event:\n'+'-'*125)
            bestand.close()

    def write(self, info):
        try:
            # Open het bestand en sla de informatie op met de huidige datum en tijd.
            with open(self.bestandnaam, 'a') as bestand:
                bestand.write('\n{0} | {1} | {2}'.format(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"),str(info)))
                bestand.close()
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Logbestand niet gevonden, of kan het bestand niet lezen!')

"""

 Naam: sequentie
 Functie: Het opslaan van 4 variabelen in 1 object; in dit geval alle informatie over een sequentie in het bestand.
 Parameters: Bij de creatie de variablen die erin opgeslagen moeten worden: een sequentie id, kwaliteitsscore, sequentie en type sequentie.
 Methode: getValue(value) -> vul 'sequentie_id', 'kwaliteitsscore', 'sequentie' of 'type' in -> geeft de waarde van de opgegeven naam terug.

"""
class sequentie:
    def __init__(self, sequentie_id, kwaliteitsscore, sequentie, type_seq):
        # Slaat de informatie van de sequentie op.
        self._sequentie_id = sequentie_id
        self._kwaliteits_score = kwaliteitsscore
        self._sequentie = sequentie
        self._type = type_seq
        
    def getValue(self, value):
        # Geeft een waarde terug afhankelijk van de variable 'value'.
        if value == 'sequentie_id':
            return self._sequentie_id
        elif value == 'kwaliteitsscore':
            return self._kwaliteits_score
        elif value == 'sequentie':
            return self._sequentie
        elif value == 'type':
            return self._type
        else:
            raise ValueError('Geen of een verkeerde value opgevraagd!')

"""
 
 Naam: seq_data
 Functie: Leest twee sequentiebestanden in (de forward en reverse), filtert de sequenties afhankelijk van wat er in de settings staat, slaat de gefilterde data (in de vorm van sequentieobjecten) op in het object en het object kan geitereerd worden en geeft steeds een sequentieobject terug.
 Parameters: Bij de creatie moet de namen van de forward en reverse sequentiebestanden worden opgegeven en het settingsobject met de settings.
 Methoden: __iter__() -> deze functie wordt door de for loop in de main functie aangeroepen om een itereerbaar object terug te geven (in dit geval het object zelf) -> geeft zichzelf terug.
           next() -> deze functie wordt door de for loop aangeroepen om de volgende sequentie terug te geven -> geeft het volgende sequentieobject uit de lijst terug.
           __readFile__(bestandnaam) -> vul een bestandnaam in -> geeft een lijst met sequentieobjecten met seqeuntie informatie uit het bestand terug.
           __filterData__(data, parameters) -> geef deze functie een lijst met data en het settingsobject -> geeft een gefilterde lijst met data terug afhankelijk van welke 'range' in de settings is opgegeven.
           set_loop(proces_number) -> vul een index in waarbij de iteratie moet beginnen (of verdergaan) -> zorgt ervoor dat de next() functie begint of verdergaat bij de opgegeven index.
           get_progress() -> geeft de index terug van de huidige sequentie in het object (van het itereren).
           
"""
class seq_data:
    def __init__(self, fwd_bestandnaam, rev_bestandnaam, parameters):
        self.data = []
        self.index = 0
        # Haal data op uit de forward en reverse sequentie in de vorm van sequentieobjecten
        self.fwd_data = self.__readFile__(fwd_bestandnaam)
        self.rev_data = self.__readFile__(rev_bestandnaam)
        # Filter de opgehaalde data aan de hand van de settings
        self.__filterData__(self.fwd_data, parameters)
        self.__filterData__(self.rev_data, parameters)
        
    # Deze functie is nodig voor de iteratie; geeft zichzelf terug.        
    def __iter__(self):
        return self
    
    # Deze functie is nodig voor de iteratie; geeft de volgende sequentie in de lijst terug.
    def next(self):
        # Als hij bij de laatste index van de data is -> stop de iteratie.
        if self.index == len(self.data):
            raise StopIteration
        # Sla de huidige index tijdelijk op, tel bij de originele index 1 op voor de volgende next() -> geef het huidige sequentieobject terug
        index = self.index
        self.index += 1
        return self.data[index]
        
    def __readFile__(self, bestandnaam):
        try:
            # Opent het bestand.
            with open(bestandnaam, 'r') as bestand:
                data = []
                regelnummer = -1
                for regel in bestand:
                    regelnummer += 1
                    # Reset het regelnummer na de vierde regel (elk 'blok' met informatie bestaat uit vier regels).
                    if regelnummer > 3:
                        regelnummer = 0
                    # Uit de eerste regel kan de sequentie id en het de type sequentie opgehaald worden.
                    if regelnummer == 0:
                        sequentie_id = regel[1:regel.find('/')]
                        type_seq = regel.replace('\n', '').replace('\r', '').replace(' ','')[-1]
                    # Uit de tweede regel kan de sequentie opgehaald worden.
                    if regelnummer == 1:
                        seq = regel
                    # In de derde regel staat een '+', hier hebben we niets aan, dus wordt genegeerd.
                    # In de vierde regel staat de kwaliteitsscore
                    if regelnummer == 3:
                        kwaliteitsscore = regel
                        # Alle data is nu opgehaald, een sequentieobject met de informatie wordt aangemaakt en toegevoegd aan de 'data' lijst.
                        data.append(sequentie(sequentie_id, kwaliteitsscore, seq, type_seq))
                bestand.close()
                return data
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Kan sequentiebestand niet vinden of lezen!')
    
    def __filterData__(self, data, parameters):
        startReading = False
        # Loop door de data.
        for sequentie in data:
            # Als de eerste sequentie gevonden is, start met het toevoegen van data aan de 'definitieve' lijst met data.
            if sequentie.getValue('sequentie_id') == parameters.get(26):
                startReading = True
            if startReading:
                self.data.append(sequentie)
            # Als de laatste sequentie gevonden is, stop met het toevoegen van data.
            if sequentie.getValue('sequentie_id') == parameters.get(27):       
                startReading = False
    
    # Zet de index naar een specifieke waarde (de waarde die gebruikt wordt bij het itereren van de data).
    def set_loop(self, proces_number):
        self.index = int(proces_number)
    
    # Haal de huidige index op.
    def get_progress(self):
        return self.index

"""

 Naam: type_operation
 Functie: Dient als een lijst object met vier waarden; maar dan met extra functionaliteit. Er kan vastgesteld worden waar de 'lijst' moet beginnen met itereren.
 Parameters: Geen
 Methoden: __iter__() -> deze functie wordt door de for loop in de main functie aangeroepen om een itereerbaar object terug te geven (in dit geval het object zelf) -> geeft zichzelf terug.
           next() -> deze functie wordt door de for loop aangeroepen om de volgende sequentie terug te geven -> geeft het volgende sequentieobject uit de lijst terug.
           set_loop(index) -> vul een index in waarbij de iteratie moet beginnen (of verdergaan) -> zorgt ervoor dat de next() functie begint of verdergaat bij de opgegeven index.

"""
class type_operation:
    def __init__(self):
        # Dit zijn de vier functies die in het programma gebruikt worden.
        self.operations = ['save_sequentie', 'blastn', 'blastx', 'tblastx']
        self.index = 0
        self.resume = False
    
    # Deze functie is nodig voor de iteratie; geeft zichzelf terug.
    def __iter__(self):
        # Zet de index op 0 als de iteratie begint. Een uitzondering hierop is als de set_loop functie voor deze functie gebruikt is.
        if self.resume == False:
            self.index = 0
        return self
    
    # Deze functie is nodig voor de iteratie; geeft de volgende operatie (of functie) in de lijst terug.
    def next(self):
        # Als hij bij de laatste index van de data is -> stop de iteratie.
        if self.index == len(self.operations):
            if self.resume:
                self.resume = False
            raise StopIteration
        # Sla de huidige index tijdelijk op, tel bij de originele index 1 op voor de volgende next() -> geef de huidige operatie (of functie) terug.
        index = self.index
        self.index += 1
        return self.operations[index]
        
    def set_loop(self, index):
        self.resume = True
        # Afhankelijk van de ingevulde 'index' (eigenlijk functie) zet de index naar een specifieke waarde die in de 'self.operations' lijst weer naar de functie verwijst.
        if index == 'save_sequentie':
            self.index = 0
        elif index == 'blastn':
            self.index = 1
        elif index == 'blastx':
            self.index = 2
        elif index == 'tblastx':
            self.index = 3
        else:
            raise ValueError('Geen of een verkeerde waarde ingevuld!')

"""

 Naam: BLAST
 Functie: Wordt gebruikt om een 'BLAST' op de 'NCBI-server' uit te voeren en de resultaten daarvan op te slaan in dit object.
 Parameters: Geen
 Methoden: do_blast(type_blast, sequentie, parameters) -> vul het type_blast, sequentieobject en het settingsobject in -> slaat een 'BLAST_record' object op waarin de resulten van de BLAST resultaten staan.
           get_results() -> geeft het 'BLAST_record' object terug dat in dit object zit.
 
"""    
class BLAST:
    def __init__(self):
        # Er zijn nog geen 'BLAST' resultaten.
        self.blast_record = None
        
    def do_blast(self, type_blast, sequentie, parameters):
        # Zet de filters om die in de settings staan, naar leesbare parameters voor de BLAST-functie.
        filters = ''
        if (type_blast == 'blastn' and parameters.get(13) == 'True') or (type_blast == 'blastx' and parameters.get(18) == 'True') or (type_blast == 'tblastx' and parameters.get(24) == 'True'):
            filters += 'L'
        if (type_blast == 'blastn' and parameters.get(14) == 'True') or (type_blast == 'blastx' and parameters.get(19) == 'True') or (type_blast == 'tblastx' and parameters.get(25) == 'True'):
            filters += 'M'
        if filters == '':
            filters = 'none'
        # Als het type blast 'blastn' is, voer een 'blastn' uit met de parameters voor 'blastn'.
        if type_blast == 'blastn':
            record_handle = NCBIWWW.qblast(type_blast, parameters.get(11), sequentie.getValue('sequentie'), expect=parameters.get(12), filter=filters)
        # Als de type blast 'blastx' is, voer een 'blastx' uit met de parameters voor 'blastx'.
        elif type_blast == 'blastx':
            record_handle = NCBIWWW.qblast(type_blast, parameters.get(15), sequentie.getValue('sequentie'), expect=parameters.get(17), filter=filters, matrix_name=parameters.get(16), gapcosts=parameters.get(20)[:parameters.get(20).find(',')]+' '+parameters.get(20)[parameters.get(20).find(',')+1:])
        # Als de type blast 'blastx' is, voer een 'blastx' uit met de parameters voor 'tblastx'.
        elif type_blast == 'tblastx':
            record_handle = NCBIWWW.qblast(type_blast, parameters.get(21), sequentie.getValue('sequentie'), expect=parameters.get(23), filter=filters, matrix_name=parameters.get(22))
        # Parse het XML bestand dat uit de 'BLAST' komt en haal de 'BLAST_record' er uit en zet het in 'self.blast_record'
        blast_results = NCBIXML.parse(record_handle)
        self.blast_record = next(blast_results)
        
    def get_results(self):
        # Return het 'BLAST_record'.
        return self.blast_record

"""
 
 Naam: database
 Functie: Verbinding maken met de database en de sequentie informatie en 'BLAST' resultaten erop zetten.
 Parameters: Bij de creatie moet het settingsobject meegegeven worden om de waarden voor (inlog)gegevens de verbinding.
 Methoden: send_seq_data(sequentie) -> vul een sequentieobject in om opgeslagen te worden -> slaat de gegevens van de sequentie op in de database.
           send_blast_results(type_blast, sequentie, parameters, blast_record, program_log) -> vul het type blast, sequentieobject, settingsobject, 'BLAST_record' (de resultaten van de blast) en logboekobject in om de 'BLAST' resultaten op te slaan -> Slaat de gegevens over de 'BLAST', parameters van de 'BLAST' en resultaten van de 'BLAST' op in de database.
           
"""
class database:
    def __init__(self, parameters):
        # Maak verbinding met de database met behulp van het settingsobject.
        self.connection = mysql.connector.connect(host=parameters.get(7), user=parameters.get(8), db=parameters.get(9), password=parameters.get(10))
        # Maak een 'cursor' aan die acties op de database kan uitvoeren.
        self.cursor = self.connection.cursor()
        
    def send_seq_data(self, sequentie):
        # Check of deze sequentie al in de database staat
        self.cursor.execute("""SELECT Sequentie_identifier
                               FROM Sequentie
                               WHERE Sequentie_identifier = '{0}'""".format(sequentie.getValue('sequentie_id'), sequentie.getValue('type')))
        results = self.cursor.fetchall()
        self.cursor.close()
        # Maak een nieuwe cursor aan om gegevens aan de database toe te voegen.
        self.cursor = self.connection.cursor()
        try:
            results[0]
        except IndexError:
            # Als de sequentie er niet in staat, voeg het toe aan de database.
            self.cursor.execute("INSERT INTO Sequentie VALUES ('{0}');".format(sequentie.getValue('sequentie_id')))
        # Sla de sequentiegegevens op in de database.
        self.cursor.execute("INSERT INTO Sequentie_informatie VALUES ('{0}', '{1}', {2}, '{3}');".format(sequentie.getValue('kwaliteitsscore'), sequentie.getValue('sequentie'), sequentie.getValue('type'), sequentie.getValue('sequentie_id')))
        # Commit de data en sluit de verbinding
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        
    def send_blast_results(self, type_blast, sequentie, parameters, blast_record, program_log):
        # Kijk wat de hoogste ID in de database is.
        self.cursor.execute("SELECT max(Parameters_ID) FROM Resultaat")
        results = self.cursor.fetchall()
        self.cursor.close()
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
        
        # Zet de low complexity en mask lookup uit de settings om naar leesbare parameters voor het invoegen in de database (een 0 of 1).
        if (type_blast == 'blastn' and parameters.get(13) == 'True') or (type_blast == 'blastx' and parameters.get(18) == 'True') or (type_blast == 'tblastx' and parameters.get(24) == 'True'):
            low_complexity = 1
        else:
            low_complexity = 0
        if (type_blast == 'blastn' and parameters.get(14) == 'True') or (type_blast == 'blastx' and parameters.get(19) == 'True') or (type_blast == 'tblastx' and parameters.get(25) == 'True'):
            mask_lookup = 1
        else:
            mask_lookup = 0
            
        # Maak een cursor aan om de gegevens naar de database te versturen.
        self.cursor = self.connection.cursor()
        # Als het type blast 'blastn' is, vul dan de resultaten en parameters voor een 'blastn' specifiek in (niet alle blasts hebben dezelfde typen parameters).
        if type_blast == 'blastn':
            self.cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', NULL, {2}, {3}, NULL, {4}, {5});""".format(type_blast, parameters.get(11), low_complexity, mask_lookup, parameters_id, resultaat_id))
        # Als het type blast 'blastx' is, vul dan de resultaten en parameters voor een 'blastn' specifiek in (niet alle blasts hebben dezelfde typen parameters).
        if type_blast == 'blastx':
            self.cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', '{2}', {3}, {4}, '{5}', {6}, {7});""".format(type_blast, parameters.get(15), parameters.get(16), low_complexity, mask_lookup, parameters.get(20), parameters_id, resultaat_id))
        # Als het type blast 'tblastx' is, vul dan de resultaten en parameters voor een 'blastn' specifiek in (niet alle blasts hebben dezelfde typen parameters).
        if type_blast == 'tblastx':
            self.cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', '{2}', {3}, {4}, NULL, {5}, {6});""".format(type_blast, parameters.get(21), parameters.get(22), low_complexity, mask_lookup, parameters_id, resultaat_id))
        
        # Stuur de gegevens over de 'BLAST' zelf naar de database.
        self.cursor.execute("""INSERT INTO Resultaat VALUES ('{0}', CURRENT_DATE(), CURRENT_TIME(), '{1}', {2}, {3}, {4});""".format(query_id, sequentie.getValue('sequentie_id'), resultaat_id , parameters_id, has_results))        
        
        # Stuur de resultaten van de 'BLAST' naar de database.
        # Voor elke alignment en 'hsp' object in de resultaten.
        for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                if hsp.expect < float(parameters.get(3)):
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
                        print("Unicode object bij sequentie '{0}': 'organisme_eiwit_info'".format(sequentie.getValue('sequentie_id')))
                        program_log.write("Unicode object bij sequentie '{0}: 'organisme_eiwit_info'".format(sequentie.getValue('sequentie_id')))
                    # Probeer de informatie over het organisme en/of eiwit id te halen.
                    try:
                        organisme_eiwit_ID = str(alignment.hit_id.encode('utf-8'))
                    except AttributeError:
                        # Lukt het ophalen van de informatie niet, door een AttributeError (op een of andere manier komt er een Unicodeobject?) -> negeer het dan en maak er een 'NULL' van en schijf het op in het logbestand.
                        organisme_eiwit_ID = 'NULL'
                        print("Unicode object bij sequentie '{0}': 'organisme_eiwit_ID'".format(sequentie.getValue('sequentie_id')))
                        program_log.write("Unicode object bij sequentie '{0}: 'eiwit_ID'".format(sequentie.getValue('sequentie_id')))
                    # Probeer de titel van het organisme en/of eiwit te halen.
                    try:
                        organisme_eiwit_title = str(alignment.title.encode('utf-8'))
                    except AttributeError:
                        # Lukt het ophalen van de informatie niet, door een AttributeError (op een of andere manier komt er een Unicodeobject?) -> negeer het dan en maak er een 'NULL' van en schijf het op in het logbestand.
                        organisme_eiwit_title = 'NULL'
                        print("Unicode object bij sequentie '{0}': 'organisme_eiwit_title'".format(sequentie.getValue('sequentie_id')))
                        program_log.write("Unicode object bij sequentie '{0}: 'organisme_eiwit_title'".format(sequentie.getValue('sequentie_id')))
                    # Maak een 'alignment' door de 'query' sequentie, de 'matches' en 'subject' sequentie.
                    alignment = hsp.query+'\n'+hsp.match+'\n'+hsp.sbjct
                    # Als het type blast 'blastn' is, vul informatie de database in die bekend is over een 'blastn'.
                    if type_blast == 'blastn':
                        self.cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, NULL, '{9}', '{10}', '{11}', '{12}', {13});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
                    # Als het type blast 'blastx' is, vul informatie de database in die bekend is over een 'blastx'.
                    if type_blast == 'blastx':
                        self.cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, '{9}', '{10}', '{11}', '{12}', '{13}', {14});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, hsp.frame, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
                    # Als het type blast 'tblastx' is, vul informatie de database in die bekend is over een 'tblastx'.                    
                    if type_blast == 'tblastx':
                        self.cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, '{9}', '{10}', '{11}', '{12}', '{13}', {14});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, hsp.frame, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
        
        # Commit de data en sluit de verbinding met de database.
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

"""

 Naam: main
 Functie: de hoofdfunctie die alle classes in het programma aanroept
 Parameters: Geen
 Output: De status van het programma en zodra voltooid een database gevuld met sequentie en 'BLAST' data.
 
"""       
def main():
    # Init de objecten: settings, seq_data, type_operation en log.
    parameters = settings('Auto_BLAST_settings.settings')
    champignon_data = seq_data(parameters.get(0), parameters.get(1), parameters)
    operations = type_operation()
    program_log = log(parameters.get(2))
    
    # Zet de twee loops op de juiste plek (om door te gaan als het programma was gestopt).
    champignon_data.set_loop(parameters.get(4))
    operations.set_loop(parameters.get(5))
    
    # Main loop, voor elke sequentie in de datasets en voor elke functie.
    for sequentie in champignon_data:
        for function in operations:
            try:
                # Haal uit het sequentieobject de sequentie id op (hij wordt hier vaak gebruikt).
                sequentie_id = sequentie.getValue('sequentie_id')
                # Sla het huidige proces op in het settingsbestand, zodat hij hier weer verdergaat bij het opnieuw opstarten van het programma.
                parameters.set_progress(champignon_data.get_progress()-1, function, sequentie_id)
                # Print de huidige functie en sequentie id die verwerkt worden.
                print(function+': '+sequentie_id)
                # Als hij bij de functie 'save_sequentie' is.
                if function == 'save_sequentie':
                    # Stuur de sequentieinformatie op naar de database.
                    db = database(parameters)
                    db.send_seq_data(sequentie)
                # Als de functie een 'blastn', 'blastx' of 'tblastx' is.
                elif function in ['blastn', 'blastx', 'tblastx']:
                    # Voer een 'BLAST' uit met de huidige sequentie.
                    NCBI = BLAST()
                    NCBI.do_blast(function, sequentie, parameters)
                    # Sla de gegevens en resultaten van de 'BLAST' op in de database.
                    db = database(parameters)
                    db.send_blast_results(function, sequentie, parameters, NCBI.get_results(), program_log)
                # Schijf in het logboek dat de huidige functie bij de huidige sequentie gelukt is.
                program_log.write("{0} van sequentie '{1}' is gelukt!".format(function, sequentie_id))
            # Als er een error optreedt in de main loop.
            except Exception as error:
                # Print dat een error heeft plaatsgevonden.
                print("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
                # Schijf in het logboek op dat er een error heeft plaatsgevonden.
                program_log.write("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
                # Wacht 30 seconden totdat het programma verder gaat met zijn volgende taak (dit kan handig zijn als de NCBI server het programma 'kickt' van de server, dat hij misschien na 30 seconden weer wordt toegelaten).
                print('30 seconden wachten tot nieuwe poging...')
                time.sleep(30)

# Roep de main functie aan
main()
