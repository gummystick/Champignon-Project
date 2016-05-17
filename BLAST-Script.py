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
import time

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
    
    def set_progress(self, proces_number, sequentie_id):
        with open(self.bestandnaam, 'r') as bestand:
            settings = bestand.readlines()
            bestand.close()
        with open(self.bestandnaam, 'w') as bestand:
            settings[7] = '	proces_number: {0}\n'.format(str(proces_number))
            settings[8] = '	sequence_id: {0}\n'.format(str(sequentie_id))
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
        
def main():
    parameters = settings('Auto_BLAST_settings.settings')
    champignon_data = seq_data(parameters.get(0), parameters.get(1))
    program_log = log(parameters.get(2))  
    
    champignon_data.set_loop(parameters.get(4))
    for sequentie in champignon_data:
        for type_blast in ['blastn', 'blastx', 'tblastx']:
            try:
                sequentie_id = sequentie.getValue('sequentie_id')
                if type_blast == 'blastn':
                    #blastn
                    print('Blastn:',sequentie_id)
                    blastn = None
                    program_log.write("blastn van sequentie '{0}' is gelukt!".format(sequentie_id))
                elif type_blast == 'blastx':
                    #blastx
                    print('Blastx:',sequentie_id)
                    blastx = None
                    program_log.write("blastx van sequentie '{0}' is gelukt!".format(sequentie_id))
                elif type_blast == 'tblastx':
                    #tblastx
                    print('Tblastx:',sequentie_id)
                    tblastx = None
                    program_log.write("tblastx van sequentie '{0}' is gelukt!".format(sequentie_id))
            except Exception as error:
                program_log.write("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
                print("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
        try:
            #save data to database
            print('Saving:',sequentie_id)
            database = None
        except Exception as error:
            program_log.write("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
            print("Error bij sequentie '{0}': '{1}'".format(sequentie_id, error))
        parameters.set_progress(champignon_data.get_progress(), sequentie_id)

main()
