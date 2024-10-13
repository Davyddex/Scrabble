import random                # Add some random when the piece are pick
import urllib.request        # Url reader


def split_word(word):
    """word --> List of letter"""
    L = []
    for letter in word:
        L.append(letter)
    return L


def decaler(w, nb):
    """Shift a letter by nb"""
    m = ord(w) + nb
    if m > ord("j"):
        m = m - ord("j") - 1 + ord("a")
    elif m < ord("a"):
        m = m - ord("a") + 1 + ord("j")
    return chr(m)


def decode(code_ip):
    """Use to decode the server IP"""
    list_ip = []
    ip = ""
    it = 0
    double = False
    for i in range(0, len(code_ip)):
        if "K" <= code_ip[i] <= "T" and it != 2:
            list_ip.append(str(ord(code_ip[i])-ord("K")))
            list_ip.append(".")

        elif "a" <= code_ip[i] <= "z" or code_ip[i] == "-":
            it += 1
            if code_ip[i] == "-":
                double = True
                it = 0
            if double and it == 2:
                list_ip.append(str(ord(code_ip[i-1]) - ord("a")))
                list_ip.append(str(ord(code_ip[i]) - ord("a") - 4))
                list_ip.append(".")
                it = 0
                double = False


            elif not(double) and it == 2:
                if "a" <= code_ip[i-1] <= "j" :
                    list_ip.append("0")
                    list_ip.append(str(ord(code_ip[i-1]) - ord("a")))
                    list_ip.append(str(ord(decaler(code_ip[i], -4))- ord("a")))
                    list_ip.append(".")
                    it = 0
                else :
                    list_ip.append(str(ord(code_ip[i - 1]) - ord("a")))
                    list_ip.append(str(ord(decaler(code_ip[i], -4))- ord("a")))
                    list_ip.append(".")
                    it = 0
    list_ip.pop()

    for j in list_ip:
        ip += j

    return ip


def code(ip):
    """Use to code the server IP"""
    decal = 4
    L = ip.split(".")
    code_ip = ""

    for i in range(0, len(L)):
        # 000
        if len(L[i]) == 3:
            diz = int((split_word(L[i])[0])) * 10
            dec = int(split_word(L[i])[1])
            code_ip += chr(diz + dec + 97)

            a = chr(int(split_word(L[i])[2]) + 97)
            code_ip += decaler(a, decal)

        # 00
        elif len(L[i]) == 2:
            code_ip += "-"
            diz = int((split_word(L[i])[0]))
            code_ip += chr(diz + 97)

            dec = chr(int(split_word(L[i])[1]) + 97)
            code_ip += decaler(dec, decal)


        # 0
        elif len(L[i]) == 1:
            a = chr(int(split_word(L[i])[0]) + ord("K"))
            code_ip += a

    return(code_ip)


def take_in_pool(x, Pool):
    """Take the Pool list, and return x random letters and remove theme from the pool"""
    if x == 0:
        return []
    L = []
    it = 0
    nbvoyelle = 0
    tomanyloop = 0
    while True:
        if len(Pool) == 0:
            return L
        else:
            letter = random.choice(Pool)
            Pool.remove(letter)
            L.append(letter)
            it += 1

            if it == x:
                # protection against bad luck
                if tomanyloop == 3:
                    # stay in the loop for to long
                    return L
                for letter in L:
                    if letter in ["A", "E", "U", "I", "O"]:
                        nbvoyelle += 1
                if nbvoyelle >= 2:
                    # if there is enough voyelle
                    return L
                elif x >= 5:
                    # protection against bad luck only apply for big draw
                    for letter in L:
                        Pool.append(letter)
                    L = []
                    it = 0
                    tomanyloop += 1
                else:
                    return L


def objetHeader(w):
    """Return the word and his header according to his length"""
    headersize = 20
    Headerinfo = str(len(w))
    return " " * (headersize-len(Headerinfo)) + Headerinfo + w


def onlyHeader(w):
    """Return only the header according to the length a word"""
    headersize = 19
    Headerinfo = str(len(w))
    return " " * (headersize - len(Headerinfo)) + Headerinfo


def public_ip_adresse() :
    """Use to get the Global server address"""
    public_ip_brut = str(urllib.request.urlopen("http://ip.jsontest.com/").read())
    L = public_ip_brut.split()
    public_ip = ""
    for i in range (0,len(L[-1])):
        if (L[-1])[i] in {".","0","1","2","3","4","5","6","7","8","9"} :
            public_ip += (L[-1])[i]

    return public_ip