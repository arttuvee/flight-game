import mysql.connector
import story
import rules
import random
from geopy import distance
import sys
from time import sleep
import time

yhteys = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='last_of_usa1',
    user='user1',
    password='sala1',
    autocommit=True)

# Resources that the player needs to manage
water = 0
food = 0
medicine = 0
solar = 0
resources_found = False

p_day = 1
p_range = 100000 # start range in km = ?

# If all the necessary resources are found the boolean is True
if water == 1 and food == 1 and solar == 1 and medicine == 1:
    resources_found = True

#Get the starting airport
def starting_airport():
    sql = """ select * from airport
    where iso_country = "US"
    and type = "small_airport"
    and longitude_deg > -125
    order by rand()
    limit 1;"""
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# selects all airports for the game
def get_airports():
    sql = """ select name, ident, type, latitude_deg, longitude_deg from airport where ident = "KLAX" or ident = "KJFK" or ident = "KAUS" or ident = "KMKE" or ident = "KSEA"
            or ident = "KABQ" or ident = "KALN" or ident = "KBIL" or ident = "KBIS" or ident = "KCHO" or ident = "KCSG" or ident = "KGRI"
            or ident = "KLCH" or ident = "KPTK" or ident = "KPVU";"""
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# Selects the final airport where the game ends
def final_airport():
    sql = "SELECT ident FROM airport WHERE name = 'Key West International Airport'"
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
def get_airport_info(ident):
    sql = f'''SELECT iso_country, ident, name, latitude_deg, longitude_deg
                  FROM airport
                  WHERE ident = %s'''
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()
    return result

# Using two airport Idents calculates the distance in-between.
def calculate_distance(current, target):
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km

# get airports in range
def airports_in_range(current_ident, a_ports, range):      #Nää kaks funktioo vaikuttais toimivan mut en keksi järkevää tapaa legit checkata - aleksi
    in_range = []
    for a_port in a_ports:
        distance = calculate_distance((current_ident), a_port['ident'])
        if distance <= range and not distance == 0:
            in_range.append(a_port)
    return in_range

# Change that airport has been visited
def change_airport_visited(ident, game_id):
    sql = "UPDATE ports SET opened=true where airport ='" + str(ident) + "' and game =  '" + str(game_id) + "'"
    cursor = yhteys.cursor()
    cursor.execute(sql)
    return
'''
def check_airport_visited(ident, game_id): #TODO EI VALMIS / en osaa
    sql = "SELECT opened FROM ports where airport ='" + ident + "'and game = '" + game_id +"'"
    cursor = yhteys.cursor()
    result = cursor.execute(sql)
    if result == '1':
        return True
    else:
        return False
'''

def check_airport_visited(ident, game_id):
    sql = "SELECT opened FROM ports where airport = %s and game = %s"
    cursor = yhteys.cursor()
    cursor.execute(sql, (ident, game_id))
    result = cursor.fetchone()
    for result in cursor:
        if result[0] == '1':
            return True
    return False

#removes ability to visit same airport twice
def get_unvisited_airports(game_id): #TODO Pushasin tän ny mut jos tätä ei haluu käyttää nii voi poistaa.
    sql = """
        SELECT airport.name, airport.ident, airport.type, airport.latitude_deg, airport.longitude_deg
        FROM airport
        LEFT JOIN ports ON airport.ident = ports.airport AND ports.game = %s
        WHERE airport.ident IN (
            'KLAX', 'KJFK', 'KAUS', 'KMSP', 'KSEA',
            'KABQ', 'KALN', 'KBIL', 'KBIS', 'KCHO', 'KCSG', 'KGRI',
            'KLCH', 'KPTK', 'KPVU'
        ) AND (ports.opened IS NULL OR ports.opened = '0')
    """
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (game_id,))
    result = cursor.fetchall()
    return result

    


# check if airport has a goal
def check_goal(game_id, location):
    sql = """SELECT ports.id, goal, goal.id as goal_id, name 
    FROM ports 
    JOIN goal ON goal.id = ports.goal 
    WHERE game = %s 
    AND airport = %s """
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (game_id, location))
    result = cursor.fetchall()
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

# Prints statements according to found goals or already acquired resources.
def goal_notifier(ports_goal):
    global food, water, medicine, solar
    if ports_goal[0]['name'] == "Ruoka":
        if food == 0:
            food += 1
            return print('Löysit tarvitsemasi ruokatarvikkeet!')
        else:
            return print("Löysit lisää ruokatarvikkeita, mutta sinulla on niitä jo tarpeeksi...")
    elif ports_goal[0]['name'] == "Vesi":
        if water == 0:
            water += 1
            return print('Löysit tarvitsemasi vedenpuhdistuslaitteen!')
        else:
            return print("Löysit uuden vedenpuhdistuslaitteen, vaikka nykyinen tilanteesi oli riittävä.")
    elif ports_goal[0]['name'] == "Lääketarvikkeet":
        if medicine == 0:
            medicine += 1
            return print('Löysit tarvitsemasi lääkintätarvikkeet!')
        else:
            return print("Löysit lisää lääkintätarvikkeita, vaikka nykyinen tilanteesi oli riittävä.")
    elif ports_goal[0]['name'] == "Aurinkoenergia":
        if solar == 0:
            solar += 1
            return print('Löysit tarvitsemasi aurinkokennot!')
        else:
            return print("Löysit toisen aurinkokennon, mutta et tarvitse toista...")
    elif ports_goal[0]['name'] == "Ryöstäjä":

        if random.randint(1,2) == 1:
            return print("Et löytänyt kentältä mitään ja joudut lähteä tyhjin käsin pois.")
        else:
            return print('Kohtasit ryöstäjän matkalla, mutta pääsit karkuun. Et valitettavasti kerennyt löytämään mitään')

# game settings
p_name = input("Syötä nimesi: ")

#Get all airports
all_airports = get_airports()
end_airport = final_airport()
end_ident = end_airport[0]['ident']
start_airport = starting_airport() # osa ongelmaa

# Player locations
current_port = start_airport[0]['name']
current_ident = start_airport[0]['ident']

# game id
port_for_create = str(current_port[0])
game_id = create_game(current_port,p_name,p_range,all_airports)

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

#Pääohjelman Loop alkaa
while p_day < 9:
    all_unvisited = get_unvisited_airports(game_id)
    # Creates a list with only large airports that have not been visited
    all_large_ports = [elem for elem in all_unvisited if elem.get('type') == 'large_airport']

    #TODO Pitää keksiä tapa tarkastaa onko airport visited (huom se funktio)?

    # Creates a list with only medium airports that have not been visited
    all_medium_ports = [elem for elem in all_unvisited if elem.get('type') == 'medium_airport']

    # Airports in players range

    larges_in_range = airports_in_range(current_ident,all_large_ports,p_range)
    mediums_in_range = airports_in_range(current_ident,all_medium_ports,p_range)

    # If player has no airports in their range they get stuck and fail the game.
    if len(larges_in_range) == 0 and len(mediums_in_range) == 0:
        print("Lentokoneesi toimintamatka ei riitä seuraavalle lentokentälle. Jäät nykyiseen sijaintiisi jumiin ja epäonnistut tehtävässäsi.")
        sys.exit()

    print(f"\nPäivä numero {p_day} lähtee nyt käyntiin, Sinulla on enään {10 - p_day} päivää aikaa etsiä tarvittavat resurssit ")
    print(f"Olet tällä hetkellä paikassa: {current_port}\n")
    print(f"Haluatko käyttää päiväsi tutkimalla:\n 1. Yhden ison lentokentän (Toimitamatkasi sisällä on: {len(larges_in_range)} kpl isoa lentokenttää) \n 2. Kaksi keskikokoista lentokenttää? (Toimitamatkasi sisällä on: {len(mediums_in_range)} kpl keskikokoista lentokenttää)\n")

    # User chooses how to spend the day
    user_input = input(": ")

    # Player is shown a list of large airports he can explore
    if user_input == "1":
        print("Kopioi lentokentän ICAO-Koodi konsoliin, jonka haluat tutkia.")
        for port in larges_in_range:
            print(f"    {port['name']}  ICAO-Koodi: {port['ident']}")

        # Player makes the choise to explore a specific airport
        user_input = input(": ")
        # Calculate distance and remove range
        travel = calculate_distance(current_ident,user_input)
        p_range = p_range - travel
        # Range increases due to charging the plane
        p_range += 3000

        # Update player locations
        current_port = get_airport_info(user_input)['name']
        print(f"Matkustit kohteeseen: {current_port}")
        current_ident = get_airport_info(user_input)['ident']
        update_location(current_port,game_id)

        # Checks the goal in the airport
        port_goal = check_goal(game_id,current_ident)
        # Notify the player on what they found
        found_goal = goal_notifier(port_goal)

        # Update database on visitation
        change_airport_visited(current_ident,game_id)
        print(f"Latasit lentokonetta etsintäsi ajan ja nyt sinulla on {p_range:.2f}km toimintamatkaa jäljellä.\n")

    # Player is shown a list of medium airports he can explore
    elif user_input == "2":
        print("Kopioi lentokentän ICAO-Koodi konsoliin, jonka haluat tutkia.")
        for port in mediums_in_range:
            print(f"    {port['name']}  ICAO-Koodi: {port['ident']}")

        # Player makes the choise to explore a specific airport
        user_input = input(": ")

        # Calculate distance and remove range
        travel = calculate_distance(current_ident, user_input)
        p_range = p_range - travel

        # Update player locations
        current_port = get_airport_info(user_input)['name']
        current_ident = get_airport_info(user_input)['ident']
        update_location(current_port, game_id)

        print(f"Matkustit kohteeseen: {current_port}")
        print(f"Lennon jälkeen koneessasi on {p_range:.2f} km toimintamatkaa jäljellä.\n")

        # Checks the goal in the airport
        port_goal = check_goal(game_id,current_ident)
        # Notify the player on what they found
        found_goal = goal_notifier(port_goal)

        # Update visitation on database
        change_airport_visited(current_ident, game_id)

        # Player chooses second airport to explore
        print("Kopioi lentokentän ICAO-Koodi konsoliin, jonka haluat tutkia seuraavaksi.")
        for port in mediums_in_range:
            print(f"    {port['name']}  ICAO-Koodi: {port['ident']}")

        # Player makes the choise to explore a specific airport
        user_input = input(": ")

        # Calculate distance and remove range
        travel = calculate_distance(current_ident, user_input)
        p_range = p_range - travel

        # Update player locations
        current_port = get_airport_info(user_input)['name']
        current_ident = get_airport_info(user_input)['ident']
        update_location(current_port, game_id)

        # Checks the goal in the airport
        port_goal = check_goal(game_id,current_ident)
        found_goal = goal_notifier(port_goal)

        # Update visitation on database
        change_airport_visited(current_ident, game_id)

        print(f"Matkustit kohteeseen: {current_port}")
        print(f"Lennon jälkeen koneessasi on {p_range:.2f} km toimintamatkaa jäljellä.\n")

    # Player chooses to view the rules and resources
    elif user_input == "?":
        print("Haluatko tarkastaa resurssisi? K/E")
        user_input = input(": ")

        # Player Wants to see resources they have gathered
        if user_input == "K" or user_input == "k":
            if resources_found == True:
                print("Sinulla on jo kaikki tarvitsemasi!")
            else:
                if water == 0:
                    print("Et ole löytänyt vedenpuhdistuslaitetta. Tarvitset sen.")
                else:
                    print("Sinulla on tarvitsemasi vedenpuhdistuslaite!")
                if food == 0:
                    print("Sinulla ei ole riittävästi ruokaa. Tarvitset lisää.")
                else:
                    print("Sinulla on riittävästi ruokaa")
                if medicine == 0:
                    print("Sinulla ei ole riittävästi lääkintätarvikkeita. Tarvitset lisää.")
                else:
                    print("Sinulla on riittävästi lääkintätarvikkeita")
                if solar == 0:
                    print("Sinulta puuttuu tarvitsemasi aurinkokennot. Tarvitset ne.")
                else:
                    print("Sinulla on tarvitsemasi aurinkokenno")

        # If player wants to see the rules they are printed for them.
        print("\nHaluatko nähdä pelin säännöt? K/E?")
        user_input = input(": ")
        if user_input == "K" or user_input == "k":
            get_rules()
        p_day -= 1 # So the player doesn't get punished for checking the rules / resources
    for i in range(120):
        print("=", end="")
    p_day += 1

# Day number 9 starts now. Last day is spent travelling to the destination - no looting.
# TODO visuaalinen ilme
print("\nYhdeksäs päivä lähti nyt käyntiin. Et kerkeä tutkia tänään uusia lentokenttiä. Koko päiväsi kuluu matkustamiseen.\n")
last_needed_distance = calculate_distance(current_ident,end_ident)

if p_range >= last_needed_distance:
    print("Lentokoneesi toimintamatka riittää Floridan Key Westiin saakka ja aloitat lentomatkan...\n")
    sleep(10)# Semmonen loading ..... juttu ois kova
    if resources_found == True:
        print("Saavut perille tarvittavien resurssien kanssa ja olet onnistunut tehtävässäsi")
    else:
        print("Saavut perille ilman tarvittavia resursseja. Olet epäonnistunut tehtävässäsi")
else:
    if resources_found == True:
        print("Vaikka löysit tarvittavat resurssit, ei toimintamatkasi riitä lentämään tapaamispaikkaan saakka. Olet epäonnistunut tehtävässäsi")
    else:
        print("Olet liian kaukana tapaamispaikasta etkä ole kerännyt tarvittavia resursseja. Olet epäonnistunut tehtävässäsi")

