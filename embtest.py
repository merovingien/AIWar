# -*- coding: utf-8 -*-

# Exemple of AI implementation #

import aiwar
import random

### handlers: MANDATORY ###

def play_base(self):
    self.log("*********BASE**********")
    self.log("Vie: {}".format(self.life()))
    self.log("MineralStorage: {}".format(self.mineralStorage()))

    n = self.neighbours()

    # refuel friend ships
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.BASE_REFUEL_RADIUS():
            self.log("je fais le plein de mon ami")
            self.refuel(aiwar.MININGSHIP_START_FUEL(), i)

    # create new MiningShip
    if self.mineralStorage() > aiwar.BASE_MININGSHIP_PRICE() and random.randint(1, 20) == 1:
        self.createMiningShip()

    # communiquer avec les copains
    for i in n:
        if (isinstance(i, aiwar.Base) or isinstance(i, aiwar.MiningShip)) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # si on connait la position du mineral
            posMineralSelf = (self.getMemoryFloat(2), self.getMemoryFloat(3))
            if posMineralSelf != (0.0, 0.0):
            #envoi de la position du mineral s'il ne la connait pas
                posMineralCopain = (self.getMemoryFloat(2,i), self.getMemoryFloat(3,i))
                if posMineralCopain == (0.0, 0.0):
                    self.setMemoryFloat(2, posMineralSelf[0], i)
                    self.setMemoryFloat(3, posMineralSelf[1], i)
                    self.log("J'ai donne la position de mon minerais a mon copain")


def play_miningship(self):
    self.log("*******MININGSHIP******")
    self.log("Vie: {}".format(self.life()))
    self.log("MineralStorage: {}".format(self.mineralStorage()))
    self.log("Fuel: {}".format(self.fuel()))

    n = self.neighbours()

    # recherche de la base amie
    baseConnue = False
    basePos = (self.getMemoryFloat(0), self.getMemoryFloat(1))
    if basePos != (0.0, 0.0):
        self.log("je connais ma base")
        baseConnue = True
    else:
        for i in n:
            if isinstance(i, aiwar.Base) and self.isFriend(i):
                self.log("base trouvee")
                px,py = basePos = i.pos()
                self.setMemoryFloat(0, px)
                self.setMemoryFloat(1, py)
                baseConnue = True
                break

    # communiquer avec les copains
    for i in n:
        if (isinstance(i, aiwar.Base) or isinstance(i, aiwar.MiningShip)) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # si on connait la position du mineral
            posMineralSelf = (self.getMemoryFloat(2), self.getMemoryFloat(3))
            if posMineralSelf != (0.0, 0.0):
            #envoi de la position du mineral s'il ne la connait pas
                posMineralCopain = (self.getMemoryFloat(2,i), self.getMemoryFloat(3,i))
                if posMineralCopain == (0.0, 0.0):
                    self.setMemoryFloat(2, posMineralSelf[0], i)
                    self.setMemoryFloat(3, posMineralSelf[1], i)
                    self.log("J'ai donne la position de mon minerais a mon copain")

    # rentrer a la base ?
    if self.mineralStorage() == aiwar.MININGSHIP_MAX_MINERAL_STORAGE() or self.fuel() < ( self.distanceTo(basePos) if baseConnue else 170 ):
        if baseConnue:
            self.log("je rentre a la base")
            self.rotateTo(basePos)
            self.move()
            # base en vue et assez proche pour donner le minerai ?
            for i in n:
                if isinstance(i, aiwar.Base) and self.isFriend(i):
                    if self.distanceTo(i) <= aiwar.MININGSHIP_MINING_RADIUS():
                        self.log("je donne mon minerai a ma base")
                        self.pushMineral(i, self.mineralStorage())
                    break
            return
        else:
            self.log("je cherche ma base")
            random_move(self)
            return
        
    # recherche de minerais visible
    for i in n:
        if isinstance(i, aiwar.Mineral):
            self.log("je sauvegarde la position du minerai")
            mpx,mpy = i.pos()
            self.setMemoryFloat(2, mpx)
            self.setMemoryFloat(3, mpy)
            self.log("je vais au minerais visible")
            self.rotateTo(i)
            self.move()
            if self.distanceTo(i) <= (aiwar.MININGSHIP_MINING_RADIUS()-1):
                self.log("je mine")
                self.extract(i)
            return
        
    # recherche de minerai connu
    minPos = (self.getMemoryFloat(2), self.getMemoryFloat(3))
    if minPos != (0.0, 0.0):
        self.log("je connais un minerai")
        if self.distanceTo(minPos) < aiwar.MININGSHIP_DETECTION_RADIUS(): # on aurait du voir le minerai -> il est vide
            # reset de la position
            self.setMemoryFloat(2, 0.0)
            self.setMemoryFloat(3, 0.0)
        else:
            self.log("je vais au minerais connus")
            self.rotateTo(minPos)
            self.move()
            return

    # deplacement aleatoire
    self.log("je cherche du minerais")
    random_move(self)


def play_fighter(self):
    self.log("********FIGHTER********")
    self.log("Vie: {}".format(self.life()))
    self.log("Fuel: {}".format(self.fuel()))
    self.log("Missiles: {}".format(self.missiles()))

    n = self.neighbours()

    for i in n:
        if isBase(i) or isMining(i) or isFighter(i):
            if not self.isFriend(i):
                if self.missiles() > 0:
                    self.launchMissile(i)

    random_move(self)


### helpers ###

def random_move(ship):
    a = random.randint(-45, 45)
    ship.rotateOf(a)
    ship.move()

def getSortedNeighbours(self):
    n = list(self.neighbours())
    n.sort(key=lambda x: self.distanceTo(x))
    return n

def isBase(s):
    return isinstance(s, aiwar.Base)

def isMineral(s):
    return isinstance(s, aiwar.Mineral)

def isMining(s):
    return isinstance(s, aiwar.MiningShip)

def isFighter(s):
    return isinstance(s, aiwar.Fighter)

def isMissile(s):
    return isinstance(s, aiwar.Missile)
