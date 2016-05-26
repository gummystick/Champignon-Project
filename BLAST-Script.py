#!/usr/bin/env python
"""

 Titel: Auto BLAST
 Beschijving: Automatisch BLASTen
 Bronnen: Geen
 Auteurs: William Sies en Alex Staritsky
 Datum: Thu May 12 12:36:07 2016
 Versie: 3.0
 Updates: Zie github
 (c) Copyright
 
"""

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import time
import mysql.connector

class settings: 
    def __init__(self, bestandnaam):
        self.settings = []
        self.bestandnaam = bestandnaam
        try:
            with open(self.bestandnaam, 'r') as bestand:
                for regel in bestand:
                    if regel[0] != '#' and regel.replace('\n','').replace('\t','').replace('\r\n','').replace('\n\r','').replace('\r','').replace(' ','') != '':
                        self.settings.append(regel[regel.find(': ')+1:].replace('\n','').replace('\t','').replace('\r\n','').replace('\n\r','').replace('\r','').replace(' ','')) 
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Settingsbestand niet gevonden, of kan het bestand niet lezen!')

    def get(self, setting):
        try:
            return self.settings[setting]
        except IndexError:
            raise Exception('Deze setting bestaat niet of is niet in het bestand opgenomen!')
    
    def set_progress(self, proces_number, function, sequentie_id):
        try:
            with open(self.bestandnaam, 'r') as bestand:
                settings = bestand.readlines()
                bestand.close()
            with open(self.bestandnaam, 'w') as bestand:
                settings[7] = '	proces_number: {0}\n'.format(str(proces_number))
                settings[8] = '	function: {0}\n'.format(str(function))
                settings[9] = '	sequence_id: {0}\n'.format(str(sequentie_id))
                bestand.writelines(settings)
                bestand.close()
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Settingsbestand niet gevonden, of kan het bestand niet lezen!')

class log:
    def __init__(self, bestandnaam):
        self.bestandnaam = bestandnaam
        try:
            bestand = open(self.bestandnaam, 'r')
            bestand.close()
        except IOError or FileNotFoundError or UnicodeDecodeError:
            bestand = open(self.bestandnaam, 'w')
            bestand.write('-'*125+'\nDatum:     | Tijd:    | Event:\n'+'-'*125)
            bestand.close()

    def write(self, info):
        try:
            with open(self.bestandnaam, 'a') as bestand:
                bestand.write('\n{0} | {1} | {2}'.format(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"),str(info)))
                bestand.close()
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Logbestand niet gevonden, of kan het bestand niet lezen!')
        
class sequentie:
    def __init__(self, sequentie_id, kwaliteitsscore, sequentie, type_seq):
        self._sequentie_id = sequentie_id
        self._kwaliteits_score = kwaliteitsscore
        self._sequentie = sequentie
        self._type = type_seq
        
    def getValue(self, value):
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

class seq_data:
    def __init__(self, fwd_bestandnaam, rev_bestandnaam, parameters):
        self.data = []
        self.index = 0
        self.fwd_data = self.__readFile__(fwd_bestandnaam)
        self.rev_data = self.__readFile__(rev_bestandnaam)
        self.__filterData__(self.fwd_data, parameters)
        self.__filterData__(self.rev_data, parameters)
        
    def __iter__(self):
        return self
    
    def next(self):
        if self.index == len(self.data):
            raise StopIteration
        index = self.index
        self.index += 1
        return self.data[index]
        
    def __readFile__(self, bestandnaam):
        try:
            with open(bestandnaam, 'r') as bestand:
                data = []
                regelnummer = -1
                for regel in bestand:
                    regelnummer += 1
                    if regelnummer > 3:
                        regelnummer = 0
                    if regelnummer == 0:
                        sequentie_id = regel[1:regel.find('/')]
                        type_seq = regel.replace('\n', '').replace('\r', '').replace(' ','')[-1]
                    if regelnummer == 1:
                        seq = regel
                    if regelnummer == 3:
                        kwaliteitsscore = regel
                        data.append(sequentie(sequentie_id, kwaliteitsscore, seq, type_seq))
                bestand.close()
                return data
        except IOError or FileNotFoundError or UnicodeDecodeError:
            raise Exception('Kan sequentiebestand niet vinden of lezen!')
    
    def __filterData__(self, data, parameters):
        startReading = False
        for sequentie in self.data:
            if sequentie.getValue('sequentie_id') == parameters.get(26):
                startReading = True
            if startReading:
                self.data.append(sequentie)
            if sequentie.getValue('sequentie_id') == parameters.get(27):       
                startReading = False
    
    def set_loop(self, proces_number):
        self.index = int(proces_number)
    
    def get_progress(self):
        return self.index

class type_operation:
    def __init__(self):
        self.operations = ['save_sequentie', 'blastn', 'blastx', 'tblastx']
        self.index = 0
        self.resume = False
        
    def __iter__(self):
        if self.resume == False:
            self.index = 0
        return self
        
    def next(self):
        if self.index == len(self.operations):
            if self.resume:
                self.resume = False
            raise StopIteration
        index = self.index
        self.index += 1
        return self.operations[index]
        
    def set_loop(self, index):
        self.resume = True
        if index == 'save_sequentie':
            self.index = 0
        elif index == 'blastn':
            self.index = 1
        elif index == 'blastx':
            self.index = 2
        elif index == 'tblastx':
            self.index = 3
        else:
            raise ValueError('Geen of een verkeerde value opgevraagd!')
            
class BLAST:
    def __init__(self):
        self.blast_record = None
        
    def do_blast(self, type_blast, sequentie, parameters):
        filters = ''
        if (type_blast == 'blastn' and parameters.get(13) == 'True') or (type_blast == 'blastx' and parameters.get(18) == 'True') or (type_blast == 'tblastx' and parameters.get(24) == 'True'):
            filters += 'L'
        if (type_blast == 'blastn' and parameters.get(14) == 'True') or (type_blast == 'blastx' and parameters.get(19) == 'True') or (type_blast == 'tblastx' and parameters.get(25) == 'True'):
            filters += 'M'
        if filters == '':
            filters = 'none'
        if type_blast == 'blastn':
            record_handle = NCBIWWW.qblast(type_blast, parameters.get(11), sequentie.getValue('sequentie'), expect=parameters.get(12), filter=filters, )
        elif type_blast == 'blastx':
            record_handle = NCBIWWW.qblast(type_blast, parameters.get(15), sequentie.getValue('sequentie'), expect=parameters.get(17), filter=filters, matrix_name=parameters.get(16), gapcosts=parameters.get(20)[:parameters.get(20).find(',')]+' '+parameters.get(20)[parameters.get(20).find(',')+1:])
        elif type_blast == 'tblastx':
            record_handle = NCBIWWW.qblast(type_blast, parameters.get(21), sequentie.getValue('sequentie'), expect=parameters.get(23), filter=filters, matrix_name=parameters.get(22))
        blast_results = NCBIXML.parse(record_handle)
        self.blast_record = next(blast_results)
        
    def get_results(self):
        return self.blast_record

class database:
    def __init__(self, parameters):
        # Variabelen voor verbinding
        self.connection = mysql.connector.connect(host=parameters.get(7), user=parameters.get(8), db=parameters.get(9), password=parameters.get(10))
        self.cursor = self.connection.cursor()
        
    def send_seq_data(self, sequentie):
        # Check of deze sequentie al in de database staat
        self.cursor.execute("""SELECT s.Sequentie_identifier 
                               FROM Sequentie s, Sequentie_informatie i 
                               WHERE s.Sequentie_identifier = '{0}' AND i.Sequentie_identifier = '{0}' AND i.Type = {1}""".format(sequentie.getValue('sequentie_id'), sequentie.getValue('type')))
        results = self.cursor.fetchall()
        self.cursor.close()
        try:
            results[0]
        except IndexError:
            # Als het er niet in staat, voeg het toe
            self.cursor = self.connection.cursor()
            self.cursor.execute("INSERT INTO Sequentie VALUES ('{0}');".format(sequentie.getValue('sequentie_id')))
            self.cursor.execute("INSERT INTO Sequentie_informatie VALUES ('{0}', '{1}', {2}, '{3}');".format(sequentie.getValue('kwaliteitsscore'), sequentie.getValue('sequentie'), sequentie.getValue('type'), sequentie.getValue('sequentie_id')))
            self.connection.commit()
            self.cursor.close()
        # Sluit de verbinding
        self.connection.close()
        
    def send_blast_results(self, type_blast, sequentie, parameters, blast_record, program_log):
        # Create_id's
        self.cursor.execute("SELECT max(Parameters_ID) FROM Resultaat")
        results = self.cursor.fetchall()
        self.cursor.close()
        if results[0][0] == None:
            parameters_id = 1   
        else:
            parameters_id = int(results[0][0])+1
        query_id = str(parameters_id)
        resultaat_id = parameters_id
        
        # Has_results
        has_results = 1
        for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                if hsp.num_alignments == 'None':
                    has_results = 0
        
        # Low_complexity en mask_lookup
        if (type_blast == 'blastn' and parameters.get(13) == 'True') or (type_blast == 'blastx' and parameters.get(18) == 'True') or (type_blast == 'tblastx' and parameters.get(24) == 'True'):
            low_complexity = 1
        else:
            low_complexity = 0
        if (type_blast == 'blastn' and parameters.get(14) == 'True') or (type_blast == 'blastx' and parameters.get(19) == 'True') or (type_blast == 'tblastx' and parameters.get(25) == 'True'):
            mask_lookup = 1
        else:
            mask_lookup = 0
            
        # Send parameters
        self.cursor = self.connection.cursor()
        if type_blast == 'blastn':
            self.cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', NULL, {2}, {3}, NULL, {4}, {5});""".format(type_blast, parameters.get(11), low_complexity, mask_lookup, parameters_id, resultaat_id))
        if type_blast == 'blastx':
            self.cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', '{2}', {3}, {4}, '{5}', {6}, {7});""".format(type_blast, parameters.get(15), parameters.get(16), low_complexity, mask_lookup, parameters.get(20), parameters_id, resultaat_id))
        if type_blast == 'tblastx':
            self.cursor.execute("""INSERT INTO Parameters VALUES ('{0}', '{1}', '{2}', {3}, {4}, NULL, {5}, {6});""".format(type_blast, parameters.get(21), parameters.get(22), low_complexity, mask_lookup, parameters_id, resultaat_id))
        
        # Send BLAST
        self.cursor.execute("""INSERT INTO Resultaat VALUES ('{0}', CURRENT_DATE(), CURRENT_TIME(), '{1}', {2}, {3}, {4});""".format(query_id, sequentie.getValue('sequentie_id'), resultaat_id , parameters_id, has_results))        
        
        # Send eiwitten
        for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                if hsp.expect < float(parameters.get(3)):
                    total_aligned = hsp.align_length
                    identity_perc = float(float(hsp.identities)/float(total_aligned))*100
                    positives_perc = float(float(hsp.positives)/float(total_aligned))*100
                    try:
                        organisme_eiwit_info = str(alignment.hit_def.encode('utf-8'))
                    except AttributeError:
                        organisme_eiwit_info = 'NULL'
                        print("Unicode object bij sequentie '{0}': 'organisme_eiwit_info'".format(sequentie.getValue('sequentie_id')))
                        program_log.write("Unicode object bij sequentie '{0}: 'organisme_eiwit_info'".format(sequentie.getValue('sequentie_id')))
                    try:
                        organisme_eiwit_ID = str(alignment.hit_id.encode('utf-8'))
                    except AttributeError:
                        organisme_eiwit_ID = 'NULL'
                        print("Unicode object bij sequentie '{0}': 'organisme_eiwit_ID'".format(sequentie.getValue('sequentie_id')))
                        program_log.write("Unicode object bij sequentie '{0}: 'eiwit_ID'".format(sequentie.getValue('sequentie_id')))
                    try:
                        organisme_eiwit_title = str(alignment.title.encode('utf-8'))
                        print("Unicode object bij sequentie '{0}': 'organisme_eiwit_title'".format(sequentie.getValue('sequentie_id')))
                        program_log.write("Unicode object bij sequentie '{0}: 'organisme_eiwit_title'".format(sequentie.getValue('sequentie_id')))
                    except AttributeError:
                        organisme_eiwit_title = 'NULL'
                    alignment = hsp.query+'\n'+hsp.match+'\n'+hsp.sbjct
                    if type_blast == 'blastn':
                        self.cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, NULL, '{9}', '{10}', '{11}', '{12}', {13});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
                    if type_blast == 'blastx':
                        self.cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, '{9}', '{10}', '{11}', '{12}', '{13}', {14});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, hsp.frame, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
                    if type_blast == 'tblastx':
                        self.cursor.execute("""INSERT INTO BLAST_resultaat__informatie VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, '{9}', '{10}', '{11}', '{12}', '{13}', {14});""".format(hsp.expect, hsp.bits, hsp.score, hsp.identities, hsp.positives, hsp.gaps, identity_perc, positives_perc, total_aligned, hsp.frame, organisme_eiwit_ID, organisme_eiwit_title, organisme_eiwit_info, alignment, resultaat_id))
        
        # Commit data en close verbinding
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        
def main():
    # Init objecten
    parameters = settings('Auto_BLAST_settings.settings')
    champignon_data = seq_data(parameters.get(0), parameters.get(1), parameters)
    operations = type_operation()
    program_log = log(parameters.get(2))
    
    # Zet de loop goed (om door te gaan als het programma stopte)
    champignon_data.set_loop(parameters.get(4))
    operations.set_loop(parameters.get(5))
    
    # Main loop
    for sequentie in champignon_data:
        for function in operations:
            try:
                sequentie_id = sequentie.getValue('sequentie_id')
                parameters.set_progress(champignon_data.get_progress()-1, function, sequentie_id)
                print(function+': '+sequentie_id)
                if function == 'save_sequentie':
                    db = database(parameters)
                    db.send_seq_data(sequentie)
                elif function in ['blastn', 'blastx', 'tblastx']:
                    NCBI = BLAST()
                    NCBI.do_blast(function, sequentie, parameters)
                    db = database(parameters)
                    db.send_blast_results(function, sequentie, parameters, NCBI.get_results(), program_log)
                program_log.write("{0} van sequentie '{1}' is gelukt!".format(function, sequentie_id))
            except Exception as error:
                print("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
                program_log.write("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
                print('30 seconden wachten tot nieuwe poging...')
                time.sleep(30)
                
main()
