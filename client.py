import socket
import pygame
import sys

def parseAndPrintDataMsg(data):
    print(data)
    dataString = data.split(' ||| ')[1]
    d = dataString.split(' || ')
    dataDict={}
    dataDict['category']=d[0]
    dataDict['blankWord']=d[1]
    letterUsed = d[2].split(' | ')
    dataDict['letterUsed'] = letterUsed
    players = d[3].split(' | ')
    playersNew = []
    for i in players:
        p = ( i.split(' -> ')[0], i.split(' -> ')[1])
        playersNew.append(p)
    dataDict['players'] = playersNew
    print('CATEGORY: ' + dataDict['category'])
    print('YOU''RE WORD: ' + dataDict['blankWord'])
    if dataDict['letterUsed'].count('NONE') == 0:
        lu = 'USED LETTERS: '
        for i in dataDict['letterUsed']:
            lu += i +', '
        print(lu)
    else:
        print('NO LETTER USED')
    print('PLAYER AND REWARD:')
    for i in dataDict['players']:
        print(i[0] + ' : ' + i[1])




if __name__ == '__main__':
    try:

        if len(sys.argv) < 2:
            print('BRAK PARAMETROW URUCHOMIENIA PROGRAMU, ZAMYKAM')
            exit(-1)
        ip = sys.argv[1]
        port = int(sys.argv[2])
        clientSocket = None
        if ip.find('.') != -1:
            try:
                socket.inet_pton(socket.AF_INET, ip)
                clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            except socket.error:
                print('NIEPRAWIDLOWY ADRES IPV4, KONIEC PROGRAMU')
                exit(-1)

        elif ip.find(':') != -1:
            try:
                socket.inet_pton(socket.AF_INET6,socket.SOCK_STREAM)
                clientSocket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
            except:
                print('NIEPRAWIDLOWY ADRES IPV6, KONIEC PROGRAMU')
                exit(-1)


        clientSocket.connect((ip, port))
        playerName = input('Podaj swoj nickname')
        joined = False
        menuChoice= input('Wpisz nowa jesli chcesz postawic NOWA gre lub DOLACZ jesli chcesz dolaczyc')
        while menuChoice.upper() != 'NOWA' and menuChoice.upper() != 'DOLACZ':
            menuChoice = input('NIEPRAWIDLOWA KOMENDA, WPISZ PONOWNIE\n')
        if menuChoice.upper() == 'NOWA':
            joined = False
            gameName = input('podaj nazwe gry ')
            playersNum = input('podaj liczbe graczy')
            while not str.isdecimal(playersNum):
                playersNum = input('ILOSC GRACZY MUSI BYC LICZBA, WPISZ PONOWNIE')
            msg = 'NEW | '+playerName+ ' | ' + gameName + ' | ' + playersNum
            clientSocket.send(bytes(msg, encoding='utf-8'))
        elif menuChoice.upper() == 'DOLACZ':
            joined = True
            msg = 'JOIN | '+ playerName
            clientSocket.send(bytes(msg,encoding='utf-8'))
            ans = str(clientSocket.recv(4096),encoding='utf-8')
            if ans != 'NO GAMES':
                gameList = ans.split(' | ')
                print('wybierz jedna z gier poprzez wpisanie jej nazwy\n')
                for ga in gameList:
                    print(ga)
                choice = input()
                msg = 'GAME | '+ choice
                clientSocket.send(bytes(msg,encoding='utf-8'))

            else:
                print(ans)
                exit(0)
        if not joined:
            msg = 'START'

            clientSocket.send(bytes(msg, encoding='utf-8'))

            ans = str(clientSocket.recv(4096),encoding='utf-8')
            if ans.startswith('OK'):
                y = input('wpisz L jesli chcesz wylosowac kategorie lub Q jesli chcesz wyjsc ')
                while y.upper() != 'L' and y.upper() != 'Q':
                    y=input('NIEPRAWIDLOWA KOMENDA , WPISZ PONOWNIE\n')
                if y == 'L':
                    msg = 'GET-CATEGORY'
                    clientSocket.send(bytes(msg,encoding='utf-8'))
                    ans = str(clientSocket.recv(4096),encoding='utf-8')
                    print(ans)
                    if ans.startswith('CATEGORY'):
                        print('losowanie slowa...')
                        msg = 'GET-WORD'
                        clientSocket.send(bytes(msg,encoding='utf-8'))
                        ans  = str(clientSocket.recv(4096), encoding='utf-8')
                        if ans.startswith('GOTIT'):
                            print('CZAS NA LOSOWANIE NAGRODY, WPISZ L ABY WYLOSOWAC')
                            print('\n')
                            odp = input()
                            while odp.upper() != 'L':
                                odp = input('NIEPRAWIDLOWA KOMENDA, WPISZ PONOWNIE\n')
                            if odp.upper() == 'L':
                                msg = 'GET-REWARD'
                                clientSocket.send(bytes(msg,encoding='utf-8'))
                                ans = str(clientSocket.recv(4096),encoding='utf-8')
                                print(ans)
                                if ans.startswith('YOU'):
                                    msg = 'GET-DATA'
                                    clientSocket.send(bytes(msg,encoding='utf-8'))
                                    ans = str(clientSocket.recv(4096),encoding='utf-8')
                                    parseAndPrintDataMsg(ans)
                                    odp=input('WPISZ L ABY ZGADYWAC LITERE LUB S ABY ZGADYWAC SLOWO\n')
                                    while odp.upper() != 'L' and odp != 'S':
                                        odp = input('NIEPRAWIDLOWA KOMENDA, WPISZ PONOWNIE\n')
                                    if odp.upper() == 'L':
                                        ch = input('podaj litere\n').upper()
                                        msg = 'CHECK '+ ch
                                        clientSocket.send(bytes(msg,encoding='utf-8'))
                                        ans = str(clientSocket.recv(4096),encoding='utf-8')
                                        while ans != 'GOOD' and ans != 'BAD':
                                            ch = input('LITERA ZOSTALA JUZ UZYTA, PODAJ INNA\n')
                                            msg = 'CHECK ' + ch
                                            clientSocket.send(bytes(msg, encoding='utf-8'))
                                            ans = str(clientSocket.recv(4096), encoding='utf-8')
                                        if ans == 'GOOD':
                                            print('DOBRZE!!!\n')
                                        elif ans == 'BAD':
                                            print('NIESTETY NIEPOPRAWNIE, PROBUJ DALEJ\n')

                                    elif odp.upper() == 'S':
                                        od = input('wpisz slowo\n')
                                        msg = 'SHOT | ' + od
                                        clientSocket.send(bytes(msg,encoding='utf-8'))
                                        ans = str(clientSocket.recv(4096),encoding='utf-8')
                                else:
                                    if ans.startswith('HALF'):
                                        print('NIESTETY TWOJA WYGRANA ZOSTALA ZMNIEJSZONA O POLOWE')

                                    elif ans.startswith('ZERO'):
                                        print('NIESTETY JESTES SPLUKANY')


                elif y.upper() == 'Q':
                    exit(0)

            joined = True
        ans = str(clientSocket.recv(4096),encoding='utf-8')
        while True:
            if ans.startswith('TIME'):
                msg = 'GET-DATA'
                clientSocket.send(bytes(msg, encoding='utf-8'))
                ans = str(clientSocket.recv(4096), encoding='utf-8')
                parseAndPrintDataMsg(ans)
                odp = input('Wpisz L jesli chcesz zakrecic kolem i zgadywac litere lub S jesli chcesz zgadywać haslo\n')
                while odp != 'L' and odp != 'S':
                    odp = input('ZLA KOMENDA, SPROBUJ PONOWNIE')
                if odp.upper() == 'L':
                    msg = 'GET-REWARD'
                    clientSocket.send(bytes(msg,encoding='utf-8'))
                    ans = str(clientSocket.recv(4096),encoding='utf-8')
                    if not ans.startswith('ZERO') and not ans.startswith('HALF'):
                        print(ans)
                        ch = input('Podaj litere\n').upper()
                        msg = 'CHECK ' + ch
                        clientSocket.send(bytes(msg, encoding='utf-8'))
                        ans = str(clientSocket.recv(4096), encoding='utf-8')
                        while ans != 'GOOD' and ans != 'BAD':
                            ch = input('LITERA ZOSTALA JUZ UZYTA, PODAJ INNA\n')
                            msg = 'CHECK ' + ch
                            clientSocket.send(bytes(msg,encoding='utf-8'))
                            ans = str(clientSocket.recv(4096), encoding='utf-8')
                        if ans == 'GOOD':
                            print('DOBRZE!!!\n')
                        elif ans == 'BAD':
                            print('NIESTETY NIEPOPRAWNIE, PROBUJ DALEJ\n')
                    else:
                        if ans.startswith('HALF'):
                            print('NIESTETY TWOJA WYGRANA ZOSTALA ZMNIEJSZONA O POLOWE')
                            msg = 'GET-DATA'
                            clientSocket.send(bytes(msg, encoding='utf-8'))
                            ans = str(clientSocket.recv(4096), encoding='utf-8')
                            parseAndPrintDataMsg(ans)
                        elif ans.startswith('ZERO'):
                            print('NIESTETY JESTES SPLUKANY')
                            msg = 'GET-DATA'
                            clientSocket.send(bytes(msg, encoding='utf-8'))
                            ans = str(clientSocket.recv(4096), encoding='utf-8')
                            parseAndPrintDataMsg(ans)


                elif odp.upper() == 'S':
                    od = input('Wpisz slowo\n')
                    msg = 'SHOT | ' + od
                    clientSocket.send(bytes(msg, encoding='utf-8'))
                    ans = str(clientSocket.recv(4096), encoding='utf-8')
                    print(ans)

                ans= str(clientSocket.recv(4096),encoding='utf-8')

            elif ans.startswith('END'):
                print(ans)
                break
        clientSocket.close()
        exit(0)
    except ConnectionError:
        print('POLACZENIE ZERWANE, KONIEC PROGRAMU')
        exit(-1)

