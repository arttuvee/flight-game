import mysql.connector
import story
import random
from geopy import distance
import sys
from time import sleep

yhteys = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='last_of_usa',
    user='user1',
    password='sala1',
    autocommit=True)

# Color codes
red = '\33[91m'
green = '\33[92m'
white = '\33[0m'
blue = '\33[94m'
yellow = '\33[93m'

# Resources that the player needs to manage
water = 0
food = 0
medicine = 0
solar = 0
p_day = 1
p_range = 5000
resources_found = False

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
    sql = f'''SELECT * FROM airport
                  WHERE ident = %s'''
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()
    return result
# Using two airport Idents calculates the distance in-between.
def calculate_distance(current, destination):
    first = get_airport_info(current)
    second = get_airport_info(destination)
    return distance.distance((first['latitude_deg'], first['longitude_deg']), (second['latitude_deg'], second['longitude_deg'])).km
# get airports in range
def airports_in_range(current_ident, a_ports, range):
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
#removes ability to visit same airport twice
def get_unvisited_airports(game_id):
    sql = """
        SELECT airport.name, airport.ident, airport.type, airport.latitude_deg, airport.longitude_deg
        FROM airport
        LEFT JOIN ports ON airport.ident = ports.airport AND ports.game = %s
        WHERE airport.ident IN (
            'KLAX', 'KJFK', 'KAUS', 'KMKE', 'KSEA',
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
    sql = """SELECT ports.id,name FROM ports 
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
def get_story():
        for line in story.getStory():
            print(line)
def line_printer():
    line = ""
    for i in range(120):
        print("=", end="")
    return line
def get_rules():
    text = '''Tavoite: Kerää tarvittavat resurssit ja tapaa loput ryhmästä aikamääreen puutteessa Floridan Key Westissä.
    -Voit valita yhden ison tai kaksi keskikokoista lentokenttää tutkittavaksi per päivä.
    -Valittuasi kentän ohjelma simuloi etsimiseen kestävää aikaa noin muutaman sekunnin. Tämä ominaisuus ei vaadi pelaajalta toimenpiteitä
    -Lentäminen lentokenttien välillä vähentää jäljellä olevaa toimintamatkaa.
    -Toimintamatkaa on mahdollista kasvattaa lataamalla konetta isolla lentokentällä.
    -Lataaminen ei vaadi pelaajalta lisätoimenpiteitä, pelkkä vierailu kentällä riittää ja toimintamatka päivittyy automaattisesti päivän loppuessa.
    -Ryöstön kohteeksi joutuminen johtaa lentokentältä poistumiseen tyhjin käsin. 
    -Resurssien lukumäärä, toimintamatka ja jäljellä oleva aika päivittyy automaattisesti.
    -Voit tarkastella kerättyjen resurssien lukumäärää ja sääntöjä kesken pelin, syöttämällä konsoliin ? -merkin.'''
    return print(text)
# Prints statements according to found goals or already acquired resources.
def goal_notifier(ports_goal):
    global food, water, medicine, solar
    if ports_goal[0]['name'] == "Ruoka":
        if food == 0:
            food += 1
            return print(green + 'Löysit tarvitsemasi ruokatarvikkeet!' + white)
        else:
            return print(yellow + "Löysit lisää ruokatarvikkeita, mutta sinulla on niitä jo tarpeeksi..." + white)
    elif ports_goal[0]['name'] == "Vesi":
        if water == 0:
            water += 1
            return print(green + 'Löysit tarvitsemasi vedenpuhdistuslaitteen!' + white)
        else:
            return print(yellow + "Löysit toisen vedenpuhdistuslaitteen, mutta sinulla on niitä jo tarpeeksi..." + white)
    elif ports_goal[0]['name'] == "Lääketarvikkeet":
        if medicine == 0:
            medicine += 1
            return print(green + 'Löysit tarvitsemasi lääkintätarvikkeet!' + white)
        else:
            return print(yellow + "Löysit lisää lääkintätarvikkeita, vaikka sinulla on niitä jo tarpeeksi..." + white)
    elif ports_goal[0]['name'] == "Aurinkoenergia":
        if solar == 0:
            solar += 1
            return print(green + 'Löysit tarvitsemasi aurinkokennot!' + white)
        else:
            return print(yellow + "Löysit toisen aurinkokennon, mutta sinulla on niitä jo tarpeeksi..." + white)
    elif ports_goal[0]['name'] == "Ryöstäjä":
        if random.randint(1,2) == 1:
            return print(red + "Et löytänyt kentältä mitään ja joudut lähteä tyhjin käsin pois..." + white)
        else:
            return print(red + 'Kohtasit ryöstäjän matkalla, mutta pääsit karkuun. Et valitettavasti kerennyt löytämään mitään...' + white)

# Player name
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

# The player is introduced to the game
print("\033[1m" + "+--------------+" + "\033[0m")
print("\033[1m" + "| Last of USA! |" + "\033[0m")
print("\033[1m" + "+--------------+" + "\033[0m")
print(f"Tervetuloa pelaamaan {p_name}!")
#Starting dialogue
story_question = input("Haluatko tutustua pelin tarinaan ennen pelin aloittamista? (K/E): \n")
if story_question == "K" or story_question == "k":
    get_story()
    line_printer()
rules_question = input("\nHaluatko tutustua pelin sääntöihin ennen pelin aloittamista? (K/E): \n")
if rules_question == "K" or rules_question == "k":
    get_rules()
else:
    print("\033[1m" + "Pääset tarkastelemaan kerättyjä resursseja tai sääntöjä joka päivän alussa syöttämällä konsoliin ? -merkin" + "\033[0m")
line_printer()

#Main program loop begins
while p_day < 9:
    # Get all airports the player can visit
    all_unvisited = get_unvisited_airports(game_id)
    all_large_ports = [elem for elem in all_unvisited if elem.get('type') == 'large_airport']
    all_medium_ports = [elem for elem in all_unvisited if elem.get('type') == 'medium_airport']
    # Airports in players range
    larges_in_range = airports_in_range(current_ident, all_large_ports, p_range)
    mediums_in_range = airports_in_range(current_ident,all_medium_ports,p_range)

    # If player has no airports in their range they get stuck and fail the game.
    if len(larges_in_range) == 0 and len(mediums_in_range) == 0:
        print(red + "\nLentokoneesi toimintamatka ei riitä seuraavalle lentokentälle. Jäät nykyiseen sijaintiisi jumiin ja epäonnistut tehtävässäsi." + white)
        input("Paina mitä tahansa sulkeaksesi pelin: ")
        sys.exit()

    print("\033[1m" + f"\nPäivä numero {p_day} lähtee nyt käyntiin, Sinulla on enään {10 - p_day} päivää aikaa etsiä tarvittavat resurssit "+ "\033[0m")
    print(f"Olet tällä hetkellä paikassa: {current_port}\n")
    print(f"Haluatko käyttää päiväsi tutkimalla:\n 1. Yhden ison lentokentän (Toimitamatkasi sisällä on: {len(larges_in_range)} kpl isoa lentokenttää) \n 2. Kaksi keskikokoista lentokenttää? (Toimitamatkasi sisällä on: {len(mediums_in_range)} kpl keskikokoista lentokenttää)")

    # User chooses how to spend the day and input is checked.
    user_input = input(": ")
    while user_input != "1" and user_input != "2" and user_input != "?":
        user_input = input("Tarkista syöte: ")
    # Player is shown a list of large airports he can explore
    if user_input == "1":
        print("\nKopioi lentokentän ICAO-Koodi konsoliin, jonka haluat tutkia.")
        for port in larges_in_range:
            print(f"    {port['name']}  ICAO-Koodi: {port['ident']}")

        # Player makes the choice to explore a specific airport
        user_input = input(": ").upper()
        while user_input not in [port['ident'] for port in larges_in_range]:
            print("Syötä toimiva ICAO-koodi!")
            user_input = input(":").upper()
        # Calculate distance and remove range accordingly
        travel = calculate_distance(current_ident, user_input)
        p_range = p_range - travel
        # Range increases due to charging the plane
        p_range += 3000
        # Update player locations
        current_port = get_airport_info(user_input)['name']
        current_ident = get_airport_info(user_input)['ident']
        update_location(current_port,game_id)

        print(f"Matkustat kohteeseen: {current_port} ja alat tutkimaan lentokenttää...")
        sleep(3)

        # Checks the goal in the airport
        port_goal = check_goal(game_id,current_ident)
        # Notify the player on what they found
        goal_notifier(port_goal)
        # Update database on visitation
        change_airport_visited(current_ident,game_id)

        print(f"Latasit lentokonetta etsintäsi ajan ja nyt sinulla on {blue}{p_range:.2f}km{white} toimintamatkaa jäljellä.\n")
        line_printer()

    # If the player chooses to explore two airports, they are shown a list of medium airports.
    elif user_input == "2":
        print("Kopioi lentokentän ICAO-Koodi konsoliin, jonka haluat tutkia.")
        for port in mediums_in_range:
            print(f"    {port['name']}  ICAO-Koodi: {port['ident']}")

        # Player makes the choise to explore a specific airport
        user_input = input(": ").upper()
        while user_input not in [port['ident'] for port in mediums_in_range]:
            print("Syötä toimiva ICAO-koodi!")
            user_input = input(": ").upper()
        # Calculate distance and remove range
        travel = calculate_distance(current_ident, user_input)
        p_range = p_range - travel

        # Update player locations
        current_port = get_airport_info(user_input)['name']
        current_ident = get_airport_info(user_input)['ident']
        update_location(current_port, game_id)
        # Checks the goal in the airport
        port_goal = check_goal(game_id,current_ident)

        print(f"Matkustat kohteeseen: {current_port} ja alat tutkimaan lentokenttää...")
        sleep(2)
        # Notify the player on what they found
        goal_notifier(port_goal)

        print(f"Lennon jälkeen koneessasi on {blue}{p_range:.2f}km{white} toimintamatkaa jäljellä.\n")
        # Update visitation on database
        change_airport_visited(current_ident, game_id)

        #Check if there is a second airport in-range
        mediums_in_range = airports_in_range(current_ident, all_medium_ports, p_range)
        if len(mediums_in_range) == 0:
            print(red + "\nLentokoneesi toimintamatka ei riitä seuraavalle lentokentälle. Jäät nykyiseen sijaintiisi jumiin ja epäonnistut tehtävässäsi." + white)
            input("Paina mitä tahansa sulkeaksesi pelin: ")
            sys.exit()

        # If there is airports in range, the player chooses one.
        print('''Kerkeät tutkia tänään vielä toisen lentokentän!
Kopioi lentokentän ICAO-Koodi konsoliin, jonka haluat tutkia seuraavaksi.\n''')
        for port in mediums_in_range:
            print(f"    {port['name']}  ICAO-Koodi: {port['ident']}")
        # Player makes the choise to explore a specific airport
        user_input = input(": ").upper()
        while user_input not in [port['ident'] for port in mediums_in_range]:
            print("Syötä toimiva ICAO-koodi!")
            user_input = input(":").upper()
        # Calculate distance and remove range
        travel = calculate_distance(current_ident, user_input)
        p_range = p_range - travel
        # Update player locations
        current_port = get_airport_info(user_input)['name']
        current_ident = get_airport_info(user_input)['ident']
        update_location(current_port, game_id)
        # Checks the goal in the airport
        port_goal = check_goal(game_id, current_ident)
        # Update visitation on database
        change_airport_visited(current_ident, game_id)

        print(f"Matkustat kohteeseen: {current_port} ja alat tutkimaan lentokenttää...")
        sleep(2)
        goal_notifier(port_goal)
        print(f"Lennon jälkeen koneessasi on {blue}{p_range:.2f}km{white} toimintamatkaa jäljellä.\n")

        if water == 1 and food == 1 and solar == 1 and medicine == 1:
            resources_found = True
        line_printer()

    # Player chooses to view the rules and resources
    elif user_input == "?":
        print("Haluatko tarkastaa resurssisi? K/E")
        user_input = input(": ")
        # Player Wants to see resources they have gathered
        if user_input == "K" or user_input == "k":
            if resources_found == True:
                print(green + "Olet löytänyt jo kaikki resurssit!" + white)
            else:
                if water == 0:
                    print(red + "Et ole löytänyt vedenpuhdistuslaitetta. Tarvitset sen." + white)
                else:
                    print(green + "Sinulla on tarvitsemasi vedenpuhdistuslaite!" + white)
                if food == 0:
                    print(red + "Sinulla ei ole riittävästi ruokaa. Tarvitset lisää." + white)
                else:
                    print(green + "Sinulla on riittävästi ruokaa" + white)
                if medicine == 0:
                    print(red + "Sinulla ei ole riittävästi lääkintätarvikkeita. Tarvitset lisää." + white)
                else:
                    print(green + "Sinulla on riittävästi lääkintätarvikkeita" + white)
                if solar == 0:
                    print(red + "Sinulta puuttuu tarvitsemasi aurinkokennot. Tarvitset ne." + white)
                else:
                    print(green + "Sinulla on tarvitsemasi aurinkokenno" + white)

        # If player wants to see the rules they are printed for them.
        print("\nHaluatko nähdä pelin säännöt? K/E?")
        user_input = input(": ")
        if user_input == "K" or user_input == "k":
            get_rules()
        p_day -= 1 # So the player doesn't get punished for checking the rules / resources
        line_printer()

    # Distance to end point.
    last_needed_distance = calculate_distance(current_ident, end_ident)
    # Check if the player has found all needed resources during the day
    if water == 1 and food == 1 and solar == 1 and medicine == 1:
        resources_found = True
        # The player is given the choice to end the game, if they have all the necessary resources and enough range left
        print("\033[1m" + "\nOlet löytänyt kaikki tarvittavat resurssit. Voit aloittaa matkan kohti Key Westiä "+ "\033[0m")
        if p_range >= last_needed_distance:
            print("Sinulla riittää toimintamatka Key Westiin saakka. Haluatko matkustaa sinne nyt? K/E")
            sus = input(": ")
            if sus == "K" or sus == "k":
                print("Aloitat matkasi Floridaan...")
                sleep(3)
                print(green + "Saavut perille tarvittavien resurssien kanssa ja olet onnistunut tehtävässäsi" + white)
                input("Paina mitä tahansa sulkeaksesi pelin: ")
                sys.exit()
    p_day += 1

# Day number 9 starts now. Last day is spent travelling to the destination - no looting.
line_printer()
print("\033[1m" + "\nAamu sarastaa ja viimeinen päiväsi lähtee käyntiin, Joudut käyttämään koko päivän matkustamiseen, jotta kerkeät tapaamispaikalle ajoissa. Et siis pysty tutkia tänään uutta lentokenttää.\n"+ "\033[0m")
user_input = input("Paina Enter jatkaaksesi: ")
# Different scenarios if the player has enough range left. They automatically start the journey to Florida.
if p_range >= last_needed_distance:
    print(green + "Lentokoneesi toimintamatka riittää Floridan Key Westiin saakka ja aloitat lentomatkan..." + white)
    sleep(3)
    if resources_found == True:
        print(green + "Saavut perille tarvittavien resurssien kanssa ja olet onnistunut tehtävässäsi" + white)
    else:
        print(red + "Saavut ryhmäsi luokse Floridaan ilman tarvittavia resursseja. Olet epäonnistunut tehtävässäsi" + white)
# Different scenarios if the player doesn't have enough range left.
else:
    if resources_found == True:
        print(red + "Vaikka löysit tarvittavat resurssit, ei toimintamatkasi riitä lentämään tapaamispaikkaan saakka. Olet epäonnistunut tehtävässäsi" + white)
    else:
        print(red + "Olet liian kaukana tapaamispaikasta etkä ole kerännyt tarvittavia resursseja. Olet epäonnistunut tehtävässäsi" + white)

# Gives the player a change to reflect on their game / Doesn't exit the program straight away.
input("Paina mitä tahansa sulkeaksesi pelin: ")
