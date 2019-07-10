import socket
import gameThread
import sys
import threading

def onePlayerThread(socket,games):
    try:
        entry = str(client.recv(4096), encoding='utf-8')
        print('ENTRY: ' + entry)
        name = entry.split(' | ')[1]
        p = gameThread.Player(name, client)
        if entry.startswith('NEW'):
            p.joined = False
            g = gameThread.Game()
            g.players.append(p)
            g.name = entry.split(' | ')[2]
            g.playersNumber = int(entry.split(' | ')[3])
            games.append(g)

        elif entry.startswith('JOIN'):
            p.joined = True
            openGameList = ''
            for i in games:
                if len(i.players) < i.playersNumber:
                    if openGameList == '':
                        openGameList += i.name
                    else:
                        openGameList += ' | '
                        openGameList += i.name

            if openGameList != '':
                client.send(bytes(openGameList, encoding='utf-8'))
                ans = str(client.recv(4096), encoding='utf-8')
                if ans.startswith('GAME'):
                    print(ans)
                    gname = ans.split(' | ')[1]

                    for i in games:
                        if i.name == gname:
                            i.players.append(p)

            else:
                client.send(bytes('NO GAMES', encoding='utf-8'))

        for g in games:
            if g.playersNumber == len(g.players) and not g.isAlive() and not g.isStarted:
                g.start()
                g.isStarted = True
    except ConnectionError:
        print('POLACZENIE Z ADRESEM ' + adress[0] + ':' + str(adress[1]) + ' ZOSTALO ZERWANE')

    except ValueError:
        print('BLAD KOMUNIKACJI, NIEPRAWIDLOWE WPROWADZONE DANE GRY')

if __name__ == '__main__':
    games = []


    s = None
    if len(sys.argv) < 2:
        print('BRAK PARAMETROW URUCHOMIENIA PROGRAMU, ZAMYKAM')
        exit(-1)
    ip = sys.argv[1]
    port = int(sys.argv[2])
    if ip.find('.') != -1:
        try:
            socket.inet_pton(socket.AF_INET,ip)
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except socket.error:
            print('NIEPRAWIDLOWY ADRES IPV4, KONIEC PROGRAMU')
            exit(-1)

    elif ip.find(':') != -1:
        try:
            socket.inet_pton(socket.AF_INET6,ip)
            s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
        except:
            print('NIEPRAWIDLOWY ADRES IPV6, KONIEC PROGRAMU')
            exit(-1)

    try:
        s.bind((ip, port))
        s.listen(555)
    except ConnectionError:
        print('BLAD SERWERA, KONIEC PROGRAMU')
        exit(-1)



    while True:
        try:
            client, adress = s.accept()
            with open('log.txt' , 'a') as log:
                log.write('POLACZONO Z SERWEREM Z ADRESU '+adress[0]+':'+ str(adress[1]) )
            t = threading.Thread(target=onePlayerThread, args=[client,games])
            t.start()
        except ConnectionError:
            print('NIE UDALO SIE USTANOWIC POLACZENIA')
            continue
    log.close()
    s.close()


