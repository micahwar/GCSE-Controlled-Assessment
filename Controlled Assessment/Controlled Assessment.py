from csv import DictReader
from random import randint
from re import sub
import passhash, getpass, sqlite3, atexit

song_List = "chart2000-songmonth-0-3-0050.csv"
data_In = DictReader(open(song_List))
data = [row for row in data_In]
length = len(data) - 1

SQLite_Connection = sqlite3.connect("users.sqlite3")
SQLite_Cursor = SQLite_Connection.cursor()
fromDB = ()
def onExit():
   SQLite_Connection.close()
atexit.register(onExit)
registered = ""
while registered != "y" and registered != "n":
   registered = input("Are you registered? (Y/N): ").lower()
registered = (True if registered == "y" else False)
if registered:
   print("Starting login process...")
   while True:
      username = (input("Username: "),)
      password = getpass.getpass()
      SQLite_Cursor.execute('SELECT * FROM users WHERE username=?', username)
      fromDB = SQLite_Cursor.fetchone()
      if fromDB == None:
         print("Username not found")
         continue
      if not passhash.verify_password(fromDB[2], password):
         print("Incorrect Password")
         continue
      print("Correct Password!")
      break
else:
   print("Starting registration process...")
   while True:
      username = input("Username: ")
      SQLite_Cursor.execute('SELECT username FROM users WHERE username=?', (username,))
      if SQLite_Cursor.fetchone() != None:
         print("Username already in use.")
         continue
      password = getpass.getpass()
      SQLite_Cursor.execute('INSERT INTO users(username, passHash) VALUES (?, ?)', (username, passhash.hash_password(password)))
      SQLite_Connection.commit()
      break
SQLite_Cursor.execute('SELECT bestScore FROM users WHERE username=?', username)
bestScore = SQLite_Cursor.fetchone()[0]
print("You highscore is %s\n" % bestScore)
score = 0
playing = True
while playing:
   chosen_Data = data[randint(0, length)]
   output = ""
   output += chosen_Data["artist"] + "\n\t"
   output += "\t".join([word[0] for word in chosen_Data["song"].split()])
   print(output)
   for i in range(1, 3):
      user_Input = input("Enter name of Song: ")
      if sub(r'[^\w\s]','',user_Input.lower()) == sub(r'[^\w\s]','',chosen_Data["song"].lower()):
         if i == 1:
            score += 3
            print("+3")
            break
         elif i == 2:
            score += 1
            print("+1")
      else:
         if i == 2:
            print("Incorrect, Game Over!\n\nBetter luck next time!")
            print("Correct answer was '", chosen_Data["song"],"'\n")
            playing = False
         else:
            print("Incorrect, try again!")
   print("Total Score: " + str(score) + "\n")


SQLite_Cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username[0], score))
SQLite_Connection.commit()
SQLite_Cursor.execute('SELECT username, score FROM scores')
scores = SQLite_Cursor.fetchall()
leaderboard = list(reversed(sorted(scores, key=lambda score: score[1])))
top_five = [[str(y) for y in x] for x in leaderboard[0:5]]
top_five = [": ".join(x) for x in top_five]
print("Leaderboard:")
for lScore in top_five:
   print("\t" + lScore)
if score > bestScore:
   SQLite_Cursor.execute("UPDATE users SET bestScore=? WHERE username=?", (score, username[0]))
   SQLite_Connection.commit()
tmp = input("\nPRESS ENTER TO CONTINUE")
