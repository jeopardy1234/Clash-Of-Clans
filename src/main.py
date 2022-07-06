import colorama
from colorama import init, Fore, Back, Style
import numpy as np
from sklearn import neural_network
from sqlalchemy import null
import src.config as config
import subprocess as sp
from src.input import input_to
import time
import os
import src.building as bb
import src.character as cc
import src.spell as ss
import json
import sys, signal

from game import InputVar

colorama.init(autoreset=True)

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

files = os.listdir("./replays")
num_files = len(files)
f = open(f"./replays/{num_files+1}.txt", "a+")

class Level:
    def __init__(self, lvl, sceneWidth, sceneHeight):
        self.level = lvl
        self._sceneWidth = sceneWidth
        self._sceneHeight = sceneHeight
        self.scene = np.array([[[Back.BLACK + Style.BRIGHT + ' ',0] for i in range(self._sceneWidth)] for j in range(self._sceneHeight)], dtype=object)
        for i in range(self._sceneHeight):
            for j in range(self._sceneWidth):
                if(i == 0 or i == self._sceneHeight - 1 or j == 0 or j == self._sceneWidth - 1):
                    self.scene[i][j][0] = Back.BLACK + Style.BRIGHT + '#'
                    self.scene[i][j][1] = "boundary"
        self.scene[0][0][0] = Back.GREEN + Style.BRIGHT + ' '
        self.scene[self._sceneHeight - 1][self._sceneWidth - 1][0] = Back.GREEN + Style.BRIGHT + ' '
        self.scene[self._sceneHeight - 1][0][0] = Back.GREEN + Style.BRIGHT + ' '
        self.th = bb.TownHall()
        self.cannons = []
        self.huts = []  
        self.walls = []
        self.wizard_towers = []
        self.hero = 0
        self.troops = []
        self.objArray = []
        self.infoDisplay = np.array([[Back.BLACK + Style.BRIGHT + ' ' for i in range(self._sceneWidth)] for j in range(8)], dtype=object)
        self.barbsLeft = config.MAX_BARBARIANS
        self.archLeft = config.MAX_ARCHERS
        self.loonsLeft = config.MAX_BALLOONS
        self.HealsLeft = config.HEAL_SPELL_LIMIT
        self.RageLeft = config.RAGE_SPELL_LIMIT
        self.rageActive = False
        self.leviathan = False
        self.eagleArrow = False
        self.arrowCallTime = 0

def BuildLevel(lvl, xcen, ycen, sceneWidth, sceneHeight, type):
    l = Level(lvl, sceneWidth, sceneHeight)
    if(type == 0): l.hero = cc.King(xcen-1, sceneHeight - 4)
    else: l.hero = cc.Queen(xcen-1, sceneHeight - 4)
    if(lvl == 0):
        l.th = bb.TownHall()
        l.cannons = [ 
                        bb.Cannon(xcen//2 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                        ,bb.Cannon(3*xcen//2 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                    ]
        
        l.huts = [
                    bb.BuilderHut(xcen//2 - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(xcen - 3 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(3*xcen//2 - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(3*xcen//2 - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(xcen//2 - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2)
                ]
        l.wizard_towers = [bb.WizardTower(xcen - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2), bb.WizardTower(xcen - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2)]
        for i in range(3*xcen//4, 5*xcen//4+1):
            for j in range(3*ycen//4, 5*ycen//4+1):
                if(i == 3*xcen//4 or i == 5*xcen//4 or j == 3*ycen//4 or j == 5*ycen//4):
                    l.walls.append(bb.Wall(i, j))
        for i in range(xcen//4, 7*xcen//4+1):
            for j in range(ycen//4, 7*ycen//4+1):
                if(i == xcen//4 or i == 7*xcen//4 or j == ycen//4 or j == 7*ycen//4):
                    l.walls.append(bb.Wall(i, j))
        l.objArray.append(l.th)
        for i in l.cannons:
            l.objArray.append(i)
        for i in l.wizard_towers:
            l.objArray.append(i)
        for i in l.huts:
            l.objArray.append(i)
    if(lvl == 1):
        l.th = bb.TownHall()
        l.cannons = [ 
                        bb.Cannon(xcen//2 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                        ,bb.Cannon(3*xcen//2 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                        ,bb.Cannon(xcen//2 - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2)
                    ]
        
        l.huts = [
                    bb.BuilderHut(xcen - 3 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(5*xcen//8 - config.CANNON_WIDTH//2, 5*ycen//4 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(xcen + 3 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(3*xcen//2 - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(xcen//2 - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2)
                ]
        l.wizard_towers = [bb.WizardTower(xcen - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2), bb.WizardTower(xcen - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2), bb.WizardTower(3*xcen//2 - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2)]
        for i in range(3*xcen//4, 5*xcen//4+1):
            for j in range(3*ycen//4, 5*ycen//4+1):
                if(i == 3*xcen//4 or i == 5*xcen//4 or j == 3*ycen//4 or j == 5*ycen//4):
                    l.walls.append(bb.Wall(i, j))
        for i in range(xcen//4, 7*xcen//4+1):
            for j in range(ycen//4, 7*ycen//4+1):
                if(i == xcen//4 or i == 7*xcen//4 or j == ycen//4 or j == 7*ycen//4):
                    l.walls.append(bb.Wall(i, j))
        l.objArray.append(l.th)
        for i in l.cannons:
            l.objArray.append(i)
        for i in l.wizard_towers:
            l.objArray.append(i)
        for i in l.huts:
            l.objArray.append(i)
    elif(lvl == 2):
        l.th = bb.TownHall()
        l.cannons = [ 
                        bb.Cannon(xcen//2 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                        ,bb.Cannon(3*xcen//2 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                        ,bb.Cannon(xcen//2 - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2)
                        ,bb.Cannon(xcen//2 - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2)
                    ]
        
        l.huts = [
                    bb.BuilderHut(xcen - 3 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(5*xcen//8 - config.CANNON_WIDTH//2, 5*ycen//4 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(xcen + 3 - config.CANNON_WIDTH//2, ycen - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(11*xcen//8 - config.CANNON_WIDTH//2, 5*ycen//4 - config.CANNON_WIDTH//2)
                    ,bb.BuilderHut(xcen + 1 - config.CANNON_WIDTH//2, 5*ycen//8+1 - config.CANNON_WIDTH//2)
                ]
        l.wizard_towers = [
                            bb.WizardTower(xcen - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2), 
                            bb.WizardTower(xcen - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2), 
                            bb.WizardTower(3*xcen//2 - config.CANNON_WIDTH//2, ycen//2 - config.CANNON_WIDTH//2),
                            bb.WizardTower(3*xcen//2 - config.CANNON_WIDTH//2, 3*ycen//2 - config.CANNON_WIDTH//2),
                        ]
        for i in range(3*xcen//4, 5*xcen//4+1):
            for j in range(3*ycen//4, 5*ycen//4+1):
                if(i == 3*xcen//4 or i == 5*xcen//4 or j == 3*ycen//4 or j == 5*ycen//4):
                    l.walls.append(bb.Wall(i, j))
        for i in range(xcen//4, 7*xcen//4+1):
            for j in range(ycen//4, 7*ycen//4+1):
                if(i == xcen//4 or i == 7*xcen//4 or j == ycen//4 or j == 7*ycen//4):
                    l.walls.append(bb.Wall(i, j))
        l.objArray.append(l.th)
        for i in l.cannons:
            l.objArray.append(i)
        for i in l.wizard_towers:
            l.objArray.append(i)
        for i in l.huts:
            l.objArray.append(i)
    return l


        
class COC:
    def __init__(self):
        self._sceneWidth = config.SCENE_WIDTH
        self._sceneHeight = config.SCENE_HEIGHT
        self.xcen = int(self._sceneWidth / 2)
        self.ycen = int(self._sceneHeight / 2)
        self.NetFrames = 0

        self.levels = [Level(0, self._sceneWidth, self._sceneHeight), Level(1, self._sceneWidth, self._sceneHeight), Level(2, self._sceneWidth, self._sceneHeight)]
        self.curr_lvl = 0
        self.__lastRefresh = 0
        self.levels[self.curr_lvl].objArray = []
        self.LvlChange = True
        sp.call('clear', shell=True) 
        self.__ChooseHero()
        self.Refresh()

    def __ChooseHero(self):
        print("Choose Queen or King(q/k)")
        while(1):
            p = input_to(InputVar)
            if(p == 'q'):
                self.__type = 1
                break
            elif(p == 'k'):
                self.__type = 0
                break

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
                    if(obj != self.levels[self.curr_lvl].hero):
                        self.levels[self.curr_lvl].scene[j][i][1] = obj
                else:
                    self.levels[self.curr_lvl].scene[j][i][0] = Back.BLACK + Style.BRIGHT + ' '
                    self.levels[self.curr_lvl].scene[j][i][1] = 0
    
    def SceneObjects(self):
        # Town Hall
        if(self.levels[self.curr_lvl].th.alive):
            self.levels[self.curr_lvl].th.Recompute(self.levels[self.curr_lvl].scene)
        self._drawObj(self.levels[self.curr_lvl].th)
        # Cannons
        for i in self.levels[self.curr_lvl].cannons:
            if(i.alive):
                i.Recompute(self.levels[self.curr_lvl].scene)
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
                i.Attack(self.levels[self.curr_lvl].troops, self.levels[self.curr_lvl].hero)
        # Wizard Towers
        for i in self.levels[self.curr_lvl].wizard_towers:
            if(i.alive):
                i.Recompute(self.levels[self.curr_lvl].scene)
            if(i.isActive):
                for j in range(i.x, i.x  + i.width):
                    for k in range(i.y, i.y + i.height):
                        if(i.alive):
                            if(i.textCol == 'light_blue'): self.levels[self.curr_lvl].scene[k][j][0] = Fore.LIGHTBLUE_EX + Back.YELLOW + Style.BRIGHT + i.character
                            elif(i.textCol == 'blue'): self.levels[self.curr_lvl].scene[k][j][0] = Fore.BLUE + Back.YELLOW + Style.BRIGHT + i.character
                            elif(i.textCol == 'red'): self.levels[self.curr_lvl].scene[k][j][0] = Fore.RED + Back.YELLOW + Style.BRIGHT + i.character
                        else:
                            self._drawObj(i)
            else:
                if(i.alive):
                    self._drawObj(i)
            if(self.NetFrames > 25):
                i.Attack(self.levels[self.curr_lvl].troops, self.levels[self.curr_lvl].hero)
        # Huts
        for i in self.levels[self.curr_lvl].huts:
            if(i.alive):
                i.Recompute(self.levels[self.curr_lvl].scene)
            self._drawObj(i)
        # Walls
        for i in self.levels[self.curr_lvl].walls:
            self._drawObj(i)
        #Hero
        if(self.levels[self.curr_lvl].hero and self.levels[self.curr_lvl].hero.alive):
            if(self.levels[self.curr_lvl].hero.health > 0.7*config.KING_HEALTH):
                self.levels[self.curr_lvl].hero.textCol = 'cyan'
            elif(self.levels[self.curr_lvl].hero.health > 0.4*config.KING_HEALTH):
                self.levels[self.curr_lvl].hero.textCol = 'yellow'
            else:
                self.levels[self.curr_lvl].hero.textCol = 'green'
            self._drawObj(self.levels[self.curr_lvl].hero)
            if(self.levels[self.curr_lvl].hero.swordAttatched != 0):
                if(self.levels[self.curr_lvl].hero.prevKey == 'w'):
                    self.ColorGrid(self.levels[self.curr_lvl].hero.ycen, self.levels[self.curr_lvl].hero.xcen, 'red', '^')
                if(self.levels[self.curr_lvl].hero.prevKey == 'a'):
                    self.ColorGrid(self.levels[self.curr_lvl].hero.ycen, self.levels[self.curr_lvl].hero.xcen, 'red', '<')
                if(self.levels[self.curr_lvl].hero.prevKey == 's'):
                    self.ColorGrid(self.levels[self.curr_lvl].hero.ycen, self.levels[self.curr_lvl].hero.xcen, 'red', 'v')
                if(self.levels[self.curr_lvl].hero.prevKey == 'd'):
                    self.ColorGrid(self.levels[self.curr_lvl].hero.ycen, self.levels[self.curr_lvl].hero.xcen, 'red', '>')
                else: pass
                self.levels[self.curr_lvl].hero.swordAttatched += 1
                if(self.levels[self.curr_lvl].hero.swordAttatched == 3):
                    self.levels[self.curr_lvl].hero.displaySword = False
                    self.levels[self.curr_lvl].hero.swordAttatched = 0
            
        #Troops
        for i in self.levels[self.curr_lvl].troops:
            if(i.name == 'Barbarian'):
                if(i.alive):
                    if(i.health > 7):
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.MAGENTA + Style.BRIGHT + 'B'
                    elif(i.health > 4):
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.LIGHTMAGENTA_EX + Style.BRIGHT + 'B'
                    else:
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.YELLOW + Style.BRIGHT + 'B'
            elif(i.name == 'Archer'):
                if(i.alive):
                    if(i.health > 7):
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.BLUE + Style.BRIGHT + 'A'
                    elif(i.health > 4):
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.LIGHTBLUE_EX + Style.BRIGHT + 'A'
                    else:
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.YELLOW + Style.BRIGHT + 'A'
            else:
                if(i.alive):
                    if(i.health > 7):
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.RED + Style.BRIGHT + 'O'
                    elif(i.health > 4):
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.LIGHTRED_EX + Style.BRIGHT + 'O'
                    else:
                        self.levels[self.curr_lvl].scene[i.ycen][i.xcen][0] = Back.YELLOW + Style.BRIGHT + 'O'
            i.Move(self.levels[self.curr_lvl].objArray, self.levels[self.curr_lvl].scene,i.range)
    def Refresh(self):
        while(True):
            if(self.LvlChange):
                self.levels[self.curr_lvl] = BuildLevel(self.curr_lvl,self.xcen,self.ycen, self._sceneWidth, self._sceneHeight, self.__type)
                self.LvlChange = False
            if(self.levels[self.curr_lvl].rageActive == True):
                if(time.time() - self.rageTime > config.RAGE_TIME):
                    self.levels[self.curr_lvl].rageActive = False
                    self.rageTime = 0
                    self.levels[self.curr_lvl].hero.damage /= config.RAGE_MULTIPLIER
                    self.levels[self.curr_lvl].hero.moveAfter *= config.RAGE_MULTIPLIER
                    for i in self.levels[self.curr_lvl].troops:
                        i.damage /= config.RAGE_MULTIPLIER
                        i.moveAfter *= config.RAGE_MULTIPLIER
            if(self.levels[self.curr_lvl].hero and self.levels[self.curr_lvl].hero.alive == False and self.levels[self.curr_lvl].barbsLeft == 0 and len(self.levels[self.curr_lvl].troops) == 0):
                sp.call('clear', shell=True)
                DefeatText()
                break
            p = input_to(InputVar)
            if(len(self.levels[self.curr_lvl].objArray) == 0 or p == '+'):
                sp.call('clear', shell=True)
                VictoryText()
                if(self.curr_lvl ==2):
                    break
                else:
                    self.curr_lvl += 1
                    self.LvlChange = True
                    print("\nContinue to Next Level? (y/n)")
                    out = False
                    while(True):
                        q = input_to(InputVar)
                        if(q == 'y'):
                            break
                        elif(q == 'n'):
                            out = True
                            break
                    if(out):
                        break
                    continue
            if(p != None):
                f.write(str(p))
            else:
                f.write('#')
            if(p == 'q'):
                sp.call('clear', shell=True)
                DefeatText()
                break
            elif(p == 'g'):
                self.levels[self.curr_lvl].scene[0][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].barbsLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Barbarian(1, 1))
                    self.levels[self.curr_lvl].barbsLeft -= 1
            elif(p == 'j'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][self._sceneWidth - 1][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].barbsLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Barbarian(self._sceneWidth - 2, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].barbsLeft -= 1
            elif(p == 'h'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].barbsLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Barbarian(1, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].barbsLeft -= 1
            elif(p == 'b'):
                self.levels[self.curr_lvl].scene[0][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].archLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Archer(1, 1))
                    self.levels[self.curr_lvl].archLeft -= 1
            elif(p == 'm'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][self._sceneWidth - 1][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].archLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Archer(self._sceneWidth - 2, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].archLeft -= 1
            elif(p == 'n'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].archLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Archer(1, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].archLeft -= 1
            elif(p == 'e'):
                self.levels[self.curr_lvl].scene[0][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].loonsLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Balloon(1, 1))
                    self.levels[self.curr_lvl].loonsLeft -= 1
            elif(p == 't'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][self._sceneWidth - 1][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].loonsLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Balloon(self._sceneWidth - 2, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].loonsLeft -= 1
            elif(p == 'r'):
                self.levels[self.curr_lvl].scene[self._sceneHeight - 1][0][0] = Back.MAGENTA + Style.BRIGHT + ' '
                if(self.levels[self.curr_lvl].loonsLeft > 0):
                    self.levels[self.curr_lvl].troops.append(cc.Balloon(1, self._sceneHeight - 2))
                    self.levels[self.curr_lvl].loonsLeft -= 1
            elif(p == 'o'):
                if(self.levels[self.curr_lvl].HealsLeft > 0):
                    ss.Heal("heal", config.HEALTH_MULTIPLIER).IncreaseHealth(self.levels[self.curr_lvl].hero, self.levels[self.curr_lvl].troops)
                    self.levels[self.curr_lvl].HealsLeft -= 1
            elif(p == 'p'):
                if(self.levels[self.curr_lvl].RageLeft > 0):
                    ss.Rage("rage", config.RAGE_MULTIPLIER).IncreaseHealth(self.levels[self.curr_lvl].hero, self.levels[self.curr_lvl].troops)
                    self.levels[self.curr_lvl].RageLeft -= 1
                    self.levels[self.curr_lvl].rageActive = True
                    self.rageTime = time.time()
            elif(p == 'z'):
                if(self.levels[self.curr_lvl].hero and self.levels[self.curr_lvl].hero.name == "King"):
                    if(self.levels[self.curr_lvl].leviathan == False):
                        self.levels[self.curr_lvl].leviathan = True
                        sp.call('aplay -q audio/king_levi.wav&', shell=True)
                if(self.levels[self.curr_lvl].hero and self.levels[self.curr_lvl].hero.name == 'Queen'):
                    if(self.levels[self.curr_lvl].eagleArrow == False):
                        self.levels[self.curr_lvl].eagleArrow = True
                        self.levels[self.curr_lvl].arrowCallTime = time.time()
                    else:
                        if(time.time() - self.levels[self.curr_lvl].arrowCallTime > config.EAGLE_ARROW_COOLDOWN):
                            self.levels[self.curr_lvl].eagleArrow = False
                            self.levels[self.curr_lvl].hero.SpecialAttack(self.levels[self.curr_lvl].scene, self.levels[self.curr_lvl].objArray)
            elif(p == 'a'):
                self.levels[self.curr_lvl].hero.Movement('a', self.levels[self.curr_lvl].scene)
            elif(p == 'w'):
                self.levels[self.curr_lvl].hero.Movement('w', self.levels[self.curr_lvl].scene)
            elif(p == 's'):
                self.levels[self.curr_lvl].hero.Movement('s', self.levels[self.curr_lvl].scene)
            elif(p == 'd'):
                self.levels[self.curr_lvl].hero.Movement('d', self.levels[self.curr_lvl].scene)
            elif(p == ' '):
                if(self.levels[self.curr_lvl].eagleArrow): continue
                if(self.levels[self.curr_lvl].hero and self.levels[self.curr_lvl].hero.swordAttatched == 0):
                        self.levels[self.curr_lvl].hero.swordAttatched = 1
                        if(self.levels[self.curr_lvl].leviathan == False):
                            self.levels[self.curr_lvl].hero.Attack(self.levels[self.curr_lvl].scene, self.levels[self.curr_lvl].objArray)
                        else:
                            self.levels[self.curr_lvl].hero.LeviathanAttack(self.levels[self.curr_lvl].scene, self.levels[self.curr_lvl].objArray)
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
                string.append("Level: " + str(self.curr_lvl + 1))
                string.append("Hero's Health: ")
                string.append("Troops Left: " + str(self.levels[self.curr_lvl].barbsLeft + self.levels[self.curr_lvl].loonsLeft +self.levels[self.curr_lvl].archLeft))
                string.append("Troops Alive: " + str(len(self.levels[self.curr_lvl].troops)))
                string.append("Heals Left: " + str(self.levels[self.curr_lvl].HealsLeft))
                string.append("Rage Left: " + str(self.levels[self.curr_lvl].RageLeft))
                string.append("Buildings Left: " + str(len(self.levels[self.curr_lvl].objArray)))
                cells_left = config.SCENE_WIDTH - len(string[0]) - 5
                if(self.levels[self.curr_lvl].hero):to_color = int(cells_left * self.levels[self.curr_lvl].hero.health / config.KING_HEALTH)
                for i in range(len(string)):
                    for j in range(len(string[i])):
                        self.levels[self.curr_lvl].infoDisplay[i][j] = Back.BLACK + Style.BRIGHT + string[i][j]
                if(self.levels[self.curr_lvl].hero):
                    for i in range(to_color): 
                        if(self.levels[self.curr_lvl].hero.textCol == 'green'):self.levels[self.curr_lvl].infoDisplay[1][i + len(string[0]) + 5] = Back.GREEN + Style.BRIGHT + ' '
                        elif(self.levels[self.curr_lvl].hero.textCol == 'cyan'):self.levels[self.curr_lvl].infoDisplay[1][i + len(string[0]) + 5] = Back.CYAN + Style.BRIGHT + ' '
                        else : self.levels[self.curr_lvl].infoDisplay[1][i + len(string[0]) + 5] = Back.YELLOW + Style.BRIGHT + ' '
                info_str = ""
                for i in range(len(self.levels[self.curr_lvl].infoDisplay)):
                    for j in range(len(self.levels[self.curr_lvl].infoDisplay[i])):
                        info_str += self.levels[self.curr_lvl].infoDisplay[i][j]
                    info_str += "\n"
                self.SceneObjects()
                self._drawScene()
                self.__lastRefresh = time.time()
                print(info_str)
                self.NetFrames += 1
        f.close()
        