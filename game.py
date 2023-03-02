import mysql.connector
import story
import rules
import random
from geopy.distance import geodesic

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
p_range = 1000 # start range in km = ?

# If all the necessary resources are found the boolean is True
if water == 1 and food == 1 and solar == 1 and medicine == 1:
    resources_found = True

# selects all airports for the game
def get_airports():
    sql = """ select name, ident, type, latitude_deg, longitude_deg from airport where ident = "KLAX" or ident = "KJFK" or ident = "KAUS" or ident = "KMSP" or ident = "KSEA"
            or ident = "KABQ" or ident = "KALN" or ident = "KBIL" or ident = "KBIS" or ident = "KCHO" or ident = "KCSG" or ident = "KGRI"
            or ident = "KLCH" or ident = "KPTK" or ident = "KPVU";"""
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# get all goals (ruoka, vesi, lääketarvikkeet, aurinkoenergia, ryöstäjä)
def get_goals():
    sql = "SELECT * from goal;"
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# get starting airport
def starting_airport():  # Huom hakee nimen ja identin
    sql = """ select name, ident from airport
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

    #Brings all the airports to the started game session
    goal_airports = a_ports.copy()
    random.shuffle(goal_airports)

    for i, goal_id in enumerate(goal_list):
        sql = "INSERT INTO ports (game, airport, goal) VALUES (%s, %s, %s);"
        cursor = yhteys.cursor(dictionary=True)
        cursor.execute(sql, (game_id, goal_airports[i]['ident'], goal_id))
    return game_id

# get airport info
def get_airport_info(ident): #TODO TOIMIIKO?
    sql = f'''SELECT iso_country, ident, name, latitude_deg, longitude_deg
                  FROM airport
                  WHERE ident = %s'''
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()
    return result

# Gets the coordinates from airport using Ident
def airport_coordinates(ident):
    sql = "SELECT latitude_deg, longitude_deg FROM airport "
    sql += "WHERE ident = '" + ident + "'"
    cursor = yhteys.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# Using two airport Idents calculates the distance in-between.
def distance_calculator(current_ident, destination_ident):
    distance = geodesic(airport_coordinates(current_ident), airport_coordinates(destination_ident))
    return distance

# get airports in range
def airports_in_range(current_ident, a_ports, range):      #Nää kaks funktioo vaikuttais toimivan mut en keksi järkevää tapaa legit checkata - aleksi
    in_range = []
    for a_port in a_ports:
        distance = distance_calculator(current_ident, a_port['ident'])
        if distance <= range and not distance == 0:
            in_range.append(a_port)
    return in_range

# Change that airport has been visited
def airport_visited(ident, game_id):
    sql = "UPDATE ports SET opened=true where airport ='" + str(ident) + "' and game =  '" + str(game_id) + "'"
    cursor = yhteys.cursor()
    cursor.execute(sql)
    return

# check if airport has a goal
def check_goal(game_id, location): # vähän sus mut salee ok
    sql = """SELECT ports.id, goal, goal.id as goal_id, name 
    FROM ports 
    JOIN goal ON goal.id = ports.goal 
    WHERE game = %s 
    AND airport = %s """
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (game_id, location))
    result = cursor.fetchone()
    if result is None:
        return False
    return result

# update location
def update_location(location,g_id):
    sql = f'''UPDATE game SET location = %s  WHERE id = %s'''
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (location, g_id))

# ask to show the story and rules
def get_story():
        for line in story.getStory():
            print(line)

def get_rules():
    for line in rules.getRules():
        print(line)

# game settings
p_name = input("Syötä nimesi: ")

#Get all airports
all_airports = get_airports()
airport_start = starting_airport()

# Player locations
current_ident = airport_start[1]
current_port = airport_start[0]

port_for_create = str(current_port[0])

# game id
game_id = create_game(current_port,p_name,p_range,all_airports)
print(check_goal(game_id, 'KJFK'))

#Pelin esittely
"""
print(f"Tervetuloa pelaamaan Last Of USA {p_name}!")
print(f"Olet paikassa: {current_port}! Ident koodisi on {current_ident}")

story_question = input("Haluatko tutustua pelin tarinaan ennen pelin aloittamista? (K/E): \n")
if story_question == "K" or story_question == "k":
    get_story()

rules_question = input("Haluatko tutustua pelin sääntöihin ennen pelin aloittamista? (K/E): \n")
if rules_question == "K" or rules_question == "k":
    get_rules()

print('Pääset tarkastelemaan kerättyjä resursseja tai sääntöjä kesken pelin syöttämällä konsoliin " ? " \n')
"""
"""
#Pääohjelman Loop alkaa
while p_day < 10:
    print(f"Päivä numero {p_day} lähtee nyt käyntiin, Sinulla on {10 - p_day} enään päivää aikaa etsiä tarvittavat resurssit ")
    print("Haluatko käyttää päiväsi tutkimalla:\n 1. Yhden ison lentokentän \n 2. Kaksi keskikokoista lentokenttää?")
    user_input = input(": ")

    if user_input == "1":
        print(all_airports) # 1 iso lentokenttä
    elif user_input == "2":
        print("2") # 2 medium kenttää

    elif user_input == "?":
        print("?") # ? -merkki antaa säännöt ja resurssit
    p_day += 1
    
"""