import threading as thr
import os
#FONCTION DE LECTURE
#la fonction prends ligne ligne par ligne et si elle trouve ce qu'elle veut elle crée une lsite avec le nom et le contenu et renvoie le contenu
#écriture spécifique
'''nom£contenu'''

def rechercher(string,doc):
    
    fichier=open(doc)
    for ligne in fichier:
        L=ligne.split('Â£')
        for indice in (0,len(L)):
            
            try:
                if string==L[indice]:
                    élémentrecherché=L[indice+1]
                    fichier.close()
                    return élémentrecherché
                else:
                    continue
            except:
                pass
    fichier.close()
    return None


#vérification du fait que le contenu est un chiffre
def rechercher_nb(string,doc):
    contenu=rechercher(string,doc)
    if contenu!=None:
        try:
            contenuchiffré=int(contenu)
            return contenuchiffré
        except:
            return None
            
    else:
        return None

#création d'une liste avec le contenu
#écriture spéfique
'''contenu1¤contenu2¤contenu3'''
#autre cas '''liste de liste gérée par § pour separer les éléments d'un autre liste


def rechercher_list(string,doc):
    k=rechercher(string,doc)
    if k!=None:
        l=k.split('Â¤')
        for indice in range (0,len(l)):
            liste_int=l[indice].split('$')
            test_string=''
            for élément in liste_int:
                test_string+=élément
            if test_string!=l[indice]:
                l[indice]=liste_int
            
                
        
        return l
    else:
        return None

#les liste de dictionnaires
def rechercher_list_dico(string,doc):
    k=rechercher_list(string,doc)
    if k!=None:
        for élé in range (0,len(k)):
            if type(k[élé])==type([]):
                D={}
                for ind in range(0,len(k[élé])):
                    if ind%2==0:
                        D[k[élé][ind]] = str(k[élé][ind+1])
                
                for entrée in D:
                    test_string=D[entrée].split('-')
                    if (D[entrée]!=''.join(test_string)):
                            D[entrée]=test_string
                    k[élé]=D
        return k
    else:
        return None
    
                
                      
        
                             
#vérification des nombres
def rechercher_list_nb(string,doc):
    l=rechercher_list(string,doc)
    if l!=None:
        for i in range (0,len(l)):
            try:
                l[i]=int(l[i])
            except:
                return None
        return l
    else:
        return None
    
    
#création d'un dictionnaire avec un contenu de type list
#écriture spécifique
'''[contenu1µcontenu2]¤[contenu1'µcontenu2']'''
def rechercher_dict(string,doc):
    l=rechercher_list(string,doc)
    if l!=None:
        L=[]
        for i in l:
            L.append(i.split('Âµ'))
        D={}
        for k in L:
            D[k[0]]=k[1]
        return D
    else:
        return None


#vérification des nb
def rechercher_dict_nb(string,doc):
    l=rechercher_list(string,doc)
    if l!=None:
        L=[]
        for i in l:
            L.append(i.split('Âµ'))
        D={}
        for k in L:
            try:
                o=int(k[1])
                D[k[0]]=o
            except:
                return None
        return D
    else:
        return None

#utilisation de liste dans les dico pour créer de dico à plusieurs entrées
#écriture spécifique
'''utilisation de § pour séparerer les contenu des liste'''

def rechercher_dict_list(string,doc):
    D=rechercher_dict(string,doc)
    listeentrée=[]
    if D!=None:
        for key in D:
            listeentrée.append(key)
        for entrée in listeentrée:
            D[entrée]=D[entrée].split('Â§')
            try:
                for valeur in range(0,len(D[entrée])):
                    stringtesté=int(D[entrée][valeur])
                    D[entrée][valeur]=stringtesté
            except:
                pass
                
        return D
    else:
        return None


#gestion de couples de deux infos
def couples(liste):
    string=''.join(liste)
    liste=string.split(',')
    try:
        
        a1=int(liste[0])
        a2=int(liste[1])
    except:
        a1=liste[0]
        a2=liste[1]
    return (a1,a2)
#correction d'un dicco pour géré des tupples de 2
def correction(Dico):
    d={}
    for key in Dico:
        L=list(key)
        
        if L[0]=='(' and L[len(L)-1]==')':
            L.remove(')')
            L.remove('(')
            L.remove(' ')
            tup=couples(L)
            d[tup]=Dico[key]
        else:
            d[key]=Dico[key]
            
                   
    return d

#correction de la présence de string pour false et pour true
def correction_bool(objet_acorrigé):
    if type(objet_acorrigé)==type('t'):
        if objet_acorrigé=='False':
            return False
        elif objet_acorrigé=='True':
            return True
    elif type(objet_acorrigé)==type([]):
        for i in range(0,len(objet_acorrigé)):
            if type(objet_acorrigé[i])==type('t'):
                if objet_acorrigé[i]=='False':
                    objet_acorrigé[i]=False
                elif objet_acorrigé[i]=='True':
                    objet_acorrigé[i]=True
            elif type(objet_acorrigé[i])==type([]):
                for e in range (0,len(objet_acorrigé[i])):
                    if objet_acorrigé[i][e]=='False':
                        objet_acorrigé[i][e]=False
                    elif objet_acorrigé[i][e]=='True':
                        objet_acorrigé[i][e]=True
            elif type(objet_acorrigé[i])==type({}):
                for key in objet_acorrigé[i]:
                    ver=objet_acorrigé[i][key]
                    if type(ver)==type('t'):
                        if ver=='False':
                            objet_acorrigé[i][key]=False
                        elif ver=='True':
                            objet_acorrigé[i][key]=True
                    elif type(ver)==type([]):
                        for k in range(0,len(ver)):
                            if ver[k]=='False':
                                objet_acorrigé[i][key][k]=False
                            elif ver[k]=='True':
                                objet_acorrigé[i][key][k]=True
    elif type(objet_acorrigé)==type({}):
        for key in objet_acorrigé:
            ver=objet_acorrigé[key]
            if type(ver)==type('t'):
                if ver=='False':
                    objet_acorrigé[key]=False
                elif ver=='True':
                    objet_acorrigé[key]=True
            elif type(ver)==type([]):
                for e in range (0,len(objet_acorrigé[key])):
                    if objet_acorrigé[key][e]=='False':
                        objet_acorrigé[key][e]=False
                    elif objet_acorrigé[key][e]=='True':
                        objet_acorrigé[key][e]=True
    return objet_acorrigé
            
        
                
                    
        
        
def lire(recherche,doc,typ='string'):
    '''typ accepted: 'string','nombre','liste','liste_nombre','dictionnaire','dictionnaire_nombre','dictionnaire_list','list_dictionnaire'.'''
    if typ=='string':
        return correction_bool(rechercher(recherche,doc))        
    elif typ=='nombre' :
        return rechercher_nb(recherche,doc)
    elif typ=='liste' :
        return correction_bool(rechercher_list(recherche,doc))
    elif typ=='liste_nombre':
        return rechercher_list_nb(recherche,doc)
    elif typ=='dictionnaire':
        return correction_bool(correction(rechercher_dict(recherche,doc)))
    elif typ=='dictionnaire_nombre':
        return correction(rechercher_dict_nb(recherche,doc))
    elif typ=='dictionnaire_list':
        return correction_bool(correction(rechercher_dict_list(recherche,doc)))
    elif typ=='list_dictionnaire':
        return correction_bool(rechercher_list_dico(recherche,doc))
    else:
        return None
        
    



#FONCTION D'ÉCRITURE

#écriture du nom et de l'info avec le format nom£info
#l'info est un string
    
def écrire_string(nom_fichier,nom_info,info,format_fichier='txt'):
    try:
        format_fichier=str(format_fichier)
        nom_utile=nom_fichier+'.'+format_fichier
        fichier=open(nom_utile)
        fichier.close()
        fichier=open(nom_utile,'a')
        aécrire=nom_info+'Â£'+info
        fichier.write('Â£\n')
        fichier.write(aécrire)
        fichier.close()


    except:
        format_fichier=str(format_fichier)
        nom_utile=nom_fichier+'.'+format_fichier
        fichier=open(nom_utile,'w')
        aécrire=nom_info+'Â£'+info
        fichier.write('Â£\n')
        fichier.write(aécrire)
        fichier.close()

#adaptation de l'info liste en string sous le format e1Â¤e2Â¤e3Â¤e4
def écrire_list(nom_fichier,nom_info,info_list,format_fichier='txt'):
    info=''
    for indélé in range (0,len(info_list)):
        if indélé==len(info_list)-1:
            if type (info_list[indélé])==type([]):
                str_list=''
                for élé in range (0,len(info_list[indélé])):
                    if élé!=len(info_list[indélé])-1:
                        str_list=str_list+str(info_list[indélé][élé])+'$'
                    else:
                         str_list=str_list+str(info_list[indélé][élé])
                info=info+str_list
            elif type(info_list[indélé])==type({}):
                List_dictionnaire=[]
                for entrée in info_list[indélé]:
                    List_dictionnaire.append(entrée)
                    List_dictionnaire.append(info_list[indélé][entrée])              #[{'A':345,'H':475},{'T':89}]
                str_list=''
                for élé in range (0,len(List_dictionnaire)):
                    if élé!=len(List_dictionnaire)-1:
                        if type(List_dictionnaire[élé])==type([]):
                            str_list_int=''
                            for élé2 in range (0,len(List_dictionnaire[élé])):
                                if élé2!=len(List_dictionnaire[élé])-1:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])+'-'    #'ZszS' sert à séparer les élément d'une liste qui est dans un dictionnaire lui-même dans une liste
                                else:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])
                            str_list=str_list+str(str_list_int)+'$'
                                    
                        else:
                            str_list=str_list+str(List_dictionnaire[élé])+'$'
                    else:
                        if type(List_dictionnaire[élé])==type([]):
                            str_list_int=''
                            for élé2 in range (0,len(List_dictionnaire[élé])):
                                if élé2!=len(List_dictionnaire[élé])-1:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])+'-'    #'ZszS' sert à séparer les élément d'une liste qui est dans un dictionnaire lui-même dans une liste
                                else:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])
                            str_list=str_list+str_list_int

                        else:
                            str_list=str_list+str(List_dictionnaire[élé])
            #else:
                #str_list=str_list+str(info_list[indélé])
                
                info=info+str_list
                
            else:
                info=info+str(info_list[indélé])
        
        else:
            if type(info_list[indélé])==type([1,8]):
                str_list=''
                for élé in range (0,len(info_list[indélé])):
                    if élé!=len(info_list[indélé])-1:
                        str_list=str_list+str(info_list[indélé][élé])+'$'
                    else:
                         str_list=str_list+str(info_list[indélé][élé])
                info=info+str_list+'Â¤'
            elif type(info_list[indélé])==type({}):
                List_dictionnaire=[]
                for entrée in info_list[indélé]:
                    List_dictionnaire.append(entrée)
                    List_dictionnaire.append(info_list[indélé][entrée])
                str_list=''
                for élé in range (0,len(List_dictionnaire)):
                    if élé!=len(List_dictionnaire)-1:
                        if type(List_dictionnaire[élé])==type([]):
                            str_list_int=''                               #[{'A':345,'H':475},{'T':89}]
                            for élé2 in range (0,len(List_dictionnaire[élé])):
                                if élé2!=len(List_dictionnaire[élé])-1:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])+'-'    #'ZszS' sert à séparer les élément d'une liste qui est dans un dictionnaire lui-même dans une liste
                                else:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])
                            str_list=str_list+str_list_int+'$'
                                    
                        else:
                            str_list=str_list+str(List_dictionnaire[élé])+'$'
                    else:
                        if type(List_dictionnaire[élé])==type([]):
                            str_list_int=''
                            for élé2 in range (0,len(List_dictionnaire[élé])):
                                if élé2!=len(List_dictionnaire[élé])-1:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])+'-'    #'ZszS' sert à séparer les élément d'une liste qui est dans un dictionnaire lui-même dans une liste
                                else:
                                    str_list_int=str_list_int+str(List_dictionnaire[élé][élé2])
                            str_list=str_list+str_list_int
                        else :
                            str_list=str_list+str(List_dictionnaire[élé])
                info=info+str_list+'Â¤'
            else:
                info=info+str(info_list[indélé])+'Â¤'
    écrire_string(nom_fichier,nom_info,info,format_fichier)









#adaptation de l'info dictionnaire en string sous le format key1ÂµinfoÂ¤....
#comptez aussi les dico de listes formater comme tel key1Âµi0Â§i1Â§i2Â¤key2....
def écrire_dico(nom_fichier,nom_info,info_dico,format_fichier='txt'):
    info=''
    for key in info_dico:
        entry=info_dico[key]
        if type(entry)==type([]):
            str_list=''
            for ind in range (0,len(entry)):
                if ind!=len(entry)-1:
                    str_list=str_list+str(entry[ind])+'Â§'
                else :
                    str_list=str_list+str(entry[ind])
            info=info+str(key)+'Âµ'+str_list+'Â¤'
        else:
            info=info+str(key)+'Âµ'+str(info_dico[key])+'Â¤'
    liste_imprimé=list(info)
    info_imprimé=''
    for ind in range(0,len(liste_imprimé)-2):
        info_imprimé+=str(liste_imprimé[ind])
    écrire_string(nom_fichier,nom_info,info_imprimé,format_fichier)

#fonction sauvegarder qui sert de synthèse des trois fonctions d'écriture


def sauvegarder(nom_fichier,nom_info,info,format_fichier='txt'):
    if type(info)==type('abc') or type(info)==type(12) or type(info)==type(12.4):
        écrire_string(nom_fichier,nom_info,info,format_fichier)
        return True
    elif type(info)==type([]):
        écrire_list(nom_fichier,nom_info,info,format_fichier)
        return True
    elif type(info)==type({}):
        écrire_dico(nom_fichier,nom_info,info,format_fichier)
        return True
    else:
        return False


#print(os.listdir('Test'))

#récupérer le cheminement complet vers un fichier
#for path, subdirs, files in os.walk('folder'):
#    for name in files:
#        print(os.path.join(path, name))


#fonction pour récupérer une liste des fichiers dans un folder
def list_doc(path,extension=False):
    if extension:
        List_fichier=os.listdir(path)
        
        for ind in range (0,len(List_fichier)):
            List_fichier[ind]=(List_fichier[ind].split('.')[0])
        return List_fichier
    else:
        
        return os.listdir(path)

#fonction de sauvegarde avec écrasement de fichier
def sauvegarde(nom_fichier,nom_info,info,format_fichier='txt',crush=False):
    if crush:
        nom=nom_fichier+'.'+format_fichier
        
        f=open(nom,'w')
        f.close
        return sauvegarder(nom_fichier,nom_info,info,format_fichier)
    else:
        return sauvegarder(nom_fichier,nom_info,info,format_fichier)


#fonction pour effacer un fichier
def effacer(path):
    os.remove(path)


#d={(0,0): ['<tkinter.Canvas object .!canvas.!canvas2.!canvas>', False, '', 'MT'], (0,1): ['<tkinter.Canvas object .!canvas.!canvas2.!canvas2>', False, '', 'None'], (0,2): ['<tkinter.Canvas object .!canvas.!canvas2.!canvas3>', False, '', 'None'], (0,3): ['<tkinter.Canvas object .!canvas.!canvas2.!canvas4>', False, '', 'LD']}
#sauvegarder('test1','dico long',d)
#print(lire('dico long','test1.txt','dictionnaire_list'))



#L=[{'A':['t',8],'H':475},{'T':89}]
#print(sauvegarde('tt','ab',L))
#print(lire('ab','tt.txt','list_dictionnaire'))
#print(sauvegarde('tt','carac','-'))
#print(lire('carac','tt.txt','string'))



#a='lol'
#g=a.split('-')
#print(g, 8)
#if g!=[a]:
#    print(g)
#G=[{'h':[1,2,3,4,5],'a':8},{'t':9}]

#print(sauvegarde('tuit','test',G))
#G1=lire("Players_info",'defe.txt', "list_dictionnaire")
#lire('test','tuit.txt','list_dictionnaire'))
#print(G1)





        


    








        



























        
    
    
    
                
                
    
        


    
   






            





        
            

