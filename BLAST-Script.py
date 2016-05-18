"""

 Titel: Auto BLAST
 Beschijving: Automatisch BLASTen
 Bronnen: Geen
 Auteur: William Sies en Alex Staritsky
 Datum: Thu May 12 12:36:07 2016
 Versie: 2.0
 Updates: Zie github
 © Copyright
 
"""

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import Bio
import time
import mysql.connector

class settings:
    def __init__(self, bestandnaam):
        self.settings = []
        self.bestandnaam = bestandnaam
        with open(self.bestandnaam, 'r') as bestand:
            for regel in bestand:
                if regel[0] != '#' and regel.replace('\n','').replace('\t','').replace(' ','') != '':
                    self.settings.append(regel[regel.find(': ')+1:].replace('\n','').replace('\t','').replace(' ',''))            

    def get(self, setting):
        try:
            return self.settings[setting]
        except IndexError:
            raise Exception('Deze setting bestaat niet of is niet in het bestand opgenomen!')
    
    def set_progress(self, proces_number, function, sequentie_id):
        with open(self.bestandnaam, 'r') as bestand:
            settings = bestand.readlines()
            bestand.close()
        with open(self.bestandnaam, 'w') as bestand:
            settings[7] = '	proces_number: {0}\n'.format(str(proces_number))
            settings[8] = '	function: {0}\n'.format(str(function))
            settings[9] = '	sequence_id: {0}\n'.format(str(sequentie_id))
            bestand.writelines(settings)
            bestand.close()

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
        with open(self.bestandnaam, 'a') as bestand:
            bestand.write('\n{0} | {1} | {2}'.format(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"),str(info)))
            bestand.close()
        
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
    def __init__(self, fwd_bestandnaam, rev_bestandnaam):
        self.data = []
        self.index = 0
        self.__readFile__(fwd_bestandnaam)
        self.__readFile__(rev_bestandnaam)
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index == len(self.data):
            raise StopIteration
        index = self.index
        self.index += 1
        return self.data[index]
        
    def __readFile__(self, bestandnaam):
        with open(bestandnaam, 'r') as bestand:
            regelnummer = -1
            for regel in bestand:
                regelnummer += 1
                if regelnummer > 3:
                    regelnummer = 0
                if regelnummer == 0:
                    sequentie_id = regel[1:regel.find('/')]
                    type_seq = regel[-2]
                if regelnummer == 1:
                    seq = regel
                if regelnummer == 3:
                    kwaliteitsscore = regel
                    self.data.append(sequentie(sequentie_id, kwaliteitsscore, seq, type_seq))
            bestand.close()
            
    def set_loop(self, proces_number):
        self.index = int(proces_number)
    
    def get_progress(self):
        return self.index

class type_operation:
    def __init__(self):
        self.operations = ['blastn', 'blastx', 'tblastx', 'save_data']
        self.index = 0
        self.resume = False
        
    def __iter__(self):
        if self.resume == False:
            self.index = 0
        return self
        
    def __next__(self):
        if self.index == len(self.operations):
            if self.resume:
                self.resume = False
            raise StopIteration
        index = self.index
        self.index += 1
        return self.operations[index]
        
    def set_loop(self, index):
        self.resume = True
        if index == 'blastn':
            self.index = 0
        elif index == 'blastx':
            self.index = 1
        elif index == 'tblastx':
            self.index = 2
        elif index == 'save_data':
            self.index = 3
        else:
            raise ValueError('Geen of een verkeerde value opgevraagd!')

class Blast_data:
    def __init__(self, bestand_data):
        self.bestand_data = bestand_data
        
    def Blast(self):
        program = None
        database = None
        sequence = None
        print(self.bestand_data)
        for seq in self.bestand_data:
            record_handle = NCBIWWW.qblast(program, database, sequence, expect='', gapcosts='', matrix_name='')
        return

#SQL connector juiste instellingen vanaf de server geen last van firewall.
def datasearch():
	conn = mysql.connector.connect(host="localhost", user="owe4_bi1e_2", db="owe4_bi1e_2", password='blaat1234')
	cursor = conn.cursor()
	cursor.execute ("""INSERT INTO `BLAST_resultaat__informatie`(`E_value`, `Bit_score`, `Score`, `Identity`, `Gaps`, `Query_coverage`, `Identity_percentage`, `Max_Score`, `Total_Score`, `Frame`, `Organisme`, `Eiwit`) 
	VALUES (0.0001,273,200,50,2,75,99,274,234,-2,'Homo_sapien','Protje')""")
	#row = cursor.fetchall ()
	conn.commit()
	cursor.close ()
	conn.close()
	print("Query executed")
	#print(row)
	return #row
        
def main():
    # Init objecten
    parameters = settings('Auto_BLAST_settings.settings')
    champignon_data = seq_data(parameters.get(0), parameters.get(1))
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
                print(function+': '+sequentie_id)
                parameters.set_progress(champignon_data.get_progress(), function, sequentie_id)
                if function == 'blastn':
                    # blastn
                    blastn = None
                elif function == 'blastx':
                    # blastx
                    blastx = None
                elif function == 'tblastx':
                    # tblastx
                    tblastx = None
                elif function == 'save_data':
                    # save_data
                    database = None
                program_log.write("{0} van sequentie '{1}' is gelukt!".format(function, sequentie_id))
            except Exception as error:
                print("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
                program_log.write("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))

main()
