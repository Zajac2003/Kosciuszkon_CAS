import sqlite3
import PySimpleGUI as sg
import datetime
import matplotlib.pyplot as plt
import numpy as np
from plyer import notification


def create_window(zakladka, searched_id=1, activityid=0):
    # Definiujemy układ graficzny okna, zależne od 'zakladka'
    # zakladka menu
    if zakladka == 'menu':
        ####################
        db = sqlite3.connect("LIFTMATE_DATABASE.db")
        cursor = db.cursor()

        cursor.execute('SELECT * from activity')
        result = cursor.fetchall()

        total_distance = 0
        total_burnt_calorie = 0
        counter = 0

        for wiersz in result:
            total_distance += wiersz[4]
            counter += 1

        total_distance = round(total_distance)
        total_burnt_calorie = round(total_distance * 60)
        ############
        db.commit()
        db.close()
        y = np.array([35, 25, 25, 15])
        mylabels = ["Strength", "Endurance", "Speed", "Agility"]

        plt.pie(y,labels=mylabels, textprops={'color':"#FFFF00", 'size' : 'xx-large'}, autopct="%i")
        plt.savefig("Stat_Chart", dpi=40, format=None, transparent=True)

        sg.theme('DarkAmber')
        layout = [
            [sg.MenuBar([["=", ["Opcja1", "Opcja2"]]])],
            [sg.Image(filename="Stat_Chart.png")],
            [sg.Text("Total burnt calories today " + str(total_burnt_calorie))],
            [sg.Text("Total km travelled " + str(total_distance) + "km")],
            [sg.Text("Trainings today " + str(counter))],
            [sg.Text()],
            [sg.Image(filename="add_icon.png", enable_events=True, key="-post_add-"), sg.Push(), sg.Image(filename="fight_icon.png", enable_events=True, key="-fightButton-"), sg.Push(), sg.Image(filename="post_lookup_icon.png", enable_events=True, key="-post_lookup-"), sg.Push(),sg.Image(filename="search_icon.png", enable_events=True, key="-search-")],
        ]

        window = sg.Window("LIFTMATE", layout, size=(300, 420))
        window.set_icon("icon.ico")
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'OK':
                break
            elif event == '-fight_window-':
                window.close()
                window = create_window("fight_window")
            elif event == '-post_lookup-':
                window.close()
                window = create_window("post_lookup")
            elif event == "-post_add-":
                window.close()
                window = create_window("post_add")
            elif event == "-search-":
                window.close()
                window = create_window("search")
            elif event == '-fightButton-':
                window.close()
                window = create_window("fight_window")
        window.close()

    #zakładka walki
    elif zakladka == "fight_window":
        sg.theme('DarkAmber')
####################
        db = sqlite3.connect("LIFTMATE_DATABASE.db")
        cursor = db.cursor()

        cursor.execute('SELECT stat_strength, stat_endurance, stat_speed, stat_agility from accounts')
        result = cursor.fetchall()

        my_moc = 0
        enemy_moc = 0
        i=0
        for moc in result:
            if i==0:
                my_moc = int(moc[0]) + int(moc[1])+ int(moc[2])+ int(moc[3])
            if i==1:
                enemy_moc = int(moc[0]) + int(moc[1]) + int(moc[2]) + int(moc[3])
            i+=1

        db.commit()
        db.close()

        layout = [
            [sg.Text("Twoja moc: " + str(my_moc)), sg.MenuBar([["=", ["Opcja1", "Opcja2"]]])],
            [sg.Text("Moc przeciwnika: " + str(enemy_moc))],
            [sg.Button("Fight!", key='-FIGHT-'), sg.Button("Back", key='-cancel-')],
        ]

        window = sg.Window("FITMATE/SEARCH", layout)
        window.set_icon("icon.ico")
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'OK':
                break
            elif event == "-cancel-":
                window.close()
                window = create_window("menu")
            if event == '-FIGHT-':
                window.close()
                if( my_moc > enemy_moc):
                    window = create_window("lost")
                elif (my_moc <= enemy_moc):
                    window = create_window("won")
    
    #zakladka, ktora pojawia sie, gdy klikniemy "dodaj post" (po lewej)
    elif zakladka == "post_add":
        sg.theme('DarkAmber')
        layout = [
            [sg.Spin(["Run", "Gym", "Dancing", "Swimming"]), sg.MenuBar([["=", ["Opcja1", "Opcja2"]]])],
            [sg.Input("distance or time ", key='distanceortime')],
            [sg.Button("Share", key='-Share-'), sg.Push(), sg.Button("Cancel", key='-cancel-')]
        ]

        window = sg.Window("LIFTMATE/POST_ADD", layout)
        window.set_icon("icon.ico")
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'OK':
                break
            elif event == "-cancel-":
                window.close()
                window = create_window("menu")
            elif event == '-Share-':
                db = sqlite3.connect("LIFTMATE_DATABASE.db")
                cursor = db.cursor()
                activity = values[0]

                czasdata = datetime.datetime.now()
                czasdata = str(czasdata)
                czasdata = czasdata[0:10]

                notification.notify(
                    title = 'Post created',
                    message = 'Post created successfully',
                    app_icon = "icon.ico",
                    timeout = 2,
                )
                print(values['distanceortime'])
                if activity == "Run" or activity == "Swimming" or activity == "Dancing":
                    dystans = values['distanceortime']
                    czas = 0
                    punkty = int(dystans) / 2

                else:
                    dystans = 0
                    czas = values['distanceortime']
                    print("EEOEO")
                    print(int(czas))
                    punkty = int(czas)/20

                cursor.execute(
                    "INSERT INTO activity (id, data, type_of_activity, distance, time) VALUES (0, ?, ?, ?, ?)",
                    (czasdata, activity, dystans, czas))
                db.commit()
                db.close()

                db = sqlite3.connect("LIFTMATE_DATABASE.db")
                cursor = db.cursor()
                ########DODAWANIE PUNKTÓW
                if activity == "Run" or activity == "Swimming" or activity == "Dancing":
                    cursor.execute('UPDATE accounts SET stat_endurance = stat_endurance + ? WHERE account_id = ?',(punkty, 0))
                    cursor.execute('UPDATE accounts SET stat_speed = stat_speed + ? WHERE account_id = ?',(punkty, 0))
                    cursor.execute('UPDATE accounts SET stat_agility = stat_agility + ? WHERE account_id = ?',(punkty, 0))
                else:
                    cursor.execute('UPDATE accounts SET stat_strength = stat_strength + ? WHERE account_id = ?', (punkty, 0))
                    cursor.execute('UPDATE accounts SET stat_endurance = stat_endurance + ? WHERE account_id = ?', (punkty, 0))

                db.commit()
                db.close()

                window.close()
                window = create_window("menu")

    # zakladka, ktora pojawia sie, gdy klikniemy "search" (po prawej)
    elif zakladka == "search":
        sg.theme('DarkAmber')
        layout = [
            [sg.Text("Wyszukiwanie użytkownika", key='nick'), sg.MenuBar([["=", ["Opcja1", "Opcja2"]]])],
            [sg.Input("tu")],
            [sg.Button("Find", key="-find-"), sg.Push(), sg.Button("Cancel", key='-cancel-')]
        ]

        window = sg.Window("FITMATE/SEARCH", layout)
        window.set_icon("icon.ico")
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'OK':
                break
            elif event == "-cancel-":
                window.close()
                window = create_window("menu")
            elif event == "-find-":
                db = sqlite3.connect("LIFTMATE_DATABASE.db")
                cursor = db.cursor()
                nick_input = values[1]

                str3 = 'cursor.execute("SELECT account_id FROM accounts where nick='
                str3 += "'" + nick_input + "'"
                str3 += '")'
                eval(str3)
                #cursor.execute('SELECT * FROM accounts where nick="Zajonc"')
                result = cursor.fetchall()
                db.commit()
                db.close()
                if len(result) == 0:
                    window.close()
                    window = create_window("search")
                id= result[0][0]
                window.close()
                window = create_window("profile", searched_id=id)

    # zakladka, ktora pojawia sie, gdy klikniemy "wyszukaj ziomali"
    elif zakladka == "account_settings":
        pass
    # zakladka, ktora pojawia sie, gdy trzeba wyswietlic profil
    elif zakladka == "profile":
        sg.theme('DarkAmber')

        db = sqlite3.connect("LIFTMATE_DATABASE.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM accounts where account_id=?", (searched_id,))
        result = cursor.fetchall()

        layout = [
            [sg.Image(filename="profile_picture.png"), sg.MenuBar([["=", ["Opcja1", "Opcja2"]]])],
            [sg.Text(result[0][3], font=('Arial',16))],
            [sg.HorizontalSeparator()],
            [sg.Text( "Age: " + str(result[0][6]))],
            [sg.HorizontalSeparator(50)],
            [sg.Text( "Height: " + str(result[0][8]) )],
            [sg.HorizontalSeparator(50)],
            [sg.Text( "Weight: " + str(result[0][5]))],
            [sg.HorizontalSeparator(50)],
            [sg.Text( "Level: " + str(result[0][10]))],
            [sg.HorizontalSeparator(50)],
            [sg.Text( "Strength: " + str(result[0][12]))],
            [sg.HorizontalSeparator(50)],
            [sg.Text( "Endurance: " + str(result[0][13]))],
            [sg.HorizontalSeparator(50)],
            [sg.Text( "Speed: " + str(result[0][14]))],
            [sg.HorizontalSeparator(50)],
            [sg.Text( "Agility: " + str(result[0][15]))],
            [sg.Push(), sg.Button("Back", key='-back-')]
        ]

        window = sg.Window("LIFTMATE/Profile", layout, size=(400,445))
        window.set_icon("icon.ico")
        db.commit()
        db.close()
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == "-back-":
                window.close()
                window = create_window("menu")

        # generuje okno z aktywnością z bazy danych

    # zakladka, ktora pojawia sie gdy ogladasz aktywnosci innych (lub klikasz przycisk na srodku)
    elif zakladka == "activity" or zakladka == "post_lookup":
        sg.theme('DarkAmber')

        db = sqlite3.connect("LIFTMATE_DATABASE.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM activity where activity_id = ?", (activityid,))
        result = cursor.fetchall()
        searched_id = result[0][1]
        if result[0][3] == "Run" or result[0][3] == "Swimming":
            wartosc = result[0][4]
            tekst = "Dystans: " + str(wartosc)
        else:
            wartosc = result[0][5]
            tekst = "Czas: " + str(wartosc)
        aktywnosc = result[0][3]
        cursor.execute('SELECT nick from accounts WHERE account_id=?', (searched_id,))
        result = cursor.fetchall()
        nick = result[0][0]
        layout = [
            [sg.Text(nick, font=('Arial', 16))],
            [sg.MenuBar([["=", ["Opcja1", "Opcja2"]]])],
            [sg.Text("Activity: " + aktywnosc)],
            [sg.Text(tekst)],
            [sg.Button("Back", key='-back-'), sg.Push(), sg.Button("Next", key="-nextButton-")]
        ]

        window = sg.Window("LIFTMATE/Profile", layout, size=(400, 445))
        window.set_icon("icon.ico")
        db.commit()
        db.close()
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == "-back-":
                window.close()
                window = create_window("menu")
            elif event == "-nextButton-":
                window.close()
                window = create_window("activity", activityid = activityid+1)

    # zakladka statystyk
    elif zakladka == "statistics":
        sg.theme('DarkAmber')
        layout = [
            [sg.Text("staty")],
            [sg.Text("staty")],
            [sg.Text("staty")]
        ]

        window = sg.Window("LIFTMATE", layout)
        window.set_icon("icon.ico")
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'OK':
                break
            elif event == '-Draw-':
                draw_plot()

    elif zakladka == "won":
        sg.theme('DarkAmber')
        layout = [
            [sg.Text("You Won")],
            [sg.Button("Back", key='-back-')],
        ]

        window = sg.Window("LIFTMATE", layout)
        window.set_icon("icon.ico")
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'OK':
                break
            elif event == '-back-':
                window.close()
                window = create_window("menu")


    #window.close()



def draw_plot():
    x = np.arange(0, 10, 0.1)
    y = np.sin(x)
    plt.plot(x, y)
    plt.show()
