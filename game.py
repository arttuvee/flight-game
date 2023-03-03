import mysql.connector
import story
import rules
import random
from geopy import distance

yhteys = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='last_of_usa',
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
p_range = 2000 # start range in km = ?

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
    sql = """ select name, ident, type, latitude_deg, longitude_deg from airport where ident = "KLAX" or ident = "KJFK" or ident = "KAUS" or ident = "KMSP" or ident = "KSEA"
            or ident = "KABQ" or ident = "KALN" or ident = "KBIL" or ident = "KBIS" or ident = "KCHO" or ident = "KCSG" or ident = "KGRI"
            or ident = "KLCH" or ident = "KPTK" or ident = "KPVU";"""
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result
def final_airport():
    sql = "SELECT name, ident FROM airport WHERE name = 'Key West International Airport'"
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

def check_airport_visited(ident, game_id): #TODO EI VALMIS / en osaa
    sql = "SELECT opened FROM ports where airport ='" + ident + "'and game = '" + game_id +"'"
    cursor = yhteys.cursor()
    result = cursor.execute(sql)
    if result == '1':
        return True
    else:
        return False

# check if airport has a goal
def check_goal(game_id, location): # TODO ei löydä goaleja nimellä esim. : Minneapolis–Saint Paul International Air. identillä löytää
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

# game settings
p_name = input("Syötä nimesi: ")

#Get all airports
all_airports = get_airports()
end_airport = final_airport()
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
while p_day < 10:
    # Creates a list with only large airports that have not been visited
    all_large_ports = [elem for elem in all_airports if elem.get('type') == 'large_airport'] #TODO Pitää keksiä tapa tarkastaa onko airport visited (huom se funktio)?
    # Creates a list with only medium airports that have not been visited
    all_medium_ports = [elem for elem in all_airports if elem.get('type') == 'medium_airport']

    # Airports in players range
    larges_in_range = airports_in_range(current_ident,all_large_ports,p_range)
    mediums_in_range = airports_in_range(current_ident,all_medium_ports,p_range)

    print(f"\nPäivä numero {p_day} lähtee nyt käyntiin, Sinulla on {10 - p_day} enään päivää aikaa etsiä tarvittavat resurssit ")
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

        # Update player locations
        current_port = get_airport_info(user_input)['name']
        current_ident = get_airport_info(user_input)['ident']
        update_location(current_port,game_id)

        port_goal = check_goal(game_id,current_ident)

        # Update database on visitation
        change_airport_visited(current_ident,game_id)

        p_range += 3000 # Emt heitin vaan jotain

        print(f"Matkustit kohteeseen: {current_port}")
        print(f"Latauksen jälkeen koneessasi on toimintamatkaa {p_range:.2f}km jäljellä.\n")

        # TODO Check goal
        # TODO en tiiä toimiiks tää nyt yhtään sillee kui tän pitäis
        # TODO kerro pelaajalle löytykö mitään ja rangen lisäys
        for i in range(120):
            print("=", end="")

    # Player is shown a list of medium airports he can explore
    elif user_input == "2":
        print("2")

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
            for i in range(120):
                print("=", end="")

        p_day -= 1 # So the player doesn't get punished for checking the rules / resources
    p_day += 1
#Pääohjelman loop loppuu