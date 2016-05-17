"""

 Titel: Auto BLAST
 Beschijving: Automatisch BLASTen
 Bronnen: Geen
 Auteur: William Sies en Alex Staritsky
 Datum: Thu May 12 12:36:07 2016
 Versie: 1.4
 Updates: Zie github
 © Copyright
 
"""

class settings:
    def __init__(self, bestandnaam):
        self.settings = []
        with open(bestandnaam, 'r') as bestand:
            for regel in bestand:
                if regel[0] != '#' and regel != '':
                    self.settings.append(regel[regel.find(': ')+1:].replace('\n','').replace('\t','').replace(' ',''))            

    def get(self, setting):
        try:
            return self.settings[setting]
        except IndexError:
            raise Exception('Deze setting bestaat niet of is niet in het bestand opgenomen!')
            
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
        
def main():
    parameters = settings('Auto_BLAST_settings.settings')
    champignon_data = seq_data(parameters.get(0), parameters.get(1))
    for sequentie in champignon_data:
        print(sequentie.getValue('sequentie_id'))
    
main()
