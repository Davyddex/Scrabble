import socket  # For server management
import threading  # To be able to do multiple thing
import time  # To slow down the progression of the code
import pickle  # To easily send List/Dictionary
from File_Manager import *  # To be able save and read files
from Common_Function import *  # Store function that are common to Server.py and CoreScrabble.py

SERVER_IP = socket.gethostbyname(socket.gethostname())

# ======================== What type of connection ====================================
while True:
    server_type = input("Local or Global connection ?   ")
    if server_type.lower() == "local":
        break

    elif server_type.lower() == "global":
        print(f"The server's is : {code(public_ip_adresse())}")
        print(f"Do not forget to open the port 7564 under the address {SERVER_IP}")
        break

    else:
        print("Write 'local' for local connection or 'global' for a global connection with the rest of the world.")


# ================================ Info Server ==============================
PORT = 7564

SERVER_ADDRESS = (SERVER_IP, PORT)
nb_total_cc = 4  # total client that can connect on the serser
nb_cc = 0  # number of client connected
client_connected = []  # Storing the client address of the client connected
client_user = {}  # Associate Client and there UserName
DECFOR = "utf-8"
DATA_DISCONNECT = "!DECONNECT!"  # Message to deconnect to the server


# ================================ Game Variable =============================
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
List_valid_word_s12 = lire("mots de douze lettres", "info_scrabble.txt", "liste")
List_valid_word_s13 = lire("mots de treize lettres", "info_scrabble.txt", "liste")
List_valid_word_s14 = lire("mots de quatorze lettres", "info_scrabble.txt", "liste")
List_valid_word_s15 = lire("mots de quinze lettres", "info_scrabble.txt", "liste")


List_of_all_word = [List_valid_word_s2, List_valid_word_s3, List_valid_word_s4, List_valid_word_s5,
                    List_valid_word_s6, List_valid_word_s7, List_valid_word_s8, List_valid_word_s9,
                    List_valid_word_s10, List_valid_word_s11, List_valid_word_s12, List_valid_word_s13,
                    List_valid_word_s14, List_valid_word_s15]


Server_Players_info = []  # Store all the important information about the player
Server_grid_list = {}  # Store the letter added to the grid  {(l,c) : [letter, lock, bonus]}
# Store the basic pool rule of a scrabble game
Plan_Game = lire("lettres du scrabble", "info_scrabble.txt", "dictionnaire_list")
Pool = []  # Pool of all the piece of the game
Tomanyturn = [0]  # Store the number of turn pass without any changes to the game
GameStart = [False]


# Initialisation of the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SERVER_ADDRESS)


# =================== Scrabble Function of the Server ======================
def add_word_in_grid(lorc, nb, start, end, list_letters, lock):
    it = 0
    if lorc == "l":
        for column in range(start, end+1):
            if list_letters[it] != "":
                Server_grid_list[nb, column][0] = list_letters[it]
                Server_grid_list[nb, column][1] = lock
                it += 1
    elif lorc == "c":
        for row in range(start, end+1):
            if list_letters[it] != "":
                Server_grid_list[row, nb][0] = list_letters[it]
                Server_grid_list[row, nb][1] = lock
                it += 1


def fix_letter_on_grid():
    for row, column in Server_grid_list:
        if Server_grid_list[(row, column)][0] != "" and not Server_grid_list[(row, column)][1]:
            Server_grid_list[(row, column)][1] = True


def creatplayersdata():
    Player_data = {"ClientName": "MultiMaster", "UserName": "", "Turn": True, "SpaceInHand": 7, "Hand": [], "Score": 0}
    Server_Players_info.append(Player_data)
    for _ in range(0, 3):
        Player_data = {"ClientName": "Multi", "UserName": "", "Turn": False, "SpaceInHand": 7, "Hand": [], "Score": 0}
        Server_Players_info.append(Player_data)


def modifiedPlayers_info(indPlayer, entry, info):
    if entry in Server_Players_info[indPlayer]:
        Server_Players_info[indPlayer][entry] = info


def getPlayerIndex(client):
    Username = client_user[client]
    index = -1
    for playerdata in Server_Players_info:
        index += 1
        if playerdata["UserName"] == Username:
            return index


def get_AI_number():
    nb = 0
    for playerdata in Server_Players_info:
        if playerdata["ClientName"] == "AI":
            nb += 1
    return nb


def creat_pool(dict):
    for letter in dict:
        for nbt in range(0, dict[letter][0]):
            Pool.append(letter)


def creat_grid():
    for row in range(0, 15):
        for column in range(0, 15):
            # first diagonal
            if row == column:
                if row == 7:
                    Server_grid_list[row, column] = ["", False, "MD"]
                elif row == 0 or row == 14:
                    Server_grid_list[row, column] = ["", False, "MT"]
                elif row == 6 or row == 8:
                    Server_grid_list[row, column] = ["", False, "LD"]
                elif row == 5 or row == 9:
                    Server_grid_list[row, column] = ["", False, "LT"]
                else:
                    Server_grid_list[row, column] = ["", False, "MD"]
            # second diagonal
            elif row == -column + 14:
                if row == 14 or row == 0:
                    Server_grid_list[row, column] = ["", False, "MT"]
                elif row == 6 or row == 8:
                    Server_grid_list[row, column] = ["", False, "LD"]
                elif row == 5 or row == 9:
                    Server_grid_list[row, column] = ["", False, "LT"]
                else:
                    Server_grid_list[row, column] = ["", False, "MD"]
            # other mot triple
            elif row == 7 and (column == 0 or column == 14):
                Server_grid_list[row, column] = ["", False, "MT"]
            elif column == 7 and (row == 0 or row == 14):
                Server_grid_list[row, column] = ["", False, "MT"]
            # other lettre double
            elif (row == 0 or row == 14) and (column == 3 or column == 11):
                Server_grid_list[row, column] = ["", False, "LD"]
            elif (column == 0 or column == 14) and (row == 3 or row == 11):
                Server_grid_list[row, column] = ["", False, "LD"]
            # other lettre triple
            elif (row == 1 or row == 13) and (column == 5 or column == 9):
                Server_grid_list[row, column] = ["", False, "LT"]
            elif (column == 1 or column == 13) and (row == 5 or row == 9):
                Server_grid_list[row, column] = ["", False, "LT"]
            # more lettre double
            elif (row == 2 or row == 12) and (column == 6 or column == 8):
                Server_grid_list[row, column] = ["", False, "LD"]
            elif (column == 2 or column == 12) and (row == 6 or row == 8):
                Server_grid_list[row, column] = ["", False, "LD"]
            # last lettre double
            elif (row == 3 or row == 11) and (column == 7):
                Server_grid_list[row, column] = ["", False, "LD"]
            elif (column == 3 or column == 11) and (row == 7):
                Server_grid_list[row, column] = ["", False, "LD"]
            # everything else
            else:
                Server_grid_list[row, column] = ["", False, "None"]


def fill_hand(indexPlayer):
    SpaceinHand = 7 - len(Server_Players_info[indexPlayer]["Hand"])
    Hand = take_in_pool(SpaceinHand, Pool)
    Server_Players_info[indexPlayer]["Hand"] += Hand
    Server_Players_info[indexPlayer]["SpaceInHand"] = 7 - len(Server_Players_info[indexPlayer]["Hand"])


def fill_all_hand():
    for index in range(0, len(Server_Players_info)):
        fill_hand(index)


def setTurn():
    modifiedPlayers_info(0, "Turn", True)
    for index in range(1, len(Server_Players_info)):
        modifiedPlayers_info(index, "Turn", False)


def rotateturn():
    """Rotate the turn and let the AI play if it is her turn"""

    end, winner = victory_condition(3)

    if end:
        if winner:
            scoretothewinner = 0
            indwinner = 0
            for indplayer in range(0, len(Server_Players_info)):
                if Server_Players_info[indplayer]["UserName"] == winner:
                    indwinner = indplayer

            for playerdata in Server_Players_info:
                scoretoremove = 0
                if playerdata["UserName"] != winner:
                    for letter in playerdata["Hand"]:
                        scoretoremove += Plan_Game[letter][1]
                    print(scoretoremove)
                    scoretothewinner += scoretoremove
                    playerdata["Score"] -= scoretoremove

            Server_Players_info[indwinner]["Score"] += scoretothewinner

        for playerdata in Server_Players_info:
            if playerdata["Turn"]:
                playerdata["Turn"] = False
        print(Server_Players_info)
        send_to_list(client_connected, (Server_Players_info, Pool), True)
        time.sleep(1)
        send_to_list(client_connected, "s.game.victory")
        return

    # Rotate
    for ind_playerdata in range(0, len(Server_Players_info)):
        if Server_Players_info[ind_playerdata]["Turn"]:

            Server_Players_info[ind_playerdata]["Turn"] = False
            if ind_playerdata == len(Server_Players_info) - 1:
                ind_playerdata = -1
            ind_playerdata += 1
            Server_Players_info[ind_playerdata]["Turn"] = True

            modifiedPlayers_info(ind_playerdata, "SpaceInHand", len(Server_Players_info[ind_playerdata]["Hand"]))

            # send data of Server_Players_info
            time.sleep(1)
            send_to_list(client_connected, (Server_Players_info, Pool), True)
            break
    # AI
    for ind_playerdata in range(0, len(Server_Players_info)):
        if Server_Players_info[ind_playerdata]["ClientName"][0] == "A" and Server_Players_info[ind_playerdata]["ClientName"][1] == "I":
            if Server_Players_info[ind_playerdata]["Turn"]:
                AIturn(ind_playerdata)
                rotateturn()


def victory_condition(nb):
    """Return True and a player has no more letter and if the pool is empty,
    or just True if it's been nb turn without any modification of the grid
    or just False"""

    if Tomanyturn[0] == nb:
        return True, False
    if len(Pool) == 0:
        for Playerdata in Server_Players_info:
            if len(Playerdata["Hand"]) == 0:
                return True, Playerdata["UserName"]
        Tomanyturn[0] += 1
        return False, False
    else:
        return False, False


def revers(word):
    """Revers a given word"""
    reversword = ""
    for ind_letter in range(len(word) - 1, -1, -1):
        reversword += word[ind_letter]
    return reversword


def word_on(lorc, nb, start, end):
    """Return the word on line/column in range of the start and the end"""
    word = ""
    if lorc == "l":
        for column in range(start, end + 1):
            letter = Server_grid_list[nb, column][0]  # give "" if noting, " " for a joker, "letter" for a letter
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                return False
    elif lorc == "c":
        for row in range(start, end + 1):
            letter = Server_grid_list[row, nb][0]
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                return False
    elif lorc == "l/c":
        return Server_grid_list[start, end][0]

    return word


def always_word_on(lorc, nb, start, end):
    """Return all the information (word) of a line/column in range of the start and the end"""
    word = ""
    if lorc == "l":
        for column in range(start, end + 1):
            letter = Server_grid_list[nb, column][0]  # give "" if noting, " " for a joker, "letter" for a letter
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                word += "$"
    elif lorc == "c":
        for row in range(start, end + 1):
            letter = Server_grid_list[row, nb][0]
            if "A" <= letter <= "Z" or letter == " ":
                word += letter
            else:
                word += "$"

    return word


def detection_of_additional_letter(lorc, nb, start, end):
    """Return the new information about a word if it is build using other letter than the one the player place"""
    newstar = start
    newend = end
    if end - start == 0 and lorc == "l":
        main_word = Server_grid_list[(nb, end)][0]

    elif end - start == 0 and lorc == "c":
        main_word = Server_grid_list[(start, nb)][0]

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


def joker(word):
    """Return a list of the postion of the jokers"""
    joker = []
    for pos_letter in range(0, len(word)):
        if word[pos_letter] == " ":
            joker.append(pos_letter)
    return joker


def newcreatedword(lorc, nb, start, end):
    """Return a list of new words creat by a given word"""
    if start == end:
        return [False]
    word = False
    auxiliary_words = []
    if lorc == "l":
        for column in range(start, end + 1):
            for chekrow in range(nb - 1, nb + 2, 2):
                if (chekrow, column) in Server_grid_list:
                    if not Server_grid_list[nb, column][1]:
                        if Server_Players_info[chekrow, column][0] != "":

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
                            word = False
        return auxiliary_words
    elif lorc == "c":
        for row in range(start, end + 1):
            for chekcolumn in range(nb - 1, nb + 2, 2):
                if (row, chekcolumn) in Server_grid_list:
                    if not Server_grid_list[row, nb][1]:
                        if Server_Players_info[row, chekcolumn][0] != "":

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
                            word = False

        return auxiliary_words


def value_of_a_word(lorc, nb, star, end):
    """Return the value of a word knowing his position on the grid"""
    value = 0
    word_multiplicator = 1
    letter_multiplicator = 1
    if lorc == "l":
        for column in range(star, end + 1):
            letter = Server_grid_list[nb, column][0]
            bonus = Server_grid_list[nb, column][-1]
            letter_value = Plan_Game[letter][1]
            if bonus == "MT":
                word_multiplicator *= 3
                Server_grid_list[nb, column][-1] = ""
            elif bonus == "MD":
                word_multiplicator *= 2
                Server_grid_list[nb, column][-1] = ""
            elif bonus == "LT":
                letter_multiplicator *= 3
                Server_grid_list[nb, column][-1] = ""
            elif bonus == "LD":
                letter_multiplicator *= 2
                Server_grid_list[nb, column][-1] = ""
            value += letter_value * letter_multiplicator
            letter_multiplicator = 1

    elif lorc == "c":
        for row in range(star, end + 1):
            letter = Server_grid_list[row, nb][0]
            bonus = Server_grid_list[row, nb][-1]
            letter_value = Plan_Game[letter][1]
            if bonus == "MT":
                word_multiplicator *= 3
                Server_grid_list[row, nb][-1] = ""
            elif bonus == "MD":
                word_multiplicator *= 2
                Server_grid_list[row, nb][-1] = ""
            elif bonus == "LT":
                letter_multiplicator *= 3
                Server_grid_list[row, nb][-1] = ""
            elif bonus == "LD":
                letter_multiplicator *= 2
                Server_grid_list[row, nb][-1] = ""
            value += letter_value * letter_multiplicator
            letter_multiplicator = 1

    return value * word_multiplicator


def left_place():
    for ind_playerdata in range(0, len(Server_Players_info)):
        if Server_Players_info[ind_playerdata]["UserName"] == "":
            return ind_playerdata


def allowed_name(name):
    """Check if the name is already used and if so it change it until it is different"""
    basename = name
    it = 1
    nameit = 1
    while it > 0:
        for client in client_user:
            if client_user[client] == basename:
                basename = name + str(nameit)
                it += 1
                nameit += 1
        it -= 1
    return basename


# ========================== AI function ======================
def AI_fill_hand(ordre):
    if ordre != 0:
        left_space = 7 - len(Server_Players_info[ordre]["Hand"])
        AI_hand = take_in_pool(left_space, Pool)
        Server_Players_info[ordre]["Hand"] += AI_hand


def AI_change_hand(ordre):
    if ordre != 0:
        for lettre in Server_Players_info[ordre]["Hand"]:
            Pool.append(lettre)
        Server_Players_info[ordre]["Hand"].clear()
        AI_fill_hand(ordre)


def AI_remove_in_hand(ordre, list_lettre):
    if ordre != 0:
        for lettre in list_lettre:
            if lettre != "":
                Server_Players_info[ordre]["Hand"].remove(lettre)


def AI_place_on_grid(lorc, nb, start, end, list_lettre):
    add_word_in_grid(lorc, nb, start, end, list_lettre, False)
    Tomanyturn[0] = 0


def AI(grid_list, Player_data, difficulty):
    '''Player_data = Players_info [!=0]["Hand"]
    return : play or change, lorc, nb, start, end [letter]'''
    return "change", None, None, None, None, None
    return "play", "c", 0, 0, 1, ["L", "A"]


def AIturn(ordre):
    time.sleep(0.5)
    action, lorc, nb, start, end, list_lettre = AI(Server_grid_list, Server_Players_info[ordre]["Hand"], 2)
    if action == "change":
        AI_change_hand(ordre)

    elif action == "play":
        total = 0
        AI_place_on_grid(lorc, nb, start, end, list_lettre)

        word, lorc, nb, newstart, newend = detection_of_additional_letter(lorc, nb, start, end)
        info = f"{lorc}/{nb}/{newstart}/{newend}/{word}"

        list_of_new_word = newcreatedword(lorc, nb, newstart, newend)

        fix_letter_on_grid()

        total += value_of_a_word(lorc, nb, start, end)
        for lorc, nb, start, end in list_of_new_word:
            total += value_of_a_word(lorc, nb, start, end)

        Server_Players_info[ordre]["Score"] += total
        scoreboardinfo = f"{Server_Players_info[ordre]}/{word}/{total}"

        send_to_list(client_connected, f"s.game.play.{info}")
        send_to_list(client_connected, f"s.game.scoreboard.{scoreboardinfo}")

        AI_remove_in_hand(ordre, list_lettre)
        AI_fill_hand(ordre)


# =================== Main Function of the server ===========================
def send_to_list(list_of_user, data, pickledata=False):
    """list_of_user = list of client_information
     data = data to send to the list"""

    # coding data to send
    if pickledata:
        info = b'p'
        pickleinfo = pickle.dumps(data)
        info += onlyHeader(str(pickleinfo), 19).encode(DECFOR) + pickleinfo

    else:
        info = objetHeader(data).encode(DECFOR)

    # send  data to a list of client
    for other_client in list_of_user:
        try:
            # send of the information
            other_client.send(info)
        except:
            pass


def client_connect(client, address):
    toomany = 0
    cc = True
    # First information send in the username
    Header = client.recv(20).decode(DECFOR)
    if Header:
        try:
            Header = int(Header.strip(" "))
        except:
            pass
        if type(Header) == type(0):
            Username = client.recv(Header).decode(DECFOR)
            Username = allowed_name(Username)
            print(f"[SERVER] : {address} is connected ender the name {Username}")
            client_connected.append(client)
            client_user[client] = Username

            modifiedPlayers_info(left_place(), "UserName", Username)

            # send to everyone

            info = ""
            for i in range(0, len(Server_Players_info)):
                if Server_Players_info[i]["UserName"] != "" and i == 3:
                    info += Server_Players_info[i]["UserName"] + "/"
                elif Server_Players_info[i]["UserName"] != "":
                    info += Server_Players_info[i]["UserName"] + "/"

            send_to_list(client_connected, f"s.lobby.connected.{info}")

    while cc:
        try:
            Header = client.recv(20).decode(DECFOR)
            if Header:

                try:
                    Header = int(Header.strip(" "))
                except:
                    pass

                if type(Header) == type(0):
                    Data = client.recv(Header).decode(DECFOR)
                    Data = Data.split(".")

                    if Data[0] == "c":

                        if Data[1] == "lobby":
                            if Data[2] == DATA_DISCONNECT:
                                info = ""
                                for i in range(0, len(Server_Players_info)):
                                    if Server_Players_info[i]["UserName"] != "" and i == 3:
                                        info += Server_Players_info[i]["UserName"] + "/"
                                    elif Server_Players_info[i]["UserName"] != "":
                                        info += Server_Players_info[i]["UserName"] + "/"

                                send_to_list(client_connected, f"s.lobby.connected.{info}")

                                print(f"[SERVER] : {client_user[client]} has disconnect.")
                                client.close()
                                client_connected.remove(client)
                                del client_user[client]
                                for playerdata in Server_Players_info:
                                    if not playerdata["UserName"] in info.split():
                                        playerdata["UserName"] = ""
                                cc = False
                                if threading.activeCount() == 1:
                                    # if there is not player connected
                                    Server_Players_info.clear()
                                    Pool.clear()

                            elif Data[2] == "add_ai":
                                # add an ai in the Server_Players_info
                                nb = get_AI_number() + 1

                                for playerdata in Server_Players_info:
                                    if playerdata["UserName"] == "":
                                        playerdata["ClientName"] = "AI"
                                        playerdata["UserName"] = f"AI {nb}"

                                        info = ""
                                        for i in range(0, len(Server_Players_info)):
                                            if Server_Players_info[i]["UserName"] != "" and i == 3:
                                                info += Server_Players_info[i]["UserName"] + "/"
                                            elif Server_Players_info[i]["UserName"] != "":
                                                info += Server_Players_info[i]["UserName"] + "/"
                                        send_to_list(client_connected, f"s.lobby.connected.{info}")

                                        print(f"[SERVER] : Add AI {nb}")
                                        break


                        elif Data[1] == "game":

                            if Data[2] == "change":

                                Hand = Data[3].split("/")
                                Hand.pop(-1)
                                for letter in Hand:
                                    # replace the letter in the pool
                                    Pool.append(letter)
                                Server_Players_info[getPlayerIndex(client)]["Hand"].clear()
                                # give the new hand to the player
                                fill_hand(getPlayerIndex(client))

                                # rotation of the turn and send new info
                                rotateturn()
                            elif Data[2] == "play":

                                info = Data[3]
                                playerinfo = Data[3].split("/")
                                list_letters = split_word(playerinfo[4])

                                add_word_in_grid(playerinfo[0], int(playerinfo[1]), int(playerinfo[2])
                                                 , int(playerinfo[3]), list_letters, True)

                                list_letter = playerinfo[-1].split("*")
                                scoreboardinfo = f"{client_user[client]}/{playerinfo[4]}/{playerinfo[5]}"

                                send_to_list(client_connected, f"s.game.play.{info}")
                                send_to_list(client_connected, f"s.game.scoreboard.{scoreboardinfo}")

                                Tomanyturn[0] = 0
                                P_index = getPlayerIndex(client)
                                Server_Players_info[P_index]["Score"] += int(playerinfo[5])
                                for letter in list_letter:
                                    if letter in Server_Players_info[P_index]["Hand"]:
                                        Server_Players_info[P_index]["Hand"].remove(letter)

                                fill_hand(P_index)
                                modifiedPlayers_info(P_index, "SpaceInHand", len(Server_Players_info[P_index]["Hand"]))
                                rotateturn()



                            elif Data[2] == "rotaturn":
                                rotateturn()


                            elif Data[2] == "launch":
                                if getPlayerIndex(client) == 0:
                                    # initialisation of the grid
                                    creat_grid()
                                    # creation of the pool
                                    creat_pool(Plan_Game)
                                    # initialisation of all the hand
                                    fill_all_hand()
                                    # set the players Turn
                                    setTurn()
                                    GameStart[0] = True
                                    print("Starting Game")
                                    send_to_list(client_connected, (Server_Players_info, Pool), True)
        except:
            print("[Server] : Fail to receive message header")
            send_to_list(client_connected, (Server_Players_info, Pool), True)
            toomany += 1
            if toomany > 100:
                client.close()
                client_connected.remove(client)
                del client_user[client]



showing_cmd = {"/pool":["Show pool state", f"Pool state : {Pool}", False]
    ,"/poolsize":["Show the number of letter in the pool", f"Number of letter in the pool : {len(Pool)}", True]
    ,"/players":["Show the name of the players connected", "Players connected : ", True]
    ,"/players_info":["Show the players states", "Players info : ", False]
    ,"/displaygrid":["Show the grid", "Grid : ", True]}
active_cmd = {"/addinpool","/addletteringrid","/removeinpool","/removeingrid","/addinhand","/removeinhand","/setscore"
              ,"/end","/kick"}

def commandreceiver():
    while True:
        inp = input()
        if inp != "":
            if inp[0] == "/":
                cmd_input = inp.split(" ")
                if inp == "/help":
                    for cmd in showing_cmd:
                        if showing_cmd[cmd][-1]:
                            print(f"{cmd} : {showing_cmd[cmd][0]}")

                elif inp == "/pool":
                    print(f"Pool state : {Pool}")

                elif inp == "/poolsize":
                    print(f"Number of letter in the pool : {len(Pool)}")

                elif inp == "/players":
                    print("Players connected : ", end="")
                    for client in client_user:
                        print(client_user[client])
                    print()

                elif inp == "/players_info":
                    print("Players info : ", end="")
                    for playerdata in Server_Players_info:
                        print(playerdata)
                    print()
                elif inp == "/displaygrid":
                    for row in range(0, 14):
                        for column in range(0,14):
                            letter = Server_grid_list[row, column][0]
                            if letter != "":
                                print(f"{letter}", end="")
                            else:
                                print(f"-", end="")
                        print()

                elif cmd_input[0] == "/addinpool" and len(cmd_input) == 2:
                    if "A" <= cmd_input[1] <= "Z":
                        Pool.append(cmd_input[1])
                elif cmd_input[0] == "/addletteringrid" and len(cmd_input) == 4:
                    if "A" <= cmd_input[1] <= "Z" and (0 <= int(cmd_input[2]) <= 14 and 0 <= int(cmd_input[3]) <= 14) and GameStart[0]:
                        send_to_list(client_connected, f"s.game.play.l/{int(cmd_input[2])}/{int(cmd_input[3])}/{int(cmd_input[3])}/{cmd_input[1]}")
                elif cmd_input[0] == "/removeinpool" and len(cmd_input) == 2:
                    if cmd_input[1] in Pool:
                        Pool.remove(cmd_input[1])
                elif cmd_input[0] == "/addinhand" and len(cmd_input) == 4:
                    try:
                        letter = cmd_input[1]
                        pos = int(cmd_input[2])
                        playerindex = int(cmd_input[3])
                        if "A" <= letter <= "Z" and 0 <= pos <= 6 and 0 <= playerindex <= 3 and GameStart:
                            Server_Players_info[playerindex]["Hand"][pos] == letter

                    except:
                        print("/addinhand letter position playerindex")
                elif cmd_input[0] == "/update":
                    send_to_list(client_connected, (Server_Players_info, Pool), True)

                elif cmd_input[0] == "/setscore" and len(cmd_input) == 3:
                    try:
                        score = int(cmd_input[1])
                        playerindex = int(cmd_input[2])
                        if 0 <= playerindex <= 3 and GameStart:
                            Server_Players_info[playerindex]["Score"] == score
                    except:
                        print("/setscore score playerindex")
                elif cmd_input[0] == "/end":
                    send_to_list(client_connected, "s.game.victory")
                else:
                    print(f"[SERVER] : None valid command for more information /help")

            else:
                print(f"[SERVER] : None valid command for more information /help")


def start():
    server.listen()
    print(f"[SERVER] : Server online.")
    print(f"[SERVER] : Connected port : {PORT}")
    print(f"[SERVER] : IP Address  : {SERVER_IP}")
    print(f"[SERVER] : Active Connection  : 0/{nb_total_cc}")
    threadcmd = threading.Thread(target=commandreceiver)
    threadcmd.start()

    while True:
        client, address = server.accept()
        threadclient = threading.Thread(target=client_connect, args=(client, address))
        threadclient.start()
        time.sleep(1)
        print(f"[SERVER] : Active Connection : {threading.activeCount() - 2}/{nb_total_cc}")



print("[SERVER] : Starting")
creatplayersdata()
start()
