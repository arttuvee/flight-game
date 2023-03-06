import textwrap

story1 = "Ihmisen loputon kulutus on ajanut yhteiskunnan kriisin partaalle. Sosiaaliset rakenteet alkavat pettämään ja yhteiskuntarauha murtua. Olet muodostanut pienen yhteisön internetin välityksellä, jonka kesken suunnittelette pakenevan maasta 10 päivän kuluttua rauhalliseen kommuuniin.\n"
story2 = "\nKäytössä sinulla on pieni sähkölentokone, jota pystyt hyödyntämään matkustamiseen. Yhteiskuntaa ylläpitävä järjestelmä ei ole enään toimiva, joten joudut itse kerätä tarvittavat resurssin aikamääreen puitteissa ja tavata lopun ryhmästä Floridan Key Westissä."
story = story1 + story2

wrapper = textwrap.TextWrapper(width=130, break_long_words=True, replace_whitespace=False)
word_list = wrapper.wrap(text=story)

def getStory():
    return word_list