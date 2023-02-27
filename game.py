import mysql.connector
import story

yhteys = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='demogame',
    user='user1',
    password='sala1',
    autocommit=True)




# FUNCTIONS:

# select all airports for the game
def get_airports():
    sql = """ select name, ident, type from airport where ident = "KLAX" or ident = "KJFK" or ident = "KAUS" or ident = "KMSP" or ident = "KSEA"
            or ident = "KABQ" or ident = "KALN" or ident = "KBIL" or ident = "KBIS" or ident = "KCHO" or ident = "KCSG" or ident = "KGRI"
            or ident = "KLCH" or ident = "KPTK" or ident = "KPVU";"""
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# get all goals (ruoka, vesi, lääketarvikkeet, aurinkoenergia)
def get_goals():
    sql = "SELECT * from goal;"
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# get starting airport
def starting_airport():
    sql = """ select name from airport
    where iso_country = "US"
    and type = "small_airport"
    and longitude_deg > -125
    order by rand()
    limit 1;"""
    cursor = yhteys.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    for i in result:
        return i     #TODO emt vähän sus, joku vois visioida

# create new game

    # add goals / loot boxes

    # exclude starting airport

# get airport info

# check if airport has a goal

# calculate distance between two airports

# get airports in range

# set loot box opened

# update location

# ask to show the story and rules
def get_story():
        for line in story.getStory():
            print(line)

def get_rules():
    for line in rules.getRules():
        print(line)
# game settings

# start range in km = ?


# boolean for all resources found
resources_found = False

# all airports
# starting airport ident
# current airport

# game id

# game loop


#Pelin esittely
print("Tervetuloa pelaamaan Last Of USA!")

story_question = input("Haluatko tutustua pelin tarinaan ennen pelin aloittamista? K tai E: \n")
if story_question == "K" or story_question == "k":
    get_story()

rules_question = input("Haluatko tutustua pelin sääntöihin ennen pelin aloittamista? K tai E:\n")
if rules_question == "K" or rules_question == "k":
    get_rules()

p_name = input("Syötä nimesi: ")  # TODO Pelaajan nimi täällä
print(f"Tervetuloa {p_name}! aloitus lentokenttäsi on {starting_airport()}")   #TODO sijainti vihje?


#Pääohjelman Loop alkaa
#while game_running:

