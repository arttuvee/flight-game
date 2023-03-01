import textwrap


rules = '''Tavoite:
Kerää tarvittavat resurssit ja tapaa loput ryhmästä aikamääreen puutteessa Floridan Key Westissä\n
Toiminnot:
Voit valita yhden ison tai kaksi keskikokoista lentokenttää tutkittavaksi per päivä\n
Lentäminen lentokenttien välillä vähentää jäljellä olevaa toimintamatkaa.
Toimintamatkaa on mahdollista kasvattaa lataamalla konetta isolla lentokentällä. Lataaminen ei vaadi pelaajalta lisätoimenpiteitä, pelkkä vierailu kentällä riittää ja toimintamatka päivittyy automaattisesti päivän loppuessa.\n
Ryöstön kohteeksi joutuminen johtaa lentokentältä poistumiseen tyhjin käsin.\n
Resurssien lukumäärä, toimintamatka ja jäljellä oleva aika päivittyy automaattisesti.\n
'''

wrapper = textwrap.TextWrapper(width=80, break_long_words=False, replace_whitespace=False)
word_list = wrapper.wrap(text=rules)

def getRules():
    return word_list