import mysql.connector
import story
import rules
import random

yhteys = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='last_of_usa',
    user='user1',
    password='sala1',
    autocommit=True)

# Resources that the player needs to manage
food = 0
water = 0
solar = 0
medicine = 0
resources_found = False

p_day = 1
p_range = 0 # start range in km = ?

# selects all airports for the game
def get_airports():
    sql = """ select name, ident, type, latitude_deg, longitude_deg from airport where ident = "KLAX" or ident = "KJFK" or ident = "KAUS" or ident = "KMSP" or ident = "KSEA"
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
    result = cursor.fetchall()
    for i in result:
        return i  #TODO emt vähän sus, joku vois visioida.

# create new game
def create_game(location, screen_name, player_range, a_ports):
    #Inserts the values to the new game session
    sql = " INSERT INTO game (location, screen_name, player_range) VALUES (%s, %s, %s);"
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (location, screen_name, player_range))
    game_id = cursor.lastrowid

    goals = get_goals()
    goal_list = []
    for goal in goals:
        for i in range(0, goal["probability"], 1):
            goal_list.append(goal["id"])


    # exclude starting airport

    #Brings all the airports to the started game session
    goal_airports = a_ports.copy()
    random.shuffle(goal_airports)

    for airport in goal_airports:
        goal_id = random.choices(goal_list)[0]
        sql = "INSERT INTO ports (game, airport, goal) VALUES (%s, %s, %s);"
        cursor = yhteys.cursor(dictionary=True)
        cursor.execute(sql, (game_id, airport["ident"], goal_id))

    yhteys.commit()

    return game_id

                                                           #TODO kaikki resurssit menee samalle kentälle.. ei salee mee nyt enää -j

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

# If all the necessary resources are found the boolean is True
if water == 5 and food == 5 and solar == 1 and medicine == 1: #Päätetään määrät myöhemmin
    resources_found = True

# starting airport ident

# current airport

# game id


#Pelin esittely
"""
print("Tervetuloa pelaamaan Last Of USA!")

story_question = input("Haluatko tutustua pelin tarinaan ennen pelin aloittamista? K tai E: \n")
if story_question == "K" or story_question == "k":
    get_story()

rules_question = input("Haluatko tutustua pelin sääntöihin ennen pelin aloittamista? K tai E:\n")
if rules_question == "K" or rules_question == "k":
    get_rules()

print('Pääset tarkastelemaan kerättyjä resursseja tai sääntöjä kesken pelin syöttämällä konsoliin " ? " \n')
"""

p_name = input("Syötä nimesi: ")   #Pelaajan nimi täällä

all_airports = get_airports()
airport_start = str(starting_airport()[0])
current_airport = airport_start


create_game(airport_start, p_name, p_range, all_airports) # Tietokantaan luodaan uusi peli. // Range on viel 0 mut se varmaan sovitaan sit myöhemmin et paljon se on alussa.
print(f"Tervetuloa {p_name}! aloitus lentokenttäsi on {airport_start}\n")   # sijainti vihje?

"""
#Pääohjelman Loop alkaa
while p_day < 10:
    print(f"Päivä numero {p_day} lähtee nyt käyntiin, Sinulla on {10 - p_day} enään päivää aikaa etsiä tarvittavat resurssit ")
    print("Haluatko käyttää päiväsi tutkimalla:\n 1. Yhden ison lentokentän \n 2. Kaksi keskikokoista lentokenttää?")
    user_input = input(": ")

    if user_input == "1":
        print("1") # 1 iso lentokenttä
    elif user_input == "2":
        print("2") # 2 medium kenttää
        exit()   #TODO katkasee ikuisen loopin, pitää poistaa myöhemmin
    elif user_input == "?":
        print("?") # ? -merkki antaa säännöt ja resurssit
"""