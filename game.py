import mysql.connector
import story

yhteys = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='demogame',
    user='user1',
    password='sala1',
    autocommit=True)



storyDialog = input('Paina Enter lukeaksesi pelin taustatarina: ')
if storyDialog == "":
    for line in story.getStory():
        print(line)


