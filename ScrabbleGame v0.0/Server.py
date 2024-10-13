import socket
import threading
import IPFonction
import urllib.request
import time
import pickle
from gestion_de_fichier import *
import random



# Info Serveur
PORT = 7564
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_ADDRESS = (SERVER_IP, PORT)
nb_total_cc = 4                                  # Nombre max de client connecté
nb_cc = threading.activeCount()-1                # Nombre de client connecté
client_connected = []
client_user = {}
DECFOR = "utf-8"
DATA_DISCONNECT = "!DECONNECT!"                             # Message indiquant une déconnection au serveur

# Game Variable
Server_Players_info = []
Server_grid_list = []
Plan_Game = lire("lettres du scrabble", "info_scrabble.txt", "dictionnaire_list")
Pool = []
Tomanyturn = [0]

# Initialisation du serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SERVER_ADDRESS)

def public_ip_adresse() :
    # Get the public ip
    public_ip_brut = str(urllib.request.urlopen("http://ip.jsontest.com/").read())
    L = public_ip_brut.split()
    public_ip = ""
    for i in range (0,len(L[-1])):
        if (L[-1])[i] in {".","0","1","2","3","4","5","6","7","8","9"} :
            public_ip += (L[-1])[i]

    return public_ip

# Local / Global
while True:
    server_type = input("Connection à un serveur local ou global ?   ")
    if server_type.lower() == "local":
        break

    elif server_type.lower() == "global":
        print(f"L'ip du server est {IPFonction.code(public_ip_adresse())}")
        print(f"N'oubliez pas d'ouvrir le port 7564 sous l'addresse {SERVER_IP}")
        break

    else:
        print("Ecrire 'local' pour une connection en local ou 'global' pour une connection avec le reste du monde.")


def creatplayersdata():
    Player_data = {"ClientName": "MultiMaster", "UserName": "", "Turn": True, "SpaceInHand": 0, "Hand": [], "Score": 0}
    Server_Players_info.append(Player_data)
    for _ in range(0, 3):
        Player_data = {"ClientName": "Multi", "UserName": "", "Turn": False, "SpaceInHand": 0, "Hand": [], "Score": 0}
        Server_Players_info.append(Player_data)

def modifiedPlayers_info(indPlayer, entry, info):
    if entry in Server_Players_info[indPlayer]:
        Server_Players_info[indPlayer][entry] = info


def creat_pool(dict):
    for letter in dict:
        for nbt in range(0, dict[letter][0]):
            Pool.append(letter)


def take_in_pool(x, Pool):
    '''Take the Pool list, and return x random letters and remove theme from the pool'''
    L = []
    it = 0
    while True:

        letter = chr(random.randint(ord("A"), ord("Z")+1))
        if letter == chr(ord("Z")+1):
            letter = " "
        if len(Pool) == 0:
            return L
        elif letter in Pool:
            Pool.remove(letter)
            L.append(letter)
            it += 1
            if it == x:
                return L


def getPlayerIndex(client):
    Username = client_user[client]
    index = -1
    for playerdata in Server_Players_info:
        index += 1
        if playerdata["UserName"] == Username:
            return index


def fill_hand(indexPlayer):
    SpaceinHand = len(Server_Players_info[indexPlayer]["Hand"]) + 7
    Hand = take_in_pool(SpaceinHand, Pool)
    Server_Players_info[indexPlayer]["Hand"] = Hand
    Server_Players_info[indexPlayer]["SpaceInHand"] = 7


def fill_all_hand():
    for index in range(0, len(Server_Players_info)):
        fill_hand(index)

def setTurn():
    modifiedPlayers_info(0, "Turn", True)
    for index in range(1, len(Server_Players_info)):
        modifiedPlayers_info(index, "Turn", False)


def rotateturn():
    '''Rotate the turn and let the AI play if it is her turn'''

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
                    scoretothewinner += scoretoremove
                    playerdata["Score"] -= scoretoremove

            Server_Players_info[indwinner]["Score"] += scoretothewinner

            for playerdata in Server_Players_info:
                if playerdata["Turn"]:
                    playerdata["Turn"] = False

            send_to_list(client_connected, (Server_Players_info, Pool), True)

            server.send(b"s.game.victory")
        return

    # Rotate
    for ind_playerdata in range(0, len(Server_Players_info)):
        if Server_Players_info[ind_playerdata]["Turn"]:

            Server_Players_info[ind_playerdata]["Turn"] = False
            if ind_playerdata == len(Server_Players_info)-1:
                ind_playerdata = -1
            ind_playerdata += 1
            Server_Players_info[ind_playerdata]["Turn"] = True



            modifiedPlayers_info(ind_playerdata, "SpaceInHand", len(Server_Players_info[ind_playerdata]["Hand"]))


            # send data of Server_Players_info
            send_to_list(client_connected, (Server_Players_info, Pool), True)
            break




def victory_condition(nb):
    '''Return True and the player who has no more letter,
    or just True if it's been nb turn without any modification of the grid
    or just False'''

    if Tomanyturn[0] == nb:
        return True, None
    if len(Pool) == 0:
        for Playerdata in Server_Players_info:
            if len(Playerdata["Hand"]) == 0:
                return True, Playerdata["UserName"]
        Tomanyturn[0] += 1
    else:
        return False, None


def send_to_list(list_of_user, data, pickledata=False):
    '''list_of_user = list of client_information
     data = data to send to the list'''

    # coding data to send
    if pickledata:
        info = b''
        info += ("p" * 20).encode(DECFOR)
        info += pickle.dumps(data)


    else:
        info = objetHeader(data).encode(DECFOR)

    # send  data to a list of client
    for other_client in list_of_user:
        try:
            # send of the information

            other_client.send(info)

        except :
            pass


# Main function
def client_connect(client, address):

    cc = True
    # First inforamtion send in the username
    Header = client.recv(20).decode(DECFOR)
    if Header:
        try:
            Header = int(Header.strip(" "))
        except:
            pass
        if type(Header) == type(0):
            Username = client.recv(Header).decode(DECFOR)
            print(f"[SERVER] : {address} est connecté sous le nom {Username}")
            client_connected.append(client)
            client_user[client] = Username

            modifiedPlayers_info(len(client_connected)-1, "UserName", Username)

            # send to everyone

            info = ""
            for i in range(0, len(Server_Players_info)):
                if Server_Players_info[i]["UserName"] != "" and i == 3:
                    info += Server_Players_info[i]["UserName"]
                elif Server_Players_info[i]["UserName"] != "":
                    info += Server_Players_info[i]["UserName"]+"/"



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
                                        info += Server_Players_info[i]["UserName"]
                                    elif Server_Players_info[i]["UserName"] != "":
                                        info += Server_Players_info[i]["UserName"] + "/"

                                send_to_list(client_connected, f"s.lobby.connected.{info}")

                                print(f"[SERVER] : {client_user[client]} a été déconnecté.")
                                client.close()
                                client_connected.remove(client)
                                del client_user[client]
                                for playerdata in Server_Players_info:
                                    if not playerdata["UserName"] in info.split():
                                        playerdata["UserName"] = ""
                                cc = False
                                if threading.activeCount() == 1:
                                    Server_Players_info.clear()
                                    Pool.clear()


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
                                scoreboardinfo = f"{client_user[client]}/{playerinfo[4]}/{playerinfo[5]}"

                                for other_client in client_connected:  # Envoi de l'information reçu au autre
                                    if other_client != client:
                                        server.send(objetHeader(f"s.game.play.{info}").encode(DECFOR))
                                        server.send(objetHeader(f"s.game.scoreboard.{scoreboardinfo}").encode(DECFOR))
                                Tomanyturn[0] = 0
                                P_index = getPlayerIndex(client)
                                Server_Players_info[P_index]["Score"] += playerinfo[5]
                                fill_hand(P_index)
                                rotateturn()



                            elif Data[2] == "rotaturn":
                                rotateturn()


                            elif Data[2] == "launch":
                                if getPlayerIndex(client) == 0:
                                    # creation of the pool
                                    creat_pool(Plan_Game)
                                    # initialisation of all the hand
                                    fill_all_hand()
                                    # set the players Turn
                                    setTurn()
                                    print("Starting Game")
                                    send_to_list(client_connected, (Server_Players_info, Pool), True)




        except:
            client.close()
            client_connected.remove(client)
            del client_user[client]
            print(f"[SERVER] : Un client a été déconnecté brutalement.")
            print(f"[SERVER] : Restart is require")
            cc = False

def start():

    server.listen()
    print(f"[SERVER] : Serveur en ligne.")
    print(f"[SERVER] : Port connecté : {PORT}")
    print(f"[SERVER] : Addresse IP : {SERVER_IP}")
    print(f"[SERVER] : Connection active : 0/{nb_total_cc}")

    while threading.activeCount()-1 <= nb_total_cc:
        client, address = server.accept()
        thread = threading.Thread(target=client_connect, args=(client, address))
        thread.start()
        time.sleep(1)
        print(f"[SERVER] : Connection active : {threading.activeCount()-1}/{nb_total_cc}")


def objetHeader(w):
    headersize = 20
    Headerinfo = str(len(w))
    return " "*(headersize-len(Headerinfo))+Headerinfo + w

def onlyHeader(w):
    headersize = 20
    Headerinfo = str(len(w))
    return " " * (headersize - len(Headerinfo)) + Headerinfo



print("[SERVER] : Starting")
creatplayersdata()

start()