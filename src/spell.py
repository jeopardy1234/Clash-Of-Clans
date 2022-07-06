import src.config as config
import subprocess as sp
class Spell: 
    def __init__(self,name):
        self.name = name

class Heal(Spell):
    def __init__(self,name, healMultiplier):
        super().__init__(name)
        self.damage = 10
        self.healMultiplier = healMultiplier
        sp.call('aplay -q audio/heal.wav&', shell=True)

    def IncreaseHealth (self, hero, barbarians):
        for i in barbarians:
            i.health = min(config.BARBARIANS_HEALTH, self.healMultiplier * i.health)
        if(hero):hero.health = min(config.KING_HEALTH, self.healMultiplier * hero.health)

class Rage(Spell):
    def __init__(self,name, rageMultiplier):
        super().__init__(name)
        self.damage = 10
        self.rageMultiplier = rageMultiplier
        sp.call('aplay -q audio/rage.wav&', shell=True)

    def IncreaseHealth (self, hero, barbarians):
        for i in barbarians:
            i.moveAfter /= self.rageMultiplier
            self.damage = self.rageMultiplier * i.damage
        if(hero):hero.moveAfter /= self.rageMultiplier
        if(hero):self.damage = self.rageMultiplier * hero.damage
