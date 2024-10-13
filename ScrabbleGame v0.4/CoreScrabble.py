import tkinter as tk  # Graphical interface
import time  # To slow down the progression of the code
import threading  # To be able to do multiple thing
import socket  # For server management
import pickle  # To easily send List/Dictionary
from File_Manager import *  # To be able save and read files
from Common_Function import *  # Store function that are common to Server.py and CoreScrabble.py

# ======================== Screen Variable ===============================
# {Objet1: True, Objet2: False, ...}
Loaded_objet = {}  # Store tkinter objet and if there are loaded on the screen

# [(function to call the objet, the objet it-self), ...]
Order_main_objet = []  # Use to go back to a previous window

# loaded info
# {"deletemessage": Objet, 1 or 2 ..., }
info_box = {}  # Store info messages to not make them overlap

list_of_entry = {}  # save the entry to get the text

BGC = "#57597C"

# =========================== Game Variable =====================
move_piece_on_click_activate = [False]  # If the the movable piece is moving
Main_Game_Canvas_List = []  # 0 = game_canvas, 1 = title, 2 = grid_canvas, 3 = grid_list,

List_objet = {}  # Store all tkinter objet that must be deleted at some point

# Store the basic pool rule of a scrabble game
# Plan_Game = {"A": [9, 1], ...}  letter  ->   nb of time in the pool and it's value
Plan_Game = lire("lettres du scrabble", "info_scrabble.txt", "dictionnaire_list")

# Store all the playable words in scrabble
List_valid_word_s2 = lire("mots de deux lettres", "info_scrabble.txt", "liste")
List_valid_word_s3 = lire("mots de trois lettres", "info_scrabble.txt", "liste")
List_valid_word_s4 = lire("mots de quatre lettres", "info_scrabble.txt", "liste")
List_valid_word_s5 = lire("mots de cinq lettres", "info_scrabble.txt", "liste")
List_valid_word_s6 = lire("mots de six lettres", "info_scrabble.txt", "liste")
List_valid_word_s7 = lire("mots de sept lettres", "info_scrabble.txt", "liste")
List_valid_word_s8 = lire("mots de huit lettres", "info_scrabble.txt", "liste")
List_valid_word_s9 = lire("mots de neuf lettres", "info_scrabble.txt", "liste")
List_valid_word_s10 = lire("mots de dix lettres", "info_scrabble.txt", "liste")
List_valid_word_s11 = lire("mots de onze lettres", "info_scrabble.txt", "liste")
List_valid_word_s12 = []
List_valid_word_s13 = []
List_valid_word_s14 = []
List_valid_word_s15 = []

List_of_all_word = [List_valid_word_s2, List_valid_word_s3, List_valid_word_s4, List_valid_word_s5,
                    List_valid_word_s6, List_valid_word_s7, List_valid_word_s8, List_valid_word_s9,
                    List_valid_word_s10, List_valid_word_s11, List_valid_word_s12, List_valid_word_s13,
                    List_valid_word_s14, List_valid_word_s15]

List_objet_in_hand = {}  # position in hand -> [letter, objets]
List_objet_in_grid = {}  # l, c ->    [objets, lock]    # lock = if the piece is lock

# grid_list[row, column] = [grid, False, "", "MT"] l,c -> [canvas, piece in it, txt piece, point]
# Store all tkinter objet that make up the grid
grid_list = {}

Pool = []  # Store all the piece of the game

SaveName = []  # Store the name of the game

main_game_element = {}  # Store all the important tkinter objet
main_images = {}  # Store all the images

piece_spot_list = {}  # pos -> container of the piece and if it is movable

List_of_new_word = []  # List of words add to the grid

# index ( Player ind ) -> text(Score), text(Last action)
List_ScoreBoard_objet = []  # Store all tkinter objet of the scoreboard

TransitionSave = {}  # Store temporarily information of the save file

# Store the number of turn pass without any changes to the game
Tomanyturn = [0]

# Information to connect to a server
PORT = 7564
DECFOR = "utf-8"
DATA_DISCONNECT = "!DECONNECT!"
chrmax_username = 10

Online = [False]  # Store if user is in a online game

# Initialisation of the connection type
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# index 0  -> player 1  {"ClientName":"Solo/client adress/AI{difficulty}", "UserName":"MyName", "Turn": True/False, "SpaceInHand":space_left_in_hand()+7}
Players_info = []  # Store all the important information about the player

# {"Objet1": [True,Objet1], "Objet2": [False,Objet2] ...}  Objet and if it is loaded on the screen
game_Loaded_objet = {}


# ==================== Debug Function ================
def printgamestate():
    """Use to debug by showing the Pool and the Players information"""
    return
    print("Pool State :", Pool)
    for playerdata in Players_info:
        print(f"Players Hand :{playerdata['Hand']}")


# ==================Screen Function ====================
def returnback(evt=None):
    """When the function is call it will bring the previous screen"""
    goto = len(Order_main_objet) - 2
    # Order_main_objet store all the different screen that were loaded
    # len of Order_main_objet -1 give the current screen index and with -2 the screen that was before
    main_window.unbind_all("<Button-1>")
    if goto >= 0:
        delete_loaded_objet()
        function, objet = Order_main_objet[goto]
        # load previous screen
        function()
        # remove the main screen in the order
        Order_main_objet.pop(goto + 1)
        if Online[0]:
            deco = objetHeader(f"c.lobby.{DATA_DISCONNECT}").encode(DECFOR)
            client.send(deco)
            Online[0] = False


def creatbutton(plan, txt, command, y, placement):
    """Creat a tkinter button with some given information"""
    Button = tk.Button(plan, anchor="center", text=txt, font=("", "19"), padx=50, command=command)
    Button.pack(pady=y, anchor=placement)
    Loaded_objet[Button] = True
    return Button


def creatbuttongrid(plan, txt, command, l, c, x, y):
    """Creat a tkinter button with some given information but in another way"""
    Button = tk.Button(plan, anchor="center", text=txt, font=("", "19"), padx=50, command=command)
    Button.grid(row=l, column=c, padx=x, pady=y)
    Loaded_objet[Button] = True
    return Button


def delete_loaded_objet():
    """Remove all the active or loaded objet on the screen"""
    for objet in Loaded_objet:
        if Loaded_objet[objet]:
            objet.destroy()
            Loaded_objet[objet] = False


# ================== Loading Function ===================
'''This functions just delete and load new objet on the screen'''


def loadsologameselect():
    delete_loaded_objet()
    creatSoloPlayerScreen()


def loadmultiplayer():
    delete_loaded_objet()
    creatJoinServerScreen()


def loadcreatserver():
    delete_loaded_objet()
    creatCreatServerScreen()


def loadrule():
    delete_loaded_objet()
    creatrules()


def loadgamesave():
    path = "save"
    save = list_of_entry["EntryGameSelect"].get()
    # Get the entry of the name of the file
    fun, canvas = Order_main_objet[1]
    if save:
        list_of_save = list_doc(path)
        # Verified the save exist
        if (save + ".txt") in list_of_save:
            delete_loaded_objet()
            SaveName.append(f"save/{save}.txt")
            loadSoloPlayerGameScreen(save)
            print("loading save")
        else:
            creatTemporyText(canvas, "deletemesage", "The save does not exist", 650, 520)


def deletesave():
    text = None
    path = "save/"
    save = list_of_entry["EntryGameSelect"].get()
    # Get the entry of the name of the file
    fun, canvas = Order_main_objet[1]
    if save:
        path += save
        try:
            effacer(path + ".txt")
            creatTemporyText(canvas, "deletemesage", "Save deleted with success", 650, 520)

        except:
            creatTemporyText(canvas, "deletemesage", "The save does not exist", 650, 520)


def creatnewsave():
    path = "save"
    save = list_of_entry["EntryGameSelect"].get()
    name = list_of_entry["EntryGameSelectUserName"].get()
    # Get the entry of the name of the file and the name of the player
    fun, canvas = Order_main_objet[1]
    if save:
        list_of_save = list_doc(path)

        if (save + ".txt") not in list_of_save:
            if name:
                creatplayersdata(name, 4)
                delete_loaded_objet()
                SaveName.append(f"save/{save}.txt")
                creatSoloPlayerGameScreen(save)
                print("creating new game")

            else:
                creatTemporyText(canvas, "deletemesage", "Please enter your name", 650, 520)
        else:
            creatTemporyText(canvas, "deletemesage", "The save already exist", 650, 520)


def loadserverlobby(evt=None):
    delete_loaded_objet()
    creatServerLobby()


def resetlistmemory():
    """Clear up all of the variable if a new game is created after"""
    SaveName.clear()
    Players_info.clear()
    grid_list.clear()
    List_objet_in_grid.clear()
    List_objet_in_hand.clear()
    Pool.clear()
    main_game_element.clear()
    piece_spot_list.clear()
    List_of_new_word.clear()
    List_ScoreBoard_objet.clear()
    TransitionSave.clear()
    Tomanyturn[0] = 0


# ========================== Creat screen Element ===================
def creatgameselectcanvas(evt=None):
    """Create the screen to select the game"""
    GameSelectCanvas = tk.Canvas(background=BGC)
    GameSelectCanvas.pack(fill="both", expand=True)
    Loaded_objet[GameSelectCanvas] = True

    textlabel = tk.Label(GameSelectCanvas, text="Select a game", background=BGC)
    textlabel.grid(row=0, column=1, pady=70)

    textlabel2 = tk.Label(GameSelectCanvas, text="Enter your name", background=BGC)
    textlabel2.grid(row=2, column=1, pady=30)

    entry = tk.Entry(GameSelectCanvas, font=("", "11"), )
    entry.grid(row=1, column=1)
    list_of_entry["EntryGameSelect"] = entry

    entry2 = tk.Entry(GameSelectCanvas, font=("", "11"), )
    entry2.grid(row=3, column=1)
    list_of_entry["EntryGameSelectUserName"] = entry2

    Loaded_objet[entry] = True

    creatbuttongrid(GameSelectCanvas, "Create a new game", creatnewsave, 4, 0, 90, 280)
    creatbuttongrid(GameSelectCanvas, "Load a game", loadgamesave, 4, 1, 0, 280)
    creatbuttongrid(GameSelectCanvas, "Delete a game", deletesave, 4, 2, 90, 280)
    return GameSelectCanvas


def creattitlescreenCanvas():
    """Create the title screen"""
    TitleCanvas = tk.Canvas(background=BGC)
    TitleCanvas.pack(fill="both", expand=True)
    Loaded_objet[TitleCanvas] = True
    creatbutton(TitleCanvas, "Solo", loadsologameselect, 100, "center")
    creatbutton(TitleCanvas, "Join Server", loadmultiplayer, 20, "center")
    creatbutton(TitleCanvas, "Creat Server", loadcreatserver, 20, "center")
    creatbutton(TitleCanvas, "Rules", loadrule, 40, "center")
    return TitleCanvas


def creatruleCanvas():
    """Creat the screen to see the rules"""
    RuleCanvas = tk.Canvas(background=BGC, height=600)
    RuleCanvas.pack(fill="both", expand=True)
    RuleCanvas.create_text(380, 50, text="Some information about Scrabble Game ", font=("", "19"))
    RuleCanvas.create_text(380, 150, text=
    "                  Welcome to Scrabble Game !\n\n"
    "    Scrabble Game propose 2 way of playing scrabble :\n"
    "First there is Solo were you can play againt three comptuters \n"
    "But  you  can  also  play  with  your  friend  localy  or  globaly\n"
    "with  Join  Server.  For  information  about  multiplayer  click\n"
    "on Creat Server."
                           , font=("", "13"))
    RuleCanvas.create_text(380, 260, text="Rules of Scrabble : ", font=("", "19"))
    RuleCanvas.create_text(400, 470, text=
    "The goal  of  scrabble  is to get as  much  point as possible  during a game to \n"
    "do so you  need  place  letters with a certain  point value on the grid of 15x15\n"
    "to create words on some space of the grid you can found bonus like LD or LT \n"
    "who will multiplied the value of your letter by two or three, but you can also get \n"
    "MD or MT who will multiplied th value of your word by two or three.\n\n"
    
    "At the start of a game you get seven letters in your hand, during your turn\n"
    "you have two options Change Hand if you can place any word on the grid\n"
    "or Validate Turn after you place a word on the grid \n\n"
    
    "If you click on Change Hand you will pass your turn but you get new set of seven \n"
    "letters if the pool is not empty. If it is empty Chand Hand will just pass your turn.\n"
    "If you click on Validate Turn, if your word is valid you will earn point and you will be \n"
    "refilled if your word is not valid all the piece that you place will go back in your hand\n\n"
    
    "The game end when the pool is empty and a player has no more letters in his hand,\n"
    "or after 3 turn without any changes to the game.\n"
                           , font=("", "13"))

    Loaded_objet[RuleCanvas] = True
    creatbutton(RuleCanvas, "Return", returnback, 300, "se")
    return RuleCanvas


def creatcreatserverselectcanvas():
    """Creat the screen to see how to creat a server"""
    CreatServerCanvas = tk.Canvas(background=BGC, height=600)
    CreatServerCanvas.pack(fill="both", expand=True)
    Loaded_objet[CreatServerCanvas] = True

    CreatServerCanvas.create_text(380, 100, text="How to creat a server", font=("", "19"))
    CreatServerCanvas.create_text(380, 200, text=
    "To  creat  a  server  you  must  launch  Server.py, choose  if  the  server  is for \n"
    "local  or  global  purposes. Then to connect to the server go back to title screen \n"
    "and click on Join  Server to  click  Local for local connection but also if you are \n"
    "the host for global connection. Or click on Global and enter the server's key that\n"
    "is given to by host in global connection."
                                  , font=("", "13"))

    creatbutton(CreatServerCanvas, "Return", returnback, 300, "se")
    return CreatServerCanvas


def creatjoinservercanvas():
    """Creat the screen to join a server"""
    JoinServerCanvas = tk.Canvas(background=BGC, height=600)
    JoinServerCanvas.pack(fill="both", expand=True)
    Loaded_objet[JoinServerCanvas] = True

    titlelabel = tk.Label(JoinServerCanvas, text="Join a Server", background=BGC, font=("", "19", "bold"))
    titlelabel.grid(row=0, column=1, pady=30)

    textlabel = tk.Label(JoinServerCanvas, text="Server Key", background=BGC)
    textlabel.grid(row=4, column=2, pady=20)

    textlabel2 = tk.Label(JoinServerCanvas, text="Enter your name", background=BGC)
    textlabel2.grid(row=1, column=1, pady=10)

    entry = tk.Entry(JoinServerCanvas, font=("", "11"), )
    entry.grid(row=2, column=1)
    list_of_entry["EntryServerSelectUserName"] = entry

    entry2 = tk.Entry(JoinServerCanvas, font=("", "11"), )
    entry2.grid(row=5, column=2)
    list_of_entry["EntryServerSelectAdresse"] = entry2

    creatbuttongrid(JoinServerCanvas, "Join Local Server", JoinLocalLobby, 3, 0, 110, 120)
    creatbuttongrid(JoinServerCanvas, "Join Global Server", JoinGlobalLobby, 3, 2, 110, 120)

    return JoinServerCanvas


def JoinLocalLobby():
    """When the button Local is clicked the function try to connect to the server"""
    name = list_of_entry["EntryServerSelectUserName"].get()
    # Get the username
    fun, canvas = Order_main_objet[1]
    if name:
        if not "." in name:
            SERVER_IP = socket.gethostbyname(socket.gethostname())
            SERVER_ADDRESS = (SERVER_IP, PORT)
            # Local server IP
            try:
                client.connect(SERVER_ADDRESS)
                Online[0] = True
                creatserverplayerdata(name)
                creatserverlobby()
            except:
                creatTemporyText(canvas, "deletemesage", "No connection found", 650, 520)
                Online[0] = False
        else:
            creatTemporyText(canvas, "deletemesage", "Name can not contain '.' ", 650, 520)

    else:
        creatTemporyText(canvas, "deletemesage", "Please enter your name", 650, 520)


def JoinGlobalLobby():
    """When the Global button is clicked the function try to connect to the server"""
    address = list_of_entry["EntryServerSelectAdresse"].get()
    name = list_of_entry["EntryServerSelectUserName"].get()
    # Get the needed entry to connect
    fun, canvas = Order_main_objet[1]

    if name:
        if address:
            SERVER_IP = decode(address)
            # The server key is coded so we decode it
            SERVER_ADDRESS = (SERVER_IP, PORT)
            try:
                client.connect(SERVER_ADDRESS)
                Online[0] = True
                creatserverplayerdata(name)
                creatserverlobby()

            except:
                creatTemporyText(canvas, "deletemesage", "No connection found", 650, 520)
                Online[0] = False
        else:
            creatTemporyText(canvas, "deletemesage", "Please enter server's key", 650, 520)
    else:
        creatTemporyText(canvas, "deletemesage", "Please enter your name", 650, 520)


def creatVictoryCanvas():
    """Creat the victory screen"""
    delete_loaded_objet()
    VictoryCanvas = tk.Canvas(background=BGC)
    VictoryCanvas.pack(fill="both", expand=True)
    Loaded_objet[VictoryCanvas] = True
    List_of_player = sort_Players()

    # winner part
    winnerscore, winnername = List_of_player[0]
    VictoryCanvas.create_text(630, 100, text="Winner !!", font=("", "22", "bold underline"))
    VictoryCanvas.create_text(630, 150, text=winnername, font=("", "19", "bold "), fill="#51BFFF")
    VictoryCanvas.create_text(630, 200, text=f"with {winnerscore}", font=("", "19", "bold "), fill="#FF2828")
    VictoryCanvas.create_rectangle(490, 50, 770, 250, width=5, outline="white")

    padding = (1180 - 100) / (len(List_of_player))
    varpadding = padding + 100
    # others part
    for indplayer in range(1, len(List_of_player)):
        otherscore, othername = List_of_player[indplayer]

        VictoryCanvas.create_text(varpadding, 450, text=othername, font=("", "19", "bold "), fill="#51BFFF")
        VictoryCanvas.create_text(varpadding, 500, text=f"with {otherscore}", font=("", "19", "bold "), fill="#FF2828")

        varpadding += padding

    VictoryCanvas.create_text(630, 620, text="Press Escape to return to the title screen", font=("", "15", ""))

    return VictoryCanvas


def creatTemporyText(plan, path, txt, x, y):
    """Creat a text box in the plan at coord x,y if the function is call a second time the previous message is deleted"""
    if path in info_box:
        objet, displaytext = info_box[path]
        if displaytext != txt:
            plan.delete(objet)
            text = plan.create_text(x, y, text=txt)
            info_box[path] = (text, txt)
    else:
        text = plan.create_text(x, y, text=txt)
        info_box[path] = (text, txt)


def creatserverLobbyCanvas():
    """Creat the lobby on screen"""
    max = 4
    ServerLobbyCanvas = tk.Canvas(background=BGC, height=600)
    ServerLobbyCanvas.pack(fill="both", expand=True)
    Loaded_objet[ServerLobbyCanvas] = True
    try:
        Name = SaveName[0]
    except:
        Name = "Bidule"

    ServerLobbyCanvas.create_text(640, 50, text=f"Scrabble Server of {Name}", font=("", "11", "bold"))
    ServerLobbyCanvas.create_text(400, 110, text="Players connected", font=("", "11", "bold"))

    StarButton = tk.Button(ServerLobbyCanvas, text="  Start  ", font=("", "11", "bold"),
                           command=StarServerGame)

    nbplayer = 0
    padding = (350 - 50) / (max + 1)
    varpadding = padding + 100
    for it in range(0, max):
        #  50, min 50/ max 250
        Name = Players_info[it]["UserName"]

        if Name != "":
            ServerLobbyCanvas.create_text(400, varpadding, text=Name, font=("", "11"))
            nbplayer += 1
        else:
            ServerLobbyCanvas.create_text(400, varpadding, text="...", font=("", "11"))
        varpadding += padding

    if nbplayer == max:
        StarButton.pack(anchor="e", padx="150", pady="300")


# =====================Server Function=================================

# Core Multi player Function
def receive_data():
    firstturn = True
    while Online[0]:
        time.sleep(0.05)
        try:
            # the header describe how long the message is
            Header = client.recv(20).decode(DECFOR)
            Data = ""
            Listinfoserver = []
            if Header:

                try:
                    # if the header is like some thing that we expected like "        56"
                    Header = int(Header.strip(" "))
                    # we can receive the rest of the message
                    CompactData = client.recv(Header)
                    # The information is decoded
                    Data = CompactData.decode(DECFOR).split(".")

                except:
                    pass
                # the information is sent in a coded way  sender.where.action.information or as pickle data
                try:
                    # if the header is like some thing like "p        978"
                    if Header[0] == "p":
                        realHeader = ""
                        for indexinfo in range(1, len(Header)):
                            realHeader += Header[indexinfo]

                        Header = int(realHeader.strip(" "))
                        # we can receive the rest of the message
                        PickleData = client.recv(Header)
                        # The information is decoded
                        Listinfoserver, serverpool = pickle.loads(PickleData)

                        # print(Listinfoserver, serverpool)

                        if len(Listinfoserver) != 0:
                            # The players info and the pool are update
                            modif = modifiePlayers_info(Listinfoserver)
                            modifiePool(serverpool)
                            # print(Players_info, Pool)

                            if len(grid_list) != 0:
                                # and we applied the modification if there are needed
                                UpdateScoreBoard()
                                # refill the hand
                                clearhand()
                                for letter in Players_info[0]["Hand"]:
                                    append_in_hand(letter)

                except:
                    pass



                # treatement of th information
                if Data[0] == "s":
                    # Data from the server
                    if Data[1] == "lobby":
                        if Data[2] == "connected":
                            # then the information is about the players in the lobby
                            Players_Name = Data[3].split("/")
                            Players_Name.pop(-1)

                            if SaveName == []:
                                SaveName.append(Players_Name[0])

                            knownplayer = 0
                            for playerdata in Players_info:
                                playername = playerdata["UserName"]
                                if playername != "":
                                    knownplayer += 1

                            if len(Players_Name) > knownplayer:
                                # new player has connected
                                for playerdata in Players_info:
                                    knownname = playerdata["UserName"]
                                    if knownname == "" and len(Players_Name) != 0:
                                        playerdata["UserName"] = Players_Name[0]
                                        Players_Name.pop(0)
                                    elif len(Players_Name) != 0:
                                        Players_Name.remove(knownname)



                            elif len(Players_Name) < knownplayer:
                                # a player has left the lobby
                                for playerdata in Players_info:
                                    playername = playerdata["UserName"]
                                    if not playername in Players_Name:
                                        playerdata["UserName"] = ""
                            if firstturn:
                                loadserverlobby()

                    elif Data[1] == "game":
                        # information about the game
                        if Data[2] == "play":
                            # a player has make a play
                            action = Data[3].split("/")

                            lorc = action[0]
                            nb = int(action[1])
                            start = int(action[2])
                            end = int(action[3])
                            word = action[4]

                            letter_list = []
                            for letter in word:
                                letter_list.append(letter)

                            place_word_on_grid(lorc, nb, start, end, letter_list)
                            remove_bonus(lorc, nb, start, end)
                            letter_list.clear()

                        elif Data[2] == "scoreboard":
                            # information about the scoreboard
                            info_scoreboard = Data[3].split("/")
                            Name = info_scoreboard[0]

                            if Name != Players_info[0]["UserName"]:
                                # the information are already apply for the player who send the information
                                Word = info_scoreboard[1]
                                addScore = int(info_scoreboard[2])
                                Playerindex = get_Player_index(Name)
                                Score = int(List_ScoreBoard_objet[Playerindex][0])
                                Score += addScore
                                LastAction = f"Place {Word}  + {addScore}"
                                List_ScoreBoard_objet[Playerindex][0] = Score
                                List_ScoreBoard_objet[Playerindex][1] = LastAction
                                UpdateScoreBoard()


                        elif Data[2] == "victory":
                            # if the game has to finish
                            creatVictoryScreen()


                else:
                    pass
        except:
            pass

def remove_bonus(lorc, nb, start, end):
    if lorc == "l":
        for column in range(start, end+1):
            grid_list[nb, column][-1] = None

    elif lorc == "c":
        for row in range(start, end+1):
            grid_list[row, nb][-1] = None




def get_Player_index(Name):
    """Given a name it will return the index of the player in Players_info"""
    for Playerindex in range(0, len(Players_info)):
        if Players_info[Playerindex]["UserName"] == Name:
            return Playerindex


def creatserverlobby():
    # First message send to the server is the name
    client.send((objetHeader(Players_info[0]["UserName"])).encode(DECFOR))
    client.setblocking(False)
    # start thread to receive data from the server
    listening_thread = threading.Thread(target=receive_data)
    listening_thread.start()
    # SaveName[0] --> first personne to connect



def StarServerGame():
    """Send to the server it can start the game"""
    client.send((objetHeader("c.game.launch")).encode(DECFOR))  # First message = Username
    time.sleep(2)
    creatMultiPlayerGame()


def send_information(DATA):
    """DATA is a string and send DATA in the right format"""
    if DATA:
        info = objetHeader(DATA).encode(DECFOR)
        client.send(info)


def modifiePlayers_info(Listinfoserver):
    """Modified the Players_info according to the information send by the server
    and if it modified the info of the first player it will return True"""
    modif = False
    Name = Players_info[0]["UserName"]
    old_hand = Players_info[0]["Hand"]
    for new_playerdata in Listinfoserver:
        if Name == new_playerdata["UserName"]:
            newhand = new_playerdata["Hand"]

    for letter in old_hand:
        if not letter in newhand:
            modif = True
            break
        else:
            if newhand.count(letter) != old_hand.count(letter):
                modif = True
                break

    for new_playerdata in Listinfoserver:
        for player_index in range(0, len(Players_info)):
            if new_playerdata["UserName"] == Players_info[player_index]["UserName"]:
                Players_info[player_index]["Hand"] = new_playerdata["Hand"]
                Players_info[player_index]["Turn"] = new_playerdata["Turn"]
                Players_info[player_index]["SpaceInHand"] = new_playerdata["SpaceInHand"]
    return modif


def modifiePool(serverpool):
    """Modified the Pool according to the information send by the server """
    Pool.clear()
    for letter in serverpool:
        Pool.append(letter)


def creatmultiplayergame():
    """Create the actual game screen for multiplayer"""
    game_canvas = tk.Canvas(main_window, bg="#8c562f", highlightthickness=0)
    game_canvas.pack(fill="both", expand=True)
    Loaded_objet[game_canvas] = True
    main_game_element["game_canvas"] = game_canvas

    creatspacingCanvas(game_canvas)
    creatpiece(game_canvas)
    creattitle(game_canvas, f"Scrabble game of {SaveName[0]}")
    creatgrid(game_canvas)
    creathand(game_canvas)
    ActionCanvas, ScoreCanvas = creatActionCanvas(game_canvas)
    initilisationScoreBoard(ScoreCanvas)

    sethand()

    return game_canvas


# ============================== Creat Solo Game Function ==================
def creatnewsologame(savename):
    """Create the actual game screen for solo first initialisation"""
    game_canvas = tk.Canvas(main_window, bg="#8c562f", highlightthickness=0)
    game_canvas.pack(fill="both", expand=True)
    Loaded_objet[game_canvas] = True
    main_game_element["game_canvas"] = game_canvas

    creat_pool(Plan_Game)

    creatspacingCanvas(game_canvas)
    creatpiece(game_canvas)
    creattitle(game_canvas, savename)
    creatgrid(game_canvas)
    creathand(game_canvas)
    ActionCanvas, ScoreCanvas = creatActionCanvas(game_canvas)
    initilisationScoreBoard(ScoreCanvas)

    fill_hand()
    Players_info[0]["SpaceInHand"] = space_left_in_hand() + 7

    for nb in range(0, len(Players_info)):
        AI_fill_hand(nb)
        Players_info[nb]["SpaceInHand"] = 7

    return game_canvas


def difficulty():
    """Return a random difficulty for the IA"""
    easy = 10
    simple = 25 + easy
    medium = 30 + simple
    hard = 25 + medium
    veryhard = 10 + hard
    difficulty = random.randint(0, 100)
    if 0 <= difficulty < easy:
        return 0
    elif easy <= difficulty < simple:
        return 1
    elif simple <= difficulty < medium:
        return 2
    elif medium <= difficulty < hard:
        return 3
    else:
        return 4


def creatplayersdata(name, nb):
    """Creat the Players_info for solo"""
    # For the human player
    Player_data = {"ClientName": "Solo", "UserName": name, "Turn": True, "SpaceInHand": 0, "Hand": [], "Score": 0}
    Players_info.append(Player_data)

    # for the computer players
    r = random.randint(1, 1000)
    listofname = ["GabyHappy", "HunTanLock", "Abakast", "Nigel Richards", "Kevin"]
    if r == 745:
        SpAI_data = {"ClientName": "AI3", "UserName": "Xerian", "Turn": False, "SpaceInHand": 0, "Hand": [], "Score": 0}
        Players_info.append(SpAI_data)
        SpAI_data = {"ClientName": "AI0", "UserName": "Davyddex", "Turn": False, "SpaceInHand": 0, "Hand": [],
                     "Score": 0}
        Players_info.append(SpAI_data)

        for AI in range(1, nb - 2):
            AI_data = {"ClientName": f"AI{difficulty()}", "UserName": f"AI {AI}", "Turn": False, "SpaceInHand": 0,
                       "Hand": [],
                       "Score": 0}
            Players_info.append(AI_data)

    elif 900 <= r:
        for AI in range(1, nb):

            if len(listofname) != 0:
                rand = random.randint(0, len(listofname) - 1)
                prename = listofname[rand]
                listofname.remove(prename)
                if prename == "Nigel Richards":
                    SpAI_data = {"ClientName": "AI4", "UserName": prename, "Turn": False,
                                 "SpaceInHand": 0, "Hand": [],
                                 "Score": 0}
                    Players_info.append(SpAI_data)
                else:
                    SpAI_data = {"ClientName": f"AI{difficulty()}", "UserName": prename, "Turn": False,
                                 "SpaceInHand": 0, "Hand": [],
                                 "Score": 0}
                    Players_info.append(SpAI_data)
            else:
                AI_data = {"ClientName": f"AI{difficulty()}", "UserName": f"AI {AI}", "Turn": False, "SpaceInHand": 0,
                           "Hand": [],
                           "Score": 0}
                Players_info.append(AI_data)

    else:
        for AI in range(1, nb):
            AI_data = {"ClientName": f"AI{difficulty()}", "UserName": f"AI {AI}", "Turn": False, "SpaceInHand": 0,
                       "Hand": [],
                       "Score": 0}
            Players_info.append(AI_data)


def creatserverplayerdata(name):
    """Creat the Players_info for multi"""
    max = 4
    Player_data = {"ClientName": "Multi", "UserName": name, "Turn": None, "SpaceInHand": 0, "Hand": [], "Score": 0}
    Players_info.append(Player_data)
    for it in range(1, max):
        Player_data = {"ClientName": "Multi", "UserName": "", "Turn": None, "SpaceInHand": 0, "Hand": [],
                       "Score": 0}
        Players_info.append(Player_data)


# ============================== Load Solo Game Function ======================
def loadsologame(savename):
    """Create the actual game for Solo if it was already created"""
    game_canvas = tk.Canvas(main_window, bg="#8c562f", highlightthickness=0)
    game_canvas.pack(fill="both", expand=True)
    Loaded_objet[game_canvas] = True
    main_game_element["game_canvas"] = game_canvas

    creatspacingCanvas(game_canvas)
    creatpiece(game_canvas)
    creattitle(game_canvas, savename)
    getdata()
    creatgrid(game_canvas)
    setgrid()
    creathand(game_canvas)
    sethand()
    ActionCanvas, ScoreCanvas = creatActionCanvas(game_canvas)
    initilisationScoreBoard(ScoreCanvas)

    return game_canvas


def getdata():
    """Modified Players_info, Pool, and grid_list according to the save file"""
    path = SaveName[0]
    local_Pool = lire("Pool", path, "liste")
    local_grid_list = lire("grid_list", path, "dictionnaire_list")
    local_Players_info = lire("Players_info", path, "list_dictionnaire")
    for PlayerData in local_Players_info:
        if PlayerData == "Score":
            Players_info.append(int(PlayerData))
        else:
            Players_info.append(PlayerData)

    for ll, lc in local_grid_list:
        l = int(ll)
        c = int(lc)
        TransitionSave[l, c] = local_grid_list[l, c]

    for letter in local_Pool:
        Pool.append(letter)


def setgrid():
    """After the grid is loaded with the information of TransitionSave setgrid() recreate the grid"""

    for l, c in TransitionSave:
        if TransitionSave[l, c][0]:
            letter = TransitionSave[l, c][1]
            add_in_grid(grid_list, l, c, letter, True)
            grid_list[l, c][-1] = "None"


def sethand():
    """After the hand is loaded with the information of Players_info sethand() recreate the hand"""
    for letter in Players_info[0]["Hand"]:
        append_in_hand(letter)
    Players_info[0]["SpaceInHand"] = space_left_in_hand() + 7


# ====================== Creat/ Load ===== Game Function ================
def creattitle(game_canvas, savename):
    """Create the title of the game"""
    title = tk.Canvas(game_canvas, bg="#8c562f", width="300", height="30", highlightthickness=0)
    title.create_text(150, 15, anchor="center", text=f"Partie {savename}", font=("Times", "11", ""), justify="center")
    Main_Game_Canvas_List.append(title)
    main_game_element["title_canvas"] = title
    title.grid(row=0, column=1)


def creatgrid(game_canvas):
    """Create a 15x15 grid for a scrabble game"""
    img_bg = main_images["img_bg"]
    img_centre = main_images["img_centre"]
    img_mot_triple = main_images["img_mot_triple"]
    img_mot_double = main_images["img_mot_double"]
    img_lettre_triple = main_images["img_lettre_triple"]
    img_lettre_double = main_images["img_lettre_double"]

    # creation of the grid container
    grid_canvas = tk.Canvas(game_canvas, confine=False, )
    Main_Game_Canvas_List.append(grid_canvas)
    main_game_element["grid_canvas"] = grid_canvas
    # creation of every cell of the grid + save in grid_list
    for row in range(0, 15):
        for column in range(0, 15):
            gridsize = 37
            # first diagonal
            if row == column:
                if row == 7:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_centre)
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "C"]
                elif row == 0 or row == 14:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_mot_triple)
                    grid.create_text(gridsize / 2, gridsize / 2, text="MT", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "MT"]
                elif row == 6 or row == 8:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_lettre_double)
                    grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "LD"]
                elif row == 5 or row == 9:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_lettre_triple)
                    grid.create_text(gridsize / 2, gridsize / 2, text="LT", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "LT"]
                else:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_mot_double)
                    grid.create_text(gridsize / 2, gridsize / 2, text="MD", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "MD"]
            # second diagonal
            elif row == -column + 14:
                if row == 14 or row == 0:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_mot_triple)
                    grid.create_text(gridsize / 2, gridsize / 2, text="MT", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "MT"]
                elif row == 6 or row == 8:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_lettre_double)
                    grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "LD"]
                elif row == 5 or row == 9:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_lettre_triple)
                    grid.create_text(gridsize / 2, gridsize / 2, text="LT", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "LT"]
                else:
                    grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                    grid.create_image(0, 0, image=img_mot_double)
                    grid.create_text(gridsize / 2, gridsize / 2, text="MD", font=("Yu Gothic UI", "13", ""),
                                     justify="center")
                    grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                    grid.grid(row=row, column=column)
                    grid_list[row, column] = [grid, False, "", "MD"]
            # other mot triple
            elif row == 7 and (column == 0 or column == 14):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_mot_triple)
                grid.create_text(gridsize / 2, gridsize / 2, text="MT", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "MT"]
            elif column == 7 and (row == 0 or row == 14):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_mot_triple)
                grid.create_text(gridsize / 2, gridsize / 2, text="MT", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "MT"]
            # other lettre double
            elif (row == 0 or row == 14) and (column == 3 or column == 11):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_double)
                grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LD"]
            elif (column == 0 or column == 14) and (row == 3 or row == 11):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_double)
                grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LD"]
            # other lettre triple
            elif (row == 1 or row == 13) and (column == 5 or column == 9):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_triple)
                grid.create_text(gridsize / 2, gridsize / 2, text="LT", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LT"]
            elif (column == 1 or column == 13) and (row == 5 or row == 9):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_triple)
                grid.create_text(gridsize / 2, gridsize / 2, text="LT", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LT"]
            # more lettre double
            elif (row == 2 or row == 12) and (column == 6 or column == 8):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_double)
                grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LD"]
            elif (column == 2 or column == 12) and (row == 6 or row == 8):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_double)
                grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LD"]
            # last lettre double
            elif (row == 3 or row == 11) and (column == 7):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_double)
                grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LD"]
            elif (column == 3 or column == 11) and (row == 7):
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_lettre_double)
                grid.create_text(gridsize / 2, gridsize / 2, text="LD", font=("Yu Gothic UI", "13", ""),
                                 justify="center")
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "LD"]
            # everything else
            else:
                grid = tk.Canvas(grid_canvas, height=gridsize, width=gridsize, highlightthickness=0, confine=False)
                grid.create_image(0, 0, image=img_bg)
                grid.create_rectangle(0, 0, gridsize, gridsize, outline="#ffdabc", width="2")
                grid.grid(row=row, column=column)
                grid_list[row, column] = [grid, False, "", "None"]
    grid = None
    Main_Game_Canvas_List.append(grid_list)
    grid_canvas.grid(row=1, column=1)


def creathand(game_canvas):
    """Create the hand where the letter will be place"""
    game_hand = tk.Canvas(game_canvas, bg="#8c562f", highlightthickness=0, height=60, width=700)
    Main_Game_Canvas_List.append(game_hand)
    main_game_element["game_hand"] = game_hand

    for column in range(0, 7):
        piece_spot = tk.Canvas(game_hand, height=37, width=37, highlightthickness=0, confine=False, bg="#8c562f")
        piece_spot.create_rectangle(0, 0, 37, 37, outline="#ffdabc", width="4")
        piece_spot.grid(row=0, column=column, padx=16, pady=15)
        piece_spot_list[0, column] = [piece_spot, True, ""]
    game_hand.grid(row=2, column=1)
    game_hand.create_rectangle(0, 8, 37 * 7 + 15 * 7 * 2 + 14, 2 * 15 + 30, outline="#ffdabc", width="4",
                               fill="#592E00")


def creatpiece(game_canvas):
    """Create the piece off screen who will be movable on the game screen"""

    x_piece_size = 36
    y_piece_size = 36
    img_piece = main_images["img_piece"]
    img = game_canvas.create_image(-30, -30, image=img_piece, anchor="center")
    bordure = game_canvas.create_rectangle(-5, -5, -5, -5, fill="", outline="#c69563")
    txt = game_canvas.create_text(0, 0, anchor="center", text="", font=("Times", "24", "bold"), justify="center")
    val = game_canvas.create_text(0, 0, anchor="center", text="", font=("Calibri", "8"), justify="center")
    main_game_element["img"] = img
    main_game_element["bordure"] = bordure
    main_game_element["txt"] = txt
    main_game_element["val"] = val


def creatActionCanvas(game_canvas):
    """Create the container of the scoreboard and the button to act on the game"""
    ActionCanvas = tk.Canvas(game_canvas, bg="#8c562f", width="300", height="500", highlightthickness=0)
    ActionCanvas.grid(row=1, column=2, padx=50)

    ScoreCanvas = creatScoreBoard(ActionCanvas)
    ChangeHandButton = creatCanvasButton(1, 0, ActionCanvas, 100, "Change Hand", change_hand)
    ValidTurnButton = creatCanvasButton(2, 0, ActionCanvas, 0, "Validate Turn", validation_turn)
    QuitButton = creatQuitButton(game_canvas)
    game_Loaded_objet["ActionCanvas"] = [True, ActionCanvas, QuitButton]

    return ActionCanvas, ScoreCanvas


def creatScoreBoard(ActionCanvas):
    """Create the Board that will contain the score """
    ScoreCanvas = tk.Canvas(ActionCanvas, highlightthickness=0)
    ScoreCanvas.grid(row=0, column=0)
    return ScoreCanvas


def creatspacingCanvas(game_canvas):
    """Create blank space to make sure that everything will be static"""
    spacingCanvas1 = tk.Canvas(game_canvas, height=10, width=87, highlightthickness=0, bg="#8c562f")
    spacingCanvas1.grid(row=2, column=0, padx=53)
    spacingCanvas2 = tk.Canvas(game_canvas, width="378", height="562", highlightthickness=0, bg="#8c562f")
    spacingCanvas2.grid(row=1, column=2, padx=50)
    main_game_element["spacingCanvas1"] = spacingCanvas1
    main_game_element["spacingCanvas2"] = spacingCanvas2


def creatCanvasButton(l, c, plan, y, txt, function):
    """Create a button for the action canvas"""
    Button = tk.Button(plan, anchor="center", text=txt, font=("", "19"), padx=50,
                       command=function)
    Button.grid(row=l, column=c, pady=y)
    return Button


def creatQuitButton(game_canvas):
    """Create the quit button"""
    QuitButton = tk.Button(game_canvas, anchor="center", text="Quit", font=("", "15"), padx=20, command=saveandquit)
    QuitButton.grid(row=2, column=0, padx=50)
    return QuitButton


# ============================== Game Function ===================================
def saveandquit():
    """Save the game, go back to the title screen and reset the memory
    Online it will properly disconnect the player"""

    if Online[0] and savepossible():
        deco = objetHeader(f"c.lobby.{DATA_DISCONNECT}").encode(DECFOR)
        client.send(deco)
        Online[0] = False
        returnback()
        resetlistmemory()

    if savepossible():
        path = ""
        for indcaractere in range(0, len(SaveName[0]) - 4):
            path += SaveName[0][indcaractere]

        grid_list_info = {}
        for l, c in grid_list:
            grid_list_info[l, c] = [grid_list[l, c][1], grid_list[l, c][2], grid_list[l, c][3]]


        sauvegarde(path, "Players_info", Players_info, "txt", True)
        sauvegarde(path, "grid_list", grid_list_info, "txt", False)
        sauvegarde(path, "Pool", Pool, "txt", False)
        returnback()
        resetlistmemory()


def savepossible():
    '''Check if the save is possible this mean that it is the player turn
    and he did not place any of his piece on the grid'''
    if Players_info[0]["Turn"]:
        for l, c in List_objet_in_grid:
            if not List_objet_in_grid[l, c][1]:
                return False
        return True


def creat_pool(dict):
    """Create the Pool that will be use by the game"""
    for letter in dict:
        for nbt in range(0, dict[letter][0]):
            Pool.append(letter)


# =================== Grid Function =============================
def around_select_cell(x, y):
    """Take the coordinate of the pointer and return if it is near a cell of the grid """
    x -= main_game_element["grid_canvas"].winfo_rootx() - main_window.winfo_x()
    y -= main_game_element["grid_canvas"].winfo_rooty() - main_window.winfo_y()
    # get the relative coordinate of the pointer to the grid
    l, c = main_game_element["grid_canvas"].grid_location(x, y)
    if (-1 <= c <= 15) and (-1 <= l <= 15):
        return l, c

    else:
        return None


def p_select_cell(x, y):
    """Take the coordinate of the pointer and return if it is in a cell of the grid """
    x -= main_game_element["grid_canvas"].winfo_rootx() - main_window.winfo_x()
    y -= main_game_element["grid_canvas"].winfo_rooty() - main_window.winfo_y()
    # get the relative coordinate of the pointer to the grid
    c, l = main_game_element["grid_canvas"].grid_location(x, y)
    if (0 <= c <= 14) and (0 <= l <= 14):
        return l, c
    else:
        return None


def add_in_grid(list_of_spot, row, column, letter, lock):
    """Add a letter in the grid given the row and the column and if it is movable by the player"""
    '''list_of_spot = grid_list'''
    spot = list_of_spot[row, column][0]
    img_piece = main_images["img_piece"]
    try:
        if not in_grid(row, column):
            img = spot.create_image(16, 16, image=img_piece, anchor="center")
            txt = spot.create_text(15, 15, anchor="center", text=letter, font=("Times", "24", "bold"), justify="center")
            bd = spot.create_rectangle(0, 0, 34, 34, fill="", outline="#c69563")
            val = spot.create_text(29, 29, anchor="center", text=int(Plan_Game[letter][1]),
                                   font=("Calibri", "8"), justify="center")
            list_of_spot[row, column][1] = True
            list_of_spot[row, column][2] = letter
            List_objet_in_grid[row, column] = [img, txt, bd, val, lock]

    except:
        pass


def remove_in_grid(row, column):
    """Remove a letter in the grid given the row and the column """
    if in_grid(row, column):
        grid_list[row, column][0].delete(List_objet_in_grid[row, column][1],
                                         List_objet_in_grid[row, column][2], List_objet_in_grid[row, column][0],
                                         List_objet_in_grid[row, column][3])
        del List_objet_in_grid[row, column]
        grid_list[row, column][1] = False
        grid_list[row, column][2] = ""


def is_lock(row, column):
    """Return if the cell is lock or not"""
    try:
        return List_objet_in_grid[row, column][-1]
    except:
        return False


def in_grid(row, column):
    """Return True if there is a piece in the position and False if not or the position does not exist"""
    if (row, column) in grid_list:
        return grid_list[row, column][1]
    else:
        return False


def fixpieceongrid():
    """Lock every none locked piece on the grid"""
    for l, c in List_objet_in_grid:
        if not List_objet_in_grid[l, c][-1]:
            List_objet_in_grid[l, c][-1] = True


def place_word_on_grid(lorc, nb, start, end, list_letter):
    """Given many arguments the function place a word on the grid"""
    it = 0
    if lorc == "l":
        for column in range(start, end + 1):
            letter = list_letter[it]
            add_in_grid(grid_list, nb, column, letter, True)
            it += 1

    elif lorc == "c":
        for row in range(start, end + 1):
            letter = list_letter[it]
            add_in_grid(grid_list, row, nb, letter, True)
            it += 1


# ===================== Hand Function =============================
def update_hand():
    """Update the Players_info information about the actual hand"""
    Players_info[0]["Hand"].clear()
    for pos in List_objet_in_hand:
        letter = List_objet_in_hand[pos][0]
        Players_info[0]["Hand"].append(letter)


def add_in_hand(letter, pos):
    """Add a letter in the hand at a given possition"""
    img_piece = main_images["img_piece"]
    if (0, pos) in piece_spot_list and piece_spot_list[(0, pos)][1]:
        try:
            img = piece_spot_list[(0, pos)][0].create_image(16, 16, image=img_piece, anchor="center")
            txt = piece_spot_list[(0, pos)][0].create_text(15, 15, anchor="center", text=letter,
                                                           font=("Times", "24", "bold"), justify="center")
            bordure = piece_spot_list[(0, pos)][0].create_rectangle(0, 0, 34, 34, fill="", outline="#c69563")
            val = piece_spot_list[(0, pos)][0].create_text(29, 29, anchor="center", text=int(Plan_Game[letter][1]),
                                                           font=("Calibri", "8"), justify="center")
            List_objet_in_hand[pos] = [letter, img, txt, bordure, val]
            piece_spot_list[(0, pos)][1] = False
        except:
            pass


def append_in_hand(letter):
    """Add a letter in the hand to first free position"""
    img_piece = main_images["img_piece"]
    for position in range(0, 7):
        if not in_hand(position):
            if (0, position) in piece_spot_list and piece_spot_list[(0, position)][1]:
                try:
                    img = piece_spot_list[(0, position)][0].create_image(16, 16, image=img_piece, anchor="center")
                    txt = piece_spot_list[(0, position)][0].create_text(15, 15, anchor="center", text=letter,
                                                                        font=("Times", "24", "bold"), justify="center")
                    bordure = piece_spot_list[(0, position)][0].create_rectangle(0, 0, 34, 34, fill="",
                                                                                 outline="#c69563")
                    val = piece_spot_list[(0, position)][0].create_text(29, 29, anchor="center",
                                                                        text=int(Plan_Game[letter][1]),
                                                                        font=("Calibri", "8"), justify="center")
                    List_objet_in_hand[position] = [letter, img, txt, bordure, val]
                    piece_spot_list[(0, position)][1] = False
                    return
                except:
                    pass


def remove_in_hand(pos):
    """Remove the piece at the given position"""
    if (0, pos) in piece_spot_list:
        # if there is something
        if pos in List_objet_in_hand:
            piece_spot_list[(0, pos)][0].delete(List_objet_in_hand[pos][1],
                                                List_objet_in_hand[pos][2], List_objet_in_hand[pos][3],
                                                List_objet_in_hand[pos][4])
            del List_objet_in_hand[pos]
            piece_spot_list[(0, pos)][1] = True


def clearhand():
    """Remove all the letter of the hand"""
    for pos in range(0, 8):
        if in_hand(pos):
            remove_in_hand(pos)


def in_hand(pos):
    """Return True if there is a piece in the position"""
    # if the position exist
    if (0, pos) in piece_spot_list:
        # if there is some thing
        if pos in List_objet_in_hand:
            return True
        else:
            return False


def around_select_hand(x, y):
    """Take the coordinate of the pointer and return if it is near a spot of the hand"""
    x -= main_game_element["game_hand"].winfo_rootx() - main_window.winfo_x()
    y -= main_game_element["game_hand"].winfo_rooty() - main_window.winfo_y()
    c, l = main_game_element["game_hand"].grid_location(x, y)
    if (-1 <= c <= 7) and (-1 <= l <= 1):
        return l, c
    else:
        return None


def p_select_hand(x, y):
    """Take the coordinate of the pointer and return if it is in the spot of the hand"""
    x -= main_game_element["game_hand"].winfo_rootx() - main_window.winfo_x()
    y -= main_game_element["game_hand"].winfo_rooty() - main_window.winfo_y()
    c, l = main_game_element["game_hand"].grid_location(x, y)
    if (0 <= c <= 6) and (l == 0):
        return l, c
    else:
        return None


def return_hand():
    """Return none locked letters of the grid to the player's hand"""
    list_to_remove = []
    for (row, column) in List_objet_in_grid:
        if not is_lock(row, column):
            append_in_hand(grid_list[row, column][2])
            list_to_remove.append((row, column))
    for (row, column) in list_to_remove:
        remove_in_grid(row, column)
    update_hand()


def fill_hand():
    """Fill the player's hand by take letter out of the poll"""
    list_letter = take_in_pool(space_left_in_hand(), Pool)
    for letter in list_letter:
        append_in_hand(letter)
    update_hand()


# ===================== Motion Function =================================
def handle_multi_plan(plan, letter, x, y, xsize, ysize, List_objet):
    """Make the link between all game canavas with a objet
    Enable the movable letter to be in the first plan"""
    img_piece = main_images["img_piece"]
    x -= plan.winfo_rootx() - main_window.winfo_x()
    y -= plan.winfo_rooty() - main_window.winfo_y()
    in_plan = 0 - xsize <= x <= int(plan.config("width")[-1]) + xsize and 0 - ysize <= y <= int(
        plan.config("height")[-1]) + ysize
    if in_plan and (plan not in List_objet):
        img_in_newcanvas = plan.create_image(-30, -30, image=img_piece)
        bordure_in_newcanvas = plan.create_rectangle(-3, -3, -3, -3, outline="#c69563")
        txt_in_newcanvas = plan.create_text(-30, -30, anchor="center", text=letter,
                                            font=("Times", "24", "bold"), justify="center")
        val_in_newcanvas = plan.create_text(-30, -30, anchor="center", text=int(Plan_Game[letter][1]),
                                            font=("Calibri", "8"), justify="center")

        List_objet[plan] = [img_in_newcanvas, bordure_in_newcanvas, txt_in_newcanvas, val_in_newcanvas]

    try:
        if plan in List_objet:
            plan.coords(List_objet[plan][0], x + 8, y + 15)
            plan.coords(List_objet[plan][2], x + 8, y + 15)
            plan.coords(List_objet[plan][1], x - xsize / 2 + 8, y - ysize / 2 + 15, x + xsize / 2 + 8,
                        y + ysize / 2 + 15)
            plan.coords(List_objet[plan][3], x + 22, y + 28)
        if not in_plan and plan in List_objet:
            refresh_plan(List_objet)

    except:
        pass


def refresh_plan(List_objet):
    """Clear the remaining objet that are not supposed to be visible any more"""
    L = []
    for plan in List_objet:
        plan.delete(List_objet[plan][0], List_objet[plan][1], List_objet[plan][2], List_objet[plan][3])
        L.append(plan)
    for plan in L:
        del List_objet[plan]


def move_piece(x, y, letter):
    """Given the coordinate of the pointer the letter goes to those coordinate"""
    x_piece_size = 36
    y_piece_size = 36
    main_game_element["game_canvas"].coords(main_game_element["img"], x, y - 16)
    main_game_element["game_canvas"].coords(main_game_element["txt"], x, y - 16)
    main_game_element["game_canvas"].coords(main_game_element["bordure"], x - x_piece_size / 2,
                                            y - y_piece_size / 2 - 16, x + x_piece_size / 2
                                            , y + y_piece_size / 2 - 16)

    main_game_element["game_canvas"].coords(main_game_element["val"], x + 14, y - 3)

    handle_multi_plan(main_game_element["title_canvas"], letter, x, y, x_piece_size, y_piece_size, List_objet)
    handle_multi_plan(main_game_element["game_hand"], letter, x, y, x_piece_size, y_piece_size, List_objet)

    handle_multi_plan(main_game_element["spacingCanvas2"], letter, x, y, x_piece_size, y_piece_size, List_objet)
    handle_multi_plan(main_game_element["spacingCanvas1"], letter, x, y, x_piece_size, y_piece_size, List_objet)

    if around_select_cell(x, y):
        List_of_potencial_lc = []
        c, l = around_select_cell(x, y)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= i + l <= 14 and 0 <= j + c <= 14:
                    List_of_potencial_lc.append((i + l, j + c))
            for potencial_lc in List_of_potencial_lc:
                potencial_grid = grid_list[potencial_lc][0]  # find the canvas with the coord l and c

                handle_multi_plan(potencial_grid, letter, x, y, x_piece_size, y_piece_size, List_objet)
    if around_select_hand(x, y):
        l, c = around_select_hand(x, y)
        if l == -1:
            l = 0
        if c == -1:
            c = 0
        elif c == 7:
            c = 6
        if 0 <= c <= 5:
            handle_multi_plan(piece_spot_list[l, c][0], letter, x, y, x_piece_size, y_piece_size, List_objet)
            handle_multi_plan(piece_spot_list[l, c + 1][0], letter, x, y, x_piece_size, y_piece_size, List_objet)
        elif 1 <= c <= 6:
            handle_multi_plan(piece_spot_list[l, c - 1][0], letter, x, y, x_piece_size, y_piece_size, List_objet)
            handle_multi_plan(piece_spot_list[l, c][0], letter, x, y, x_piece_size, y_piece_size, List_objet)


def move_piece_on_click(evt):
    """This function will move the letter according to the pointer coordinate
    And send to end the thread when the letter is place"""
    y = main_game_element["game_canvas"].winfo_pointery() - main_window.winfo_y()
    x = main_game_element["game_canvas"].winfo_pointerx() - main_window.winfo_x()
    refresh_plan_thread = threading.Thread(target=refresh_plan, args=(List_objet,))

    if move_piece_on_click_activate[0]:
        # get the letter of the piece
        letter = main_game_element["game_canvas"].itemcget(main_game_element["txt"], 'text')
        # place the piece
        if p_select_cell(x, y) and Players_info[0]["Turn"]:
            l, c = p_select_cell(x, y)
            if not in_grid(l, c):  # on the grid
                move_piece_on_click_activate[0] = False
                add_in_grid(grid_list, l, c, letter, False)
                refresh_plan_thread.start()
                UpdateScoreBoard()

        elif p_select_hand(x, y):  # in the hand
            l, c = p_select_hand(x, y)
            if not in_hand(c):
                move_piece_on_click_activate[0] = False
                add_in_hand(letter, c)
                refresh_plan_thread.start()
                UpdateScoreBoard()
                update_hand()

    else:
        # take the piece
        if p_select_cell(x, y) and Players_info[0]["Turn"]:
            # in grid
            l, c = p_select_cell(x, y)
            if not is_lock(l, c) and in_grid(l, c):
                deleteActionCanvas()
                letter = grid_list[l, c][2]
                remove_in_grid(l, c)
                main_game_element["game_canvas"].itemconfig(main_game_element["txt"], text=letter)
                move_piece_on_click_activate[0] = True
                main_game_element["game_canvas"].itemconfig(main_game_element["val"], text=int(Plan_Game[letter][1]))
                motion_thread = threading.Thread(target=in_motion, args=(letter,))
                motion_thread.start()


        elif p_select_hand(x, y) and (not Online[0] or Players_info[0]["Turn"]):
            # in hand (but online only if it is your turn)
            l, c = p_select_hand(x, y)
            if in_hand(c):
                deleteActionCanvas()
                letter = List_objet_in_hand[c][0]
                remove_in_hand(c)
                main_game_element["game_canvas"].itemconfig(main_game_element["txt"], text=letter)
                move_piece_on_click_activate[0] = True
                main_game_element["game_canvas"].itemconfig(main_game_element["val"], text=int(Plan_Game[letter][1]))
                motion_thread = threading.Thread(target=in_motion, args=(letter,))
                motion_thread.start()
                update_hand()


def in_motion(letter):
    """The function is call using threading and get the coordinate of the pointer every 0.01s
    and move the letter and when it stop the movable letter goes off screen"""
    while move_piece_on_click_activate[0]:
        y = main_game_element["game_canvas"].winfo_pointery() - main_window.winfo_y()
        x = main_game_element["game_canvas"].winfo_pointerx() - main_window.winfo_x()
        move_piece(x, y, letter)
        time.sleep(0.01)
    # set the piece off screen
    move_piece(-30, -30, letter)
    refresh_plan(List_objet)


def piece_near(row, column):
    """Return if there is a letter near the cell"""
    if in_grid(row + 1, column) or in_grid(row, column + 1) or in_grid(row - 1, column) or in_grid(row, column - 1):
        return True
    else:
        return False


def piece_placable(row, column):
    '''Return True if the cell can accept a piece if not False'''
    if row == column and row == 7:
        return True
    elif piece_near(row, column):
        return True
    else:
        return False


# ====================== Action/ Verification Function ================================
def add_word_in_line_or_column():
    """Verified if the none locked letters are in a row or in a column, by returning there values or False"""
    list_of_added_letter = []
    line_word = 0
    column_word = 0
    row_i, column_i = 0, 0
    row_f, column_f = 14, 14

    for (row, column) in List_objet_in_grid:
        if not is_lock(row, column):
            list_of_added_letter.append((row, column))
    if len(list_of_added_letter) != 0 and len(list_of_added_letter) != 1:
        row1, column1 = list_of_added_letter[0]
        if column_i < column1:
            column_i = column1
        if column_f > column1:
            column_f = column1
        if row_i < row1:
            row_i = row1
        if row_f > row1:
            row_f = row1

        for i in range(1, len(list_of_added_letter)):
            row, column = list_of_added_letter[i]
            if row == row1:
                line_word += 1

                if column_i < column:
                    column_i = column
                if column_f > column:
                    column_f = column
            elif column == column1:
                column_word += 1

                if row_i < row:
                    row_i = row
                if row_f > row:
                    row_f = row
            else:
                return False

        if line_word == len(list_of_added_letter) - 1:
            return "l", row1, column_f, column_i
        elif column_word == len(list_of_added_letter) - 1:
            return "c", column1, row_f, row_i
        else:
            return False

    elif len(list_of_added_letter) == 1:
        row1, column1 = list_of_added_letter[0]
        return "l/c", -1, row1, column1

    else:
        return False


def word_on(lorc, nb, start, end):
    """Return the word on line/column in range of the start and the end"""
    word = ""
    if lorc == "l":
        for column in range(start, end + 1):
            letter = grid_list[nb, column][2]  # give "" if noting, " " for a joker, "letter" for a letter
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                return False
    elif lorc == "c":
        for row in range(start, end + 1):
            letter = grid_list[row, nb][2]
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                return False
    elif lorc == "l/c":
        return grid_list[start, end][2]

    return word


def always_word_on(lorc, nb, start, end):
    """Return all the information (word) of a line/column in range of the start and the end"""
    word = ""
    if lorc == "l":
        for column in range(start, end + 1):
            letter = grid_list[nb, column][2]  # give "" if noting, " " for a joker, "letter" for a letter
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                word += "$"
    elif lorc == "c":
        for row in range(start, end + 1):
            letter = grid_list[row, nb][2]
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                word += "$"

    return word


def space_left_in_hand():
    space_left = 7
    for position in range(0, 7):
        if in_hand(position):
            space_left -= 1
    return space_left


def change_hand(evt=None):
    """When the button Change Hand is clicked"""

    if Online[0]:

        if Players_info[0]["Turn"] and len(Pool) != 0:

            for l, c in List_objet_in_grid:
                if not List_objet_in_grid[l, c][-1]:
                    return_hand()
                    return
            info = ""
            for position in range(0, 7):
                if in_hand(position):
                    letter = List_objet_in_hand[position][0]
                    info += letter + "/"
                    remove_in_hand(position)

            send_information(f"c.game.change.{info}")
            Players_info[0]["Turn"] = False
            UpdateScoreBoard()

        elif Players_info[0]["Turn"] and len(Pool) == 0:
            for l, c in List_objet_in_grid:
                if not List_objet_in_grid[l, c][-1]:
                    return_hand()
                    return
            send_information(f"c.game.rotaturn")
            UpdateScoreBoard()

    else:
        if Players_info[0]["Turn"] and len(Pool) != 0:
            for l, c in List_objet_in_grid:
                if not List_objet_in_grid[l, c][-1]:
                    return_hand()
                    return
            for position in range(0, 7):
                if in_hand(position):
                    letter = List_objet_in_hand[position][0]
                    Pool.append(letter)
                    remove_in_hand(position)
            fill_hand()
            rotateturn()
            UpdateScoreBoard()
        elif Players_info[0]["Turn"] and len(Pool) == 0:
            for l, c in List_objet_in_grid:
                if not List_objet_in_grid[l, c][-1]:
                    return_hand()
                    return
            rotateturn()
            UpdateScoreBoard()
    printgamestate()


def validation_turn(evt=None):
    """When the button Validate Turn is clicked"""
    word = False
    total = 0
    if in_grid(7, 7):
        if add_word_in_line_or_column():
            lorc, nb, start, end = add_word_in_line_or_column()

            if lorc == "c" or lorc == "l" or lorc == "l/c":
                try:
                    if lorc == "c" or lorc == "l":
                        word, lorc, nb, newstar, newend = detection_of_additional_letter(lorc, nb, start, end)
                    else:
                        if detection_of_additional_letter("l", start, end, end):
                            word, lorc, nb, newstar, newend = detection_of_additional_letter("l", start, end, end)

                        elif detection_of_additional_letter("c", end, start, start):
                            word, lorc, nb, newstar, newend = detection_of_additional_letter("c", end, start, start)

                        else:
                            return_hand()
                except:
                    return_hand()
                    return
                if word:
                    adlorc = lorc
                    adnb = nb
                    adstart = newstar
                    adend = newend

                    list_pos_joker = joker(word)
                    if valid_word(word) or valid_word_joker(word, list_pos_joker):
                        list_of_auxiliary_word = auxiliaryword(lorc, nb, newstar, newend)
                        if not find_False_in_list(list_of_auxiliary_word) or not is_lock(7, 7):
                            total += value_of_a_word(lorc, nb, newstar, newend)

                            try:
                                list_of_auxiliary_word_bonus = newcreatedword(adlorc, adnb, adstart, adend)
                            except:
                                return_hand()
                                return

                            if find_False_in_list(list_of_auxiliary_word_bonus):
                                return_hand()
                                return
                            for (lorc, nb, newstar, newend) in list_of_auxiliary_word_bonus:
                                total += value_of_a_word(lorc, nb, newstar, newend)

                            if space_left_in_hand() == 7 and Players_info[0]["SpaceInHand"] == 7:
                                print("scrabble")
                                total += 50

                            if Online[0]:
                                Players_info[0]["Turn"] = False
                                Score = List_ScoreBoard_objet[0][0]
                                Score += total
                                LastAction = f"Place {word}  + {total}"
                                List_ScoreBoard_objet[0][0] = Score
                                List_ScoreBoard_objet[0][1] = LastAction
                                list_letter = getnonelockletter()
                                fixpieceongrid()
                                Players_info[0]["Score"] = Score
                                letters = "*".join(list_letter)
                                info = f"{adlorc}/{adnb}/{adstart}/{adend}/{word}/{total}/{letters}"
                                send_information(f"c.game.play.{info}")
                                UpdateScoreBoard()

                            else:
                                Score = int(List_ScoreBoard_objet[0][0])
                                Score += total
                                LastAction = f"Place {word}  + {total}"
                                List_ScoreBoard_objet[0][0] = Score
                                List_ScoreBoard_objet[0][1] = LastAction
                                fixpieceongrid()
                                Players_info[0]["Score"] = Score
                                # reset the variable if the game is still evolving
                                Tomanyturn[0] = 0
                                fill_hand()
                                rotateturn()
                                UpdateScoreBoard()




                        else:
                            return_hand()
                    else:
                        return_hand()
                else:
                    return_hand()
        else:
            return_hand()
    else:
        return_hand()
    printgamestate()


def getnonelockletter():
    L = []
    for row, column in List_objet_in_grid:
        if not List_objet_in_grid[row, column][-1]:
            letter = grid_list[row, column][2]
            L.append(letter)
    return L


def valid_word(word):
    """Return if the word is playable"""
    for list_of_word in List_of_all_word:
        if len(word) == len(list_of_word[0]):
            if word in list_of_word:
                return True
            else:
                return False


def build_word(list):
    """List of letter --> word"""
    word = ""
    for letter in list:
        word += letter
    return word


def valid_word_joker(word, list_pos_joker):
    """Return if the word is valid when it contain joker(s)"""
    if len(list_pos_joker) == 0:
        return False
    list_of_letter = split_word(word)
    if len(list_pos_joker) == 1:
        for a_letter in range(ord("A"), ord("Z")):
            list_of_letter[list_pos_joker[0]] = chr(a_letter)
            word = build_word(list_of_letter)
            if valid_word(word):
                return True
        return False
    elif len(list_pos_joker) == 2:
        for letter1 in range(ord("A"), ord("Z")):
            for letter2 in range(ord("A"), ord("Z")):
                list_of_letter[list_pos_joker[0]] = chr(letter1)
                list_of_letter[list_pos_joker[1]] = chr(letter2)
                word = build_word(list_of_letter)
                if valid_word(word):
                    return True
        return False


def find_False_in_list(list):
    """Return if there is at least one False in a list"""
    for word in list:
        if not word:
            return True
    return False


def joker(word):
    """Return a list of the postion of the jokers"""
    joker = []
    for pos_letter in range(0, len(word)):
        if word[pos_letter] == " ":
            joker.append(pos_letter)
    return joker


def detection_of_additional_letter(lorc, nb, start, end):
    """Return the new information about a word if it is build using other letter than the one the player place"""
    newstar = start
    newend = end
    if end - start == 0 and lorc == "l":
        main_word = grid_list[(nb, end)][2]

    elif end - start == 0 and lorc == "c":
        main_word = grid_list[(start, nb)][2]

    else:
        main_word = word_on(lorc, nb, start, end)

    if main_word:
        word = ""
        befor_word = always_word_on(lorc, nb, 0, start - 1)
        after_word = always_word_on(lorc, nb, end + 1, 14)

        for ind_letter in range(len(befor_word) - 1, -1, -1):
            if befor_word[ind_letter] != "$":
                word += befor_word[ind_letter]
                newstar -= 1
            else:
                break
        word = revers(word)

        word += main_word

        for letter in after_word:
            if letter != "$":
                word += letter
                newend += 1
            else:
                break
        if len(word) != 1:
            return word, lorc, nb, newstar, newend
        else:
            return False
    return False


def revers(word):
    """Revers a given word"""
    reversword = ""
    for ind_letter in range(len(word) - 1, -1, -1):
        reversword += word[ind_letter]
    return reversword


def auxiliaryword(lorc, nb, start, end):
    """Return a list of auxiliary words creat by a given word"""
    if start == end:
        return [False]
    word = False
    auxiliary_words = []
    total_empty_spot = 0
    if lorc == "l":
        for column in range(start, end + 1):
            for chekrow in range(nb - 1, nb + 2, 2):
                if (chekrow, column) in List_objet_in_grid:
                    if List_objet_in_grid[chekrow, column][-1]:
                        if grid_list[chekrow, column][1]:

                            if detection_of_additional_letter("c", column, chekrow, nb):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("c", column, chekrow,
                                                                                                 nb)
                            elif detection_of_additional_letter("c", column, nb, chekrow):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("c", column, nb,
                                                                                                 chekrow)
                            if word:
                                list_pos_joker = joker(word)
                                if valid_word(word) or valid_word_joker(word, list_pos_joker):
                                    auxiliary_words.append((lorc, nb, newstar, newend))
                                else:
                                    auxiliary_words.append(False)
                else:
                    total_empty_spot += 1
        if total_empty_spot == (end - start + 1) * 2:
            # all empty
            return [False]

        return auxiliary_words
    elif lorc == "c":
        for row in range(start, end + 1):
            for chekcolumn in range(nb - 1, nb + 2, 2):
                if (row, chekcolumn) in List_objet_in_grid:
                    if List_objet_in_grid[row, chekcolumn][-1]:
                        if grid_list[row, chekcolumn][1]:
                            if detection_of_additional_letter("l", row, nb, chekcolumn):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("l", row, nb,
                                                                                                 chekcolumn)
                            elif detection_of_additional_letter("l", row, chekcolumn, nb):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("l", row, chekcolumn,
                                                                                                 nb)

                            if word:
                                list_pos_joker = joker(word)
                                if valid_word(word) or valid_word_joker(word, list_pos_joker):
                                    auxiliary_words.append((lorc, nb, newstar, newend))
                                else:
                                    auxiliary_words.append(False)
                else:
                    total_empty_spot += 1
        if total_empty_spot == (end - start + 1) * 2:
            # all empty
            return [False]

        return auxiliary_words


def newcreatedword(lorc, nb, start, end):
    """Return a list of new words creat by a given word"""
    if start == end:
        return [False]
    word = False
    auxiliary_words = []
    if lorc == "l":
        for column in range(start, end + 1):
            for chekrow in range(nb - 1, nb + 2, 2):
                if (chekrow, column) in List_objet_in_grid:
                    if not List_objet_in_grid[nb, column][-1]:
                        if grid_list[chekrow, column][1]:

                            if detection_of_additional_letter("c", column, chekrow, nb):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("c", column, chekrow,
                                                                                                 nb)
                            elif detection_of_additional_letter("c", column, nb, chekrow):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("c", column, nb,
                                                                                                 chekrow)
                            if word:
                                list_pos_joker = joker(word)
                                if valid_word(word) or valid_word_joker(word, list_pos_joker):
                                    auxiliary_words.append((lorc, nb, newstar, newend))
                                else:
                                    auxiliary_words.append(False)
        return auxiliary_words
    elif lorc == "c":
        for row in range(start, end + 1):
            for chekcolumn in range(nb - 1, nb + 2, 2):
                if (row, chekcolumn) in List_objet_in_grid:
                    if not List_objet_in_grid[row, nb][-1]:
                        if grid_list[row, chekcolumn][1]:
                            if detection_of_additional_letter("l", row, nb, chekcolumn):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("l", row, nb,
                                                                                                 chekcolumn)
                            elif detection_of_additional_letter("l", row, chekcolumn, nb):
                                word, lorc, nb, newstar, newend = detection_of_additional_letter("l", row, chekcolumn,
                                                                                                 nb)

                            if word:
                                list_pos_joker = joker(word)
                                if valid_word(word) or valid_word_joker(word, list_pos_joker):
                                    auxiliary_words.append((lorc, nb, newstar, newend))
                                else:
                                    auxiliary_words.append(False)

        return auxiliary_words


def value_of_a_word(lorc, nb, star, end):
    """Return the value of a word knowing his position on the grid"""
    value = 0
    word_multiplicator = 1
    letter_multiplicator = 1
    if lorc == "l":
        for column in range(star, end + 1):
            letter = grid_list[nb, column][2]
            bonus = grid_list[nb, column][3]
            letter_value = Plan_Game[letter][1]
            if bonus == "MT":
                word_multiplicator *= 3
                grid_list[nb, column][3] = ""
            elif bonus == "MD":
                word_multiplicator *= 2
                grid_list[nb, column][3] = ""
            elif bonus == "LT":
                letter_multiplicator *= 3
                grid_list[nb, column][3] = ""
            elif bonus == "LD":
                letter_multiplicator *= 2
                grid_list[nb, column][3] = ""
            value += letter_value * letter_multiplicator
            letter_multiplicator = 1
    elif lorc == "c":
        for row in range(star, end + 1):
            letter = grid_list[row, nb][2]
            bonus = grid_list[row, nb][3]
            letter_value = Plan_Game[letter][1]
            if bonus == "MT":
                word_multiplicator *= 3
                grid_list[row, nb][3] = ""
            elif bonus == "MD":
                word_multiplicator *= 2
                grid_list[row, nb][3] = ""
            elif bonus == "LT":
                letter_multiplicator *= 3
                grid_list[row, nb][3] = ""
            elif bonus == "LD":
                letter_multiplicator *= 2
                grid_list[row, nb][3] = ""
            value += letter_value * letter_multiplicator
            letter_multiplicator = 1

    return value * word_multiplicator


def rotateturn():
    """Rotate the turn and let the AI play if it is her turn
    And check if the game should end"""

    end, winner = victory_condition(3)
    if end:
        if winner:
            scoretothewinner = 0
            indwinner = 0
            for indplayer in range(0, len(Players_info)):
                if Players_info[indplayer]["UserName"] == winner:
                    indwinner = indplayer

            for playerdata in Players_info:
                scoretoremove = 0
                if playerdata["UserName"] != winner:
                    for letter in playerdata["Hand"]:
                        scoretoremove += Plan_Game[letter][1]
                    scoretothewinner += scoretoremove
                    playerdata["Score"] -= scoretoremove

            Players_info[indwinner]["Score"] += scoretothewinner
            creatVictoryScreen()
        return
    # Rotate
    for ind_playerdata in range(0, len(Players_info)):
        if Players_info[ind_playerdata]["Turn"]:
            Players_info[ind_playerdata]["Turn"] = False
            if ind_playerdata == len(Players_info) - 1:
                ind_playerdata = -1
            ind_playerdata += 1
            Players_info[ind_playerdata]["Turn"] = True
            break
    if Players_info[0]["Turn"]:
        Players_info[0]["SpaceInHand"] = space_left_in_hand() + 7
    # AI
    UpdateScoreBoard()
    for ind_playerdata in range(0, len(Players_info)):
        if Players_info[ind_playerdata]["ClientName"][0] == "A" and Players_info[ind_playerdata]["ClientName"][
            1] == "I":
            if Players_info[ind_playerdata]["Turn"]:
                AIthread = threading.Thread(target=AIturn, args=(ind_playerdata,))
                AIthread.start()


def victory_condition(nb):
    '''Return True and the player who has no more letter and if the pool is empty,
    or just True if it's been nb turn without any modification of the grid
    or just False'''

    if Tomanyturn[0] == nb:
        return True, None
    if len(Pool) == 0:
        for Playerdata in Players_info:
            if len(Playerdata["Hand"]) == 0:
                return True, Playerdata["UserName"]
        Tomanyturn[0] += 1
    else:
        return False, None


def sort_Players():
    """Sort players score in Players_info to see which one is the winner"""
    List_of_Player = []
    # 0  -> first place (player name, score)
    for playerdata in Players_info:
        name = playerdata["UserName"]
        score = playerdata["Score"]
        List_of_Player.append((score, name))
    List_of_Player.sort()
    return List_of_Player


# ========================================= AI ==================================
def AI_fill_hand(ordre):
    if ordre != 0:
        left_space = 7 - len(Players_info[ordre]["Hand"])
        AI_hand = take_in_pool(left_space, Pool)
        Players_info[ordre]["Hand"] += AI_hand
        # reset the variable if the game is still evolving
        Tomanyturn[0] = 0


def AI_change_hand(ordre):
    if ordre != 0:
        for lettre in Players_info[ordre]["Hand"]:
            Pool.append(lettre)
        Players_info[ordre]["Hand"].clear()
        AI_fill_hand(ordre)


def AI_remove_in_hand(ordre, list_lettre):
    if ordre != 0:
        for lettre in list_lettre:
            if lettre != "":
                Players_info[ordre]["Hand"].remove(lettre)


def AI_place_on_grid(lorc, nb, start, end, list_lettre):
    it = 0
    if lorc == "l":
        for column in range(start, end + 1):
            letter = list_lettre[it]
            add_in_grid(grid_list, nb, column, letter, False)
            it += 1

    elif lorc == "c":
        for row in range(start, end + 1):
            letter = list_lettre[it]
            add_in_grid(grid_list, row, nb, letter, False)
            it += 1


def AI(grid_list, Player_data, difficulty):
    '''Player_data = Players_info [!=0]["Hand"]
    return : play or change, lorc, nb, start, end [letter]'''
    return "change", None, None, None, None, None
    return "play", "c", 0, 0, 1, ["L", "A"]


def AIturn(ordre):
    time.sleep(2)
    action, lorc, nb, start, end, list_lettre = AI(grid_list, Players_info[ordre]["Hand"],
                                                   int(Players_info[ordre]["ClientName"][2]))
    if action == "change":
        AI_change_hand(ordre)

    elif action == "play":
        total = 0

        AI_place_on_grid(lorc, nb, start, end, list_lettre)
        word, lorc, nb, newstart, newend = detection_of_additional_letter(lorc, nb, start, end)
        list_of_new_word = newcreatedword(lorc, nb, newstart, newend)
        fixpieceongrid()

        total += value_of_a_word(lorc, nb, start, end)
        for lorc, nb, start, end in list_of_new_word:
            total += value_of_a_word(lorc, nb, start, end)

        Players_info[ordre]["Score"] += total
        LastAction = f"Place {word}  + {total}"
        List_ScoreBoard_objet[0][0] = Players_info[ordre]["Score"]
        List_ScoreBoard_objet[0][1] = LastAction
        UpdateScoreBoard()
        AI_remove_in_hand(ordre, list_lettre)
        AI_fill_hand(ordre)
    rotateturn()


# ======================== ScoreBoard ============================================
def initilisationScoreBoard(ScoreCanvas):
    """Create the scoreboard on screen"""
    ScoreCanvas.create_text(190, 15, text="Score Board", font=("", "15", "bold"))
    ScoreCanvas.create_text(50, 40, text="Names", font=("", "11", "bold"))
    ScoreCanvas.create_text(150, 40, text="Scores", font=("", "11", "bold"))
    ScoreCanvas.create_text(280, 40, text="Last action", font=("", "11", "bold"))
    nb_Player = len(Players_info)
    padding = (250 - 50) / (nb_Player + 1)
    varpadding = padding + 50
    for PlayerData in Players_info:
        #  50, min 50/ max 250
        Name = PlayerData["UserName"]
        Score = PlayerData["Score"]
        if PlayerData["Turn"]:
            ScoreCanvas.create_text(50, varpadding, text=Name, font=("", "11", "bold"), fill="green")
        else:
            ScoreCanvas.create_text(50, varpadding, text=Name, font=("", "11"))
        ScoreCanvas.create_text(150, varpadding, text=Score, font=("", "11"))
        LastAction = ScoreCanvas.create_text(280, varpadding, text="", font=("", "11"))

        List_ScoreBoard_objet.append([Score, ""])

        varpadding += padding


def NewScoreBoard(ScoreCanvas):
    """Create the scoreboard using information of Player_info and List_ScoreBoard_objet"""
    ScoreCanvas.create_text(190, 15, text="Score Board", font=("", "15", "bold"))
    ScoreCanvas.create_text(50, 40, text="Names", font=("", "11", "bold"))
    ScoreCanvas.create_text(150, 40, text="Scores", font=("", "11", "bold"))
    ScoreCanvas.create_text(280, 40, text="Last action", font=("", "11", "bold"))
    nb_Player = len(Players_info)
    padding = (250 - 50) / (nb_Player + 1)
    varpadding = padding + 50
    itPlayer = 0
    for PlayerData in Players_info:
        #  50, min 50/ max 250
        Name = PlayerData["UserName"]
        Score = List_ScoreBoard_objet[itPlayer][0]

        LastAction = List_ScoreBoard_objet[itPlayer][1]
        itPlayer += 1
        if PlayerData["Turn"]:
            ScoreCanvas.create_text(50, varpadding, text=Name, font=("", "11", "bold"), fill="green")
        else:
            ScoreCanvas.create_text(50, varpadding, text=Name, font=("", "11"))
        ScoreCanvas.create_text(150, varpadding, text=Score, font=("", "11"))
        ScoreCanvas.create_text(280, varpadding, text=LastAction, font=("", "11"))
        varpadding += padding


def UpdateScoreBoard():
    """Update the scoreboard"""
    if not move_piece_on_click_activate[0]:
        deleteActionCanvas()
        ActionCanvas, ScoreCanvas = creatActionCanvas(main_game_element["game_canvas"])
        NewScoreBoard(ScoreCanvas)


def deleteActionCanvas():
    """Delete the scoreboard"""
    if game_Loaded_objet["ActionCanvas"][0]:
        game_Loaded_objet["ActionCanvas"][0] = False
        game_Loaded_objet["ActionCanvas"][1].destroy()
        game_Loaded_objet["ActionCanvas"][2].destroy()


# ======================= Creation of main screen element=============================
# Function call to create the element on screen and store them in Order_main_objet
def creatSoloPlayerScreen(evt=None):
    Order_main_objet.append((creatgameselectcanvas, creatgameselectcanvas()))


def creattitlescreen(evt=None):
    Order_main_objet.append((creattitlescreenCanvas, creattitlescreenCanvas()))


def creatrules(evt=None):
    Order_main_objet.append((creatruleCanvas, creatruleCanvas()))


def creatSoloPlayerGameScreen(savename):
    Order_main_objet.append((creatnewsologame, creatnewsologame(savename)))
    main_window.bind_all("<Button-1>", move_piece_on_click)
    main_window.unbind_all('<Escape>')


def loadSoloPlayerGameScreen(savename):
    Order_main_objet.append((loadsologame, loadsologame(savename)))
    main_window.bind_all("<Button-1>", move_piece_on_click)
    main_window.unbind_all('<Escape>')


def creatVictoryScreen(evt=None):
    Order_main_objet.pop(-1)
    Order_main_objet.pop(-1)
    main_window.unbind_all("<Button-1>")
    main_window.bind_all('<Escape>', returnback)
    Order_main_objet.append((creatVictoryCanvas, creatVictoryCanvas()))
    try:
        effacer(SaveName[0])
    except:
        pass
    resetlistmemory()


def creatCreatServerScreen():
    Order_main_objet.append((creatcreatserverselectcanvas, creatcreatserverselectcanvas()))


def creatJoinServerScreen():
    Order_main_objet.append((creatjoinservercanvas, creatjoinservercanvas()))


def creatServerLobby():
    Order_main_objet.append((creatserverLobbyCanvas, creatserverLobbyCanvas()))


def creatMultiPlayerGame():
    delete_loaded_objet()
    Order_main_objet.append((creatmultiplayergame, creatmultiplayergame()))
    main_window.bind_all("<Button-1>", move_piece_on_click)
    main_window.unbind_all('<Escape>')


# ===================== Initalisation of the window ==========================
main_window = tk.Tk()
main_window.title("Scrabble Game")
main_window.config(background="black")
main_window.iconbitmap("texture/icon.ico")
main_window.geometry("1280x649+0+0")
main_window.minsize(width="780", height="649")

main_images["img_piece"] = tk.PhotoImage(file="texture/piece.png")
main_images["img_bg"] = tk.PhotoImage(file="texture/texture vert.png")
main_images["img_centre"] = tk.PhotoImage(file="texture/texture étoile.png")
main_images["img_mot_triple"] = tk.PhotoImage(file="texture/texture rouge.png")
main_images["img_mot_double"] = tk.PhotoImage(file="texture/texture jaune.png")
main_images["img_lettre_triple"] = tk.PhotoImage(file="texture/texture bleu.png")
main_images["img_lettre_double"] = tk.PhotoImage(file="texture/texture bleuciel.png")

# Creation of the element on screen
creattitlescreen()

main_window.bind_all('<Escape>', returnback)

# Start of the loop that manage the window
main_window.mainloop()
# if the window is closed

if Online[0]:
    deco = objetHeader(f"c.lobby.{DATA_DISCONNECT}").encode(DECFOR)
    client.send(deco)
    Online[0] = False
