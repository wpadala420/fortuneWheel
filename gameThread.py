import threading
import random
import socket


class Player:

    def __init__(self, name,sock):
        self.name = name
        self.rewards=0
        self.sock=sock
        self.joined=True


class Game(threading.Thread):

    def __init__(self):
        super(Game, self).__init__()
        self.alphabet=['A','B','C','D','E','F','G','H','I', 'J', 'K','L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'X', 'Y', 'Z']
        self.choosed = []
        self.categories={}
        self.prices=[]
        self.dest=''
        self.endGame = False
        self.result=''
        self.players=[]
        self.winner=None
        self.name=''
        self.playersNumber = 0
        self.isStarted= False
        self.blankWord=''
        self.category=''

        with open('categories.txt', 'r') as file:
            for line in file:
                l=line.split(' : ')
                self.categories[l[0]] = l[1].split(' , ')
                for i in self.categories[l[0]]:
                    if i.find('\n') != -1:
                        self.categories[l[0]].remove(i)

        with open('prizes.txt','r') as file:
            for line in file:
                line=line.split(' | ')
                for l in line:
                    if str.isdigit(l) and l.find('\n') == -1:
                        self.prices.append(l)
                    else:
                        if l.find('\n') == -1:
                            self.prices.append(l)



    def getCategory(self):
        return random.choice(list(self.categories.keys()))

    def getPrice(self):
        return random.choice(self.prices)


    def run(self):
        ind = random.randint(0,len(self.players)-1)
        pla = self.players[ind]
        client = pla.sock
        msg= str(client.recv(4096),encoding='utf-8')
        category=''
        word=''
        blankword=''
        tmpRew=''
        switch= False
        if msg == 'START':
            print(msg)
            answer = 'OK, LET''S START'
            self.isStarted = True
            client.send(bytes(answer,encoding='utf-8'))
            while not self.endGame:
                try:
                    msg = str(client.recv(4096),encoding='utf-8')
                    print(msg)
                    if msg.startswith('GET-DATA'):
                        answer = 'DATA ||| '
                        answer += self.category + ' || '
                        answer += self.blankWord + ' || '
                        if len(self.choosed) > 0:
                            for i in range(len(self.choosed)):
                                if i < len(self.choosed)-1:
                                    answer += self.choosed[i] + ' | '
                                else:
                                    answer += self.choosed[i] + ' || '
                        else:
                            answer += 'NONE || '

                        for i in range(len(self.players)):
                            if i < len(self.players)-1:
                                plData = self.players[i].name + ' -> ' + str(self.players[i].rewards) + ' | '
                                answer += plData
                            else:
                                plData = self.players[i].name + ' -> ' + str(self.players[i].rewards) + ' || '
                                answer += plData
                        client.send(bytes(answer,encoding='utf-8'))
                    elif msg == 'GET-CATEGORY':
                        cat = self.getCategory()
                        answer = 'CATEGORY ' + cat
                        client.send(bytes(answer, encoding='utf-8'))
                        category = cat
                        self.category=category
                    elif msg == 'GET-WORD':
                        word=random.choice(self.categories[category]).upper()
                        for i in range(len(word)):
                            if str.isalpha(word[i]):
                                blankword += '_'
                            else:
                                blankword += word[i]
                        self.blankWord= blankword
                        answer = 'GOTIT ' + self.blankWord
                        self.dest=word
                        client.send(bytes(answer, encoding='utf-8'))
                    elif msg == 'GET-REWARD':
                        tmpRew = self.getPrice()
                        if tmpRew == 'splukany':
                            pla.rewards = 0
                            answer = 'ZERO'
                            client.send(bytes(answer,encoding='utf-8'))

                            switch = True
                        elif tmpRew == '-50%':
                            pla.rewards /= 2
                            answer = 'HALF'
                            client.send(bytes(answer,encoding='utf-8'))
                            switch = True
                        else:
                            answer = 'YOU''RE REWARD IS --> ' + str(tmpRew)
                            client.send(bytes(answer,encoding='utf-8'))
                    elif msg.startswith('CHECK') and str.isdigit(tmpRew):
                        switch=True
                        char = msg.split(' ')[1].upper()
                        if self.choosed.count(char) == 0 :
                            isMatch = False
                            for i in range(len(self.dest)):
                                if self.dest[i] == char:
                                    isMatch = True
                            blankword=''
                            for i in range(len(self.dest)):
                                if self.dest[i] == char:
                                    blankword += char
                                elif str.isalpha(self.blankWord[i]):
                                    blankword += self.blankWord[i]
                                else:
                                    if str.isalpha(self.dest[i]):
                                        blankword += '_'
                                    else:
                                        blankword += self.dest[i]
                            self.blankWord = blankword

                            if isMatch:
                                answer = 'GOOD'
                                if str.isdigit(tmpRew):
                                    pla.rewards += int(tmpRew)
                                client.send(bytes(answer,encoding='utf-8'))

                            else:
                                answer = 'BAD'
                                client.send(bytes(answer,encoding='utf-8'))


                            self.choosed.append(char)

                        else:
                            answer = 'LETTER USED, ONCE AGAIN'
                            client.send(bytes(answer,encoding='utf-8'))

                    elif msg.startswith('SHOT') and str.isdigit(tmpRew):
                        switch = True
                        shot=msg.split(' | ')[1].upper()
                        if shot == self.dest:
                            answer = 'GRATULACJE, WYGRALES ' + str(pla.rewards) + ' ZL'
                            client.send(bytes(answer,encoding='utf-8'))
                            self.endGame = True

                        else:
                            answer = 'NIEPRAWIDLOWE SLOWO, GRAJ DALEJ'
                            client.send(bytes(answer,encoding='utf-8'))

                    if len(self.choosed) == len(self.alphabet):
                        ms = 'WYKORZYSTALES JUZ WSZYSTKIE LITERY NIE ZGADUJAC SLOWA, PRZEGRALES'
                        self.endGame = True
                        client.send(bytes(ms, encoding='utf-8'))

                    if switch and not self.endGame:
                        if ind == len(self.players)-1:
                            ind = 0
                        else:
                            ind+=1
                        switch = False
                        pla=self.players[ind]
                        client=pla.sock
                        client.send(bytes('TIME FOR YOU',encoding='utf-8'))
                except ConnectionError:
                    print('POLACZENIE ZERWANE, KONIEC GRY')
                    exit(-1)
            for cl in self.players:
                cl.sock.send(bytes('END GAME , PLAYER '+ pla.name + ' WON',encoding='utf-8' ))
                cl.sock.close()













