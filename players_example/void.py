# -*- coding: utf-8 -*-

# Exemple of AI implementation #

import aiwar
import random

### handlers: MANDATORY ###

def play_base(self):
    return


def play_miningship(self):
    return


def play_fighter(self):
    return


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
