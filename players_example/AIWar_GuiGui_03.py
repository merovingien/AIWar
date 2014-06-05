# -*- coding: utf-8 -*-

import aiwar
import random
import logging
import logging.handlers
import math
     
logger = logging.getLogger('test')
#hdlr = logging.FileHandler('./AIWar_GuiGui_01.log')
hdlr = logging.handlers.RotatingFileHandler('./AIWar_GuiGui_03.log', mode='a', maxBytes=1000000, backupCount=5, encoding=None, delay=0)
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
CONST_Y_DIVIDE = 51000.0

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
# 0 : X.Y position mineraux AVERE
# 1 : X.Y position mineraux ESPERE
# 2 : X.Y position ennemi1 (base ou vaisseau)
# 3 : X.Y position BASE


def compress_position(x, y):
#    tmp = int(x) + int(y)/CONST_Y_DIVIDE
#    sign_x = 0
#    sign_y = 0
    nx=x
#    if(x<0):
#        sign_x = 1
#        nx = -x
    ny=y
#    if(y<0):
#        sign_y = 1
#        ny = -y
#    tmp = int(nx+ (sign_x+2*sign_y) * CONST_Y_DIVIDE) + int(ny)/CONST_Y_DIVIDE
#    logger.info( "compress_position : x=%s\ty=%s\tcompressed=%s\tDIVIDE=%s\tsign_x=%s\tsign_y=%s", x, y, tmp, CONST_Y_DIVIDE, sign_x, sign_y )
    tmp = int(nx) + int(ny)/CONST_Y_DIVIDE
    logger.info( "compress_position : x=%s\ty=%s\tcompressed=%s\tDIVIDE=%s", x, y, tmp, CONST_Y_DIVIDE )
    return tmp

def extract_position(compressed):
    sign_x = 0
    sign_y = 0
    compressed_unsigned = compressed
    logger.debug( "extract_position : compressed_unsigned=%s", compressed_unsigned )
    if(compressed_unsigned > 2*CONST_Y_DIVIDE):
        sign_y = 1
        compressed_unsigned -= 2*CONST_Y_DIVIDE
    logger.debug( "extract_position : compressed_unsigned=%s", compressed_unsigned )
    if(compressed_unsigned > CONST_Y_DIVIDE):
        sign_x = 1
        compressed_unsigned -= CONST_Y_DIVIDE
    logger.debug( "extract_position : compressed_unsigned=%s", compressed_unsigned )
    x = int(compressed_unsigned)
    y = int( (compressed_unsigned - x)  *CONST_Y_DIVIDE )
    #Apply sign after extraction of values "x,y"
    if(sign_x == 1):
        x = -x
    if(sign_y == 1):
        y = -y
    #    tmp = ( int(compressed), int( ( compressed-int(compressed) ) *CONST_Y_DIVIDE) )
    tmp = ( x, y )
    logger.info( "extract_position : x=%s\ty=%s\tcompressed=%s\tDIVIDE=%s\tsign_x=%s\tsign_y=%s", x, y, compressed, CONST_Y_DIVIDE, sign_x, sign_y )
    return tmp

def random_move(ship):
    a = random.randint(-45, 45)
    ship.rotateOf(a)
    ship.move()

def random_target(base):
    # Destination aleatoire relative a la position de la base
    distance = (aiwar.WORLD_SIZE_X() + aiwar.WORLD_SIZE_Y())/2 - aiwar.MININGSHIP_DETECTION_RADIUS()/2
    angle = random.randint( 1, 360 )
    tmp = ( int(base[0] + distance*math.cos(math.radians(angle))) , int(base[1] + distance*math.sin(math.radians(angle))) )
    #tmp = ( base[0] + random.randint( 0, 2*aiwar.WORLD_SIZE_X() ) - aiwar.WORLD_SIZE_X() , base[1] + random.randint( 0, 2*aiwar.WORLD_SIZE_Y() ) - aiwar.WORLD_SIZE_Y() )
    logger.critical( "random_target : x=%s\ty=%s", tmp[0], tmp[1] )
    return tmp

def setMiningShipNewTarget(base, ship, i):
    temp = random_target( base )
    ship.setMemoryFloat(1, compress_position(temp[0], temp[1]), i )

def fighter_optional_target(base, ship):
    temp = random_target( base )
    ship.setMemoryFloat(1, compress_position(temp[0], temp[1]) )

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


def FighterInstantRange(ship):
    return ship.fuel()/aiwar.FIGHTER_MOVE_CONSO()*aiwar.FIGHTER_SPEED()

def MiningInstantRange(ship):
    return ship.fuel()/aiwar.MININGSHIP_MOVE_CONSO()*aiwar.MININGSHIP_SPEED()

def MissileRange():
    return aiwar.MISSILE_SPEED()*aiwar.MISSILE_MOVE_CONSO()*aiwar.MISSILE_START_FUEL()

def MissileLifeTime():
    return aiwar.MISSILE_START_FUEL()/aiwar.MISSILE_MOVE_CONSO()

def ShootFighter(distance):
    # Est-ce que la cible peut s'echaper ?
    portee = MissileRange()
    duree_vie = MissileLifeTime()
        
    if (portee-distance) > aiwar.FIGHTER_SPEED()*duree_vie :
        return True
    else :
        return False

def ShootMining(distance):
    # Est-ce que la cible peut s'echaper ?
    portee = MissileRange()
    duree_vie = MissileLifeTime()
        
    if (portee-distance) > aiwar.MININGSHIP_SPEED()*duree_vie :
        return True
    else :
        return False


def play_miningship(ship):
    play_miningship_1(ship)

def play_base(base):
    play_base_test(base)
    aiwar.WORLD_SIZE_Y() 

def play_fighter(fighter):
    play_fighter_test(fighter)


def getMyBaseMemory(self):
    mem0 = extract_position(self.getMemoryFloat(0))
    mem1 = extract_position(self.getMemoryFloat(1))
    mem2 = extract_position(self.getMemoryFloat(2))
    mem3 = extract_position(self.getMemoryFloat(3))
    mem4 = extract_position(self.getMemoryFloat(4))
    mem5 = extract_position(self.getMemoryFloat(5))
    return (mem0, mem1, mem2, mem3, mem4, mem5)

def getMyFighterMemory(self):
    mem0 = extract_position(self.getMemoryFloat(0))
    mem1 = extract_position(self.getMemoryFloat(1))
    mem2 = extract_position(self.getMemoryFloat(2))
    mem3 = extract_position(self.getMemoryFloat(3))
    return (mem0, mem1, mem2, mem3)

def getMyMiningShipMemory(self):
    return getMyFighterMemory(self)



def getFriendBaseMemory(self, i):
    logger.info( "getFriendBaseMemory : debut" )
    mem0 = extract_position(self.getMemoryFloat(0, i))
    mem1 = extract_position(self.getMemoryFloat(1, i))
    mem2 = extract_position(self.getMemoryFloat(2, i))
    mem3 = extract_position(self.getMemoryFloat(3, i))
    mem4 = extract_position(self.getMemoryFloat(4, i))
    mem5 = extract_position(self.getMemoryFloat(5, i))
    logger.info( "getFriendBaseMemory : fin" )
    return (mem0, mem1, mem2, mem3, mem4, mem5)

def getFriendFighterMemory(self, i):
    logger.info( "getFriendFighterMemory : debut" )
    mem0 = extract_position(self.getMemoryFloat(0, i))
    mem1 = extract_position(self.getMemoryFloat(1, i))
    mem2 = extract_position(self.getMemoryFloat(2, i))
    mem3 = extract_position(self.getMemoryFloat(3, i))
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

def setEnnemyBaseMemory(self, ennemyPosition, Base):
    BaseMemory = getFriendBaseMemory(self, Base)
    if ennemyPosition != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if BaseMemory[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and not in_circle( BaseMemory[1][0], BaseMemory[1][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, ennemyPosition[0], ennemyPosition[1]) \
        or BaseMemory[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and not in_circle( BaseMemory[0][0], BaseMemory[0][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, ennemyPosition[0], ennemyPosition[1]) \
        or BaseMemory[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and BaseMemory[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and not in_circle( BaseMemory[0][0], BaseMemory[0][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, ennemyPosition[0], ennemyPosition[1]) \
            and not in_circle( BaseMemory[1][0], BaseMemory[1][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, ennemyPosition[0], ennemyPosition[1]) :
            # Decaller la memoire "ennemy" de la BASE
            self.setMemoryFloat(1, compress_position(BaseMemory[0][0], BaseMemory[0][1]), Base)
            # Inscrire le nouvel ennemi dans la BASE
            self.setMemoryFloat(0, compress_position(ennemyPosition[0], ennemyPosition[1]), Base)

def setMineralBaseMemory(self, mineralPosition, Base):
    BaseMemory = getFriendBaseMemory(self, Base)
        
    if mineralPosition != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if BaseMemory[4] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and not in_circle( BaseMemory[3][0], BaseMemory[3][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, mineralPosition[0], mineralPosition[1]) \
                and not in_circle( BaseMemory[2][0], BaseMemory[2][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, mineralPosition[0], mineralPosition[1]) \
            or BaseMemory[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and not in_circle( BaseMemory[2][0], BaseMemory[2][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, mineralPosition[0], mineralPosition[1]) \
            or BaseMemory[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            or BaseMemory[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and BaseMemory[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and BaseMemory[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and not in_circle( BaseMemory[4][0], BaseMemory[4][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, mineralPosition[0], mineralPosition[1]) \
                and not in_circle( BaseMemory[3][0], BaseMemory[3][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, mineralPosition[0], mineralPosition[1]) \
                and not in_circle( BaseMemory[2][0], BaseMemory[2][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, mineralPosition[0], mineralPosition[1]) :
            # Decaller la memoire "mineral" de la BASE
            self.setMemoryFloat(4, compress_position(BaseMemory[3][0], BaseMemory[3][1]), Base)
            self.setMemoryFloat(3, compress_position(BaseMemory[2][0], BaseMemory[2][1]), Base)
            # Inscrire le nouveau minerai dans la BASE
            self.setMemoryFloat(2, compress_position(mineralPosition[0], mineralPosition[1]), Base)
    if mineralPosition == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if BaseMemory[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(4, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)
        elif BaseMemory[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(3, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)
        elif BaseMemory[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(2, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)




# ********************************
# ********************************
def play_base_test(self):
    logger.error( "#################################################################" )
    logger.error( "" )
    logger.error( "*********BASE********** : (%s, %s)", int(self.pos()[0]), int(self.pos()[1]) )
    logger.error( "Vie: %s\t-\tmineralStorage: %s", self.life(), self.mineralStorage() )
    
    logMyBaseMemory(self)
    me = getMyBaseMemory(self)
    
    # Definir la position de la BASE
    px,py = basePos = self.pos()
    

    n = getSortedNeighbours(self)
    
    # Faire vieillir la memoire des mineraux
    cpt = me[5][0] + 1
    if cpt<20 :
        vieillissement_memoire = 1
        FighterBuildRate = 100
        MiningBuildRate = 1
    elif cpt<200 :
        vieillissement_memoire = cpt/10
        FighterBuildRate = 80
        MiningBuildRate = 2
    elif cpt<400 :
        vieillissement_memoire = cpt/5
        FighterBuildRate = 60
        MiningBuildRate = 5
    elif cpt<800 :
        vieillissement_memoire = cpt/2
        FighterBuildRate = 40
        MiningBuildRate = 10
    else :
        vieillissement_memoire = 400
        FighterBuildRate = 10
        MiningBuildRate = 20
        
    self.setMemoryFloat(5, compress_position(cpt, cpt) )
    logger.error( "===============================CPT = %s\tCPTmodulo(%s) = %s", int(cpt), int(vieillissement_memoire), int(cpt%50) )
    if cpt%vieillissement_memoire == 0:
        logger.error( "Vieillissement de la memoire" )
        setMineralBaseMemory(self, (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), self)

    # Remettre a jour la liste ENNEMY en fonction de l'importance de ce qui est visible.
    logger.info( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : debut" )
    for i in n:
        if ( isinstance(i, aiwar.MiningShip) \
        or isinstance(i, aiwar.Fighter) \
        or isinstance(i, aiwar.Base) ) \
        and not self.isFriend(i):
            px,py = ennemiPos = i.pos()
            logger.error( "++Ennemi spoted near BASE : distance=%s\tx=%s\ty=%s",int(self.distanceTo(i)),int(px),int(py))
            self.setMemoryFloat(0, compress_position(px, py) )
            # Mettre a jour mon "Me"
            me = getMyBaseMemory(self)
            logMyBaseMemory(self)




#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
    # S'il existe un ennemi1 localise, creer un guerrier
    #if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and self.mineralStorage() > aiwar.BASE_FIGHTER_PRICE() and False or False and self.mineralStorage()!=0 and random.randint( 1, 1+int(5*aiwar.BASE_FIGHTER_PRICE()/self.mineralStorage()) ) == 1:
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and self.mineralStorage() > aiwar.BASE_FIGHTER_PRICE() and False or False and self.mineralStorage()!=0 and random.randint( 1, 1+int(10*aiwar.BASE_FIGHTER_PRICE()/self.mineralStorage()) ) == 1:
        logger.error( "Je fabrique un guerrier" )
        self.createFighter()
        # Initialiser la seconde cible avec "Position aleatoire"
        fighter_optional_target( basePos , self)
        if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(0, compress_position(me[1][0], me[1][1]) )
            fighter_optional_target( basePos , self)
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


#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
    # create new MiningShip
    if False and self.mineralStorage() > (2*aiwar.BASE_FIGHTER_PRICE()) and random.randint( 1, 1+ int(4*aiwar.BASE_MININGSHIP_PRICE()/self.mineralStorage()) ) == 1:
        logger.error( "Je fabrique un mineur" )
        self.createMiningShip()


    # communiquer avec les copains
    me = getMyBaseMemory(self)
    

    logger.info( "Copier memoire Fighter : debut" )
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0
            # Copie du guerrier seulement s'il revient vers nous
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and ship_isBack(self, i):
                friend = getFriendFighterMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[1]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(0, compress_position(friend[0][0], friend[0][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[1]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(0, compress_position(friend[1][0], friend[1][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.1
            # Copie du guerrier seulement s'il revient vers nous
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and ship_isBack(self, i):
                friend = getFriendFighterMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[0]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(1, compress_position(friend[0][0], friend[0][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[0]:
                    logger.error( "Poto policier" )
                    self.setMemoryFloat(1, compress_position(friend[1][0], friend[1][1]) )
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
                self.setMemoryFloat(2, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), i )
            if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and in_circle( friend[2][0], friend[2][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[1][0], me[1][1]):
            #if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] == me[1]:
                # Effacer l'ennemi de la memoire du minier
                self.setMemoryFloat(2, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), i )
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

    for i in n:
        if isinstance(i, aiwar.Base) and self.isFriend(i):
            px, py = basePos = i.pos()
            self.setMemoryFloat(3, compress_position(px, py) )
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
            self.setMemoryFloat(2, compress_position(px, py) )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
            ennemiEnVue = True

    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            logger.error( "++++Ennemy FIGHTER spoted: %s", self.distanceTo(i) )
            px,py = ennemiPos = i.pos()
            self.setMemoryFloat(2, compress_position(px, py) )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
            ennemiEnVue = True

    for i in n:
        if isinstance(i, aiwar.Base) and not self.isFriend(i):
            logger.error( "++++++Ennemy BASE spoted: %s", self.distanceTo(i) )
            px,py = ennemiPos = i.pos()
            self.setMemoryFloat(2, compress_position(px, py) )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
            ennemiEnVue = True
    logger.info( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : fin" )



    # communiquer avec les copains
    me = getMyMiningShipMemory(self)
    
    logger.info( "Copier memoire Fighter : debut" )
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0 (vide)
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.error( "Poto policier ([0]<=copy mine)" )
                    self.setMemoryFloat(0, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1 (vide)
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.error( "Poto policier ([1]<=copy mine)" )
                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1 (ECRASE)
            if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS() \
                    and distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.error( "Poto policier ([1]<=ecrase mine)" )
                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Effacer son "Ennemy" s'il est dans un FIGHTER croisé
            # Qui m'a croisé et qui s'éloigne de moi (donc plus proche de l'ennemi)
            # Et dont l'ennemi est le meme avec une precision de MININGSHIP_DETECTION_RADIUS()/4
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendFighterMemory(self, i)
                if ( friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[0][0], friend[0][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) \
                or friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[1][0], friend[1][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) ) \
                and not ship_isBack(self, i):
                    # Effacer l'ennemi de ma memoire
                    self.setMemoryFloat(2, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
    logger.info( "Copier memoire Fighter : fin" )



    logger.info( "Copier memoire Base : debut" )
    for i in n:
        if isinstance(i, aiwar.Base) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0 (vide)
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Base : me[0]" )
                friend = getFriendBaseMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "Copier memoire Base : Base[2]=>Me[0]" )
                    logger.error( "Poto rose : me[0]<=base[2]")
                    self.setMemoryFloat(0, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[3][0], friend[3][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "Copier memoire Base : Base[3]=>Me[0]" )
                    logger.error( "Poto rose : me[0]<=base[3]")
                    self.setMemoryFloat(0, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[4][0], friend[4][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "Copier memoire Base : Base[4]=>Me[0]" )
                    logger.error( "Poto rose : me[0]<=base[4]")
                    self.setMemoryFloat(0, compress_position(friend[4][0], friend[4][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1 (vide)
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Base : me[1]" )
                friend = getFriendBaseMemory(self, i)
                if friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[4][0], friend[4][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "Copier memoire Base : Base[4]=>Me[1]" )
                    logger.error( "Poto rose : me[1]<=base[4]")
                    self.setMemoryFloat(1, compress_position(friend[4][0], friend[4][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[3][0], friend[3][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "Copier memoire Base : Base[3]=>Me[1]" )
                    logger.error( "Poto rose : me[1]<=base[3]")
                    self.setMemoryFloat(1, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "Copier memoire Base : Base[2]=>Me[1]" )
                    logger.error( "Poto rose : me[1]<=base[2]")
                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1 (ECRASE)
            if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "ECRASER memoire : me[1]" )
                friend = getFriendBaseMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS() \
                    and distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "ECRASER memoire : Base[2]=>Me[1]" )
                    logger.error( "Poto rose ECRASE : me[1]<=base[2]")
                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[3][0], friend[3][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS()  \
                    and distance(friend[3][0], friend[3][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "ECRASER memoire : Base[3]=>Me[1]" )
                    logger.error( "Poto rose ECRASE : me[1]<=base[3]")
                    self.setMemoryFloat(1, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[4][0], friend[4][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS() \
                    and distance(friend[4][0], friend[4][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "ECRASER memoire : Base[4]=>Me[1]" )
                    logger.error( "Poto rose ECRASE : me[1]<=base[4]")
                    self.setMemoryFloat(1, compress_position(friend[4][0], friend[4][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)

            # Charger une cible aléatoire si je n'ai aucune cible en memoire 
            # et que je viens de croiser la base
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                target_x, target_y = random_target( (me[3][0], me[3][1]) )
                self.setMemoryFloat(1, compress_position(target_x, target_y) )

            # Effacer son "Ennemy" s'il est dans la BASE croisée
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendBaseMemory(self, i)
                if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and ( friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[0][0], friend[0][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) \
                or friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[1][0], friend[1][1], aiwar.MININGSHIP_DETECTION_RADIUS()/4, me[2][0], me[2][1]) ):
                    # Effacer l'ennemi de ma memoire
                    self.setMemoryFloat(2, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Inscrire son "Ennemy" dans la BASE croisée s'il n'y etait pas encore
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                setEnnemyBaseMemory(self, me[2], i)
    logger.info( "Copier memoire Base : fin" )



    # Copier Friend.0=>Me.1 / Friend.1=>Me.0 / Friend.2=>Me.2
    logger.info( "Copier memoire MiningShip : debut" )
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            
            # ADU ADU ADU
            # ADU ADU ADU
            # ADU ADU ADU
            # Prevoir d'effacer la memoire des autres si j'ai des mineraux mais je ne suis pas plein, si je suis sur le retour, si je croise un vaisseau avec une direction opposée à la mienne, si ca cible [0] n'est pas vide et que je ne l'ai pas dans ma memoire => effacer sa memoire car le minerais a disparu
            # ADU ADU ADU
            # ADU ADU ADU
            # ADU ADU ADU
            # Prevoir de ne pas copier la memoire si le vaisseau croisé est dans la direction exactement opposée ( i.angle()== -self.angle() ) avec une tolérance de +-5%. Il faut pour cela definir la variation possible de l'angle.
            # ADU ADU ADU
            # ADU ADU ADU
            # ADU ADU ADU
        
        
            # Me.0 (vide)
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and ( math.cos(math.radians(self.angle()) + math.cos(math.radians(i.angle()))) ) < math.cos(math.radians(80.0)) :
                logger.info( "Copier memoire Minier : Me[0]" )
                friend = getFriendMiningShipMemory(self, i)
                # Copier si la cible du poto n'est pas en visibilite de ma cible
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and distance(friend[0][0], friend[0][1], me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                    logger.info( "Copier memoire Minier : Friends[0]=>Me[0]" )
                    logger.error( "Poto minier ([0]<=copy mine)" )
                    self.setMemoryFloat(0, compress_position(friend[0][0], friend[0][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1 (ECRASE si Freind[0] existe)
            friend = getFriendMiningShipMemory(self, i)
            if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and distance(friend[0][0], friend[0][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
                logger.info( "Copier memoire Minier : Friends[0]=>Me[1]" )
                logger.error( "Poto minier ([1]<=copy mine)" )
                self.setMemoryFloat(1, compress_position(friend[0][0], friend[0][1]) )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)
            # Me.2 (vide)
            if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[2]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    logger.info( "Copier memoire Minier : Friends[2]=>Me[2]" )
                    logger.error( "Poto minier (Copy ENNEMY)" )
                    self.setMemoryFloat(2, compress_position(friend[2][0], friend[2][1]) )
                    logger.error( "++Ennemy MININGSHIP (copy): x=%s, y=%s",friend[2][0],friend[2][1])
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.3 (vide)
            if me[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "Copier memoire Minier : Me[3]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    logger.info( "Copier memoire Minier : Friends[3]=>Me[3]" )
                    logger.error( "Poto minier (Copy BASE)" )
                    self.setMemoryFloat(3, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.3 (ECRASE)
            if me[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                logger.info( "ECRASE memoire Minier : Me[3]" )
                friend = getFriendMiningShipMemory(self, i)
                if friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[3][0], friend[3][1], self.pos()[0], self.pos()[1]) < distance(me[3][0], me[3][1], self.pos()[0], self.pos()[1]):
                    logger.info( "ECRASE memoire Minier : Friends[3]=>Me[3]" )
                    logger.error( "Poto minier (ECRASE BASE)" )
                    self.setMemoryFloat(3, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
    logger.info( "Copier memoire MiningShip : fin" )

    
    # Rechercher si un mineraux est visible
    minerauxEnVue = False
    for i in n:
        if isinstance(i, aiwar.Mineral):
            minerauxEnVue = True


    # Effacer les mineraux connus qui ont disparus
    logger.info( "Effacer mineraux connu : debut" )
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and self.distanceTo(me[0]) < aiwar.MININGSHIP_DETECTION_RADIUS()*3/5 \
        and minerauxEnVue == False :
        # on aurait du voir le minerai -> il est vide
        logger.error( "j'efface le minerais 0 qui n'existe plus" )
        # reset de la position
        self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        # Mettre a jour mon "Me"
        me = getMyMiningShipMemory(self)
    if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and self.distanceTo(me[1]) < aiwar.MININGSHIP_DETECTION_RADIUS()*3/5 \
        and minerauxEnVue == False :
        logger.error( "j'efface le minerais 1 qui n'existe plus" )
        # reset de la position
        self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        # Mettre a jour mon "Me"
        me = getMyMiningShipMemory(self)
    if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and self.distanceTo(me[1]) < aiwar.MININGSHIP_DETECTION_RADIUS()*3/5 \
        and minerauxEnVue == True :
        logger.error( "Je valide minerais 1 en minerais 0. Youpi !" )
        # Decaller minerais "espere" en "AVERE"
        self.setMemoryFloat(0, compress_position( me[1][0], me[1][1]) )
        self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
    logger.info( "Effacer mineraux connu : fin" )


    # Charger une cible aléatoire si je n'ai aucune cible en memoire 
    if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        target_x, target_y = random_target( (me[3][0], me[3][1]) )
        self.setMemoryFloat(1, compress_position(target_x, target_y) )


    # Pas assez de fuel pour rejoindre la cible
    minerauxTropLoin = False
    logger.info( "InstantRange = %s - Cible1 = %s - Cible2 = %s", int(MiningInstantRange(self)), int(self.distanceTo(me[0])*11/10), int(self.distanceTo(me[1])*11/10) )
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and MiningInstantRange(self) < (self.distanceTo(me[0])*11/10) :
        logger.error( "Le minerai 1 est trop loin" )
        minerauxTropLoin = True

    if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and MiningInstantRange(self) < (self.distanceTo(me[1])*11/10) :
        logger.error( "Le minerai 2 est trop loin" )
        minerauxTropLoin = True


    # rentrer a la base ?
    logger.info( "rentrer a la base ? : debut" )
    # Rentrer à la base si plus de mine en vue avec cargaison presente
    # OU Si cargaison pleine
    # OU si fuel juste suffisant pour rentrer
    # OU ennemi en vue
    if self.mineralStorage() > 0 and minerauxEnVue == False \
        or self.mineralStorage() == aiwar.MININGSHIP_MAX_MINERAL_STORAGE() \
        or self.fuel() < ( self.distanceTo(basePos)*11/10 if baseConnue else 170 ) \
        or self.fuel() < ( self.distanceTo(basePos)*11/10 if baseConnue else 170 ) \
        or minerauxTropLoin \
        or ennemiEnVue \
        or me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) :
        if baseConnue or ennemiEnVue:
            if baseConnue or minerauxEnVue == False:
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
                        # Enregistrer dans la base les mineraux
                        if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                            setMineralBaseMemory(self, me[0], i)
                    break
            if baseConnue or minerauxEnVue == False:
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
            x,y = mePos = self.pos()
            
            # ENREGISTER DANS MEMOIRE 1
            # Si memoire 1 et 2 vide => enregistrer dans memoire 1
            # Si memoire 1 vide et 2 non vide et minerai lointain de memoire 2  => enregistrer dans memoire 1
            # Si memoire 1 non-vide et minerai en visibilité de memoire 1 et minerai plus proche BASE que memoire 1 => enregistrer dans memoire 1
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                \
                or me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[1][0], me[1][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS() \
                \
                or me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) < aiwar.MININGSHIP_DETECTION_RADIUS() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[0][0], me[0][1], me[3][0], me[3][1]) :
                logger.error( "je sauvegarde la position du minerai (cible 1)" )
                self.setMemoryFloat(0, compress_position(mpx, mpy) )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)

            # ENREGISTER DANS MEMOIRE 2
            # Si memoire 1 non-vide et 2 vide et minerai lointain de memoire 1 => enregistrer dans mem2
            # Si memoire 1 non-vide et 2 non-vide et minerai lointain de memoire 1 et minerai plus proche BASE que memoire 2 => enregistrer dans mem2
            elif me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS() \
                \
                or me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[1][1], me[0][1], me[3][0], me[3][1]) :
                logger.error( "je sauvegarde la position du minerai (cible 2)" )
                self.setMemoryFloat(1, compress_position(mpx, mpy) )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)

            # DECALLER POUR ENREGISTER DANS MEMOIRE 1
            # Si memoire 1 vide et 2 non vide et minerai en visibilité de memoire 2 et minerai plus proche BASE que memoire 2 => effacer memoire 2 + enregistrer dans memoire 1 = decaller mem1 en mem2 et enregistrer dans mem1
            # Si memoire 1 non-vide et minerai lointain de memoire 1 et minerai plus proche BASE que memoire 1 => decaller mem1 en mem2 et enregistrer dans mem1
            elif me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[1][0], me[1][1]) < aiwar.MININGSHIP_DETECTION_RADIUS() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[1][1], me[1][1], me[3][0], me[3][1]) \
                \
                or me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[0][1], me[0][1], me[3][0], me[3][1]) :
                logger.error( "je sauvegarde la position du minerai (decaller cible 1)" )
                self.setMemoryFloat(1, compress_position(me[0][0], me[0][1]) )
                self.setMemoryFloat(0, compress_position(mpx, mpy) )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)
                
               
            logger.error( "je vais au minerai visible" )
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
        logger.error( "je vais au minerai 0 : x=%s, y=%s", me[0][0], me[0][1])
        self.rotateTo(me[0])
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo(me[0]) > (aiwar.MININGSHIP_MINING_RADIUS()/2):
            self.move()
        logger.info( "Fin de traitement MiningShip (mineral 0 memoire)." )
    if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        logger.error( "je vais au minerai 1 : x=%s, y=%s", me[1][0], me[1][1])
        self.rotateTo(me[1])
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo(me[1]) > (aiwar.MININGSHIP_MINING_RADIUS()/2):
            self.move()
        logger.info( "Fin de traitement MiningShip (mineral 1 memoire)." )
    logger.info( "recherche de minerais connu : fin" )
    
    # Effacer memoire si fuel vide
    if self.fuel() == 0:
        self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        self.setMemoryFloat(2, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
    
    logger.info( "Fin de traitement MiningShip." )






# ********************************
# ********************************
def play_fighter_test(self):
    logger.error( "" )
    logger.error( "********FIGHTER******** : (%s, %s)", int(self.pos()[0]), int(self.pos()[1]) )
    logger.error( "Vie: %s\t-\tFuel: %s\t-\tMissiles: %s", self.life(), self.fuel(), self.missiles() )

    n = getSortedNeighbours(self)

    logMyFighterMemory(self)


# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# Limiter les echanges entre figthers pres de la base.
# Quand un fighter voit un ennemi sans que ca soit une cible principale, il va la signaler à la base.
# La base devra garder en MEM 1 la base adverse et ne jamais l'effacer.
# La base devra garder en MEM 2 une cible (fighter/mining) et l'info sera furtive.
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU


    # Ordre des actions :
    # 0 - Panne de fuel => effacer toutes les cibles
    # 1 - Memoriser une cible + position BASE
    # 2 - Visualiser une cible pour tirer
    # 3 - Rejoindre la cible memoire
    # 4 - Retourner a la base

    # ====== PHASE 0 ======
    if self.life()<aiwar.FIGHTER_MOVE_CONSO():
        self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
    
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
                self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), i )
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and  friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                # Enregistrer la position
                self.setMemoryFloat(1, self.getMemoryFloat(0,i))
                # Decaller le 2eme ennemi dans la memoire de l'ami
                self.setMemoryFloat(0, self.getMemoryFloat(1,i), i)
                self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), i )
            # Enregistrer position BASE
            px,py = basePos = i.pos()
            self.setMemoryFloat(3, compress_position(px, py) )
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
                self.setMemoryFloat(0, compress_position(px, py) )
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
            if self.missiles() > 0 and ShootFighter(self.distanceTo(i))==True:
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
                self.setMemoryFloat(0, compress_position(px, py) )
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
            if self.missiles() > 0 and ShootMining(self.distanceTo(i))==True:
                logger.error( "++Ennemy MININGSHIP: N'y vois rien de personnel, je fais mon job." )
                # Tirer 1 MiningShip sur 8
                if random.randint(1, 8*cpt_ship) == 1:
                    self.launchMissile(i)
                # Decaller l'ennemi 0 en 1 si l'emplacement 1 est libre
                if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    self.setMemoryFloat(1, self.getMemoryFloat(0))
                # Enregistrer la position pour le poursuivre
                px,py = Pos = i.pos()
                self.setMemoryFloat(0, compress_position(px, py) )
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
            self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )

    # ====== PHASE 4 ======
    # ADU
    # ADU
    # ADU
    # ADU

