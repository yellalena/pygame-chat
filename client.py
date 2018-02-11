import sys, pygame
from time import sleep
from sys import stdin, exit
from random import randint

from PodSixNet.Connection import connection, ConnectionListener
from _thread import *
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 30)

COLOR_INACTIVE = (138, 138, 138)
COLOR_ACTIVE = (39, 210, 39)
MY_COLOR = (randint(0, 255), randint(0, 255), randint(0, 255))
BGCOLOR = (65, 33, 12)

DISPLAYWIDTH, DISPLAYHEIGHT = 400, 400

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.text_surface = font.render(text, 1, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False

        if self.active:
            self.color = COLOR_ACTIVE
        else:
            self.color = COLOR_INACTIVE

        message = ''

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    message = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

                self.text_surface = font.render(self.text, 1, self.color)

        return message

    def update(self):
        width = max(300, self.text_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Client(ConnectionListener):
    def __init__(self, host, port):

        self.Connect((host, port))
        print("Chat client started")

        self.screen = self.makeScreen()
        self.box = InputBox(50, 300, 300, 90)

        self.message = ''
        self.latest_msg = ''


        self.userid = start_new_thread(self.InputLoop, ())
        pygame.display.set_caption('Chat: ' + str(self.userid))
        connection.Send({"action": "userid", "userid": self.userid})
        self.history = [{"author": self.userid, "message":self.message}]

    
    def Loop(self):
        connection.Pump()
        self.Pump()
    
    def InputLoop(self):
        pass

    def makeScreen(self):
        pygame.display.set_caption('Chat')
        screen = pygame.display.set_mode([DISPLAYWIDTH, DISPLAYHEIGHT])
        screen.fill(BGCOLOR)

        return screen
    def run(self):
        while True:
            connection.Pump()
            self.Pump()
            self.Loop()
            sleep(0.001)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.message = self.box.handle_event(e)
            self.screen.fill(BGCOLOR)
            self.box.update()
            self.box.draw(self.screen)

            if len(self.message) != 0:
                sleep(1)
                self.history.append({"author": self.userid, "message": str(self.userid) + ": " + self.message})
                connection.Send({"action":"message", "history":self.history})

            strins = list(reversed(range(300-50*len(self.history), 300, 50)))
            self.history.reverse()
            for m in range(len(self.history)):
                if self.history[m]["author"] == self.userid:
                    self.screen.blit(font.render(self.history[m]["message"], 1, MY_COLOR), [50, strins[m]])
                else:
                    self.screen.blit(font.render(self.history[m]["message"], 1, COLOR_ACTIVE), [50, strins[m]])
            self.history.reverse()

            pygame.display.update()
            pygame.time.delay(10)

    
    #######################################
    ### Network event/message callbacks ###
    #######################################
    
    def Network_players(self, data):
        print("*** players: " + ", ".join([str(p) for p in data['players']]))
    
    def Network_message(self, data):
        for m in data['history']:
            if m not in self.history and m['message'] != '':
                self.history.append(m)

    # built in stuff

    def Network_connected(self, data):
        print("You are now connected to the server")
    
    def Network_error(self, data):
        print('error:', data['error'])
        connection.Close()
    
    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()

if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "host:port")
    print("e.g.", sys.argv[0], "localhost:31425")
else:
    host, port = sys.argv[1].split(":")
    c = Client(host, int(port))
    c.run()
        