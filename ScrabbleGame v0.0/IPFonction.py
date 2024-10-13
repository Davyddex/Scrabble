def splitw(w):
    L = []
    for i in range(0, len(w)):
        L.append(w[i])
    return L

def decaler(w, nb):
    m = ord(w) + nb
    if m > ord("j"):
        m = m - ord("j") - 1 + ord("a")
    elif m < ord("a"):
        m = m - ord("a") + 1 + ord("j")
    return chr(m)

def decode(code_ip):
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
    decal = 4
    L = ip.split(".")
    code_ip = ""

    for i in range(0, len(L)):
        # 000
        if len(L[i]) == 3:
            diz = int((splitw(L[i])[0])) * 10
            dec = int(splitw(L[i])[1])
            code_ip += chr(diz + dec + 97)

            a = chr(int(splitw(L[i])[2]) + 97)
            code_ip += decaler(a, decal)

        # 00
        elif len(L[i]) == 2:
            code_ip += "-"
            diz = int((splitw(L[i])[0]))
            code_ip += chr(diz + 97)

            dec = chr(int(splitw(L[i])[1]) + 97)
            code_ip += decaler(dec, decal)


        # 0
        elif len(L[i]) == 1:
            a = chr(int(splitw(L[i])[0]) + ord("K"))
            code_ip += a

    return(code_ip)

