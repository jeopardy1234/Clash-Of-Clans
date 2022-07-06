from sqlalchemy import null
import src.config as config
import time
import subprocess as sp
class Building:
    def __init__(self, x, y, width, height, hitpoints):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitpoints = hitpoints
        self.original_hitpoints = hitpoints
        self.alive = True
        self.distArray  = [[1000 for i in range(config.SCENE_WIDTH)] for j in range(config.SCENE_HEIGHT)]
        self.distArray2 = [[1000 for i in range(config.SCENE_WIDTH)] for j in range(config.SCENE_HEIGHT)]
        self.previousCompute = None
        if(self.character != 'X'):
            self.ComputeMiddle()
            self.BFS()
    def find_color(self,prim,sec,ter):
        if(self.hitpoints > 0.5 * self.original_hitpoints):
            self.textCol = prim
        elif(self.hitpoints > 0.2 * self.original_hitpoints):
            self.textCol = sec
        else:
            self.textCol = ter
    def ComputeMiddle(self):
        self.xcen = self.x + self.width // 2
        self.ycen = self.y + self.height // 2
    def OnDestroy(self):
        sp.call('aplay -q audio/building_destroy.wav&', shell=True)
    def BFS(self):
        queue = []
        queue.append((self.ycen, self.xcen))
        self.distArray[self.ycen][self.xcen] = 0
        while(len(queue) > 0):
            i,j = queue.pop(0)
            if(i-1 > 0 and self.distArray[i-1][j] == 1000):
                queue.append((i-1, j))
                self.distArray[i-1][j] = self.distArray[i][j] + 1
            if(i+1 < config.SCENE_HEIGHT-1 and self.distArray[i+1][j] == 1000):
                queue.append((i+1, j))
                self.distArray[i+1][j] = self.distArray[i][j] + 1
            if(j-1 > 0 and self.distArray[i][j-1] == 1000):
                queue.append((i, j-1))
                self.distArray[i][j-1] = self.distArray[i][j] + 1
            if(j+1 < config.SCENE_WIDTH-1 and self.distArray[i][j+1] == 1000):
                queue.append((i, j+1))
                self.distArray[i][j+1] = self.distArray[i][j] + 1
            if(i-1 > 0 and j-1 > 0 and self.distArray[i-1][j-1] == 1000):
                queue.append((i-1, j-1))
                self.distArray[i-1][j-1] = self.distArray[i][j] + 1
            if(i-1 > 0 and j+1 < config.SCENE_WIDTH-1 and self.distArray[i-1][j+1] == 1000):
                queue.append((i-1, j+1))
                self.distArray[i-1][j+1] = self.distArray[i][j] + 1
            if(i+1 < config.SCENE_HEIGHT-1 and j-1 > 0 and self.distArray[i+1][j-1] == 1000):
                queue.append((i+1, j-1))
                self.distArray[i+1][j-1] = self.distArray[i][j] + 1
            if(i+1 < config.SCENE_HEIGHT-1 and j+1 < config.SCENE_WIDTH-1 and self.distArray[i+1][j+1] == 1000):
                queue.append((i+1, j+1))
                self.distArray[i+1][j+1] = self.distArray[i][j] + 1

    def Recompute(self, grid):
        if(self.previousCompute == None):
            self.previousCompute = time.time()
            return
        if(time.time() - self.previousCompute > config.BUILDING_RECOMPUTE_TIME):
            queue = []
            queue.append((self.ycen, self.xcen))
            for i in range(len(self.distArray2)):
                for j in range(len(self.distArray2[0])):
                    self.distArray2[i][j] = 1000 
            self.distArray2[self.ycen][self.xcen] = 0
            while(len(queue) > 0):
                i,j = queue.pop(0)
                if(i-1 > 0 and self.distArray2[i-1][j] == 1000 and (grid[i-1][j][1] == 0 or grid[i-1][j][1].name != 'wall')):
                    queue.append((i-1, j))
                    self.distArray2[i-1][j] = self.distArray2[i][j] + 1
                if(i+1 < config.SCENE_HEIGHT-1 and self.distArray2[i+1][j] == 1000 and (grid[i+1][j][1] == 0 or grid[i+1][j][1].name != 'wall')):
                    queue.append((i+1, j))
                    self.distArray2[i+1][j] = self.distArray2[i][j] + 1
                if(j-1 > 0 and self.distArray2[i][j-1] == 1000 and (grid[i][j-1][1] == 0 or grid[i][j-1][1].name != 'wall')):
                    queue.append((i, j-1))
                    self.distArray2[i][j-1] = self.distArray2[i][j] + 1
                if(j+1 < config.SCENE_WIDTH-1 and self.distArray2[i][j+1] == 1000 and (grid[i][j+1][1] == 0 or grid[i][j+1][1].name != 'wall')):
                    queue.append((i, j+1))
                    self.distArray2[i][j+1] = self.distArray2[i][j] + 1
                if(i-1 > 0 and j-1 > 0 and self.distArray2[i-1][j-1] == 1000 and (grid[i-1][j-1][1] == 0 or grid[i-1][j-1][1].name != 'wall')):
                    queue.append((i-1, j-1))
                    self.distArray2[i-1][j-1] = self.distArray2[i][j] + 1
                if(i-1 > 0 and j+1 < config.SCENE_WIDTH-1 and self.distArray2[i-1][j+1] == 1000 and (grid[i-1][j+1][1] == 0 or grid[i-1][j+1][1].name != 'wall')):
                    queue.append((i-1, j+1))
                    self.distArray2[i-1][j+1] = self.distArray2[i][j] + 1
                if(i+1 < config.SCENE_HEIGHT-1 and j-1 > 0 and self.distArray2[i+1][j-1] == 1000 and (grid[i+1][j-1][1] == 0 or grid[i+1][j-1][1].name != 'wall')):
                    queue.append((i+1, j-1))
                    self.distArray2[i+1][j-1] = self.distArray2[i][j] + 1
                if(i+1 < config.SCENE_HEIGHT-1 and j+1 < config.SCENE_WIDTH-1 and self.distArray2[i+1][j+1] == 1000 and (grid[i+1][j+1][1] == 0 or grid[i+1][j+1][1].name != 'wall')):
                    queue.append((i+1, j+1))
                    self.distArray2[i+1][j+1] = self.distArray2[i][j] + 1
            self.previousCompute = time.time()
    

class TownHall(Building):
    def __init__(self):
        self.character = 'T'
        super().__init__(config.SCENE_WIDTH//2 - config.TOWN_HALL_WIDTH//2, config.SCENE_HEIGHT//2 - config.TOWN_HALL_HEIGHT//2, config.TOWN_HALL_WIDTH, config.TOWN_HALL_HEIGHT, config.TOWN_HALL_HITPOINTS)
        self.find_color("magenta", "cyan", "yellow")
        self.prim = "magenta"
        self.sec = "cyan"
        self.tert = "yellow"
        self.name = "town hall"

class Cannon(Building):
    def __init__(self,x,y):
        self.character = 'C'
        super().__init__(x,y,config.CANNON_WIDTH,config.CANNON_HEIGHT,config.CANNON_HITPOINTS)
        self.target = None
        self.damage  = config.CANNON_DAMAGE
        self.LastAttack = None
        self.AttackActive = False
        self.start = time.time()
        self.find_color("green", "blue", "yellow")
        self.prim = "green"
        self.sec = "blue"
        self.tert = "red"
        self.isActive = False
        self.name = "cannon"
    
    def findTarget(self, troops, hero):
        tar = hero
        if(tar and tar.alive == False): tar = 0
        nonHero = 0
        if(hero == 0 or hero.alive == False):
            for i in troops:
                if(self.name == 'cannon'):
                    if(i.name != 'Balloon' and i.alive):
                        nonHero = i
                else:
                    if(i.alive):
                        nonHero = i
        if(tar == 0 and nonHero == 0): return None
        elif(tar == 0): tar = nonHero
        for i in troops:
            if(i.name == 'Balloon' and self.name == 'cannon'): continue
            if((i.xcen - self.xcen)**2 + (i.ycen - self.ycen)**2 < (tar.xcen - self.xcen)**2 + (tar.ycen - self.ycen)**2):
                tar = i
        if((tar.xcen - self.xcen)**2 + (tar.ycen - self.ycen)**2 < config.CANNON_RANGE**2):
            return tar
        else:
            return None
    
    def Attack(self, troops,hero):
        if(self.alive):
            if(self.target == None):
                self.isActive = False
                self.target = self.findTarget(troops,hero)
            else:
                if(self.LastAttack == None):
                    self.isActive = False
                    self.LastAttack = time.time()
                    return 
                if((self.target.xcen - self.xcen)**2 + (self.target.ycen - self.ycen)**2 < config.CANNON_RANGE**2):
                    self.isActive = True
                    x = time.time()
                    if(x - self.LastAttack > 1.0*config.CANNON_ATTACK_DELAY):
                        self.target.health -= self.damage
                        if(self.target.health <= 0):
                            self.target.health = 0
                            self.target.alive = False
                            if(self.target != hero):
                                troops.remove(self.target)
                            self.target.OnDeath()
                            self.target = None
                            self.isActive = False
                        self.LastAttack = x
                else:
                    self.isActive = False
                    self.target = None
        
class WizardTower(Cannon):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.character = 'W'
        self.find_color("red", "blue", "light_blue")
        self.prim = "red"
        self.sec = "blue"
        self.tert = "light_blue"
        self.name = "wizard_tower"
    def Attack(self, troops,hero):
        if(self.alive):
            if(self.target == None):
                self.isActive = False
                self.target = self.findTarget(troops,hero)
            else:
                if(self.LastAttack == None):
                    self.isActive = False
                    self.LastAttack = time.time()
                    return 
                if((self.target.xcen - self.xcen)**2 + (self.target.ycen - self.ycen)**2 < config.CANNON_RANGE**2):
                    self.isActive = True
                    x = time.time()
                    X = self.target.xcen
                    Y = self.target.ycen
                    valids = [[X,Y], [X+1,Y], [X-1,Y], [X,Y+1], [X,Y-1], [X+1,Y+1], [X-1,Y-1], [X+1,Y-1], [X-1,Y+1]]
                    troops_ToRemove = []    
                    if(x - self.LastAttack > 1.0*config.CANNON_ATTACK_DELAY):
                        for i in(troops):
                            if([i.xcen,i.ycen] in valids):
                                i.health -= self.damage
                                if(i.health <= 0):
                                    i.health = 0
                                    i.alive = False
                                    i.OnDeath()
                                    troops_ToRemove.append(i)
                        if(hero and [hero.xcen,hero.ycen] in valids):
                            hero.health -= self.damage
                            if(hero.health <= 0):
                                hero.health = 0
                                hero.alive = False
                                hero.OnDeath()
                        self.LastAttack = x
                    for i in troops_ToRemove:
                        troops.remove(i)
                        i.alive = False
                    if(self.target.alive == False):
                        self.target = None
                        self.isActive = False
                else:
                    self.isActive = False
                    self.target = None

                

class BuilderHut(Building):
    def __init__(self,x,y):
        self.character = 'B'
        self.textCol = "magenta"
        super().__init__(x,y,config.BUILDER_HUT_WIDTH,config.BUILDER_HUT_HEIGHT,config.BUILDER_HUT_HITPOINTS)
        self.prim = "cyan"
        self.sec = "yellow"
        self.tert = "red"
        self.find_color("cyan" , "yellow", "red")
        self.name = "builder_hut"

class Wall(Building):
    def __init__(self,x,y):
        self.character = 'X'
        self.textCol = "white"
        super().__init__(x,y,config.WALL_WIDTH,config.WALL_HEIGHT,config.WALL_HITPOINTS)
        self.find_color("white", "cyan", "red")
        self.prim = "white"
        self.sec = "cyan"
        self.tert = "red"
        del(self.distArray)
        self.xcen = x 
        self.ycen = y
        self.name = "wall"