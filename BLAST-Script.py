"""
 Titel: Auto BLAST
 Beschijving: Automatisch BLASTen
 Bronnen: Geen
 Auteur: William Sies en Alex Staritsky
 Datum: Thu May 12 12:36:07 2016
 Versie: 1.2
 Updates: Geen
 © Copyright
 
"""
import Bio
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import mysql.connector

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
    
    def summary(self):
        print('Sequentie_ID =', self._sequentie_id)
        print('Kwaliteitsscore =', self._kwaliteits_score)
        print('Sequentie =', self._sequentie)
        print('Type =', self._type)

class seq_data:
    def __init__(self, fwd_bestandnaam, rev_bestandnaam):
        self.data = []
        self.__readFile__(fwd_bestandnaam)
        self.__readFile__(rev_bestandnaam)
        
    def __iter__(self):
        self.index = 0
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
            
    def getData(self):
        return self.data
    
class Blast_data:
    def __init__(self, bestand_data):
        self.bestand_data = bestand_data
        
    def Blast(self):
        program
        database
        sequence
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
    bestand_data = seq_data('@HWI-M02942_file1.txt', '@HWI-M02942_file2.txt')
    d = Blast_data(bestand_data)
    d.check()
    data = datasearch()
    
main()
