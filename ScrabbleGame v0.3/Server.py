import socket                        # For server management
import threading                     # To be able to do multiple thing
import time                          # To slow down the progression of the code
import pickle                        # To easily send List/Dictionary
from File_Manager import *           # To be able save and read files
from Common_Function import *        # Store function that are common to Server.py and CoreScrabble.py

SERVER_IP = socket.gethostbyname(socket.gethostname())


# Local / Global
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


# Info Server
PORT = 7564

SERVER_ADDRESS = (SERVER_IP, PORT)
nb_total_cc = 4                                  # total client that can connect on the serser
nb_cc = 0                                        # number of client connected
client_connected = []                            # Storing the client address of the client connected
client_user = {}                                 # Associate Client and there UserName
DECFOR = "utf-8"
DATA_DISCONNECT = "!DECONNECT!"                  # Message to deconnect to the server

# Game Variable
Server_Players_info = []                         # Store all the important information about the player
Server_grid_list = []                            #
# Store the basic pool rule of a scrabble game
Plan_Game = lire("lettres du scrabble", "info_scrabble.txt", "dictionnaire_list")
Pool = []                                        # Pool of all the piece of the game
Tomanyturn = [0]                                 # Store the number of turn pass without any changes to the game

# Initialisation of the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SERVER_ADDRESS)


# ===================Scrabble Function of the Server======================
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


def getPlayerIndex(client):
    Username = client_user[client]
    index = -1
    for playerdata in Server_Players_info:
        index += 1
        if playerdata["UserName"] == Username:
            return index


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
            time.sleep(1)
            send_to_list(client_connected, (Server_Players_info, Pool), True)
            time.sleep(1)
            send_to_list(client_connected, "s.game.victory")
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
            time.sleep(1)
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
        info = b'p'
        pickleinfo = pickle.dumps(data)
        info += onlyHeader(str(pickleinfo)).encode(DECFOR) + pickleinfo

    else:
        info = objetHeader(data).encode(DECFOR)
    # send  data to a list of client
    for other_client in list_of_user:
        try:
            # send of the information
            other_client.send(info)
        except :
            pass


# =================== Main Function of the server ===========================
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
                    info += Server_Players_info[i]["UserName"]+"/"
                elif Server_Players_info[i]["UserName"] != "":
                    info += Server_Players_info[i]["UserName"]+"/"



            send_to_list(client_connected, f"s.lobby.connected.{info}")


    while cc:

            Header = client.recv(20).decode(DECFOR)
            if Header:

                for pladata in Server_Players_info:
                    print(pladata)
                print(Pool)
                print()

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

                                send_to_list(client_connected, f"s.game.play.{info}")
                                send_to_list(client_connected, f"s.game.scoreboard.{scoreboardinfo}")

                                Tomanyturn[0] = 0
                                P_index = getPlayerIndex(client)
                                Server_Players_info[P_index]["Score"] += int(playerinfo[5])
                                for letter in playerinfo[4]:
                                    if letter in Server_Players_info[P_index]["Hand"]:
                                        Server_Players_info[P_index]["Hand"].remove(letter)

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




            


def start():

    server.listen()
    print(f"[SERVER] : Server online.")
    print(f"[SERVER] : Connected port : {PORT}")
    print(f"[SERVER] : IP Address  : {SERVER_IP}")
    print(f"[SERVER] : Active Connection  : 0/{nb_total_cc}")



    while True:
        client, address = server.accept()
        thread = threading.Thread(target=client_connect, args=(client, address))
        thread.start()
        time.sleep(1)
        print(f"[SERVER] : Active Connection : {threading.activeCount()-1}/{nb_total_cc}")



print("[SERVER] : Starting")
creatplayersdata()
start()
