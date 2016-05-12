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

class data:
    def __init__(self, fwd_bestandnaam, rev_bestandnaam):
        self._data = []
        self.__readFile__(fwd_bestandnaam)
        self.__readFile__(rev_bestandnaam)
        
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
                    self._data.append(sequentie(sequentie_id, kwaliteitsscore, seq, type_seq))
            bestand.close()
            
    def getData(self):
        return self._data
        
def main():
    champignon_data = data('@HWI-M02942_file1.txt', '@HWI-M02942_file2.txt')
    champignon_data.getData()[0].summary()
    
main()
