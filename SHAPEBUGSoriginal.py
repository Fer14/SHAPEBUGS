#Python Source Code

#Library Imports
import pygame
from random import randint as ri
import math
pygame.init()
import time
import numpy
import random
import cv2
import threading

#GAME Parameters
screen = pygame.display.set_mode([1000, 1000])
IMAGE = 0
WHITE=(255,255,255)
BLUE=(121,159,203)
BLACK=(0,0,0)
RED=(249,102,94)
GREEN=(182,238,189)
GRAY = (105,105,105)
PURPLE = (255,189,222)
screen.fill(WHITE)
bloc = (0,0)


print('¿Cuanto de ancho quieres que sea el rectángulo?')
Rect_x = 50
Rect_x = int(input())
print('¿Cuanto de largo quieres que sea el rectángulo?')
Rect_y = 50
Rect_y = int(input())
tam_robots = 10;
n_robots = int((Rect_x/(tam_robots*2))*(Rect_y/(tam_robots*2)))
print("El número de robots necesario es: ",n_robots)
print('¿Quieres ver la localizacion que cree el robot?')
flag = input().lower()
#pygame.draw.rect(screen,BLACK,(GAME_x,GAME_y,GAME_width,GAME_height),GAME_border)

seed_points = [(290,300+Rect_y),(310,300+Rect_y),(300,300+Rect_y+16),(300,300+Rect_y-16)]
#seed_points = [(290,600),(310,600),(300,616),(300,584)]

class Button:
    def __init__ (self, colour, x, y, width, height,text):
        self.colour = colour
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def create(self,screen):
        pygame.draw.rect(screen, self.colour, [self.x, self.y,self.width ,self.height])
        font = pygame.font.SysFont('Arial', 14)
        text = font.render(self.text, True, WHITE)
        textRect = text.get_rect()
        textRect.center = (int(self.x +self.width/2) ,int(self.y + self.height/2))
        screen.blit(text, textRect)


class SHAPEBUG:
    def __init__ (self, state, gradient, x, y,direction,isSeed):
        self.state = state
        self.x = x
        self.y = y
        self.gradient = gradient
        self.direction = direction
        self.believed_location = (0,0)
        self.islocalized = False
        self.isseed = isSeed
        self.draw(screen)
        self.dnn = 999

    def draw(self,screen):

        if self.isseed:
            pygame.draw.circle(screen,GREEN,(self.x,self.y),tam_robots) 
        
        elif self.state == "end":
            pygame.draw.circle(screen,PURPLE,(self.x,self.y),tam_robots)

        elif self.state == "moving" or self.state == "moving_inside" :
            pygame.draw.circle(screen,RED,(self.x,self.y),tam_robots)
            #pygame.draw.line(screen,BLACK,(self.x,self.y),self.direction,2)
            
        elif self.state == "start":
            pygame.draw.circle(screen,BLUE,(self.x,self.y),tam_robots)

        self.font = pygame.font.SysFont('Arial', 8)
        screen.blit(self.font.render(str(self.gradient), True, BLACK), (self.x-3, self.y-3))

        if self.islocalized and flag == 'si':
            pygame.draw.circle(screen,BLACK,self.believed_location,tam_robots)

        pygame.display.update()
      
    def is_localized(self):
        return self.islocalized

    def get_believed_location(self):
        return self.believed_location

    def set_belived_location(self,location):
        if flag == 'si':
            pygame.draw.circle(screen,WHITE,self.believed_location,tam_robots)
        self.believed_location = location
        #if point_inside_rec(300,300,Rect_x,Rect_y,self.believed_location[0],self.believed_location[1]):
            #self.set_state("moving_inside")

    def is_seed(self):
        return self.isseed

    def set_state(self,state):
        self.state = state

    def get_state(self):
        return self.state        

    def setlocation(self,x,y):
        self.x = x
        self.y = y
        #if point_inside_rec(300,300,Rect_x,Rect_y,self.x,self.y):
        #    self.set_state("moving_inside")
        if point_inside_rec(300,300,Rect_x,Rect_y,self.believed_location[0],self.believed_location[1]):
            self.set_state("moving_inside")    
          
    def setdnn(self,newrobot):
        self.dnn = dist((self.x,self.y),nearest_bug(newrobot,(self.x,self.y)).get_location())

    def get_location(self):
        return (self.x,self.y)    

    def set_gradient(self,gradient):
        self.gradient = gradient

    def get_gradient(self):
        return self.gradient

    def setdirection(self,direction):
        self.direction = direction

    def move_forward(self):

        x_,y_ = self.direction
        s = []
        s.append(x_-self.x)
        s.append(y_-self.y)

        signos = numpy.sign(s)

        if 0 in signos:
            if signos[0] == 0:
                x = 0
                if signos[1] == -1:
                    y = -2
                else:
                    y = 2  
                
            if signos[1] == 0:
                y = 0
                if signos[0] == -1:
                    x = -2
                else:
                    x = 2
        else:
            if signos[1] == -1:
                y = -2
            else:
                y = 2

            if signos[0] == -1:
                x = -2
            else:
                x = 2

        pygame.draw.circle(screen,WHITE,(self.x,self.y),tam_robots)

        self.setlocation(int(self.x+x),int(self.y+y))
        x_,y_ = self.direction
        self.setdirection((int(x_+x),int(y_+y)))

        if ((self.get_state() == "moving_inside") and (not point_inside_rec(300,300,Rect_x,Rect_y,(self.get_believed_location()[0]+x),(self.get_believed_location()[1]+y)))):
            self.set_state('end')
            self.believed_location = self.get_location()

        
        #self.gradient_formation(newrobot)
        #self.draw(screen)
        #self.update_believed_location()
        #time.sleep(0.01)
        #time.sleep(1.005)

    def init_believed_location(self):
        if self.isseed == False:
            self.believed_location = (-500,-500)

        else:
            self.believed_location = self.get_location()
            self.islocalized = True

    def update_believed_location(self):

        nlist = []

        for neighbor in newrobot:
            if neighbor.get_location() != self.get_location():
                if (dist(neighbor.get_location(),self.get_location()) < 60)  and (dist(neighbor.get_location(),self.get_location()) > 0):
                    if(neighbor.get_state() == 'end') and (neighbor.is_localized()):
                        nlist.append(neighbor)

        if (len(nlist) >= 3):
            for l in nlist:
                c = dist(l.get_believed_location(),self.get_believed_location())
                if (c != 0):
                    v = ((self.get_believed_location()[0] - l.get_believed_location()[0])/(c),(self.get_believed_location()[1] - l.get_believed_location()[1] )/(c))
                    d = dist(l.get_location(),self.get_location())
                    n = (l.get_believed_location()[0] + d*v[0],l.get_believed_location()[1] + d*v[1])
                    self.set_belived_location((int(self.believed_location[0] - (self.believed_location[0]-n[0])/1),int(self.believed_location[1] - (self.believed_location[1] - n[1])/1)))
            
            self.islocalized = True    


        #print("Believed location : ",self.get_believed_location())
        #print("Real location : ",self.get_location())
        #print("Diferencias :",(self.get_believed_location()[0] - self.get_location()[0],self.get_believed_location()[1] - self.get_location()[1]))
        #time.sleep(3.0)

    def move_clockwise(self):
        x_,y_ = self.direction
        
        s = []
        s.append(x_-self.x)
        s.append(y_-self.y)
        signos = numpy.sign(s)

        if 0 in signos: 
            if (signos[0] == 0):
                if (signos[1] == -1):#Arriba
                    newy = self.y
                    newx = self.x - s[1]
                else:    #Abajo
                    newy = self.y
                    newx = self.x - s[1]
            else:
                if (signos[0] == -1):#Izquierda
                    newy = self.y + s[0]
                    newx = self.x
                   
                else:    #Derecha
                    newy = self.y + s[0]
                    newx = self.x
        else:

            if (signos[0] == -1): #Izquierda
                if (signos[1] == -1):#Arriba
                    newx = self.x - s[0]
                    newy = y_
                else:    #Abajo
                    newx = x_
                    newy = self.y - s[1]

            else: #Derecha
                if (signos[1] == -1):#Arriba
                    newx = x_
                    newy = self.y - s[1]

                else: #Abajo
                    newx = self.x - s[0]
                    newy = y_
            
        self.setdirection((newx,newy))  
          
    def move_counterclockwise(self):

        x_,y_ = self.direction
        s = []
        s.append(x_-self.x)
        s.append(y_-self.y)
        signos = numpy.sign(s)

        if 0 in signos: 
            if (signos[0] == 0):
                if (signos[1] == -1):#Arriba
                    newy = self.y
                    newx = self.x + s[1]
                else:    #Abajo
                    newy = self.y
                    newx = self.x + s[1]
            else:
                if (signos[0] == -1):#Izquierda
                    newy = self.y - s[0]
                    newx = self.x
                   
                else:    #Derecha
                    newy = self.y - s[0]
                    newx = self.x

        else:    
            if (signos[0] == -1): #Izquierda
                if (signos[1] == -1):#Arriba
                    newx = x_
                    newy = self.y - s[1]
                else:    #Abajo
                    newx = self.x - s[0]
                    newy = y_

            else: #Derecha
                if (signos[1] == -1):#Arriba
                    newx = self.x - s[0]
                    newy = y_

                else: #Abajo
                    newx = x_
                    newy = self.y - s[1]
           
        self.setdirection((newx,newy))  

    def edge_following(self):
        #print("Edge following")

        #self.set_state("moving")

        #seedrobots = [x for x in newrobot if x.is_seed()]
        
        prev = self.dnn 
        #while (self.get_state() != 'end'):

        current = dist((self.x,self.y),nearest_bug(newrobot,(self.x,self.y)).get_location())
        
        #points = [x.get_location() for x in newrobot]
        
        for n in seed_points:
            if dist(n,(self.x,self.y)) < current:
                current = dist(n,(self.x,self.y))

        if current < 20:

            if prev < current: 
                self.move_forward()
                
            else: #Move a bit to the left while mooving forward
                self.move_counterclockwise()
                self.move_forward()

        else:
            if prev > current:
                self.move_forward()
                
            else: #Move a bit to the right while mooving forward 
                self.move_clockwise()  
                self.move_forward()              
    

        prev = current
        self.dnn = prev

        if (self.get_state() == "moving_inside") and (nearest_bug(newrobot,self.get_location()).get_gradient() >= self.get_gradient()):
            self.set_state('end')
            self.believed_location = self.get_location()
            

    def gradient_formation(self,bugs):
        if self.is_seed():
            self.set_gradient(0)
        else:
            self.set_gradient(98)
            for neighbor in bugs:
                if neighbor.get_location() != self.get_location():
                    if dist(neighbor.get_location(),self.get_location()) < 30:
                        if neighbor.get_gradient() < self.get_gradient():
                            self.set_gradient(neighbor.get_gradient())
        
            self.set_gradient(self.get_gradient()+1)
            #self.transmit_gradient(bugs)

    
    def transmit_gradient(self,bugs):
        for bug in bugs:
            if bug.is_seed():
                bug.set_gradient(0)
            else:
                bug.set_gradient(98)
                for neighbor in bugs:
                    if neighbor.get_location() != bug.get_location():
                        if dist(neighbor.get_location(),bug.get_location()) < 30:
                            if neighbor.get_gradient() < bug.get_gradient():
                                bug.set_gradient(neighbor.get_gradient())
            
                bug.set_gradient(bug.get_gradient()+1)
                bug.draw(screen)   

    def wait_until_move(self):

        self.set_state('start')
        #neighbors_moving = False
        has_greatest_gradient = False
        highest_gradient = 0
        moving = []

        #while (1 in moving) or (not has_greatest_gradient):
        highest_gradient = 0
        moving = []
        for neighbor in newrobot:
            if neighbor.get_location() != self.get_location():
                if dist(neighbor.get_location(),self.get_location()) < 60:
                    if  (neighbor.get_state() == 'moving'):
                        neighbors_moving = True
                        moving.append(1)
                    else:
                        neighbors_moving = False
                        moving.append(0)

                    if  (neighbor.get_gradient() > highest_gradient) and neighbor.get_state() != 'end':
                        highest_gradient = neighbor.get_gradient()


        if (self.get_gradient() >= highest_gradient):
            has_greatest_gradient = True        

        if not (1 in moving) and has_greatest_gradient:
            self.set_state('moving')
        #self.edge_following(screen)


    def tick(self,newrobot):
        if not self.is_seed():

            if self.get_state() != 'end':

                if self.get_state() == 'start':
                    self.wait_until_move()

                elif (self.get_state() == 'moving') or (self.get_state() == 'moving_inside'):
                    self.edge_following()

            if self.get_state() != 'start':
                self.update_believed_location()
  
        
        self.gradient_formation(newrobot)
        self.draw(screen)



def nearest_bug(list,point):
    shortest_dist = 100000000000000;
    shortest_bug = (0,0)
    for bug in list:
        if (bug.get_location() != point):
            distance = dist(bug.get_location(),point)
            if distance <= shortest_dist:
                shortest_dist = distance
                shortest_bug = bug
    return  shortest_bug    

def dist(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)     

def point_inside_rec(xr,yr,wr,hr,x,y):
    if (x> xr) and (x < xr + wr) and (y > yr) and (y < yr + hr):
        return True 
    else:
        return False

def draw_enviroment(newrobot):     
    for robot in newrobot:
            robot.draw(screen)
    pygame.display.update()  

def order_by_gradient(bugs):
    bugs.reverse()
    bugs.sort(key=lambda x: x.get_gradient(), reverse=True)




running = True
rectangle = pygame.draw.rect(screen,BLACK,(300,300,Rect_x,Rect_y))
B = Button(BLACK, 450, 900, 100, 50, "Iniciar")
B.create(screen)
pygame.display.update()

newrobot = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if running==False:
            break

        m = pygame.mouse.get_pressed()
        x,y = pygame.mouse.get_pos()
        click = False

        if m[0]==1 and not click:
            if point_inside_rec(B.x,B.y, B.width, B.height,x,y):

                click = True

                #rectangle = pygame.draw.rect(screen,GRAY,(300,300,Rect_x,Rect_y))
                pygame.draw.rect(screen,GRAY,(300,300,Rect_x,Rect_y))
                pygame.draw.rect(screen,WHITE,(B.x,B.y,B.width,B.height))
                

                #Seed robots
                newrobot.append(SHAPEBUG("end", 99,290,Rect_y+300,(300,Rect_y+300),True))
                newrobot.append(SHAPEBUG("end", 99,310,Rect_y+300,(300,Rect_y+300),True))
                newrobot.append(SHAPEBUG("end", 99,300,Rect_y+300+16,(300,Rect_y+300),True))
                newrobot.append(SHAPEBUG("end", 99,300,Rect_y+300-16,(300,Rect_y+300),True))
          
                #Rest of the robots
                n = int(math.sqrt(n_robots))

                for i in range(n):
                    for j in range(n):
                        newrobot.append(SHAPEBUG("start", 99,300+i*20,(Rect_y+336)+j*20,(300,Rect_y+300),False))

                #newrobot.append(SHAPEBUG("start",99,300+0*20,(Rect_y+336)+0*20,(300,Rect_y+300),False))
                #newrobot.append(SHAPEBUG("start",99,300+0*20,(Rect_y+336)+1*20,(300,Rect_y+300),False))
                
                print("Gradient Formation")

                for robot in newrobot:
                    robot.gradient_formation(newrobot)
                    robot.setdnn(newrobot)
                    robot.init_believed_location()
                    
                
                order_by_gradient(newrobot)

                print("Start clock")

                while True:
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            break

                    for r in newrobot:
                        r.tick(newrobot)

                draw_enviroment(newrobot)

                print("End")         
                          


#Quit the Game
pygame.quit()
