from matplotlib.pyplot import close
import src.config as config
from src.config import KING_HEALTH, KING_DAMAGE, BARBARIANS_HEALTH, BARBARIANS_ATTACK_DELAY, KING_ATTACK_DELAY
import time
import subprocess as sp
class Character:
    def __init__(self, health, x, y):
        self.health = health
        self.x = x
        self.y = y
        self.alive = True
        self.swordAttatched = 1
        self.moveAfter = 0.2

class King(Character):
    def __init__(self, x, y):
        super().__init__(KING_HEALTH, x, y)
        self.name = 'King'
        self.width = 3
        self.height = 3
        self.character = 'K'
        self.textCol = "cyan"
        self.prevKey = 'w'
        self.xcen = x + 1
        self.ycen = y + 1
        self.damage = KING_DAMAGE
        self.lastAttack = time.time()
        self.displaySword = False
        self.lastMove = time.time()
    
    def Movement(self,key,grid):
        if(time.time() - self.lastMove > self.moveAfter):
            if(key == 'w' or key == 'W'):
                self.prevKey = 'w'
                if(grid[self.ycen-2][self.xcen][1] == 0 and grid[self.ycen-2][self.xcen-1][1] == 0 and grid[self.ycen-2][self.xcen+1][1] == 0):
                    self.y -= 1
                    self.ycen -= 1
            elif(key == 's' or key == 'S'):
                self.prevKey = 's'
                if(grid[self.ycen+2][self.xcen][1] == 0 and grid[self.ycen+2][self.xcen-1][1] == 0 and grid[self.ycen+2][self.xcen+1][1] == 0):
                    self.y += 1
                    self.ycen += 1
            elif(key == 'a' or key == 'A'):
                self.prevKey = 'a'
                if(grid[self.ycen][self.xcen-2][1] == 0 and grid[self.ycen-1][self.xcen-2][1] == 0 and grid[self.ycen+1][self.xcen-2][1] == 0):
                    self.x -= 1
                    self.xcen -= 1
            elif(key == 'd' or key == 'D'):
                self.prevKey = 'd'
                if(grid[self.ycen][self.xcen+2][1] == 0 and grid[self.ycen-1][self.xcen+2][1] == 0 and grid[self.ycen+1][self.xcen+2][1] == 0):
                    self.x += 1
                    self.xcen += 1
            else:
                pass
            self.lastMove = time.time()
    
    def Attack(self, grid, buildings):
        if(time.time() - self.lastAttack > KING_ATTACK_DELAY):
            sp.call('aplay -q audio/king_attack.wav&', shell=True)
            self.displaySword = True
            if(self.prevKey == 'w'):
                objs = [grid[self.ycen-2][self.xcen-1][1], grid[self.ycen-2][self.xcen][1], grid[self.ycen-2][self.xcen+1][1]]
                #remove all objects of type 'boundary'
                objs = [obj for obj in objs if obj != 'boundary']
                objs = set(objs)
                for i in objs:
                    if(i != 0):
                        i.hitpoints -= self.damage
                        i.find_color(i.prim, i.sec, i.tert)
                        if(i.hitpoints <= 0):
                            i.OnDestroy()
                            i.alive = False
                            i.hitpoints = 0
                            if(i in buildings):
                                buildings.remove(i)
            elif(self.prevKey == 's'):
                objs = [grid[self.ycen+2][self.xcen-1][1], grid[self.ycen+2][self.xcen][1], grid[self.ycen+2][self.xcen+1][1]]
                objs = [obj for obj in objs if obj != 'boundary']
                objs = set(objs)
                for i in objs:
                    if(i != 0 and i != 'boundary'):
                        i.hitpoints -= self.damage
                        i.find_color(i.prim, i.sec, i.tert)
                        if(i.hitpoints <= 0):
                            i.OnDestroy()
                            i.alive = False
                            i.hitpoints = 0
                            if(i in buildings):
                                buildings.remove(i)
            elif(self.prevKey == 'a'):
                objs = [grid[self.ycen-1][self.xcen-2][1], grid[self.ycen][self.xcen-2][1], grid[self.ycen+1][self.xcen-2][1]]
                objs = [obj for obj in objs if obj != 'boundary']
                objs = set(objs)
                for i in objs:
                    if(i != 0):
                        i.hitpoints -= self.damage
                        i.find_color(i.prim, i.sec, i.tert)
                        if(i.hitpoints <= 0):
                            i.OnDestroy()
                            i.alive = False
                            i.hitpoints = 0
                            if(i in buildings):
                                buildings.remove(i)
            elif(self.prevKey == 'd'):
                objs = [grid[self.ycen-1][self.xcen+2][1], grid[self.ycen][self.xcen+2][1], grid[self.ycen+1][self.xcen+2][1]]
                objs = [obj for obj in objs if obj != 'boundary']
                objs = set(objs)
                for i in objs:
                    if(i != 0):
                        i.hitpoints -= self.damage
                        i.find_color(i.prim, i.sec, i.tert)
                        if(i.hitpoints <= 0):
                            i.OnDestroy()
                            i.alive = False
                            i.hitpoints = 0
                            if(i in buildings):
                                buildings.remove(i)
            else:
                pass
            self.lastAttack = time.time()
    def LeviathanAttack(self, grid, buildings):
        targets = []
        if(time.time() - self.lastAttack > KING_ATTACK_DELAY):
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    if(grid[i][j][1] != 0 and grid[i][j][1] != 'boundary' and grid[i][j][1].alive == True):
                        if(abs(self.xcen - grid[i][j][1].xcen)**2 + abs(self.ycen - grid[i][j][1].ycen)**2 < 25):
                            if(grid[i][j][1] in targets):
                                continue
                            targets.append(grid[i][j][1])
                            grid[i][j][1].hitpoints -= self.damage
                            grid[i][j][1].find_color(grid[i][j][1].prim, grid[i][j][1].sec, grid[i][j][1].tert)
                            if(grid[i][j][1].hitpoints <= 0):
                                grid[i][j][1].OnDestroy()
                                grid[i][j][1].alive = False
                                grid[i][j][1].hitpoints = 0
                                if(grid[i][j][1] in buildings):
                                    buildings.remove(grid[i][j][1])
            self.lastAttack = time.time()
    
    def OnDeath(self):
        sp.call('aplay -q audio/king-die.wav&', shell=True)

class Queen(King):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.name = 'Queen'
        self.damage = int(0.75*self.damage)
        self.character = 'Q'

    def Attack(self, grid, buildings):
        if(time.time() - self.lastAttack > KING_ATTACK_DELAY):
            targets = []
            self.displaySword = True
            if(self.prevKey == 'w'):
                Y = max(self.ycen - 8, 1)
                X = self.xcen
            if(self.prevKey == 's'):
                Y = min(self.ycen + 8, len(grid)-2)
                X = self.xcen
            if(self.prevKey == 'a'):
                Y = self.ycen
                X = max(self.xcen - 8, 1)
            if(self.prevKey == 'd'):
                Y = self.ycen
                X = min(self.xcen + 8, len(grid[0])-2)
            for i in range(Y-2,Y+3):
                for j in range(X-2, X+3):
                    if(i >= 1 and i <= len(grid)-2 and j >= 1 and j <= len(grid[0])-2):
                        if(grid[i][j][1] != 0 and grid[i][j][1] != 'boundary' and grid[i][j][1].alive == True):
                            if(grid[i][j][1] in targets):
                                continue
                            targets.append(grid[i][j][1])
                            grid[i][j][1].hitpoints -= self.damage
                            grid[i][j][1].find_color(grid[i][j][1].prim, grid[i][j][1].sec, grid[i][j][1].tert)
                            if(grid[i][j][1].hitpoints <= 0):
                                grid[i][j][1].OnDestroy()
                                grid[i][j][1].alive = False
                                grid[i][j][1].hitpoints = 0
                                if(grid[i][j][1] in buildings):
                                    buildings.remove(grid[i][j][1])
    def SpecialAttack(self, grid, buildings):
        if(time.time() - self.lastAttack > KING_ATTACK_DELAY):
            targets = []
            self.displaySword = True
            if(self.prevKey == 'w'):
                Y = max(self.ycen - 16, 1)
                X = self.xcen
            if(self.prevKey == 's'):
                Y = min(self.ycen + 16, len(grid)-2)
                X = self.xcen
            if(self.prevKey == 'a'):
                Y = self.ycen
                X = max(self.xcen - 16, 1)
            if(self.prevKey == 'd'):
                Y = self.ycen
                X = min(self.xcen + 16, len(grid[0])-2)
            for i in range(Y-4,Y+5):
                for j in range(X-4, X+5):
                    if(i >= 1 and i <= len(grid)-2 and j >= 1 and j <= len(grid[0])-2):
                        if(grid[i][j][1] != 0 and grid[i][j][1] != 'boundary' and grid[i][j][1].alive == True):
                            if(grid[i][j][1] in targets):
                                continue
                            targets.append(grid[i][j][1])
                            grid[i][j][1].hitpoints -= self.damage
                            grid[i][j][1].find_color(grid[i][j][1].prim, grid[i][j][1].sec, grid[i][j][1].tert)
                            if(grid[i][j][1].hitpoints <= 0):
                                grid[i][j][1].OnDestroy()
                                grid[i][j][1].alive = False
                                grid[i][j][1].hitpoints = 0
                                if(grid[i][j][1] in buildings):
                                    buildings.remove(grid[i][j][1])

class Barbarian(Character):
    def __init__(self, x, y):
        super().__init__(10, x, y)
        self.name = 'Barbarian'
        self.width = 1
        self.height = 1
        self.closestBuilding = None
        self.direction = ((0,-1))
        self.damage = 10
        self.xcen = x
        self.ycen = y
        self.health = BARBARIANS_HEALTH
        self.lastAttack = time.time()
        self.lastMove = time.time()
        self.range = 1
        self.distArray = [[1000 for i in range (config.SCENE_WIDTH)] for j in range (config.SCENE_HEIGHT)]
        sp.call('aplay -q audio/barb_spawn.wav&', shell=True)
    
    def __ComputeClosest(self, buildings):
        closest = None
        for i in buildings:
            if(closest == None):
                closest = i
            elif(abs(self.x - i.xcen) + abs(self.y - i.ycen) < abs(self.x - closest.xcen) + abs(self.y - closest.ycen)):
                closest = i
        self.closestBuilding = closest

    def Move(self,buildings,grid,rng=1):
        if(len(buildings) == 0):
            return
        self.__ComputeClosest(buildings)
        ########################AVOIDING_WALLS##############################
        bestX = 0
        bestY = 0
        fnd = False
        for i in [self.y, self.y-1, self.y+1]:
            for j in [self.x, self.x-1,self.x+1]:
                if(j == self.x and i == self.y):
                    continue
                else:
                    if(self.closestBuilding.distArray2[i][j] < self.closestBuilding.distArray2[bestY][bestX]):
                        fnd = True
                        self.direction = ((j-self.x,i-self.y))
                        bestX = j
                        bestY = i
        if(fnd):
            if(self.closestBuilding.distArray2[self.y][self.x] <= rng):
                self.Attack(self.closestBuilding, buildings)
                return 
            elif(grid[bestY][bestX][1] == 0 or self.name == 'Balloon'):
                if(time.time() - self.lastMove > self.moveAfter):
                    self.x = bestX
                    self.y = bestY
                    self.xcen = bestX
                    self.ycen = bestY
                    self.lastMove = time.time()
            else:
                self.Attack(self.closestBuilding, buildings)
        ######################################################################
        bestX = 0
        bestY = 0
        for i in [self.y, self.y-1, self.y+1]:
            for j in [self.x, self.x-1,self.x+1]:
                if(j == self.x and i == self.y):
                    continue
                else:
                    if(self.closestBuilding.distArray[i][j] < self.closestBuilding.distArray[bestY][bestX]):
                        self.direction = ((j-self.x,i-self.y))
                        bestX = j
                        bestY = i
        if(self.closestBuilding.distArray[self.y][self.x] <= rng):
            self.Attack(self.closestBuilding, buildings)
        elif(grid[bestY][bestX][1] == 0 or self.name == 'Balloon'):
            if(time.time() - self.lastMove > self.moveAfter):
                self.x = bestX
                self.y = bestY
                self.xcen = bestX
                self.ycen = bestY
                self.lastMove = time.time()
        else :
            self.Attack(grid[bestY][bestX][1],buildings)
    
    def Attack(self, obj,buildings):
        x = time.time()
        if(x - self.lastAttack > BARBARIANS_ATTACK_DELAY):
            obj.hitpoints -= self.damage
            obj.find_color(obj.prim, obj.sec, obj.tert)
            if(obj.hitpoints <= 0):
                obj.OnDestroy()
                obj.alive = False
                obj.hitpoints = 0
                if(obj in buildings):
                    buildings.remove(obj)
    def OnDeath(self):
        sp.call('aplay -q audio/barb_die.wav&', shell=True)

class Archer(Barbarian):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = 'Archer'
        self.damage /= 2
        self.moveAfter /= 2
        self.health /= 2
        self.range = 5

class Balloon(Barbarian):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.damage *= 2
        self.moveAfter /= 2
        self.range = 0
        self.name = 'Balloon'
    
    def __ComputeClosest(self, buildings):
        closest = None
        prefOne = [i for i in buildings if i.name == 'wizard_tower' or i.name == 'cannon']
        prefTwo = [i for i in buildings if i.name != 'wizard_tower' and i.name != 'cannon']
        for i in prefOne:
            if(closest == None):
                closest = i
            elif(abs(self.x - i.xcen) + abs(self.y - i.ycen) < abs(self.x - closest.xcen) + abs(self.y - closest.ycen)):
                closest = i
        if(closest == None):
            for i in prefTwo:
                if(closest == None):
                    closest = i
                elif(abs(self.x - i.xcen) + abs(self.y - i.ycen) < abs(self.x - closest.xcen) + abs(self.y - closest.ycen)):
                    closest = i
        self.closestBuilding = closest
    def Move(self,buildings,grid,rng=1):
        if(len(buildings) == 0):
            return
        if(self.closestBuilding == None or self.closestBuilding not in buildings):
            self.__ComputeClosest(buildings)
        bestX = 0
        bestY = 0
        for i in [self.y, self.y-1, self.y+1]:
            for j in [self.x, self.x-1,self.x+1]:
                if(j == self.x and i == self.y):
                    continue
                else:
                    if(self.closestBuilding.distArray[i][j] < self.closestBuilding.distArray[bestY][bestX]):
                        self.direction = ((j-self.x,i-self.y))
                        bestX = j
                        bestY = i
        if(self.closestBuilding.distArray[self.y][self.x] <= rng):
            self.Attack(self.closestBuilding, buildings)
        elif(grid[bestY][bestX][1] == 0 or self.name == 'Balloon'):
            if(time.time() - self.lastMove > self.moveAfter):
                self.x = bestX
                self.y = bestY
                self.xcen = bestX
                self.ycen = bestY
                self.lastMove = time.time()
        else :
            self.Attack(grid[bestY][bestX][1],buildings)
    