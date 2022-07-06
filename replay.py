import imp
import colorama
from colorama import init, Fore, Back, Style
import numpy as np
from sqlalchemy import null
import src.config as config
import subprocess as sp
from src.input import input_to
import time
import os
import src.building as bb
import src.character as cc
import src.spell as ss
import sys
import src.input as input
import signal

InputVar = input.Get()

colorama.init(autoreset=True)

N = len(sys.argv)
if(N != 2):
    print("Usage: python3 replay.py <replay file>")
    exit()

f = open("./replays/" + sys.argv[1], "r")
def RepositionCursor(x, y):
    print("\033[{};{}H".format(y, x), end="")

def VictoryText():
    # print from victor.txt
    with open("./src/victory.txt", "r") as f:
        for line in f:
            print(Back.BLACK + line, end="")
def DefeatText():
    # print from defeat.txt
    with open("./src/defeat.txt", "r") as f:
        for line in f:
            print(Back.BLACK + line, end="")

class Replay:
    def __init__(self):
        self._sceneWidth = config.SCENE_WIDTH
        self._sceneHeight = config.SCENE_HEIGHT
        self.xcen = int(self._sceneWidth / 2)
        self.ycen = int(self._sceneHeight / 2)
        self.NetFrames = 0
        self.__lastRefresh = 0
        self.levels[self.curr_lvl].objArray = []
        self.timesRefreshed = 0
        self.levels[self.curr_lvl].leviathan = False
        sp.call('clear', shell=True) 
        self.levels[self.curr_lvl].scene = np.array([[[Back.BLACK + Style.BRIGHT + ' ',0] for i in range(self._sceneWidth)] for j in range(self._sceneHeight)], dtype=object)
        for i in range(self._sceneHeight):
            for j in range(self._sceneWidth):
                if(i == 0 or i == self._sceneHeight - 1 or j == 0 or j == self._sceneWidth - 1):
                    self.levels[self.curr_lvl].scene[i][j][0] = Back.BLACK + Style.BRIGHT + '#'
                    self.levels[self.curr_lvl].scene[i][j][1] = "boundary"
            
        self.levels[self.curr_lvl].scene[0][0][0] = Back.GREEN + Style.BRIGHT + ' '
        self.levels[self.curr_lvl].scene[self._sceneHeight - 1][self._sceneWidth - 1][0] = Back.GREEN + Style.BRIGHT + ' '
        self.levels[self.curr_lvl].scene[self._sceneHeight - 1][0][0] = Back.GREEN + Style.BRIGHT + ' '

        self.levels[self.curr_lvl].th = bb.TownHall()
        self.levels[self.curr_lvl].cannons = [ bb.Cannon(self.xcen//2 - config.CANNON_WIDTH//2, self.ycen - config.CANNON_WIDTH//2)
                         ,bb.Cannon(3*self.xcen//2 - config.CANNON_WIDTH//2, self.ycen - config.CANNON_WIDTH//2)
                         ,bb.Cannon(self.xcen - config.CANNON_WIDTH//2, 3*self.ycen//2 - config.CANNON_WIDTH//2)
                        ]
        
        self.levels[self.curr_lvl].huts = [bb.BuilderHut(self.xcen - config.CANNON_WIDTH//2, self.ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(self.xcen//2 - config.CANNON_WIDTH//2, 3*self.ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(3*self.xcen//2 - config.CANNON_WIDTH//2, self.ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(3*self.xcen//2 - config.CANNON_WIDTH//2, 3*self.ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(self.xcen//2 - config.CANNON_WIDTH//2, self.ycen//2 - config.CANNON_WIDTH//2)]
        
        self.levels[self.curr_lvl].walls = []
        for i in range(3*self.xcen//4, 5*self.xcen//4+1):
            for j in range(3*self.ycen//4, 5*self.ycen//4+1):
                if(i == 3*self.xcen//4 or i == 5*self.xcen//4 or j == 3*self.ycen//4 or j == 5*self.ycen//4):
                    self.levels[self.curr_lvl].walls.append(bb.Wall(i, j))
        
        for i in range(self.xcen//4, 7*self.xcen//4+1):
            for j in range(self.ycen//4, 7*self.ycen//4+1):
                if(i == self.xcen//4 or i == 7*self.xcen//4 or j == self.ycen//4 or j == 7*self.ycen//4):
                    self.levels[self.curr_lvl].walls.append(bb.Wall(i, j))
        
        self.king = cc.King(self.xcen-1, self._sceneHeight - 4)
        self.barbarians = []
        self.levels[self.curr_lvl].objArray.append(self.levels[self.curr_lvl].th)
        for i in self.levels[self.curr_lvl].cannons:
            self.levels[self.curr_lvl].objArray.append(i)
        for i in self.levels[self.curr_lvl].huts:
            self.levels[self.curr_lvl].objArray.append(i)
        self.levels[self.curr_lvl].barbsLeft = config.MAX_BARBARIANS
        self.levels[self.curr_lvl].HealsLeft = config.HEAL_SPELL_LIMIT
        self.levels[self.curr_lvl].RageLeft = config.RAGE_SPELL_LIMIT

        self.levels[self.curr_lvl].rageActive = False

        self.levels[self.curr_lvl].infoDisplay = np.array([[Back.BLACK + Style.BRIGHT + ' ' for i in range(self._sceneWidth)] for j in range(9)], dtype=object)

        self.Refresh()

    def ColorGrid(self, x, y, col, char):
        if(col == 'green'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.GREEN + Style.BRIGHT + char
        if(col == 'yellow'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.YELLOW + Style.BRIGHT + char
        if(col == 'red'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.RED + Style.BRIGHT + char
        if(col == 'blue'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.BLUE + Style.BRIGHT + char
        if(col == 'white'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.WHITE + Style.BRIGHT + char
        if(col == 'black'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.BLACK + Style.BRIGHT + char
        if(col == 'cyan'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.CYAN + Style.BRIGHT + char
        if(col == 'magenta'):self.levels[self.curr_lvl].scene[x][y][0] = Fore.MAGENTA + Style.BRIGHT + char
    
    def _drawScene(self):
        grid_str = ''
        for i in range(self._sceneHeight):
            for j in range(self._sceneWidth):
                grid_str += Fore.RESET + Back.RESET +  self.levels[self.curr_lvl].scene[i][j][0]
            grid_str += '\n'
        print(grid_str)
    
    def _drawObj(self,obj):
        for i in range(obj.x, obj.x  + obj.width):
            for j in range(obj.y, obj.y + obj.height):
                if(obj.alive):
                    self.ColorGrid(j, i, obj.textCol, obj.character)
                    if(obj != self.king):
                        self.levels[self.curr_lvl].scene[j][i][1] = obj
                else:
                    self.levels[self.curr_lvl].scene[j][i][0] = Back.BLACK + Style.BRIGHT + ' '
                    self.levels[self.curr_lvl].scene[j][i][1] = 0
    
    def SceneObjects(self):
        # Town Hall
        self._drawObj(self.levels[self.curr_lvl].th)
        # Cannons
        for i in self.levels[self.curr_lvl].cannons:
            if(i.isActive):
                for j in range(i.x, i.x  + i.width):
                    for k in range(i.y, i.y + i.height):
                        if(i.alive):
                            if(i.textCol == 'green'): self.levels[self.curr_lvl].scene[k][j][0] = Fore.GREEN + Back.YELLOW + Style.BRIGHT + i.character
                            elif(i.textCol == 'blue'): self.levels[self.curr_lvl].scene[k][j][0] = Fore.BLUE + Back.YELLOW + Style.BRIGHT + i.character
                            elif(i.textCol == 'red'): self.levels[self.curr_lvl].scene[k][j][0] = Fore.RED + Back.YELLOW + Style.BRIGHT + i.character
                        else:
                            self._drawObj(i)
            else:
                if(i.alive):
                    self._drawObj(i)
            if(self.NetFrames > 25):
                i.Attack(self.barbarians, self.king)
        # Huts
        for i in self.levels[self.curr_lvl].huts:
            self._drawObj(i)
        # Walls
        for i in self.levels[self.curr_lvl].walls:
            self._drawObj(i)
        #King
        if(self.king.alive):
            if(self.king.health > 0.7*config.KING_HEALTH):
                self.king.textCol = 'cyan'
            elif(self.king.health > 0.4*config.KING_HEALTH):
                self.king.textCol = 'yellow'
            else:
                self.king.textCol = 'green'
            self._drawObj(self.king)
            if(self.king.swordAttatched != 0):
                if(self.king.prevKey == 'w'):
                    self.ColorGrid(self.king.ycen, self.king.xcen, 'red', '^')
                if(self.king.prevKey == 'a'):
                    self.ColorGrid(self.king.ycen, self.king.xcen, 'red', '<')
                if(self.king.prevKey == 's'):
                    self.ColorGrid(self.king.ycen, self.king.xcen, 'red', 'v')
                if(self.king.prevKey == 'd'):
                    self.ColorGrid(self.king.ycen, self.king.xcen, 'red', '>')
                else: pass
                self.king.swordAttatched += 1
                if(self.king.swordAttatched == 3):
                    self.king.displaySword = False
                    self.king.swordAttatched = 0
        #Barbarians
        for i in self.barbarians:
            if(i.alive):
                if(i.health > 7):
                    self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.MAGENTA + Style.BRIGHT + 'B'
                elif(i.health > 4):
                    self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.LIGHTMAGENTA_EX + Style.BRIGHT + 'B'
                else:
                    self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.YELLOW + Style.BRIGHT + 'B'
                i.Move(self.levels[self.curr_lvl].objArray, self.levels[self.curr_lvl].scene)
    def Refresh(self):
        while(True):

            if(self.levels[self.curr_lvl].rageActive == True):
                if(time.time() - self.rageTime > config.RAGE_TIME):
                    self.levels[self.curr_lvl].rageActive = False
                    self.rageTime = 0
                    self.king.damage /= config.RAGE_MULTIPLIER
                    self.king.moveAfter *= config.RAGE_MULTIPLIER
                    for i in self.barbarians:
                        i.damage /= config.RAGE_MULTIPLIER
                        i.moveAfter *= config.RAGE_MULTIPLIER
            if(self.king.alive == False and self.levels[self.curr_lvl].barbsLeft == 0 and len(self.barbarians) == 0):
                sp.call('clear', shell=True)
                DefeatText()
                break
            if(len(self.levels[self.curr_lvl].objArray) == 0):
                sp.call('clear', shell=True)
                VictoryText()
                break
            #Read line by line from file
            z = input_to(InputVar)
            if(z == 'q'):
                break
            p = f.read(1)
            if(p == 'q'):
                sp.call('clear', shell=True)
                DefeatText()
                break
            elif(p == 'g'):
                self.levels[self.curr_lvl].scene[0][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].barbsLeft > 0):
                    self.barbarians.append(cc.Barbarian(1, 1))
                    self.levels[self.curr_lvl].barbsLeft -= 1
            elif(p == 'j'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][self._sceneWidth - 1][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].barbsLeft > 0):
                    self.barbarians.append(cc.Barbarian(self._sceneWidth - 2, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].barbsLeft -= 1
            elif(p == 'h'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].barbsLeft > 0):
                    self.barbarians.append(cc.Barbarian(1, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].barbsLeft -= 1
            elif(p == 'o'):
                if(self.levels[self.curr_lvl].HealsLeft > 0):
                    ss.Heal("heal", config.HEALTH_MULTIPLIER).IncreaseHealth(self.king, self.barbarians)
                    self.levels[self.curr_lvl].HealsLeft -= 1
            elif(p == 'p'):
                if(self.levels[self.curr_lvl].RageLeft > 0):
                    ss.Rage("rage", config.RAGE_MULTIPLIER).IncreaseHealth(self.king, self.barbarians)
                    self.levels[self.curr_lvl].RageLeft -= 1
                    self.levels[self.curr_lvl].rageActive = True
                    self.rageTime = time.time()
            elif(p == 'z'):
                if(self.levels[self.curr_lvl].leviathan == False):
                    self.levels[self.curr_lvl].leviathan = True
                    sp.call('aplay -q audio/king_levi.wav&', shell=True)
            elif(p == 'a'):
                self.king.Movement('a', self.levels[self.curr_lvl].scene)
            elif(p == 'w'):
                self.king.Movement('w', self.levels[self.curr_lvl].scene)
            elif(p == 's'):
                self.king.Movement('s', self.levels[self.curr_lvl].scene)
            elif(p == 'd'):
                self.king.Movement('d', self.levels[self.curr_lvl].scene)
            elif(p == ' '):
                if(self.king.swordAttatched == 0):
                        self.king.swordAttatched = 1
                        if(self.levels[self.curr_lvl].leviathan == False):
                            self.king.Attack(self.levels[self.curr_lvl].scene, self.levels[self.curr_lvl].objArray)
                        else:
                            self.king.LeviathanAttack(self.levels[self.curr_lvl].scene, self.levels[self.curr_lvl].objArray)
            else:
                self.levels[self.curr_lvl].scene[0][0][0] = Back.GREEN + Style.BRIGHT + ' '
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][self._sceneWidth - 1][0] = Back.GREEN + Style.BRIGHT + ' '
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][0][0] = Back.GREEN + Style.BRIGHT + ' '
            if(time.time() - self.__lastRefresh > 1/config.REFRESH_RATE):
                RepositionCursor(0,0)
                for i in range(1, self._sceneHeight - 1):
                    for j in range(1, self._sceneWidth - 1):
                        self.levels[self.curr_lvl].scene[i][j][0] = Back.BLACK + Style.BRIGHT + ' '
                for i in range(len(self.levels[self.curr_lvl].infoDisplay)):
                    for j in range(len(self.levels[self.curr_lvl].infoDisplay[i])):
                        self.levels[self.curr_lvl].infoDisplay[i][j] = Back.BLACK + Style.BRIGHT + ' '
                string= []
                string.append("King Health: ")
                string.append("Barbarians Left: " + str(self.levels[self.curr_lvl].barbsLeft))
                string.append("Barbarians Alive: " + str(len(self.barbarians)))
                string.append("Heals Left: " + str(self.levels[self.curr_lvl].HealsLeft))
                string.append("Rage Left: " + str(self.levels[self.curr_lvl].RageLeft))
                string.append("Leviathan Mode Active: " + str(self.levels[self.curr_lvl].leviathan))
                string.append("Rage Active: " + str(self.levels[self.curr_lvl].rageActive))
                string.append("Buildings Left: " + str(len(self.levels[self.curr_lvl].objArray)))
                cells_left = config.SCENE_WIDTH - len(string[0]) - 5
                to_color = int(cells_left * self.king.health / config.KING_HEALTH)
                for i in range(len(string)):
                    for j in range(len(string[i])):
                        self.levels[self.curr_lvl].infoDisplay[i][j] = Back.BLACK + Style.BRIGHT + string[i][j]
                for i in range(to_color):
                    if(self.king.textCol == 'green'):self.levels[self.curr_lvl].infoDisplay[0][i + len(string[0]) + 5] = Back.GREEN + Style.BRIGHT + ' '
                    elif(self.king.textCol == 'cyan'):self.levels[self.curr_lvl].infoDisplay[0][i + len(string[0]) + 5] = Back.CYAN + Style.BRIGHT + ' '
                    else : self.levels[self.curr_lvl].infoDisplay[0][i + len(string[0]) + 5] = Back.YELLOW + Style.BRIGHT + ' '
                info_str = ""
                for i in range(len(self.levels[self.curr_lvl].infoDisplay)):
                    for j in range(len(self.levels[self.curr_lvl].infoDisplay[i])):
                        info_str += self.levels[self.curr_lvl].infoDisplay[i][j]
                    info_str += "\n"
                self.levels[self.curr_lvl].sceneObjects()
                self._drawScene()
                self.__lastRefresh = time.time()
                print(info_str)
                self.NetFrames += 1

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    os.system("setterm -cursor off")
    MainGame = Replay()
    os.system("setterm -cursor on")