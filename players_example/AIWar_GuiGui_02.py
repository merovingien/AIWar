# -*- coding: utf-8 -*-

import aiwar
import random
import logging
import logging.handlers
import math
     
logger = logging.getLogger('test')
#hdlr = logging.FileHandler('./AIWar_GuiGui_01.log')
hdlr = logging.handlers.RotatingFileHandler('./AIWar_GuiGui_02.log', mode='a', maxBytes=1000000, backupCount=1, encoding=None, delay=0)
logger.addHandler(hdlr)
logger.setLevel(logging.ERROR) # DEBUG, INFO, WARNING, ERROR, CRITICAL
formatter = logging.Formatter('%(levelname)s %(funcName)s : %(message)s')
hdlr.setFormatter(formatter)
     
#logger.error('log info')
#logger.warn('log warning')
#logger.error('log error')
#logger.critical("Impossible d'ouvrir le fichier : %s" % path_file)

logger.critical('Lancement de AIWar_GuiGui_02 !')


# Constantes
CONST_WORLD_SIZE_X = aiwar.WORLD_SIZE_X()
CONST_WORLD_SIZE_Y = aiwar.WORLD_SIZE_Y()
CONST_Y_DIVIDE = 1000.0

CONST_ENNEMY_BASE 	    = (CONST_WORLD_SIZE_X+1)*5
CONST_ENNEMY_FIGHER 	= (CONST_WORLD_SIZE_X+1)*4
CONST_ENNEMY_MININGSHIP	= (CONST_WORLD_SIZE_X+1)*3
CONST_ENNEMY_ON_THE_WAY	= (CONST_WORLD_SIZE_X+1)*2
CONST_ENNEMY_VOID 	    = 0.0

CONST_MINERAL_MASSIVE	= (CONST_WORLD_SIZE_X+1)*4
CONST_MINERAL_REAL	    = (CONST_WORLD_SIZE_X+1)*3
CONST_MINERAL_ESTIMATE	= (CONST_WORLD_SIZE_X+1)*2
CONST_MINERAL_VOID 	    = 0.0



# Plan memoire BASE : 
# 0 : X.Y position ennemi1 (base ou vaisseau)
# 1 : X.Y position ennemi2 (vaisseau)
# 2 : X.Y position mineraux
# 3 : X.Y position mineraux
# 4 : X.Y position mineraux
# 5 : X.Y Nombre de vaisseaux X=miniers - Y=guerriers

# Plan memoire FIGHTER : 
# 0 : X.Y position ennemi1 (base ou vaisseau)
# 1 : X.Y position ennemi2 (vaisseau)
# 2 : X.Y position mineraux
# 3 : X.Y position BASE

# Plan memoire MININGSHIP : 
# 0 : X.Y position mineraux
# 1 : X.Y position mineraux
# 2 : X.Y position ennemi1 (base ou vaisseau)
# 3 : X.Y position BASE


def random_move(ship):
    a = random.randint(-45, 45)
    ship.rotateOf(a)
    ship.move()

def random_target(base):
    if random.randint(1, 2) == 1:
        # Random sur les X
        tmp = ( random.randint( 0, aiwar.WORLD_SIZE_X() ) , base[1] )
    else:
        # Random sur les Y
        tmp = ( base[0], random.randint( 0, aiwar.WORLD_SIZE_Y() ) )
    return tmp

def miningship_optional_target(base, ship):
    temp = random_target( base )
    ship.setMemoryFloat(2, temp[0] + temp[1] / CONST_Y_DIVIDE)

def fighter_optional_target(base, ship):
    temp = random_target( base )
    ship.setMemoryFloat(1, temp[0] + temp[1] / CONST_Y_DIVIDE)

def ship_isBack(base, ship):
    logger.info( "************************ Start" )
    ship_angle = ship.angle()
    sx,sy = ship_pos = ship.pos()
    nx,ny = newship_pos = ( sx + 20*math.cos(math.radians(ship_angle)), sy - 20*math.sin(math.radians(ship_angle)) )
    bx,by = base_pos = base.pos()
    
    logger.info( "Ship_angle(%s) / Ship(%s, %s) / New_ship(%s, %s) )", int(ship.angle()), int(sx),int(sy) , int(nx),int(ny) )
    logger.info( "Base(%s, %s) / distance=%s / New_distance=%s", int(bx),int(by) , int(distance( sx,sy , bx,by )), int(distance( nx,ny , bx,by ))  )
    
    if distance( nx,ny , bx,by ) < distance( sx,sy , bx,by ):
        logger.info( "*************************** End : TRUE " )
        return True
    else:
        logger.info( "*************************** End : FALSE " )
        return False

def getSortedNeighbours(self):
    n = list(self.neighbours())
    n.sort(key=lambda x: self.distanceTo(x))
    return n

def in_circle(center_x, center_y, radius, x, y):
    dist = distance(center_x, center_y, x, y)
    return dist <= radius

def distance(x1, y1, x2, y2):
    return ( math.sqrt( math.pow(x1-x2, 2) + math.pow(y1-y2, 2) ) )

def play_miningship(ship):
    play_miningship_1(ship)

def play_base(base):
    play_base_test(base)
    aiwar.WORLD_SIZE_Y() 

def play_fighter(fighter):
    play_fighter_test(fighter)


def getMyBaseMemory(self):
    mem0 = ( int(self.getMemoryFloat(0)), int( ( self.getMemoryFloat(0)-int(self.getMemoryFloat(0) ) )*CONST_Y_DIVIDE) )
    mem1 = ( int(self.getMemoryFloat(1)), int( ( self.getMemoryFloat(1)-int(self.getMemoryFloat(1) ) )*CONST_Y_DIVIDE) )
    mem2 = ( int(self.getMemoryFloat(2)), int( ( self.getMemoryFloat(2)-int(self.getMemoryFloat(2) ) )*CONST_Y_DIVIDE) )
    mem3 = ( int(self.getMemoryFloat(3)), int( ( self.getMemoryFloat(3)-int(self.getMemoryFloat(3) ) )*CONST_Y_DIVIDE) )
    mem4 = ( int(self.getMemoryFloat(4)), int( ( self.getMemoryFloat(4)-int(self.getMemoryFloat(4) ) )*CONST_Y_DIVIDE) )
    mem5 = ( int(self.getMemoryFloat(5)), int( ( self.getMemoryFloat(5)-int(self.getMemoryFloat(5) ) )*CONST_Y_DIVIDE) )
    return (mem0, mem1, mem2, mem3, mem4, mem5)

def getMyFighterMemory(self):
    mem0 = ( int(self.getMemoryFloat(0)), int( ( self.getMemoryFloat(0)-int(self.getMemoryFloat(0) ) )*CONST_Y_DIVIDE) )
    mem1 = ( int(self.getMemoryFloat(1)), int( ( self.getMemoryFloat(1)-int(self.getMemoryFloat(1) ) )*CONST_Y_DIVIDE) )
    mem2 = ( int(self.getMemoryFloat(2)), int( ( self.getMemoryFloat(2)-int(self.getMemoryFloat(2) ) )*CONST_Y_DIVIDE) )
    mem3 = ( int(self.getMemoryFloat(3)), int( ( self.getMemoryFloat(3)-int(self.getMemoryFloat(3) ) )*CONST_Y_DIVIDE) )
    return (mem0, mem1, mem2, mem3)

def getMyMiningShipMemory(self):
    return getMyFighterMemory(self)



def getFriendBaseMemory(self, i):
    logger.info( "getFriendBaseMemory : debut" )
    mem0 = ( int(self.getMemoryFloat(0, i)), int( ( self.getMemoryFloat(0, i)-int(self.getMemoryFloat(0, i) ) )*CONST_Y_DIVIDE) )
    mem1 = ( int(self.getMemoryFloat(1, i)), int( ( self.getMemoryFloat(1, i)-int(self.getMemoryFloat(1, i) ) )*CONST_Y_DIVIDE) )
    mem2 = ( int(self.getMemoryFloat(2, i)), int( ( self.getMemoryFloat(2, i)-int(self.getMemoryFloat(2, i) ) )*CONST_Y_DIVIDE) )
    mem3 = ( int(self.getMemoryFloat(3, i)), int( ( self.getMemoryFloat(3, i)-int(self.getMemoryFloat(3, i) ) )*CONST_Y_DIVIDE) )
    mem4 = ( int(self.getMemoryFloat(4, i)), int( ( self.getMemoryFloat(4, i)-int(self.getMemoryFloat(4, i) ) )*CONST_Y_DIVIDE) )
    mem5 = ( int(self.getMemoryFloat(5, i)), int( ( self.getMemoryFloat(5, i)-int(self.getMemoryFloat(5, i) ) )*CONST_Y_DIVIDE) )
    logger.info( "getFriendBaseMemory : fin" )
    return (mem0, mem1, mem2, mem3, mem4, mem5)

def getFriendFighterMemory(self, i):
    logger.info( "getFriendFighterMemory : debut" )
    mem0 = ( int(self.getMemoryFloat(0, i)), int( ( self.getMemoryFloat(0, i)-int(self.getMemoryFloat(0, i) ) )*CONST_Y_DIVIDE) )
    mem1 = ( int(self.getMemoryFloat(1, i)), int( ( self.getMemoryFloat(1, i)-int(self.getMemoryFloat(1, i) ) )*CONST_Y_DIVIDE) )
    mem2 = ( int(self.getMemoryFloat(2, i)), int( ( self.getMemoryFloat(2, i)-int(self.getMemoryFloat(2, i) ) )*CONST_Y_DIVIDE) )
    mem3 = ( int(self.getMemoryFloat(3, i)), int( ( self.getMemoryFloat(3, i)-int(self.getMemoryFloat(3, i) ) )*CONST_Y_DIVIDE) )
    logger.info( "getFriendFighterMemory : fin" )
    return (mem0, mem1, mem2, mem3)

def getFriendMiningShipMemory(self, i):
    logger.info( "getFriendMiningShipMemory : debut-fin" )
    return getFriendFighterMemory(self, i)


def logMyBaseMemory(self):
    memory = getMyBaseMemory(self)
    logger.critical( "Ennemy1 = %s\tEnnemy2 = %s\tNb fighters = %s\tNb miningship = %s", memory[0], memory[1], memory[5][0], memory[5][1] )
    logger.critical( "Mineral1 = %s\tMineral2 = %s\tMineral3 = %s", memory[2], memory[3], memory[4] )

def logMyFighterMemory(self):
    memory = getMyFighterMemory(self)
    logger.critical( "Ennemy1 = %s\tEnnemy2 = %s", memory[0], memory[1] )
    logger.critical( "Mineral1 = %s\tBase = %s", memory[2], memory[3] )

def logMyMiningShipMemory(self):
    memory = getMyMiningShipMemory(self)
    logger.critical( "Mineral1 = %s\tMineral2 = %s", memory[0], memory[1] )
    logger.critical( "Ennemy1 = %s\tBase = %s", memory[2], memory[3] )



# ********************************
# ********************************
def play_base_test(self):
    logger.error( "#################################################################" )
    logger.error( "" )
    logger.error( "*********BASE********** : (%s, %s)", int(self.pos()[0]), int(self.pos()[1]) )
    logger.error( "Vie: %s\t-\tmineralStorage: %s", self.life(), self.mineralStorage() )
    
    logMyBaseMemory(self)
    me = getMyBaseMemory(self)
    
    # Definir la position opposee a la BASE
    px,py = basePos = self.pos()
    # X position
    px_cible=CONST_WORLD_SIZE_X - px
    # Y position
    py_cible=CONST_WORLD_SIZE_Y - py
    
    # Initialiser la direction a prendre pour decouvrir la carte
    posMineralSelf = me[2]
    if posMineralSelf == (CONST_MINERAL_VOID, CONST_MINERAL_VOID):
        logger.error( "Voici ma position: X=%s - Y=%s", px, py )
        # Ajouter l'information ESTIMEE
        # CONST_MINERAL_ESTIMATE
        #ADU ADU ADU ADU
        #ADU ADU ADU ADU
        #ADU ADU ADU ADU
        # Enregister la position cible - MiningShip
        self.setMemoryFloat( 2, int(px_cible) + int(py_cible)/CONST_Y_DIVIDE )
        # Enregister la position cible - Fighter
        self.setMemoryFloat( 0, int(px_cible) + int(py_cible)/CONST_Y_DIVIDE )
        # Mettre a jour mon "Me"
        me = getMyBaseMemory(self)
        logger.error( "J'initialise la trajectoire a explorer: X=%s - Y=%s", px_cible, py_cible )


    n = self.neighbours()


    # Remettre a jour la liste ENNEMY en fonction de l'importance de ce qui est visible.
    logger.info( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : debut" )
    for i in n:
        if ( isinstance(i, aiwar.MiningShip) \
        or isinstance(i, aiwar.Fighter) \
        or isinstance(i, aiwar.Base) ) \
        and not self.isFriend(i):
            px,py = ennemiPos = i.pos()
            logger.error( "++Ennemi spoted near BASE : distance=%s\tx=%s\ty=%s",int(self.distanceTo(i)),int(px),int(py))
            self.setMemoryFloat(0, int(px) + int(py) / CONST_Y_DIVIDE )
            # Mettre a jour mon "Me"
            me = getMyBaseMemory(self)
            logMyBaseMemory(self)


    # S'il existe un ennemi1 localise, creer un guerrier
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and self.mineralStorage() > aiwar.BASE_FIGHTER_PRICE() or self.mineralStorage()!=0 and random.randint( 1, 1+int(5*aiwar.BASE_FIGHTER_PRICE()/self.mineralStorage()) ) == 1:
        logger.error( "Je fabrique un guerrier" )
        self.createFighter()
        # Initialiser la seconde cible avec "Position opposée BASE" +/- 45 degres
        fighter_optional_target( (px_cible, py_cible) , self)
        if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(0, me[1][0] + me[1][1] / CONST_Y_DIVIDE )
            fighter_optional_target( (px_cible, py_cible) , self)
        logMyBaseMemory(self)


    # remissile friend ships
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.BASE_GIVE_MISSILE_RADIUS():
            logger.error( "je fais le plein de MISSILES mon ami" )
            self.giveMissiles(aiwar.FIGHTER_MAX_MISSILE(), i)
            

    # refuel friend ships
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.BASE_REFUEL_RADIUS():
            logger.error( "je fais le plein de FUEL de mon ami" )
            self.refuel(aiwar.MININGSHIP_START_FUEL(), i)
            

    # create new MiningShip
    if self.mineralStorage() > (2*aiwar.BASE_FIGHTER_PRICE()) and random.randint( 1, 1+ int(5*aiwar.BASE_MININGSHIP_PRICE()/self.mineralStorage()) ) == 1:
        logger.error( "Je fabrique un mineur" )
        self.createMiningShip()
        # Initialiser la seconde mine avec "Position opposée BASE" +/- 45 degres
        miningship_optional_target( (px_cible, py_cible) , self)
        logMyBaseMemory(self)


    # communiquer avec les copains
    me = getMyBaseMemory(self)
    
    # Copier Friend.0=>Me.1 / Friend.1=>Me.0 / Friend.2=>Me.2
    logger.info( "Copier memoire MiningShip : debut" )
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[0]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[1]:
                    logger.info( "Copier memoire Minier : Friends[2]=>Me[0]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(0, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.1
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[1]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[0]:
                    logger.info( "Copier memoire Minier : Friends[2]=>Me[1]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(1, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.2
            if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[2]" )
                friend = getFriendMiningShipMemory(self, i)
                logger.info( "Copier memoire Minier : getFriendMiningShipMemory" )
                if friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[3] and friend[1] != me[4]:
                    logger.info( "Copier memoire Minier : Friends[1]=>Me[2]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(2, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[3] and friend[1] != me[4]:
                    logger.info( "Copier memoire Minier : Friends[0]=>Me[2]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(2, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.3
            if me[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[3]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[2] and friend[0] != me[4]:
                    logger.info( "Copier memoire Minier : Friends[0]=>Me[3]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(3, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[2] and friend[0] != me[4]:
                    logger.info( "Copier memoire Minier : Friends[1]=>Me[3]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(3, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.4
            if me[4] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[4]" )
                friend = getFriendMiningShipMemory(self, i)
                logger.info( "Copier memoire Minier : getFriendMiningShipMemory" )
                if friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[3] and friend[1] != me[2]:
                    logger.info( "Copier memoire Minier : Friends[1]=>Me[4]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(4, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[3] and friend[1] != me[2]:
                    logger.info( "Copier memoire Minier : Friends[0]=>Me[4]" )
                    logger.error( "Poto minier" )
                    self.setMemoryFloat(4, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
    logger.info( "Copier memoire MiningShip : fin" )

    logger.info( "Copier memoire Fighter : debut" )
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0
            # Copie du guerrier seulement s'il revient vers nous
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and ship_isBack(self, i):
                friend = getFriendFighterMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[1]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(0, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[1]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(0, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.1
            # Copie du guerrier seulement s'il revient vers nous
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and ship_isBack(self, i):
                friend = getFriendFighterMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[0]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(1, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[0]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(1, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.2
            if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[3] and friend[2] != me[4]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(2, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.3
            if me[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[2] and friend[2] != me[4]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(3, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.4
            if me[4] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[3] and friend[2] != me[2]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(4, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
    logger.info( "Copier memoire Fighter : fin" )
    
    # Effacer de tous les miniers, les ennemis deja enregistrés
    logger.info( "Effacer Ennemi de la memoire MiningShip : debut" )
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            friend = getFriendMiningShipMemory(self, i)
            if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and in_circle( friend[2][0], friend[2][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[0][0], me[0][1]):
            #if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] == me[0]:
                # Effacer l'ennemi de la memoire du minier
                self.setMemoryFloat(2, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID / CONST_Y_DIVIDE, i )
            if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and in_circle( friend[2][0], friend[2][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[1][0], me[1][1]):
            #if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] == me[1]:
                # Effacer l'ennemi de la memoire du minier
                self.setMemoryFloat(2, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID / CONST_Y_DIVIDE, i )
    logger.info( "Effacer Ennemi de la memoire MiningShip : fin" )




# ********************************
# ********************************
def play_miningship_1(self):
    logger.error( "" )
    logger.error( "*******MININGSHIP****** : (%s, %s)", int(self.pos()[0]), int(self.pos()[1]) )
    logger.error( "Vie: %s\t-\tfuel: %s\t-\tmineralStorage: %s", self.life() , self.fuel(), self.mineralStorage() )

    n = getSortedNeighbours(self)
    
    logMyMiningShipMemory(self)
    me = getMyMiningShipMemory(self)


    # recherche de la base amie
    baseConnue = False
    basePos = me[3]
    if basePos != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        logger.error( "je connais ma base" )
        baseConnue = True
    else:
        logger.info( "je ne connais pas ma base" )
        for i in n:
            if isinstance(i, aiwar.Base) and self.isFriend(i):
                logger.error( "base trouvee" )
                px, py = basePos = i.pos()
                self.setMemoryFloat(3, int(px) + int(py) / CONST_Y_DIVIDE )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)
                baseConnue = True
                break


    # Fuir si un ennemi devient visible
    logger.info( "Fuir si un ennemi devient visible : debut" )
    ennemiEnVue = False
    ennemiPos = me[2]
    if ennemiPos != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        logger.error( "j'ai un ennemi en memoire" )
        ennemiEnVue = True
    logger.info( "Fuir si un ennemi devient visible : fin" )
    
    # Remettre a jour la liste en fonction de l'importance de ce qui est visible.
    logger.info( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : debut" )
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            px,py = ennemiPos = i.pos()
            logger.error( "++Ennemy MININGSHIP spoted: distance=%s\tx=%s\ty=%s",self.distanceTo(i),px,py)
            self.setMemoryFloat(2, int(px) + int(py) / CONST_Y_DIVIDE )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
            ennemiEnVue = True

    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            logger.error( "++++Ennemy FIGHTER spoted: %s", self.distanceTo(i) )
            px,py = ennemiPos = i.pos()
            self.setMemoryFloat(2, int(px) + int(py) / CONST_Y_DIVIDE )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
            ennemiEnVue = True

    for i in n:
        if isinstance(i, aiwar.Base) and not self.isFriend(i):
            logger.error( "++++++Ennemy BASE spoted: %s", self.distanceTo(i) )
            px,py = ennemiPos = i.pos()
            self.setMemoryFloat(2, int(px) + int(py) / CONST_Y_DIVIDE )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
            ennemiEnVue = True
    logger.info( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : fin" )


    # communiquer avec les copains
    me = getMyMiningShipMemory(self)
    
    # Copier Friend.0=>Me.1 / Friend.1=>Me.0 / Friend.2=>Me.2
    logger.info( "Copier memoire MiningShip : debut" )
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[0]" )
                friend = getFriendMiningShipMemory(self, i)
                logger.info( "Copier memoire Minier : getFriendMiningShipMemory" )
                if friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[1]:
                    logger.info( "Copier memoire Minier : Friens[1]=>Me[0]" )
                    logger.error( "Poto minier ([0]<=copy mine)" )
                    self.setMemoryFloat(0, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[1]:
                    logger.info( "Copier memoire Minier : Friens[0]=>Me[0]" )
                    logger.error( "Poto minier ([0]<=copy mine)" )
                    self.setMemoryFloat(0, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[1]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[0]:
                    logger.info( "Copier memoire Minier : Friens[0]=>Me[1]" )
                    logger.error( "Poto minier ([1]<=copy mine)" )
                    self.setMemoryFloat(1, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[0]:
                    logger.info( "Copier memoire Minier : Friens[1]=>Me[1]" )
                    logger.error( "Poto minier ([1]<=copy mine)" )
                    self.setMemoryFloat(1, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.2
            if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[2]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    logger.info( "Copier memoire Minier : Friens[2]=>Me[2]" )
                    logger.error( "Poto minier (Copy ENNEMY)" )
                    self.setMemoryFloat(2, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    logger.error( "++Ennemy MININGSHIP (copy): x=%s, y=%s",friend[2][0],friend[2][1])
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.3
            if me[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[3]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    logger.info( "Copier memoire Minier : Friens[3]=>Me[3]" )
                    logger.error( "Poto minier (Copy BASE)" )
                    self.setMemoryFloat(3, int(friend[3][0]) + int(friend[3][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
    logger.info( "Copier memoire MiningShip : fin" )

    logger.info( "Copier memoire Fighter : debut" )
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[1]:
                    logger.error( "Poto policier ([0]<=copy mine)" )
                    self.setMemoryFloat(0, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[0]:
                    logger.error( "Poto policier ([1]<=copy mine)" )
                    self.setMemoryFloat(1, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Effacer son "Ennemy" s'il est dans un FIGHTER croisé
            # Qui m'a croisé et qui s'éloigne de moi (donc plus proche de l'ennemi)
            # Et dont l'ennemi est le meme avec une precision de MININGSHIP_DETECTION_RADIUS()/4
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and ( friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[0][0], friend[0][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) \
                or friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[1][0], friend[1][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) ) \
                and not ship_isBack(self, i):
                    # Effacer l'ennemi de ma memoire
                    self.setMemoryFloat(2, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID / CONST_Y_DIVIDE)
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                    
#            #Ne pas enregistrer les ennemis de la base ou des fighters
#            # Me.2
#            if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                friend = getFriendFighterMemory(self, i)
#                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                    logger.error( "Poto policier" )
#                    self.setMemoryFloat(2, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
#                    # Mettre a jour mon "Me"
#                    me = getMyMiningShipMemory(self)
#            # Me.3
#            if me[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                friend = getFriendFighterMemory(self, i)
#                if friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                    logger.error( "Poto policier" )
#                    self.setMemoryFloat(3, int(friend[3][0]) + int(friend[3][1]) / CONST_Y_DIVIDE )
#                    # Mettre a jour mon "Me"
#                    me = getMyMiningShipMemory(self)
#    logger.info( "Copier memoire Fighter : fin" )

    logger.info( "Copier memoire Base : debut" )
    for i in n:
        if isinstance(i, aiwar.Base) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Base : me[0]" )
                friend = getFriendBaseMemory(self, i)
                logger.info( "Copier memoire Base : getFriendBaseMemory" )
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[1]:
                    logger.info( "Copier memoire Base : Base[2]=>Me[0]" )
                    logger.error( "Poto rose")
                    self.setMemoryFloat(0, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[3] != me[1]:
                    logger.info( "Copier memoire Base : Base[3]=>Me[0]" )
                    logger.error( "Poto rose")
                    self.setMemoryFloat(0, int(friend[3][0]) + int(friend[3][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[4] != me[1]:
                    logger.info( "Copier memoire Base : Base[4]=>Me[0]" )
                    logger.error( "Poto rose")
                    self.setMemoryFloat(0, int(friend[4][0]) + int(friend[4][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Base : me[1]" )
                friend = getFriendBaseMemory(self, i)
                if friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[4] != me[0]:
                    logger.info( "Copier memoire Base : Base[4]=>Me[1]" )
                    logger.error( "Poto rose")
                    self.setMemoryFloat(1, int(friend[4][0]) + int(friend[4][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[3] != me[0]:
                    logger.info( "Copier memoire Base : Base[3]=>Me[1]" )
                    logger.error( "Poto rose")
                    self.setMemoryFloat(1, int(friend[3][0]) + int(friend[3][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != me[0]:
                    logger.info( "Copier memoire Base : Base[2]=>Me[1]" )
                    logger.error( "Poto rose")
                    self.setMemoryFloat(1, int(friend[2][0]) + int(friend[2][1]) / CONST_Y_DIVIDE )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Effacer son "Ennemy" s'il est dans la BASE croisée
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and ( friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[0][0], friend[0][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) \
                or friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[1][0], friend[1][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) ):
                #if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] == me[2]:
                    # Effacer l'ennemi de ma memoire
                    self.setMemoryFloat(2, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID / CONST_Y_DIVIDE)
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                    
#            # Ne pas enregistrer les ennemis de la base ou des fighters
#            # Me.2
#            if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                logger.info( "Copier memoire Base : me[3]" )
#                friend = getFriendBaseMemory(self, i)
#                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                    logger.error( "Poto rose")
#                    self.setMemoryFloat(2, int(friend[0][0]) + int(friend[0][1]) / CONST_Y_DIVIDE )
#                    # Mettre a jour mon "Me"
#                    me = getMyMiningShipMemory(self)
#                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                    logger.error( "Poto rose")
#                    self.setMemoryFloat(2, int(friend[1][0]) + int(friend[1][1]) / CONST_Y_DIVIDE )
#                    # Mettre a jour mon "Me"
#                    me = getMyMiningShipMemory(self)
    logger.info( "Copier memoire Base : fin" )

    
    # rentrer a la base ?
    logger.info( "rentrer a la base ? : debut" )
    if self.mineralStorage() == aiwar.MININGSHIP_MAX_MINERAL_STORAGE() or self.fuel() < ( self.distanceTo(basePos) if baseConnue else 170 ) or ennemiEnVue:
        if baseConnue or ennemiEnVue:
            if baseConnue:
                logger.error( "je rentre a la base" )
            if ennemiEnVue:
                logger.error( "je fuis a la base" )
            self.rotateTo(basePos)
            # Se deplacer tant qu'on est loin de la cible
            if self.distanceTo(basePos) > (aiwar.MININGSHIP_MINING_RADIUS()/4):
                self.move()
            # base en vue et assez proche pour donner le minerai ?
            for i in n:
                if isinstance(i, aiwar.Base) and self.isFriend(i):
                    if self.distanceTo(i) < aiwar.MININGSHIP_MINING_RADIUS():
                        logger.error( "je donne mon minerai a ma base" )
                        self.pushMineral(i, self.mineralStorage())
                    break
            if baseConnue:
                logger.info( "Fin de traitement MiningShip (rapporter minerais)." )
            if ennemiEnVue:
                logger.info( "Fin de traitement MiningShip (sauve qui peut !)." )
            return
        else:
            logger.error( "je cherche ma base" )
            random_move(self)
            logger.info( "Fin de traitement MiningShip (recherche base)." )
            return
    logger.info( "rentrer a la base ? : fin" )
        
    # recherche de minerais visible
    logger.info( "recherche de minerais visible : debut" )
    for i in n:
        if isinstance(i, aiwar.Mineral):
            mpx,mpy = minPos = i.pos()
            # Me.0
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and minPos!= me[1]:
                logger.error( "je sauvegarde la position du minerai" )
                self.setMemoryFloat(0, int(mpx) + int(mpy) / CONST_Y_DIVIDE)
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)
            # Me.1
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and minPos!= me[0]:
                logger.error( "je sauvegarde la position du minerai" )
                self.setMemoryFloat(1, int(mpx) + int(mpy) / CONST_Y_DIVIDE)
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)
            logger.error( "je vais au minerais visible" )
            self.rotateTo(minPos)
            # Se deplacer tant qu'on est loin de la cible
            if self.distanceTo(minPos) > (aiwar.MININGSHIP_MINING_RADIUS()/2):
                self.move()
            if self.distanceTo(i) < aiwar.MININGSHIP_MINING_RADIUS():
                logger.error( "je mine" )
                self.extract(i)
            logger.info( "Fin de traitement MiningShip (mineral visible)." )
            return
    logger.info( "recherche de minerais visible : fin" )
        
    # recherche de minerai connu
    logger.info( "recherche de minerais connu : debut" )
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        logger.error( "je connais un minerai 0" )
        # on aurait du voir le minerai -> il est vide
        if self.distanceTo(me[0]) < aiwar.MININGSHIP_DETECTION_RADIUS():
            # reset de la position
            self.setMemoryFloat(0, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID / CONST_Y_DIVIDE)
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
        else:
            logger.error( "je vais au minerais connus 0" )
            self.rotateTo(me[0])
            # Se deplacer tant qu'on est loin de la cible
            if self.distanceTo(me[0]) > (aiwar.MININGSHIP_MINING_RADIUS()/2):
                self.move()
            logger.info( "Fin de traitement MiningShip (mineral 0 memoire)." )
            return
    elif me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        logger.error( "je connais un minerai 1" )
        if self.distanceTo(me[1]) < aiwar.MININGSHIP_DETECTION_RADIUS(): # on aurait du voir le minerai -> il est vide
            # reset de la position
            self.setMemoryFloat(1, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID / CONST_Y_DIVIDE)
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
        else:
            logger.error( "je vais au minerais connus 1" )
            self.rotateTo(me[1])
            # Se deplacer tant qu'on est loin de la cible
            if self.distanceTo(me[1]) > (aiwar.MININGSHIP_MINING_RADIUS()/2):
                self.move()
            logger.info( "Fin de traitement MiningShip (mineral 1 memoire)." )
            return
    logger.info( "recherche de minerais connu : fin" )
    logger.info( "Fin de traitement MiningShip." )




# ********************************
# ********************************
def play_fighter_test(self):
    logger.error( "" )
    logger.error( "********FIGHTER******** : (%s, %s)", int(self.pos()[0]), int(self.pos()[1]) )
    logger.error( "Vie: %s\t-\tFuel: %s\t-\tMissiles: %s", self.life(), self.fuel(), self.missiles() )

    n = getSortedNeighbours(self)

    logMyFighterMemory(self)

    # Ordre des actions :
    # 0 - Panne de fuel => effacer toutes les cibles
    # 1 - Memoriser une cible + position BASE
    # 2 - Visualiser une cible pour tirer
    # 3 - Rejoindre la cible memoire
    # 4 - Retourner a la base

    # ====== PHASE 0 ======
    if self.life()<aiwar.FIGHTER_MOVE_CONSO():
        self.setMemoryFloat(0, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID/CONST_Y_DIVIDE)
        self.setMemoryFloat(1, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID/CONST_Y_DIVIDE)
    
    # ====== PHASE 1 ======
    # S'il existe un ennemi1 localise dans BASE, je go le combattre
    me = getMyFighterMemory(self)
    # Chercher une cible dans mon entourage
    for i in n:
        if isinstance(i, aiwar.Base) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() and self.isFriend(i):
            friend = getFriendBaseMemory(self, i)
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and  friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                # Enregistrer la position
                self.setMemoryFloat(0, self.getMemoryFloat(0,i))
                # Decaller le 2eme ennemi dans la memoire de l'ami
                self.setMemoryFloat(0, self.getMemoryFloat(1,i), i)
                self.setMemoryFloat(1, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID/CONST_Y_DIVIDE, i)
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and  friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                # Enregistrer la position
                self.setMemoryFloat(1, self.getMemoryFloat(0,i))
                # Decaller le 2eme ennemi dans la memoire de l'ami
                self.setMemoryFloat(0, self.getMemoryFloat(1,i), i)
                self.setMemoryFloat(1, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID/CONST_Y_DIVIDE, i)
            # Enregistrer position BASE
            px,py = basePos = i.pos()
            self.setMemoryFloat(3, int(px) + int(py) / CONST_Y_DIVIDE)
            # Mettre a jour mon "Me"
            me = getMyFighterMemory(self)
        
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() and self.isFriend(i):
            friend = getFriendFighterMemory(self, i)
            if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and me[1] != friend[0]:
                    # Enregistrer la position
                    self.setMemoryFloat(0, self.getMemoryFloat(0,i))
                elif me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and me[0] != friend[0]:
                    # Enregistrer la position
                    self.setMemoryFloat(1, self.getMemoryFloat(0,i))
                # Mettre a jour mon "Me"
                me = getMyFighterMemory(self)


    # ====== PHASE 2 ======
    # Ordre des cibles : 
    #   1 - BASE
    #   2 - FIGHTER
    #   3 - MININGSHIP
    for i in n:
        if isinstance(i, aiwar.Base) and not self.isFriend(i):
            logger.error( "++++++Ennemy BASE: %s", self.distanceTo(i) )
            if self.missiles() > 0:
                logger.error( "++++++Ennemy BASE: BOOM dans ta face !" )
                # Tirer sans condition sur la BASE
                self.launchMissile(i)
                # Decaller l'ennemi 0 en 1 si l'emplacement 1 est libre
                if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    self.setMemoryFloat(1, self.getMemoryFloat(0))
                # Enregistrer la position pour le poursuivre
                px,py = Pos = i.pos()
                self.setMemoryFloat(0, int(px) + int(py) / CONST_Y_DIVIDE)
                # Mettre a jour mon "Me"
                me = getMyFighterMemory(self)
            else:
                logger.error( "++++++Ennemy BASE: Plus de munitions ! :'(" )


    cpt_ship = 0
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            cpt_ship +=1
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            logger.error( "++++Ennemy FIGHTER: %s", self.distanceTo(i) )
            if self.missiles() > 0:
                logger.error( "++++Ennemy FIGHTER: Attrape ca !" )
                # Tirer 1 fighter sur 3
                if random.randint(1, 3*cpt_ship) == 1:
                    self.launchMissile(i)
                    # On fait un pas en arriere pour sortir de la zone visible de l'ennemi
                    # Si ca peut eviter de se prendre un missile ... :c)
                    self.rotateTo(i)
                    if random.randint(1, 2) == 1:
                        self.rotateOf(90)
                    else:
                        self.rotateOf(-90)
                    self.move()
                # Decaller l'ennemi 0 en 1 si l'emplacement 1 est libre
                if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    self.setMemoryFloat(1, self.getMemoryFloat(0))
                # Enregistrer la position pour le poursuivre
                px,py = Pos = i.pos()
                self.setMemoryFloat(0, int(px) + int(py) / CONST_Y_DIVIDE)
                # Mettre a jour mon "Me"
                me = getMyFighterMemory(self)
            else:
                logger.error( "++++Ennemy FIGHTER: Plus de munitions ! :'(" )

    cpt_ship = 0
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            cpt_ship +=1
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            logger.error( "++Ennemy MININGSHIP: %s", self.distanceTo(i) )
            if self.missiles() > 0:
                logger.error( "++Ennemy MININGSHIP: N'y vois rien de personnel, je fais mon job." )
                # Tirer 1 MiningShip sur 8
                if random.randint(1, 8*cpt_ship) == 1:
                    self.launchMissile(i)
                # Decaller l'ennemi 0 en 1 si l'emplacement 1 est libre
                if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    self.setMemoryFloat(1, self.getMemoryFloat(0))
                # Enregistrer la position pour le poursuivre
                px,py = Pos = i.pos()
                self.setMemoryFloat(0, int(px) + int(py) / CONST_Y_DIVIDE)
                # Mettre a jour mon "Me"
                me = getMyFighterMemory(self)
            else:
                logger.error( "++Ennemy MININGSHIP: Plus de munitions ! :'(" )

    # ====== PHASE 3 ======
    # Initialiser ma cible
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        # S'il ne reste plus de missiles, rentrer a la maison
        if self.missiles() <= 0:
            # Plus de missiles, retourner a la base
            self.rotateTo(me[3])
            self.move()
        # Se deplacer tant qu'on est loin de la cible
        elif self.distanceTo(me[0]) > (aiwar.FIGHTER_DETECTION_RADIUS()/10):
            self.rotateTo(me[0])
            self.move()
        # Proche de la cible avec des missiles => elle n'est plus là. Passer à la cible suivante.
        else:
            # Decaller l'ennemi 1 en 0
            self.setMemoryFloat(0, self.getMemoryFloat(1))
            # Effacer la cible decaller pour ne pas avoir de doublon
            self.setMemoryFloat(1, CONST_ENNEMY_VOID + CONST_ENNEMY_VOID / CONST_Y_DIVIDE)

    # ====== PHASE 4 ======
    # ADU
    # ADU
    # ADU
    # ADU

