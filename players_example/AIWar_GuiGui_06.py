# -*- coding: utf-8 -*-

import aiwar
import random
import logging
import logging.handlers
import math

logger = logging.getLogger('test')
hdlr = logging.handlers.RotatingFileHandler('./AIWar_GuiGui.log', mode='a', maxBytes=1000000, backupCount=2, encoding=None, delay=0)
logger.addHandler(hdlr)
logger.setLevel(logging.CRITICAL+10) # DEBUG, INFO, WARNING, ERROR, CRITICAL
formatter = logging.Formatter('%(levelname)s %(funcName)s : %(message)s')
hdlr.setFormatter(formatter)

# Todo list:
# => Les MINIERS font demi-tours si un fighter ennemy est en vue et qu'ils voient un missile. => ok!
# => Les MINIERS n'avancent plus jusqu'à la base pour vider leur cargaison, ils s'arretent le plus loin possible. => ok!
# => Les MINIERS qui voient la base adverse inscrive la POSITION dans la cible et dans le mineraux ! Il faut alimenter le champs de bataille. => ok!
# => Les MINIERS qui cherchent en aleatoire déclarent le nombre de voisins MINIERS pour que le random soit plus pertinent (360/NbMiners pour chacun) => ok!
# => Les GUERRIERS tirent s'ils se font tirer dessus sans chercher à etre à portée => ok!
# => Les GUERRIERS ne gardent plus de position de mineraux. Ils n'explorent jamais. A la place ils enregistrent : => ok!
#       - le type de cible 1, 
#       - le nombre de cible 1,
#       - le type de cible 2 et 
#       - le nombre de cible 2,
#       - le nombre de voisins qui vont à la meme cible qu'eux et qui sont plus proches.
# Le but est de controler le nombre des guerriers qui partent pour une cible.
# => Les GUERRIERS efface les ennemis de la memoire de la BASE quand il prend la cible.


#logger.debug('log debug')
#logger.info('log info')
#logger.warning('log warning')
#logger.error('log error')
#logger.critical("Impossible d'ouvrir le fichier : %s" % path_file)



# Constantes
CONST_WORLD_SIZE_X = aiwar.WORLD_SIZE_X()
CONST_WORLD_SIZE_Y = aiwar.WORLD_SIZE_Y()
CONST_Y_DIVIDE = 51000.0
CONST_NB_COMMUNICATION_MAX = 10

CONST_ENNEMY_BASE 	    = 3
CONST_ENNEMY_FIGTHER 	= 2
CONST_ENNEMY_MININGSHIP	= 1
CONST_ENNEMY_VOID 	    = 0

CONST_MINERAL_MASSIVE	= 3
CONST_MINERAL_REAL	    = 2
CONST_MINERAL_ESTIMATE	= 1
CONST_MINERAL_VOID 	    = 0

CONST_LOG_INFO = 1
CONST_LOG_DEBUG = 2
CONST_LOG_WARNING = 3
CONST_LOG_ERROR = 4
CONST_LOG_CRITICAL = 5
CONST_LOG_JOKE = 100
CONST_LOG_VOID = 200

CONST_LOG = CONST_LOG_JOKE

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
# 2 : Type cible 1 (2 bits) / Nb Cible 1 (4 bits) / Nb voisins vers cible 1 (4 bits) / Type cible 2 / Nb cible 2 / Nb voisins vers cible 2 [RESTE 12 bits]
# 3 : X.Y position BASE


# Plan memoire MININGSHIP : 
# 0 : X.Y position mineraux AVERE
# 1 : X.Y position mineraux ESPERE
# 2 : X.Y position ennemi1 (base ou vaisseau) + "bit 0 = fuite"
# 3 : X.Y position BASE

def show_log(log_level):
    if log_level >= CONST_LOG:
        return True
    return False

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
#    logger.debug( "compress_position : x=%s\ty=%s\tcompressed=%s\tDIVIDE=%s\tsign_x=%s\tsign_y=%s", x, y, tmp, CONST_Y_DIVIDE, sign_x, sign_y )
    tmp = int(nx) + int(ny)/CONST_Y_DIVIDE
#    if show_log(10+CONST_LOG_DEBUG):
#        self.log("compress_position : x="+ str(int(x)) +"\ty="+ str(int(y)) +"\tcompressed="+str(int(tmp))+"\tDIVIDE="+ str(int(CONST_Y_DIVIDE)) )
    logger.debug( "compress_position : x=%s\ty=%s\tcompressed=%s\tDIVIDE=%s", x, y, tmp, CONST_Y_DIVIDE )
    return tmp

def compress_position2(x, y, bx, by):
    if(x==CONST_ENNEMY_VOID or x==CONST_MINERAL_VOID) and (y==CONST_ENNEMY_VOID or y==CONST_MINERAL_VOID):
        return int(CONST_ENNEMY_VOID)
        
    nx=int(CONST_WORLD_SIZE_X + x-bx)
    ny=int(CONST_WORLD_SIZE_Y + y-by)
    tmp = int( (nx & 0xFFF)<<20 ) + int( (ny & 0xFFF)<<8 )
#    if show_log(10+CONST_LOG_DEBUG):
#        self.log("compress_position : x="+ str(int(x)) +"\ty="+ str(int(y)) +"\tcompressed="+str(int(tmp))+"\tDIVIDE="+ str(int(CONST_Y_DIVIDE)) )
    logger.critical( "compress_position2 : x=%s\ty=%s\tbx=%s\tby=%s\tcompressed=%s\tMULTIPLY=%s", int(x), int(y), int(bx), int(by), int(tmp), CONST_WORLD_SIZE_Y )
    return tmp

# 2 : Type cible 1 (2 bits) / Nb Cible 1 (4 bits) / Nb voisins vers cible 1 (4 bits) / Type cible 2 / Nb cible 2 / Nb voisins vers cible 2 [RESTE 12 bits]
def compress_fighter_infos(cible_1_type, cible_1_nb_ennemies, cible_1_nb_allies, cible_2_type, cible_2_nb_ennemies, cible_2_nb_allies):
    # Saturation de la valeur a stocker
    if int(cible_1_nb_ennemies) > 0xF:
        cible_1_nb_ennemies = 0xF
    if int(cible_1_nb_allies) > 0xF:
        cible_1_nb_allies = 0xF
    if int(cible_2_nb_ennemies) > 0xF:
        cible_2_nb_ennemies = 0xF
    if int(cible_2_nb_allies) > 0xF:
        cible_2_nb_allies = 0xF
    tmp = ( (cible_1_type & 0x3)<<30 )
    tmp += ( (cible_1_nb_ennemies & 0xF)<<26 )
    tmp += ( (cible_1_nb_allies & 0xF)<<22 )
    tmp += ( (cible_2_type & 0x3)<<20 )
    tmp += ( (cible_2_nb_ennemies & 0xF)<<16 )
    tmp += ( (cible_2_nb_allies & 0xF)<<12 )

    logger.critical( "extract_fighter_infos : cible_1_type=%s\tcible_1_nb_ennemies=%s\tcible_1_nb_allies=%s\tcible_2_type=%s\tcible_2_nb_ennemies=%s\tcible_2_nb_allies=%s\tcompress=%s", cible_1_type, cible_1_nb_ennemies, cible_1_nb_allies, cible_2_type, cible_2_nb_ennemies, cible_2_nb_allies, tmp )
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
    logger.debug( "extract_position : x=%s\ty=%s\tcompressed=%s\tDIVIDE=%s\tsign_x=%s\tsign_y=%s", x, y, compressed, CONST_Y_DIVIDE, sign_x, sign_y )
    return tmp

def extract_position2(compressed, bx, by):
    if(compressed==CONST_ENNEMY_VOID):
        tmp = ( int(CONST_ENNEMY_VOID), int(CONST_ENNEMY_VOID) )
        return tmp
        
    nx=int(compressed)>>20 & 0xFFF
    ny=int(compressed)>>8  & 0xFFF
    x = int(nx - CONST_WORLD_SIZE_X + bx)
    y = int(ny - CONST_WORLD_SIZE_Y + by)
    tmp = ( x, y )
    logger.debug( "extract_position2 : x=%s\ty=%s\tbx=%s\tby=%s\tcompressed=%s\tWORLD_SIZE=%s", x, y, bx, by, compressed, CONST_WORLD_SIZE_X )
    return tmp

# 2 : Type cible 1 (2 bits) / Nb Cible 1 (4 bits) / Nb voisins vers cible 1 (4 bits) / Type cible 2 / Nb cible 2 / Nb voisins vers cible 2 [RESTE 12 bits]
def extract_fighter_infos(compressed_infos):
    cible_1_type        = (int(compressed_infos)>>30) & 0x3
    cible_1_nb_ennemies = (int(compressed_infos)>>26) & 0xF
    cible_1_nb_allies   = (int(compressed_infos)>>22) & 0xF
    cible_2_type        = (int(compressed_infos)>>20) & 0x3
    cible_2_nb_ennemies = (int(compressed_infos)>>16) & 0xF
    cible_2_nb_allies   = (int(compressed_infos)>>12) & 0xF

    tmp = ( cible_1_type, cible_1_nb_ennemies, cible_1_nb_allies, cible_2_type, cible_2_nb_ennemies, cible_2_nb_allies )
    logger.critical( "extract_fighter_infos : cible_1_type=%s\tcible_1_nb_ennemies=%s\tcible_1_nb_allies=%s\tcible_2_type=%s\tcible_2_nb_ennemies=%s\tcible_2_nb_allies=%s\tcompress=%s", cible_1_type, cible_1_nb_ennemies, cible_1_nb_allies, cible_2_type, cible_2_nb_ennemies, cible_2_nb_allies, compressed_infos )
    return tmp

def random_move(ship):
    a = random.randint(-45, 45)
    ship.rotateOf(a)
    ship.move()

def random_target(base, nb_ships):
    # Destination aleatoire relative a la position de la base
    distance = (aiwar.WORLD_SIZE_X() + aiwar.WORLD_SIZE_Y())/2 - aiwar.MININGSHIP_DETECTION_RADIUS()/2
    if(nb_ships == 0):
        angle = random.randint( 1, 360 )
    else:
        angle = 360/nb_ships*random.randint( 0, nb_ships+1 )

    tmp = ( int(base[0] + distance*math.cos(math.radians(angle))) , int(base[1] + distance*math.sin(math.radians(angle))) )
    #tmp = ( base[0] + random.randint( 0, 2*aiwar.WORLD_SIZE_X() ) - aiwar.WORLD_SIZE_X() , base[1] + random.randint( 0, 2*aiwar.WORLD_SIZE_Y() ) - aiwar.WORLD_SIZE_Y() )
    logger.error( "random_target : x=%s\ty=%s", tmp[0], tmp[1] )
    return tmp

def setMiningShipNewTarget(base, ship, i):
    temp = random_target( base )
    ship.setMemoryFloat(1, compress_position(temp[0], temp[1]), i )

def fighter_optional_target(base, ship):
    temp = random_target( base )
    ship.setMemoryFloat(1, compress_position(temp[0], temp[1]) )

def ship_isBack(base, ship):
    logger.debug( "************************ Start" )
    ship_angle = ship.angle()
    sx,sy = ship_pos = ship.pos()
    nx,ny = newship_pos = ( sx + 20*math.cos(math.radians(ship_angle)), sy - 20*math.sin(math.radians(ship_angle)) )
    bx,by = base_pos = base.pos()
    
    logger.debug( "Ship_angle(%s) / Ship(%s, %s) / New_ship(%s, %s) )", int(ship.angle()), int(sx),int(sy) , int(nx),int(ny) )
    logger.debug( "Base(%s, %s) / distance=%s / New_distance=%s", int(bx),int(by) , int(distance( sx,sy , bx,by )), int(distance( nx,ny , bx,by ))  )
    
    if distance( nx,ny , bx,by ) < distance( sx,sy , bx,by ):
        logger.debug( "*************************** End : TRUE " )
        return True
    else:
        logger.debug( "*************************** End : FALSE " )
        return False

def missile_spoted_me(self, missile):
    if show_log(CONST_LOG_DEBUG):
        self.log("******missile_spoted_me*********** Start" )
    me_x, me_y = me_pos= self.pos()
    missile_angle = missile.angle()
    mx,my = missile_pos = missile.pos()
    missile_distance = self.distanceTo(missile)
    
    nx,ny = newmissile_pos = ( mx + missile_distance*math.cos(math.radians(missile_angle)), my - missile_distance*math.sin(math.radians(missile_angle)) )
    
    if distance( nx,ny , me_x,me_y ) < aiwar.WORLD_SIZE_X()/100:
        if show_log(CONST_LOG_DEBUG):
            self.log("******missile_spoted_me*********** End : TRUE " )
        return True
    else:
        if show_log(CONST_LOG_DEBUG):
            self.log("******missile_spoted_me*********** End : FALSE " )
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
    return aiwar.MISSILE_SPEED()*MissileLifeTime()

def MissileLifeTime():
    return aiwar.MISSILE_START_FUEL()/aiwar.MISSILE_MOVE_CONSO()

def ShootFighter(distance):
    # Est-ce que la cible peut s'echaper ?
    portee = MissileRange()
    duree_vie = MissileLifeTime()
        
    # +1 pour le cas le plus defavorable (cible va jouer)
    if (portee-distance) > aiwar.FIGHTER_SPEED()*(duree_vie+1) :
        return True
    else :
        return False

def ShootMining(distance):
    # Est-ce que la cible peut s'echaper ?
    portee = MissileRange()
    duree_vie = MissileLifeTime()

    # +1 pour le cas le plus defavorable (cible va jouer)
    if (portee-distance) > aiwar.MININGSHIP_SPEED()*(duree_vie+1) :
        return True
    else :
        return False

def MiningDistanceProche():
    return aiwar.MININGSHIP_DETECTION_RADIUS()/4

def MiningDistanceEffacerMinerai():
    return aiwar.MININGSHIP_DETECTION_RADIUS()*3/5

def MiningDistanceCopierMinerai():
    distance = aiwar.MININGSHIP_DETECTION_RADIUS()*4/5
    if distance < (MiningDistanceEffacerMinerai()+aiwar.COMMUNICATION_RADIUS()):
        distance = MiningDistanceEffacerMinerai()+2*aiwar.COMMUNICATION_RADIUS()
    return distance

def MiningDistanceEffacerEnnemi():
    return aiwar.COMMUNICATION_RADIUS()/2

def MiningDistanceCopierEnnemi():
    distance = aiwar.MININGSHIP_DETECTION_RADIUS()*3/2
    if distance < (MiningDistanceEffacerEnnemi()+aiwar.COMMUNICATION_RADIUS()):
        distance = MiningDistanceEffacerEnnemi()+2*aiwar.COMMUNICATION_RADIUS()
    return distance

def MiningDistanceLoin():
    return aiwar.MININGSHIP_DETECTION_RADIUS()

def FighterDistanceLoin():
    return aiwar.FIGHTER_DETECTION_RADIUS()

def FighterDistanceProche():
    return aiwar.FIGHTER_DETECTION_RADIUS()/10

def FighterNombreMaxGuerrierParCible():
    return 3

def FighterConvoiPunitifHorsCommunication():
    return aiwar.COMMUNICATION_RADIUS()*5/4

def readFriendMemory(Counter = 0):
    if Counter <= CONST_NB_COMMUNICATION_MAX :
        return True
    return False



def play_miningship(ship):
    play_miningship_1(ship)

def play_base(base):
    play_base_test(base)

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
    mem2 = extract_fighter_infos(self.getMemoryUInt(2))
    mem3 = extract_position(self.getMemoryFloat(3))
    return (mem0, mem1, mem2, mem3)

def getMyMiningShipMemory_old(self):
    return getMyFighterMemory(self)

def getMyMiningShipMemory(self):
    mem0 = extract_position(self.getMemoryFloat(0))
    mem1 = extract_position(self.getMemoryFloat(1))
    mem3 = extract_position(self.getMemoryFloat(3))
    mem2 = extract_position2(self.getMemoryUInt(2), mem3[0], mem3[1])
    return (mem0, mem1, mem2, mem3)



def getFriendBaseMemory(self, i):
    if show_log(CONST_LOG_DEBUG):
        self.log( "getFriendBaseMemory : debut" )
    mem0 = extract_position(self.getMemoryFloat(0, i))
    mem1 = extract_position(self.getMemoryFloat(1, i))
    mem2 = extract_position(self.getMemoryFloat(2, i))
    mem3 = extract_position(self.getMemoryFloat(3, i))
    mem4 = extract_position(self.getMemoryFloat(4, i))
    mem5 = extract_position(self.getMemoryFloat(5, i))
    if show_log(CONST_LOG_DEBUG):
        self.log( "getFriendBaseMemory : fin" )
    return (mem0, mem1, mem2, mem3, mem4, mem5)

def getFriendFighterMemory(self, i):
    if show_log(CONST_LOG_DEBUG):
        self.log( "getFriendFighterMemory : debut" )
    mem0 = extract_position(self.getMemoryFloat(0, i))
    mem1 = extract_position(self.getMemoryFloat(1, i))
    mem2 = extract_fighter_infos(self.getMemoryUInt(2, i))
    mem3 = extract_position(self.getMemoryFloat(3, i))
    if show_log(CONST_LOG_DEBUG):
        self.log( "getFriendFighterMemory : fin" )
    return (mem0, mem1, mem2, mem3)

def getFriendMiningShipMemory_old(self, i):
    if show_log(CONST_LOG_DEBUG):
        self.log( "getFriendMiningShipMemory_old : debut-fin" )
    return getFriendFighterMemory(self, i)

def getFriendMiningShipMemory(self, i):
    if show_log(CONST_LOG_DEBUG):
        self.log( "getFriendMiningShipMemory : debut" )
    mem0 = extract_position(self.getMemoryFloat(0, i))
    mem1 = extract_position(self.getMemoryFloat(1, i))
    mem3 = extract_position(self.getMemoryFloat(3, i))
    mem2 = extract_position2(self.getMemoryUInt(2, i), mem3[0], mem3[1])
    if show_log(CONST_LOG_DEBUG):
        self.log( "getFriendMiningShipMemory : fin" )
    return (mem0, mem1, mem2, mem3)


def logFighter_cible_type(cible_type):
    log = ""
    if cible_type == CONST_ENNEMY_MININGSHIP :
            log += "Mining"
    elif cible_type == CONST_ENNEMY_FIGTHER :
            log += "Fighter"
    elif cible_type == CONST_ENNEMY_BASE :
            log += "Base"
    else:
            log += "vide"
    return log                

def logMyBaseMemory(self):
    memory = getMyBaseMemory(self)
    if show_log(CONST_LOG_ERROR):
        self.log( "Ennemy1 = "+ str(memory[0]) +"   Ennemy2 = "+ str(memory[1]) +"   Nb fighters = "+ str(int(memory[5][0])) +"   Nb miningship = "+ str(int(memory[5][1])) )
        self.log( "Mineral1 = "+ str(memory[2]) +"   Mineral2 = "+ str(memory[3]) +"   Mineral3 = "+ str(memory[4]) )

def logMyFighterMemory(self):
    memory = getMyFighterMemory(self)
    if show_log(CONST_LOG_ERROR):
        self.log( "Ennemy1 = "+ str(memory[0]) +"   Ennemy2 = "+ str(memory[1]) +"   Base = "+ str(memory[3]))
        self.log(  "Cible 1 : Type = "+ logFighter_cible_type(memory[2][0]) +" - Nb ennemies = "+ str(memory[2][1]) +" - Nb allies = "+ str(memory[2][2]) )
        self.log(  "Cible 2 : Type = "+ logFighter_cible_type(memory[2][3]) +" - Nb ennemies = "+ str(memory[2][4]) +" - Nb allies = "+ str(memory[2][5]) )

def logMyMiningShipMemory(self):
    memory = getMyMiningShipMemory(self)
    if show_log(CONST_LOG_ERROR):
        self.log( "Mineral1 = "+ str(memory[0]) +"   Mineral2 = "+ str(memory[1]) )
        self.log( "Ennemy1 = "+ str(memory[2]) +"   Base = "+ str(memory[3]) )

def setEnnemyBaseMemory(self, ennemyPosition, Base):
    BaseMemory = getFriendBaseMemory(self, Base)
    if ennemyPosition != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if BaseMemory[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and not in_circle( BaseMemory[1][0], BaseMemory[1][1], MiningDistanceProche(), ennemyPosition[0], ennemyPosition[1]) \
        or BaseMemory[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and not in_circle( BaseMemory[0][0], BaseMemory[0][1], MiningDistanceProche(), ennemyPosition[0], ennemyPosition[1]) \
        or BaseMemory[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and BaseMemory[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and not in_circle( BaseMemory[0][0], BaseMemory[0][1], MiningDistanceProche(), ennemyPosition[0], ennemyPosition[1]) \
            and not in_circle( BaseMemory[1][0], BaseMemory[1][1], MiningDistanceProche(), ennemyPosition[0], ennemyPosition[1]) :
            # Decaller la memoire "ennemy" de la BASE
            self.setMemoryFloat(1, compress_position(BaseMemory[0][0], BaseMemory[0][1]), Base)
            # Inscrire le nouvel ennemi dans la BASE
            self.setMemoryFloat(0, compress_position(ennemyPosition[0], ennemyPosition[1]), Base)
    else :
        if BaseMemory[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)
        elif BaseMemory[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)

def setMineralBaseMemory(self, mineralPosition, Base):
    BaseMemory = getFriendBaseMemory(self, Base)
        
    if mineralPosition != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if BaseMemory[4] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and not in_circle( BaseMemory[3][0], BaseMemory[3][1], MiningDistanceProche(), mineralPosition[0], mineralPosition[1]) \
                and not in_circle( BaseMemory[2][0], BaseMemory[2][1], MiningDistanceProche(), mineralPosition[0], mineralPosition[1]) \
            or BaseMemory[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and not in_circle( BaseMemory[2][0], BaseMemory[2][1], MiningDistanceProche(), mineralPosition[0], mineralPosition[1]) \
            or BaseMemory[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            or BaseMemory[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and BaseMemory[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and BaseMemory[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and not in_circle( BaseMemory[4][0], BaseMemory[4][1], MiningDistanceProche(), mineralPosition[0], mineralPosition[1]) \
                and not in_circle( BaseMemory[3][0], BaseMemory[3][1], MiningDistanceProche(), mineralPosition[0], mineralPosition[1]) \
                and not in_circle( BaseMemory[2][0], BaseMemory[2][1], MiningDistanceProche(), mineralPosition[0], mineralPosition[1]) :
            # Decaller la memoire "mineral" de la BASE
            self.setMemoryFloat(4, compress_position(BaseMemory[3][0], BaseMemory[3][1]), Base)
            self.setMemoryFloat(3, compress_position(BaseMemory[2][0], BaseMemory[2][1]), Base)
            # Inscrire le nouveau minerai dans la BASE
            self.setMemoryFloat(2, compress_position(mineralPosition[0], mineralPosition[1]), Base)
    else :
        if BaseMemory[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(4, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)
        elif BaseMemory[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(3, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)
        elif BaseMemory[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            self.setMemoryFloat(2, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), Base)




# ********************************
# ********************************
def play_base_test(self):
    if show_log(CONST_LOG_CRITICAL):
        self.log( "*********BASE********** : (" + str(int(self.pos()[0])) + ", " + str(int(self.pos()[1])) + ")"  )
        self.log( "Vie: " + str(self.life()) + "\t-\tmineralStorage: " + str(self.mineralStorage()) )
    
    
    logMyBaseMemory(self)
    me = getMyBaseMemory(self)
    
    # Definir la position de la BASE
    px,py = basePos = self.pos()
    

    n = getSortedNeighbours(self)
    
    # Faire vieillir la memoire des mineraux
    cpt = me[5][0] + 1
    if cpt<20 :
        vieillissement_memoire = 1
        FighterBuildRate = 0
        MiningBuildRate = 100
        FuelReserve = 0
    elif cpt<200 :
        vieillissement_memoire = cpt/10
        FighterBuildRate = 0
        MiningBuildRate = 100
        FuelReserve = 0
    elif cpt<400 :
        vieillissement_memoire = cpt/5
        FighterBuildRate = 10
        MiningBuildRate = 90
        FuelReserve = 1000
    elif cpt<800 :
        vieillissement_memoire = 100
        FighterBuildRate = 40
        MiningBuildRate = 60
        FuelReserve = 4000
    elif cpt<1200 :
        vieillissement_memoire = 100
        FighterBuildRate = 50
        MiningBuildRate = 30
        FuelReserve = 12000
    else :
        vieillissement_memoire = 100
        FighterBuildRate = 70
        MiningBuildRate = 30
        FuelReserve = 24000
        
    self.setMemoryFloat(5, compress_position(cpt, cpt) )
    if show_log(CONST_LOG_WARNING):
        self.log( "===============================CPT = " + str(cpt) + "   CPTmodulo(" + str(vieillissement_memoire) + ") = "+ str(cpt%vieillissement_memoire)  )
    if cpt%vieillissement_memoire == 0:
        if show_log(CONST_LOG_WARNING):
            self.log( "Vieillissement de la memoire" )
        setMineralBaseMemory(self, (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), self)

    # Remettre a jour la liste ENNEMY en fonction de l'importance de ce qui est visible.
    if show_log(CONST_LOG_DEBUG):
        self.log( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : debut" )
    for i in n:
        if ( isinstance(i, aiwar.MiningShip) \
        or isinstance(i, aiwar.Fighter) \
        or isinstance(i, aiwar.Base) ) \
        and not self.isFriend(i) \
		and self.distanceTo(i) < FighterDistanceLoin() : # L'ennemy doit etre visible des fighters
            px,py = ennemiPos = i.pos()
            if show_log(CONST_LOG_WARNING):
                self.log( "++Ennemi spoted near BASE : distance=" + str(self.distanceTo(i)) + "   x=" + str(int(px)) + "   y="+ str(int(px))  )
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
    # S'il existe un ennemi1 localise, creer un guerrier
    #if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and self.mineralStorage() > aiwar.BASE_FIGHTER_PRICE() and False or False and self.mineralStorage()!=0 and random.randint( 1, 1+int(5*aiwar.BASE_FIGHTER_PRICE()/self.mineralStorage()) ) == 1:
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and (self.mineralStorage() - FuelReserve) > aiwar.BASE_FIGHTER_PRICE() \
    and True \
    or True \
    and self.mineralStorage() > FuelReserve \
    and random.randint( 1, 100-FighterBuildRate+1+int(10*aiwar.BASE_FIGHTER_PRICE()/(self.mineralStorage()-FuelReserve)) ) == 1 \
    or self.mineralStorage() >= (0.9*aiwar.BASE_MAX_MINERAL_STORAGE()) \
    and random.randint(0,1)==0 :
        if show_log(CONST_LOG_WARNING):
            self.log( "Je fabrique un guerrier" )
        self.createFighter()
        # ***** TEST TEST TEST ****** Effacer les ennemis des Miniers de maniere inconditionnelle
        for i in n:
            if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.BASE_REFUEL_RADIUS():
                # Effacer l'ennemi de la memoire du minier
                self.setMemoryFloat(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, basePos[0], basePos[1] ), i )
        logMyBaseMemory(self)


    # remissile friend ships
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.BASE_GIVE_MISSILE_RADIUS():
            if show_log(CONST_LOG_WARNING):
                self.log( "je fais le plein de MISSILES de mon ami" )
            self.giveMissiles(aiwar.FIGHTER_MAX_MISSILE(), i)
            

    # refuel friend ships
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.BASE_REFUEL_RADIUS():
            if show_log(CONST_LOG_WARNING):
                self.log( "je fais le plein de FUEL de mon ami" )
            self.refuel(aiwar.MININGSHIP_START_FUEL(), i)


#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
#ANNULATION CONSTRUCTION GUERRIER POUR DEBUGGER MINIER "and False or False and"
    # create new MiningShip
    if (self.mineralStorage() - FuelReserve) > (2*aiwar.BASE_FIGHTER_PRICE()) \
    and random.randint( 1, 100 - MiningBuildRate + 1+ int(4*aiwar.BASE_MININGSHIP_PRICE()/self.mineralStorage()) ) == 1 \
    or self.mineralStorage() >= (0.9*aiwar.BASE_MAX_MINERAL_STORAGE()) \
    and random.randint(0,1)==0 :
        if show_log(CONST_LOG_WARNING):
            self.log( "Je fabrique un mineur" )
        self.createMiningShip()


    # communiquer avec les copains
    me = getMyBaseMemory(self)
    

    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire Fighter : debut" )
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) \
            and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() \
            and ( me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) or me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) ):
            # Me.0
            # Copie du guerrier seulement s'il revient vers nous
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and ship_isBack(self, i):
                friend = getFriendFighterMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[1]:
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto policier" )
                    self.setMemoryFloat(0, compress_position(friend[0][0], friend[0][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[1]:
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto policier" )
                    self.setMemoryFloat(0, compress_position(friend[1][0], friend[1][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
            # Me.1
            # Copie du guerrier seulement s'il revient vers nous
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and ship_isBack(self, i):
                friend = getFriendFighterMemory(self, i)
                if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[0] != me[0]:
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto policier" )
                    self.setMemoryFloat(1, compress_position(friend[0][0], friend[0][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
                elif friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[1] != me[0]:
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto policier" )
                    self.setMemoryFloat(1, compress_position(friend[1][0], friend[1][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyBaseMemory(self)
    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire Fighter : fin" )
    
    # Effacer de tous les miniers, les ennemis deja enregistrés
    if show_log(CONST_LOG_DEBUG):
        self.log( "Effacer Ennemi de la memoire MiningShip : debut" )
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) \
            and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() \
            and ( me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                or me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) ):
            friend = getFriendMiningShipMemory(self, i)
            if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and in_circle( friend[2][0], friend[2][1], MiningDistanceProche(), me[0][0], me[0][1]):
            #if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] == me[0]:
                # Effacer l'ennemi de la memoire du minier
                self.setMemoryFloat(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, friend[3][0], friend[3][1] ), i )
            if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and in_circle( friend[2][0], friend[2][1], MiningDistanceProche(), me[1][0], me[1][1]):
            #if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and friend[2] == me[1]:
                # Effacer l'ennemi de la memoire du minier
                self.setMemoryFloat(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, friend[3][0], friend[3][1] ), i )
    if show_log(CONST_LOG_DEBUG):
        self.log( "Effacer Ennemi de la memoire MiningShip : fin" )


    # ***** TEST TEST TEST PLUS ***** DE COPIE des ENNEMIS DES FIGHTERS
    # Effacer la memoire des ennemis de la base.
    self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
    self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
    

    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # Pendant les 800 tours du debut:
    # Prevoir de calculer une zone autour de la base à explorer
    # A chaque fois qu'un minier revient sans cible => Deduire une zone dédiée à ne plus explorer
    # A chaque fois qu'un minier revient AVEC cible => Maintenir la zone dediée et effacer la zone opposée ou mathématiquement trop loin pour etre sur la MAP
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU
    # ADU ADU ADU ADU ADU ADU ADU ADU ADU




# ********************************
# ********************************
def play_miningship_1(self):
    if show_log(CONST_LOG_CRITICAL):
        self.log( "*******MININGSHIP****** : (" + str(int(self.pos()[0])) + ", " + str(int(self.pos()[1])) + ")" )
        self.log( "Vie: " + str(self.life()) + "\t-\tfuel: " + str(self.fuel()) + "\t-\tmineralStorage: " + str(self.mineralStorage()) )

    n = getSortedNeighbours(self)
    
    logMyMiningShipMemory(self)
    me = getMyMiningShipMemory(self)

    cpt_friend_mining = 0
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            cpt_friend_mining +=1

    cpt_friend_fighter = 0
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            cpt_friend_fighter +=1


    # recherche de la base amie
    baseConnue = False
    basePos = me[3]
    if basePos != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if show_log(CONST_LOG_CRITICAL):
            self.log( "je connais ma base" )
        baseConnue = True

    for i in n:
        if isinstance(i, aiwar.Base) and self.isFriend(i):
            px, py = basePos = i.pos()
            self.setMemoryFloat(3, compress_position(px, py) )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
            baseConnue = True
            break

    # NE PLUS FUIR, SAUF LES MISSILES !!  ***** EN TEST *****
    # NE PLUS FUIR, SAUF LES MISSILES !!  ***** EN TEST *****
    # NE PLUS FUIR, SAUF LES MISSILES !!  ***** EN TEST *****
    # NE PLUS FUIR, SAUF LES MISSILES !!  ***** EN TEST *****
    # NE PLUS FUIR, SAUF LES MISSILES !!  ***** EN TEST *****
    # FUIR si bit 1 'Ennemy" = TRUE
    if show_log(CONST_LOG_DEBUG):
        self.log( "Fuir si un ennemi devient visible : debut" )
    ennemiEnVue = False
    bit_fuite = self.getMemoryUInt(2) & 0x01
    if show_log(CONST_LOG_DEBUG):
        self.log( "self.getMemoryUInt(2) = " + str(self.getMemoryUInt(2)) + " -  self.getMemoryUInt(2) & 0x01 = " + str(self.getMemoryUInt(2) & 0x01) )
    if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and (bit_fuite == 1):
        if show_log(CONST_LOG_DEBUG) or show_log(CONST_LOG_JOKE):
            self.log( "FUITE !!!" )
        ennemiEnVue = True
    #if ennemiPos != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
    #    if show_log(CONST_LOG_WARNING):
    #        self.log( "j'ai un ennemi en memoire" )
    #    ennemiEnVue = True
    if show_log(CONST_LOG_DEBUG):
        self.log( "Fuir si un ennemi devient visible : fin" )
    
    # Remettre a jour la liste en fonction de l'importance de ce qui est visible.
    if show_log(CONST_LOG_DEBUG):
        self.log( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : debut" )
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            px,py = ennemiPos = i.pos()
            if show_log(CONST_LOG_WARNING):
                self.log( "++Ennemy MININGSHIP spoted: distance="+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)) )
            self.setMemoryUInt(2, compress_position2(px, py, me[3][0], me[3][1]) | bit_fuite )
            # Un minier ennemi ne fait plus fuir
            #ennemiEnVue = True
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)

    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            px,py = ennemiPos = i.pos()
            if show_log(CONST_LOG_WARNING):
                self.log( "++++Ennemy FIGHTER spoted: "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)) )
            self.setMemoryUInt(2, compress_position2(px, py, me[3][0], me[3][1]) | bit_fuite )
            self.log( "++++Ennemy compress_position2: "+ str(compress_position2(px, py, me[3][0], me[3][1])) )
            self.log( "++++Ennemy self.setMemoryUInt(2): "+ str(self.getMemoryUInt(2)) )
            # Un FIGTHER ennemi ne fait plus fuir (sauf son missile)
            #ennemiEnVue = True
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)

    for i in n:
        if isinstance(i, aiwar.Missile):
            if (missile_spoted_me(self, i) == True):
                px,py = ennemiPos = i.pos()
                if show_log(CONST_LOG_WARNING):
                    self.log( "++++ MISSILE ON MY WAY !! Distance= "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)) )
                if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                    self.setMemoryUInt(2, compress_position2(px, py, me[3][0], me[3][1]) | bit_fuite )
                self.setMemoryUInt(2, self.getMemoryUInt(2) | 0x01 )
                ennemiEnVue = True
            else:
                if show_log(CONST_LOG_WARNING):
                    self.log( "++++ MISSILE away and I'm safe ! Distance= "+ str(int(self.distanceTo(i))) )
            #self.setMemoryFloat(2, compress_position(px, py) )
            # Un FIGTHER ennemi ne fait plus fuir (sauf son missile)
            #ennemiEnVue = True
            # Mettre a jour mon "Me"
            #me = getMyMiningShipMemory(self)

    for i in n:
        if isinstance(i, aiwar.Base) and not self.isFriend(i):
            px,py = ennemiPos = i.pos()
            if show_log(CONST_LOG_WARNING):
                self.log( "++++++Ennemy BASE spoted: "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)) )
            # "+1" pour la fuite.
            self.setMemoryUInt(2, compress_position2(px, py, me[3][0], me[3][1]) | 0x01 )
            # La vue de la BASE ENNEMIE provoque la fuite à la base pour avertir tout le monde
            ennemiEnVue = True
            # Ajouter la base ennemy en cible 0 pour alimenter continuellement en fighter
            self.setMemoryFloat(0, compress_position(px, py) )
            # Mettre a jour mon "Me"
            me = getMyMiningShipMemory(self)
    if show_log(CONST_LOG_DEBUG):
        self.log( "Remettre a jour la liste en fonction de l'importance de ce qui est visible : fin" )


    # communiquer avec les copains
    me = getMyMiningShipMemory(self)
    
    friend_fighter = (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID)
    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire Fighter : debut" )
    Counter = 1
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) > aiwar.COMMUNICATION_RADIUS():
            friend_fighter = i.pos()
            
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0 n'est jamais copié d'un Fighter
            
# LE FIGTHER NE MEMORISE PLUS DE MINERAUX DANS SA MEMOIRE 2 !!!
#            # Me.1 (vide)
#            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                friend = getFriendFighterMemory(self, i)
#                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
#                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= aiwar.MININGSHIP_DETECTION_RADIUS():
#                    if show_log(CONST_LOG_WARNING):
#                        self.log( "Poto policier ([1]<=copy mine)" )
#                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
#                    # Mettre a jour mon "Me"
#                    me = getMyMiningShipMemory(self)
#            # Me.1 (ECRASE)
#            if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
#                friend = getFriendFighterMemory(self, i)
#                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
#                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= MiningDistanceLoin() \
#                    and distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= MiningDistanceLoin():
#                    if show_log(CONST_LOG_WARNING):
#                        self.log( "Poto policier ([1]<=ecrase mine)" )
#                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
#                    # Mettre a jour mon "Me"
#                    me = getMyMiningShipMemory(self)
            # Effacer son "Ennemy" s'il est dans un FIGHTER croisé
            # Qui m'a croisé et qui s'éloigne de moi (donc plus proche de l'ennemi)
            # Et dont l'ennemi est le meme avec une precision de MININGSHIP_DETECTION_RADIUS()/4
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if readFriendMemory(Counter) :
                    Counter += 1
                    friend = getFriendFighterMemory(self, i)
                    if ( friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and in_circle( friend[0][0], friend[0][1], MiningDistanceProche(), me[2][0], me[2][1]) \
                    and not ship_isBack(self, i) \
                    or friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and in_circle( friend[1][0], friend[1][1], MiningDistanceProche(), me[2][0], me[2][1]) ) \
                    and not ship_isBack(self, i):
                        # Effacer l'ennemi de ma memoire
                        self.setMemoryUInt(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, me[3][0], me[3][1]) )
                        # Mettre a jour mon "Me"
                        me = getMyMiningShipMemory(self)
    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire Fighter : fin" )


    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire Base : debut" )
    for i in n:
        if isinstance(i, aiwar.Base) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            # Me.0 (vide)
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if show_log(CONST_LOG_DEBUG):
                    self.log( "Copier memoire Base : me[0]" )
                friend = getFriendBaseMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Base : Base[2]=>Me[0]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose : me[0]<=base[2]" )
                    self.setMemoryFloat(0, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[3][0], friend[3][1], me[1][0], me[1][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Base : Base[3]=>Me[0]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose : me[0]<=base[3]" )
                    self.setMemoryFloat(0, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[4][0], friend[4][1], me[1][0], me[1][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Base : Base[4]=>Me[0]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose : me[0]<=base[4]" )
                    self.setMemoryFloat(0, compress_position(friend[4][0], friend[4][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1 (vide)
            if me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if show_log(CONST_LOG_DEBUG):
                    self.log( "Copier memoire Base : me[1]" )
                friend = getFriendBaseMemory(self, i)
                if friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[4][0], friend[4][1], me[0][0], me[0][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Base : Base[4]=>Me[1]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose : me[1]<=base[4]" )
                    self.setMemoryFloat(1, compress_position(friend[4][0], friend[4][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[3][0], friend[3][1], me[0][0], me[0][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Base : Base[3]=>Me[1]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose : me[1]<=base[3]" )
                    self.setMemoryFloat(1, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Base : Base[2]=>Me[1]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose : me[1]<=base[2]" )
                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.1 (ECRASE)
            if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if show_log(CONST_LOG_DEBUG):
                    self.log( "ECRASER memoire : me[1]" )
                friend = getFriendBaseMemory(self, i)
                if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= MiningDistanceLoin() \
                    and distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "ECRASER memoire : Base[2]=>Me[1]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose ECRASE : me[1]<=base[2]" )
                    self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[3][0], friend[3][1], me[0][0], me[0][1]) >= MiningDistanceLoin()  \
                    and distance(friend[3][0], friend[3][1], me[1][0], me[1][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "ECRASER memoire : Base[3]=>Me[1]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose ECRASE : me[1]<=base[3]" )
                    self.setMemoryFloat(1, compress_position(friend[3][0], friend[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
                elif friend[4] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[4][0], friend[4][1], me[0][0], me[0][1]) >= MiningDistanceLoin() \
                    and distance(friend[4][0], friend[4][1], me[1][0], me[1][1]) >= MiningDistanceLoin():
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "ECRASER memoire : Base[4]=>Me[1]" )
                    if show_log(CONST_LOG_WARNING):
                        self.log( "Poto rose ECRASE : me[1]<=base[4]" )
                    self.setMemoryFloat(1, compress_position(friend[4][0], friend[4][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)

            # Charger une cible aléatoire si je n'ai aucune cible en memoire 
            # et que je viens de croiser la base
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                target_x, target_y = random_target( (me[3][0], me[3][1]), cpt_friend_mining )
                self.setMemoryFloat(1, compress_position(target_x, target_y) )

            # Effacer son "Ennemy" s'il est dans la BASE croisée
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                friend = getFriendBaseMemory(self, i)
                if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and ( friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[0][0], friend[0][1], MiningDistanceEffacerEnnemi(), me[2][0], me[2][1]) \
                or friend[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and in_circle( friend[1][0], friend[1][1], MiningDistanceEffacerEnnemi(), me[2][0], me[2][1]) ):
                    # Effacer l'ennemi de ma memoire
                    self.setMemoryUInt(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, me[3][0], me[3][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Inscrire son "Ennemy" dans la BASE croisée s'il n'y etait pas encore
            # Me.2
            if me[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                setEnnemyBaseMemory(self, me[2], i)
    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire Base : fin" )


    # Copier Friend.0=>Me.1 / Friend.1=>Me.0 / Friend.2=>Me.2
    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire MiningShip : debut" )
    Counter = 1
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            
            # ADU ADU ADU
            # ADU ADU ADU
            # ADU ADU ADU
            # Prevoir d'effacer la memoire des autres si j'ai des mineraux mais je ne suis pas plein, si je suis sur le retour, si je croise un vaisseau avec une direction opposée à la mienne, si ca cible [0] n'est pas vide et que je ne l'ai pas dans ma memoire => effacer sa memoire car le minerais a disparu
            # ADU ADU ADU
            # ADU ADU ADU
            # ADU ADU ADU
        
            # Copier memoire d'un ami uniquement si je suis hors de la zone "MiningDistanceCopierMinerai" avec pour reference la cible à copier. Le but est d'eviter un blocage par echange d'information entre les vaisseaux qui rentrent à la base et ceux qui vont vers un minerai epuisé
            # Me.0 (vide)
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) :
                if readFriendMemory(Counter) :
                    Counter += 1
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Minier : Me[0]" )
                    friend = getFriendMiningShipMemory(self, i)
                    # Copier si la cible du poto n'est pas en visibilite de ma cible
                    if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[0][0], friend[0][1], me[1][0], me[1][1]) >= MiningDistanceLoin() \
                    and self.distanceTo( (friend[0][0], friend[0][1]) ) > MiningDistanceCopierMinerai() :
                        if show_log(CONST_LOG_DEBUG):
                            self.log( "Copier memoire Minier : Friends[0]=>Me[0]" )
                        if show_log(CONST_LOG_WARNING):
                            self.log( "Poto minier ([0]<=copy mine)" )
                        self.setMemoryFloat(0, compress_position(friend[0][0], friend[0][1]) )
                        # Mettre a jour mon "Me"
                        me = getMyMiningShipMemory(self)
            # Me.1 (ECRASE si Friend[0] existe)
            else :
                if readFriendMemory(Counter) :
                    Counter += 1
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Minier (else) : Me[0]" )
                    friend = getFriendMiningShipMemory(self, i)
                    if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and distance(friend[0][0], friend[0][1], me[0][0], me[0][1]) >= MiningDistanceLoin() \
                    and self.distanceTo( (friend[0][0], friend[0][1]) ) > MiningDistanceCopierMinerai() :
                        if show_log(CONST_LOG_DEBUG):
                            self.log( "Copier memoire Minier : Friends[0]=>Me[1]" )
                        if show_log(CONST_LOG_WARNING):
                            self.log( "Poto minier ([1]<=copy mine)" )
                        self.setMemoryFloat(1, compress_position(friend[0][0], friend[0][1]) )
                        # Mettre a jour mon "Me"
                        me = getMyMiningShipMemory(self)
            # Me.2 (vide)
            if me[2] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if readFriendMemory(Counter) :
                    Counter += 1
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Minier : Me[2]" )
                    friend = getFriendMiningShipMemory(self, i)
                    if friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                    and self.distanceTo( (me[3][0], me[3][1]) ) > MiningDistanceCopierEnnemi():
                        if show_log(CONST_LOG_DEBUG):
                            self.log( "Copier memoire Minier : Friends[2]=>Me[2]" )
                        if show_log(CONST_LOG_WARNING):
                            self.log( "Poto minier (Copy ENNEMY)" )
                        self.setMemoryUInt(2, compress_position2(friend[2][0], friend[2][1], me[3][0], me[3][1]) )
                        if show_log(CONST_LOG_WARNING):
                            self.log( "++Ennemy MININGSHIP (copy): x="+ str(friend[2][0]) +", y="+ str(friend[2][1]) )
                    # Mettre a jour mon "Me"
                    me = getMyMiningShipMemory(self)
            # Me.3 (vide)
            if me[3] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if readFriendMemory(Counter) :
                    Counter += 1
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "Copier memoire Minier : Me[3]" )
                    friend = getFriendMiningShipMemory(self, i)
                    if friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                        if show_log(CONST_LOG_DEBUG):
                            self.log( "Copier memoire Minier : Friends[3]=>Me[3]" )
                        if show_log(CONST_LOG_WARNING):
                            self.log( "Poto minier (Copy BASE)" )
                        self.setMemoryFloat(3, compress_position(friend[3][0], friend[3][1]) )
                        # Mettre a jour mon "Me"
                        me = getMyMiningShipMemory(self)
            # Me.3 (ECRASE)
            if me[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if readFriendMemory(Counter) :
                    Counter += 1
                    if show_log(CONST_LOG_DEBUG):
                        self.log( "ECRASE memoire Minier : Me[3]" )
                    friend = getFriendMiningShipMemory(self, i)
                    if friend[3] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                        and distance(friend[3][0], friend[3][1], self.pos()[0], self.pos()[1]) < distance(me[3][0], me[3][1], self.pos()[0], self.pos()[1]):
                        if show_log(CONST_LOG_DEBUG):
                            self.log( "Copier memoire Minier : Friends[3]=>Me[3]" )
                        if show_log(CONST_LOG_WARNING):
                            self.log( "Poto minier (ECRASE BASE)" )
                        self.setMemoryFloat(3, compress_position(friend[3][0], friend[3][1]) )
                        # Mettre a jour mon "Me"
                        me = getMyMiningShipMemory(self)
    if show_log(CONST_LOG_DEBUG):
        self.log( "Copier memoire MiningShip : fin" )


    # Rechercher si un mineraux est visible
    minerauxEnVue = False
    for i in n:
        if isinstance(i, aiwar.Mineral):
            minerauxEnVue = True


    # Effacer les mineraux connus qui ont disparus
    if show_log(CONST_LOG_DEBUG):
        self.log( "Effacer mineraux connu : debut" )
        self.log( "self.distanceTo(mineral0)=" + str( int(self.distanceTo(me[0])) ) + "< MiningDistanceEffacerMinerai()=" + str( int(MiningDistanceEffacerMinerai()) ) )
        self.log( "self.distanceTo(mineral1)=" + str( int(self.distanceTo(me[1])) ) )
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and self.distanceTo(me[0]) < MiningDistanceEffacerMinerai() \
        and minerauxEnVue == False :
        # on aurait du voir le minerai -> il est vide
        if show_log(CONST_LOG_WARNING):
            self.log( "j'efface le minerais 0 qui n'existe plus" )
        # reset de la position
        self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        # Mettre a jour mon "Me"
        me = getMyMiningShipMemory(self)
    if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and self.distanceTo(me[1]) < MiningDistanceEffacerMinerai() \
        and minerauxEnVue == False :
        if show_log(CONST_LOG_WARNING):
            self.log( "j'efface le minerais 1 qui n'existe plus" )
        # reset de la position
        self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        # Mettre a jour mon "Me"
        me = getMyMiningShipMemory(self)
    if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
        and self.distanceTo(me[1]) < MiningDistanceEffacerMinerai() \
        and minerauxEnVue == True :
        if show_log(CONST_LOG_WARNING):
            self.log( "Je valide minerais 1 en minerais 0. Youpi !" )
        # Decaller minerais "espere" en "AVERE"
        self.setMemoryFloat(0, compress_position( me[1][0], me[1][1]) )
        self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
    if show_log(CONST_LOG_DEBUG):
        self.log( "Effacer mineraux connu : fin" )


    # Charger une cible aléatoire si je n'ai aucune cible en memoire 
    if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        target_x, target_y = random_target( (me[3][0], me[3][1]), cpt_friend_mining )
        self.setMemoryFloat(1, compress_position(target_x, target_y) )


    # Pas assez de fuel pour rejoindre la cible
    minerauxTropLoin = False
    if show_log(CONST_LOG_DEBUG):
        self.log( "InstantRange = "+ str(int(MiningInstantRange(self))) +" - Cible1 = "+ str(int(self.distanceTo(me[0])*11/10)) +" - Cible2 = "+ str(int(self.distanceTo(me[1])*11/10)) )
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and MiningInstantRange(self) < (self.distanceTo(me[0])*11/10 + distance(me[0][0], me[0][1], me[3][0], me[3][1]) ) :
        if show_log(CONST_LOG_WARNING):
            self.log( "Le minerai 1 est trop loin" )
        minerauxTropLoin = True

    if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and MiningInstantRange(self) < (self.distanceTo(me[1])*11/10 + distance(me[1][0], me[1][1], me[3][0], me[3][1]) ) :
        if show_log(CONST_LOG_WARNING):
            self.log( "Le minerai 2 est trop loin" )
        minerauxTropLoin = True


    # rentrer a la base ?
    if show_log(CONST_LOG_DEBUG):
        self.log( "rentrer a la base ? : debut" )
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
                if show_log(CONST_LOG_WARNING):
                    self.log( "je rentre a la base" )
                chercher_fighter = 0
            if ennemiEnVue:
                chercher_fighter = 0
                # Si ennemi en vue, retourner a la base ou chercher un fighter proche 
                # (mais il faut pouvoir le cibler durablement et l'abandonner s'il n'a pas de fuel)
                # ANNULE TANT QUE LE FUEL et LA CIBLE N'EST PAS DURABLE.
                if False and friend_fighter != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) and random.randint(0,1)==0:
                    chercher_fighter = 1
            if chercher_fighter == 0:
                if show_log(CONST_LOG_WARNING):
                    self.log( "je fuis a la base" )
                self.rotateTo(basePos)
                # Se deplacer tant qu'on est loin de la cible
                if self.distanceTo(basePos) > (0.9*aiwar.MININGSHIP_MINING_RADIUS()):
                    self.move()
            else:
                if show_log(CONST_LOG_WARNING):
                    self.log( "je fuis vers un fighter" )
                self.rotateTo(friend_fighter)
                # Se deplacer tant qu'on est loin de la cible
                if self.distanceTo(friend_fighter) > (aiwar.COMMUNICATION_RADIUS()):
                    self.move()
            # base en vue et assez proche pour donner le minerai ?
            for i in n:
                if isinstance(i, aiwar.Base) and self.isFriend(i):
                    if self.distanceTo(i) < aiwar.MININGSHIP_MINING_RADIUS():
                        if show_log(CONST_LOG_WARNING):
                            self.log( "Mineraux en stock = " + str( int(self.mineralStorage()) ) )
                        mineralPushed = 0
                        mineralPushed = self.pushMineral(i, self.mineralStorage())
                        if show_log(CONST_LOG_WARNING):
                            self.log( "je donne mon minerai a ma base=" + str( int(mineralPushed) ) )
                            self.log( "Mineraux en stock = " + str( int(self.mineralStorage()) ) )
                        
                        # Enregistrer dans la base les mineraux
                        if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                            setMineralBaseMemory(self, me[0], i)
                    break
            if baseConnue or minerauxEnVue == False:
                if show_log(CONST_LOG_DEBUG):
                    self.log( "Fin de traitement MiningShip (rapporter minerais)." )
            if ennemiEnVue:
                if show_log(CONST_LOG_DEBUG):
                    self.log( "Fin de traitement MiningShip (sauve qui peut !)." )
            return
        else:
            if show_log(CONST_LOG_WARNING):
                self.log( "je cherche ma base" )
            random_move(self)
            if show_log(CONST_LOG_DEBUG):
                self.log( "Fin de traitement MiningShip (recherche base)." )
            return
    if show_log(CONST_LOG_DEBUG):
        self.log( "rentrer a la base ? : fin" )
        
        
    # recherche de minerais visible
    if show_log(CONST_LOG_DEBUG):
        self.log( "recherche de minerais visible : debut" )
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
                and distance(mpx, mpy, me[1][0], me[1][1]) >= MiningDistanceLoin() \
                \
                or me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) < MiningDistanceLoin() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[0][0], me[0][1], me[3][0], me[3][1]) :
                if show_log(CONST_LOG_WARNING):
                    self.log( "je sauvegarde la position du minerai (cible 1)" )
                self.setMemoryFloat(0, compress_position(mpx, mpy) )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)

            # ENREGISTER DANS MEMOIRE 2
            # Si memoire 1 non-vide et 2 vide et minerai lointain de memoire 1 => enregistrer dans mem2
            # Si memoire 1 non-vide et 2 non-vide et minerai lointain de memoire 1 et minerai plus proche BASE que memoire 2 => enregistrer dans mem2
            elif me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) >= MiningDistanceLoin() \
                \
                or me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) >= MiningDistanceLoin() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[1][1], me[0][1], me[3][0], me[3][1]) :
                if show_log(CONST_LOG_WARNING):
                    self.log( "je sauvegarde la position du minerai (cible 2)" )
                self.setMemoryFloat(1, compress_position(mpx, mpy) )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)

            # DECALLER POUR ENREGISTER DANS MEMOIRE 1
            # Si memoire 1 vide et 2 non vide et minerai en visibilité de memoire 2 et minerai plus proche BASE que memoire 2 => effacer memoire 2 + enregistrer dans memoire 1 = decaller mem1 en mem2 et enregistrer dans mem1
            # Si memoire 1 non-vide et minerai lointain de memoire 1 et minerai plus proche BASE que memoire 1 => decaller mem1 en mem2 et enregistrer dans mem1
            elif me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[1][0], me[1][1]) < MiningDistanceLoin() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[1][1], me[1][1], me[3][0], me[3][1]) \
                \
                or me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
                and distance(mpx, mpy, me[0][0], me[0][1]) >= MiningDistanceLoin() \
                and distance(mpx, mpy, me[3][0], me[3][1]) < distance(me[0][1], me[0][1], me[3][0], me[3][1]) :
                if show_log(CONST_LOG_WARNING):
                    self.log( "je sauvegarde la position du minerai (decaller cible 1)" )
                self.setMemoryFloat(1, compress_position(me[0][0], me[0][1]) )
                self.setMemoryFloat(0, compress_position(mpx, mpy) )
                # Mettre a jour mon "Me"
                me = getMyMiningShipMemory(self)
                
               
            if show_log(CONST_LOG_WARNING):
                self.log( "je vais au minerai visible" )
            self.rotateTo(minPos)
            # Se deplacer tant qu'on est loin de la cible
            if self.distanceTo(minPos) > aiwar.MININGSHIP_MINING_RADIUS():
                self.move()
            if self.distanceTo(i) < aiwar.MININGSHIP_MINING_RADIUS():
                if show_log(CONST_LOG_WARNING):
                    self.log( "je mine" )
                self.extract(i)
            if show_log(CONST_LOG_DEBUG):
                self.log( "Fin de traitement MiningShip (mineral visible)." )
            return
    if show_log(CONST_LOG_DEBUG):
        self.log( "recherche de minerais visible : fin" )
        
    # recherche de minerai connu
    if show_log(CONST_LOG_DEBUG):
        self.log( "recherche de minerais connu : debut" )
    if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if show_log(CONST_LOG_WARNING):
            self.log( "je vais au minerai 0 : x="+ str(me[0][0]) +", y="+ str(me[0][1]) )
        self.rotateTo(me[0])
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo(me[0]) > (aiwar.MININGSHIP_MINING_RADIUS()):
            self.move()
        if show_log(CONST_LOG_DEBUG):
            self.log( "Fin de traitement MiningShip (mineral 0 memoire)." )
    if me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        if show_log(CONST_LOG_WARNING):
            self.log( "je vais au minerai 1 : x="+ str(me[1][0]) +", y="+ str(me[1][1]) )
        self.rotateTo(me[1])
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo(me[1]) > (aiwar.MININGSHIP_MINING_RADIUS()):
            self.move()
        if show_log(CONST_LOG_DEBUG):
            self.log( "Fin de traitement MiningShip (mineral 1 memoire)." )
    if show_log(CONST_LOG_DEBUG):
        self.log( "recherche de minerais connu : fin" )
    
    # Effacer memoire si fuel vide
    if self.fuel() == 0:
        self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        self.setMemoryUInt(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, me[3][0], me[3][1]) )
    
    if show_log(CONST_LOG_DEBUG):
        self.log( "Fin de traitement MiningShip." )



# ********************************
# ********************************
def play_fighter_test(self):
    if show_log(CONST_LOG_CRITICAL):
        self.log( "********FIGHTER******** : (" + str(int(self.pos()[0])) + ", " + str(int(self.pos()[1])) + ")" )
        self.log( "Vie: " + str(self.life()) + "\t-\tFuel: " + str(self.fuel()) + "\t-\tMissiles: " + str(self.missiles()) )

    n = getSortedNeighbours(self)

    logMyFighterMemory(self)
    me = getMyFighterMemory(self)


# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# Limiter les echanges entre figthers pres de la base.
# Quand un fighter voit un ennemi sans que ca soit une cible principale, il va la signaler à la base.
# La base devra garder en MEM 1 la base adverse et ne jamais l'effacer.
# La base devra garder en MEM 2 une cible (fighter/mining) et l'info sera ponctuelle.
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU


    # Ordre des actions :
    # 0 - Panne de fuel => effacer toutes les cibles
    # 1 - Visualiser une cible pour tirer
    # 2 - Memoriser une cible + position BASE
    # 3 - Rejoindre la cible memoire

    if show_log(CONST_LOG_INFO) or show_log(CONST_LOG_JOKE):
        self.log( "Fighter : ====== PHASE 0 ======" )
    # ====== PHASE 0 ======
    if self.fuel()<aiwar.FIGHTER_MOVE_CONSO():
        self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
        self.setMemoryUInt(2, 0 )
        if self.missiles() <= 0 :
            return
            # Fin de vie du guerrier (plus de missile et plus de fuel)

    
	if show_log(CONST_LOG_INFO) or show_log(CONST_LOG_JOKE):
		self.log( "Fighter : ====== PHASE 1 ======" )
    # ====== PHASE 1 ======
    # Ordre des cibles :
    #   0 - Missile 
    #   1 - BASE
    #   2 - FIGHTER
    #   3 - MININGSHIP
    under_attack=False
    for i in n:
        if isinstance(i, aiwar.Missile):
            if (missile_spoted_me(self, i) == True):
                px, py = missilePos = i.pos()
                under_attack=True
                if show_log(CONST_LOG_WARNING):
                    self.log( "++++ MISSILE ON MY WAY !! Distance= "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)) )
                # On evite les missiles Sauf si la base est menacee (avec une marge) : dist(missile,base) > dist(missile, moi)
                if (distance(px, py, me[3][0], me[3][1]) -20) > distance(px, py, self.pos()[0], self.pos()[1]) :
                    if show_log(CONST_LOG_WARNING):
                        self.log( "++++ Fuir missile : dist(missile,base)-20="+ str(int(distance(px, py, me[3][0], me[3][1]) -20)) + " > dist(missile, moi)=" + str(int(distance(px, py, self.pos()[0], self.pos()[1]))) )
                    if random.randint(0,1)==0:
                        signe=1
                    else:
                        signe=-1
                    self.rotateTo(i)
                    # Quand le missile est loin, fuir avec l'angle min/max.
                    # Quand il s'approche, fuir avec zero degres pour aller dans la meme direction que le missile et se maintenir a distance.
                    angle_facteur = 1 - ( MissileRange()-distance(px, py, self.pos()[0], self.pos()[1]) ) / ( MissileRange() ) 
                    angle_min=int( 70* angle_facteur )
                    angle_max=int( 90* angle_facteur )
                    self.log( "++++ angle_min= "+ str(int(angle_min)) + "++++ angle_max= "+ str(int(angle_max)) )
                    self.rotateOf(180+signe*random.randint(angle_min, angle_max))
                    self.move()
            else:
                if show_log(CONST_LOG_WARNING):
                    self.log( "++++ MISSILE away and I'm safe ! Distance= "+ str(int(self.distanceTo(i))) )

    for i in n:
        if isinstance(i, aiwar.Base) and not self.isFriend(i):
            if show_log(CONST_LOG_WARNING):
                self.log( "++++++Ennemy BASE: "+ str(self.distanceTo(i)) )
            px,py = Pos = i.pos()
            # Decaller l'ennemi 0 en 1 si l'emplacement 0 etait utilisé
            if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and distance(px, py, me[0][0], me[0][1]) >= FighterDistanceLoin():
                self.setMemoryFloat(1, self.getMemoryFloat(0))
                self.setMemoryUInt(2, compress_fighter_infos(CONST_ENNEMY_VOID, 0, 0, me[2][0], me[2][1], me[2][2]) )
            # Enregistrer la position pour le poursuivre
            self.setMemoryFloat(0, compress_position(px, py) )
            # Enregistrer CIBLE 1=BASE
            self.setMemoryUInt(2, compress_fighter_infos(CONST_ENNEMY_BASE, 1, me[2][2], me[2][3], me[2][4], me[2][5]) )
            # Mettre a jour mon "Me"
            me = getMyFighterMemory(self)
            if self.missiles() > 0 and MissileRange() > self.distanceTo(i) :
                if show_log(CONST_LOG_WARNING) or show_log(CONST_LOG_JOKE):
                    self.log( "++++++Ennemy BASE: BOOM dans ta face !" )
                # Tirer sans condition sur la BASE
                self.launchMissile(i)
            else:
                if show_log(CONST_LOG_WARNING):
                    self.log( "++++++Ennemy BASE: Plus de munitions/Trop loin ! :'(" )


    cpt_ship = 0
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            cpt_ship +=1
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            if show_log(CONST_LOG_WARNING):
                self.log( "++++++Ennemy FIGHTER: "+ str(self.distanceTo(i)) )
            px,py = Pos = i.pos()
            # Si aucune cible (1 ou 2) n'avait cette cible en portee => ENREGISTRER
            # Si la cible 1 n'est pas une BASE !!
            if distance(px, py, me[0][0], me[0][1]) >= FighterDistanceLoin() \
            and distance(px, py, me[1][0], me[1][1]) >= FighterDistanceLoin() \
            and me[2][0] != CONST_ENNEMY_BASE:
                # Decaller l'ennemi 0 en 1 si l'emplacement 0 etait plein
                if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) :
                    self.setMemoryFloat(1, self.getMemoryFloat(0))
                    self.setMemoryUInt(2, compress_fighter_infos(CONST_ENNEMY_VOID, 0, 0, me[2][0], me[2][1], me[2][2]) )
                # Enregistrer la position pour le poursuivre
                self.setMemoryFloat(0, compress_position(px, py) )
                # Enregistrer CIBLE 1=BASE
                self.setMemoryUInt(2, compress_fighter_infos(CONST_ENNEMY_FIGTHER, cpt_ship, me[2][2], me[2][3], me[2][4], me[2][5]) )
                # Mettre a jour mon "Me"
                me = getMyFighterMemory(self)
            if self.missiles() > 0 and ShootFighter(self.distanceTo(i))==True:
                if show_log(CONST_LOG_WARNING) or show_log(CONST_LOG_JOKE):
                    self.log( "++++Ennemy FIGHTER: Attrape ca !" )
                # Tirer 1 fighter sur 2
                if random.randint(1, 2*cpt_ship) == 1:
                    self.launchMissile(i)
                    # On fait un pas en arriere pour sortir de la zone visible de l'ennemi
                    # Si ca peut eviter de se prendre un missile ... :c)
                    self.rotateTo(i)
                    if random.randint(1, 2) == 1:
                        self.rotateOf(90)
                    else:
                        self.rotateOf(-90)
                    self.move()
                    if show_log(CONST_LOG_WARNING):
                        self.log( "***************** BOUGEAGE PARASITE **************" )
                    if show_log(CONST_LOG_JOKE):
                        self.log( " La danse de la mort !! Ha ha ha ! :D" )
            else:
                if show_log(CONST_LOG_WARNING):
                    self.log( "++++Ennemy FIGHTER: Plus de munitions/Trop loin ! :'(" )

    cpt_ship = 0
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            cpt_ship +=1
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            if show_log(CONST_LOG_WARNING):
                self.log( "++Ennemy MININGSHIP: "+ str(self.distanceTo(i)) )
            px,py = Pos = i.pos()
            # Si aucune cible (1 ou 2) n'avait cette cible en portee => ENREGISTRER
            # Si la cible 1 n'est pas une BASE ou FIGHTER !!
            if distance(px, py, me[0][0], me[0][1]) >= FighterDistanceLoin() \
            and distance(px, py, me[1][0], me[1][1]) >= FighterDistanceLoin() \
            and me[2][0] != CONST_ENNEMY_BASE \
            and me[2][0] != CONST_ENNEMY_FIGTHER:
                # Decaller l'ennemi 0 en 1 si l'emplacement 0 etait plein
                if me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) :
                    self.setMemoryFloat(1, self.getMemoryFloat(0))
                    self.setMemoryUInt(2, compress_fighter_infos(CONST_ENNEMY_VOID, 0, 0, me[2][0], me[2][1], me[2][2]) )
                # Enregistrer la position pour le poursuivre
                self.setMemoryFloat(0, compress_position(px, py) )
                # Enregistrer CIBLE 1=MININGSHIP
                self.setMemoryUInt(2, compress_fighter_infos(CONST_ENNEMY_MININGSHIP, cpt_ship, me[2][2], me[2][3], me[2][4], me[2][5]) )
                # Mettre a jour mon "Me"
                me = getMyFighterMemory(self)
            if self.missiles() > 0 and ShootMining(self.distanceTo(i))==True:
                if show_log(CONST_LOG_WARNING) or show_log(CONST_LOG_JOKE):
                    self.log( "++Ennemy MININGSHIP: N'y vois rien de personnel, je fais mon job." )
                # Tirer 1 MiningShip sur 4
                if random.randint(1, 4*cpt_ship) == 1:
                    self.launchMissile(i)
            else:
                if show_log(CONST_LOG_WARNING):
                    self.log( "++Ennemy MININGSHIP: Plus de munitions/Trop loin ! :'(" )

    # Si plus de fuel : tirer a vue et ne plus traiter la memoire
    if self.fuel()<aiwar.FIGHTER_MOVE_CONSO():
        return


	if show_log(CONST_LOG_INFO) or show_log(CONST_LOG_JOKE):
		self.log( "Fighter : ====== PHASE 2 ======" )
    # ====== PHASE 2 ======
    # S'il existe un ennemi1 localise dans BASE, je go le combattre
    # Chercher une cible dans mon entourage
    for i in n:
        # Recuperer cible de la BASE
        if isinstance(i, aiwar.Base) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() and self.isFriend(i):
            friend = getFriendBaseMemory(self, i)
            if show_log(CONST_LOG_INFO) or show_log(CONST_LOG_JOKE):
				self.log( "Fighter : ENREGISTRE ENNEMI BASE : me[0]="+ str(me[0][0]) + " - friend[0]=" + str(friend[0][0]) + " - me[1]=" + str(me[1][0]) )
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  ( me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
			or distance(friend[0][0], friend[0][1], me[1][0], me[1][1]) >= FighterDistanceLoin() ):
                self.log( "Fighter : ENREGISTRE ENNEMI BASE" )
                # Enregistrer la position
                self.setMemoryFloat(0, self.getMemoryFloat(0,i))
                # Decaller le 2eme ennemi dans la memoire de l'ami
                self.setMemoryFloat(0, self.getMemoryFloat(1,i), i)
                self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID), i )
                
            elif me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  ( me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
			or distance(friend[0][0], friend[0][1], me[0][0], me[0][1]) >= FighterDistanceLoin() ):
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
            
        # Recuperer cible du MININGSHIP
        if isinstance(i, aiwar.MiningShip) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() and self.isFriend(i):
            friend = getFriendMiningShipMemory(self, i)
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  ( me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
			or distance(friend[2][0], friend[2][1], me[1][0], me[1][1]) >= FighterDistanceLoin() ):
                # Enregistrer la position
                self.setMemoryFloat(0, compress_position(friend[2][0], friend[2][1]) )
                # Effacer la cible dans la memoire de l'ami
                self.setMemoryUInt(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, friend[3][0], friend[3][1]), i )
                
            elif me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  friend[2] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and  ( me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
			or distance(friend[2][0], friend[2][1], me[0][0], me[0][1]) >= FighterDistanceLoin() ):
                # Enregistrer la position
                self.setMemoryFloat(1, compress_position(friend[2][0], friend[2][1]) )
                # Effacer la cible dans la memoire de l'ami
                self.setMemoryUInt(2, compress_position2(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID, friend[3][0], friend[3][1]), i )
            # Mettre a jour mon "Me"
            me = getMyFighterMemory(self)


    # DEBUT : CONSTRUCTION CONVOI
    friend_pos = ennemy_pos = (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID)
    taille_escadron = 0
    # Recherche cible si je n'en ai pas.
    if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
    and me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) :
        Counter = 1
        # Chercher 1 Fighter en route pour la guerre
        for i in n:
            if isinstance(i, aiwar.Fighter) \
            and self.isFriend(i) \
            and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() \
            and ennemy_pos == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                if readFriendMemory(Counter) :
                    Counter += 1
                    friend = getFriendFighterMemory(self, i)
                    if friend[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                        # Enregister ennemi
                        if ennemy_pos == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
                            ennemy_pos = friend[0]
                            friend_pos = i.pos()
                            ennemy_type = friend[2][0]
                            ennemy_nb = friend[2][1]
    
    
    # Compter l'escouade potentielle en route
    cpt=1
    if friend_pos != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        for i in n:
            if isinstance(i, aiwar.Fighter) and self.isFriend(i):
                if show_log(CONST_LOG_ERROR):
                    self.log( "++++++Ennemy cpt="+ str(int(cpt)) +" ... f(x,y)=("+ str(int(friend_pos[0])) +","+ str(int(friend_pos[1])) +") ... i(x,y)=("+ str(int(i.pos()[0])) +","+ str(int(i.pos()[1])) +") ... me(x,y)=("+ str(int(int(self.pos()[0]))) +","+ str(int(int(self.pos()[1]))) +") ... Ennemy(x,y)=("+ str(int(ennemy_pos[0])) +","+ str(int(ennemy_pos[1])) +")" )
                
                cpt +=1
                log=""
                
                if isinstance(i, aiwar.Fighter) and self.isFriend(i):
                    log +="  Fighter and Friend = TRUE"
                else:
                    log +="  Fighter and Friend = false"
                if distance(i.pos()[0], i.pos()[1], friend_pos[0], friend_pos[1]) <= aiwar.COMMUNICATION_RADIUS():
                    log +=" / Fighter dans le rayon de Friend = TRUE"
                else:
                    log +=" / Fighter dans le rayon de Friend = false"
                if distance(i.pos()[0], i.pos()[1], ennemy_pos[0], ennemy_pos[1]) < self.distanceTo(ennemy_pos) :
                    log +=" / Fighter plus proche de ennemi que moi = TRUE"
                else:
                    log +=" / Fighter plus proche de ennemi que moi = false"
                if log != "":
                    if show_log(CONST_LOG_INFO):
                        self.log( log )
                    
            if isinstance(i, aiwar.Fighter) \
            and self.isFriend(i) \
            and distance(i.pos()[0], i.pos()[1], ennemy_pos[0], ennemy_pos[1]) < self.distanceTo(ennemy_pos) :
# Pas de contrainte sur la capacité de parler à l'ami
#            and distance(i.pos()[0], i.pos()[1], friend_pos[0], friend_pos[1]) <= aiwar.COMMUNICATION_RADIUS() \
                taille_escadron += 1
                if show_log(CONST_LOG_ERROR):
                    self.log( "++++++Ennemy taille_escadron="+ str(int(taille_escadron)) )
                
        # S'il reste de la place dans le convoi punitif, enregistrer la cible
        if taille_escadron < FighterNombreMaxGuerrierParCible() \
        and ennemy_pos != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
            # Enregister ennemi
            if me[0] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and distance(ennemy_pos[0], ennemy_pos[1], me[1][0], me[1][1]) >= FighterDistanceLoin():
                # Enregistrer la position
                self.setMemoryFloat( 0, compress_position(ennemy_pos[0], ennemy_pos[1]) )
                # Enregistrer les infos CIBLE
                self.setMemoryUInt(2, compress_fighter_infos(ennemy_type, ennemy_nb, me[2][2], me[2][3], me[2][4], me[2][5]) )
                if show_log(CONST_LOG_ERROR):
                    self.log( "++++++Ennemy Fighter [0]: x="+ str(int(ennemy_pos[0])) +" ; y="+ str(int(ennemy_pos[1])) +" ; T_escadron="+ str(int(taille_escadron)) )
            elif me[1] == (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) \
            and distance(ennemy_pos[0], ennemy_pos[1], me[0][0], me[0][1]) >= FighterDistanceLoin():
                # Enregistrer la position
                self.setMemoryFloat(1, compress_position(ennemy_pos[0], ennemy_pos[1]) )
                # Enregistrer les infos CIBLE
                self.setMemoryUInt(2, compress_fighter_infos(ennemy_type, ennemy_nb, me[2][2], me[2][3], me[2][4], me[2][5]) )
                if show_log(CONST_LOG_ERROR):
                    self.log( "++++++Ennemy Fighter [1]: x="+ str(int(ennemy_pos[0])) +" ; y="+ str(int(ennemy_pos[1])) +" ; T_escadron="+ str(int(taille_escadron)) )
            # Mettre a jour mon "Me"
            me = getMyFighterMemory(self)
    # FIN : CONSTRUCTION CONVOI


	if show_log(CONST_LOG_INFO) or show_log(CONST_LOG_JOKE):
		self.log( "Fighter : ====== PHASE 3 ======" )
    # ====== PHASE 3 ======
    # Initialiser ma cible
    
    # S'il ne reste plus de missiles, rentrer a la maison
    if self.missiles() <= 0:
        # Plus de missiles, retourner a la base
        self.rotateTo(me[3])
        self.move()
        if show_log(CONST_LOG_WARNING):
            self.log( "++Ennemy: Plus de munitions, retour BASE." )
            
    elif me[0] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo(me[0]) > FighterDistanceProche():
            self.rotateTo(me[0])
            self.move()
            if show_log(CONST_LOG_WARNING):
                self.log( "++Ennemy: Go cible 1.("+ str(int(me[0][0])) +", "+ str(int(me[0][1])) +")" )
        # Proche de la cible avec des missiles => elle n'est plus là. Passer à la cible suivante.
        else:
            # Effacer la cible 1
            self.setMemoryFloat(0, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
            self.setMemoryUInt(2, compress_fighter_infos(CONST_ENNEMY_VOID, 0, 0, me[2][3], me[2][4], me[2][5]) )
            
    elif me[1] != (CONST_ENNEMY_VOID, CONST_ENNEMY_VOID):
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo(me[1]) > FighterDistanceProche():
            self.rotateTo(me[1])
            self.move()
            if show_log(CONST_LOG_WARNING):
                self.log( "++Ennemy: Go cible 2.("+ str(int(me[1][0])) +", "+ str(int(me[1][1])) +")" )
        # Proche de la cible avec des missiles => elle n'est plus là. Passer à la cible suivante.
        else:
            # Effacer la cible 2
            self.setMemoryFloat(1, compress_position(CONST_ENNEMY_VOID, CONST_ENNEMY_VOID) )
            self.setMemoryUInt(2, compress_fighter_infos(me[2][0], me[2][1], me[2][2], CONST_ENNEMY_VOID, 0, 0) )


