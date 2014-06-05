# -*- coding: utf-8 -*-

# Exemple of AI implementation #

import aiwar
import random
import math

CONST_LOG_INFO = 1
CONST_LOG_DEBUG = 2
CONST_LOG_WARNING = 3
CONST_LOG_ERROR = 4
CONST_LOG_CRITICAL = 5

CONST_LOG_SHIP_STATE = 10
CONST_LOG_MEMORY = 1
CONST_LOG_JOKE = 100
CONST_LOG_VOID = 200
CONST_LOG_DEBUG_TMP = 300

CONST_LOG = CONST_LOG_JOKE

CONST_NB_COMMUNICATION_MAX = 10

### To Do list
###   * Reinitialiser le cycle de la base (lie au compteur et la proportion de budget minier/fighter) si "CPT" grand et "Banque" excessive largement (seuils à definir).


### handlers: MANDATORY ###


def play_base(self):
    log(CONST_LOG_SHIP_STATE, "***********************", self)
    log(CONST_LOG_SHIP_STATE, "*********BASE  ({}, {})  **********".format(int(self.pos()[0]), int(self.pos()[1])), self)
    log(CONST_LOG_SHIP_STATE, "Vie: {}".format(self.life()), self)
    log(CONST_LOG_SHIP_STATE, "MineralStorage: {}".format(self.mineralStorage()), self)
    
    # Memoire base
    logMyBaseMemory(self)
    me = extractMyBaseMemory(self)

    n = self.neighbours()

    # Definir la position de la BASE
    px,py = basePos = self.pos()

    #Incrementer le nombre de rounds
    me['info']['nbr'] += 1
    compressMyBaseMemory(self, me)
    # Mettre a jour mon "Me"
    me = extractMyBaseMemory(self)
    
    
    # Faire vieillir la memoire des mineraux
    if me['info']['nbr']<20 :
        FighterBuildRate = 0
        MiningBuildRate = 100
        FuelReserve = 0
    elif me['info']['nbr']<200 :
        FighterBuildRate = 0
        MiningBuildRate = 100
        FuelReserve = 0
    elif me['info']['nbr']<400 :
        FighterBuildRate = 10
        MiningBuildRate = 90
        FuelReserve = 1000
    elif me['info']['nbr']<800 :
        FighterBuildRate = 40
        MiningBuildRate = 60
        FuelReserve = 4000
    elif me['info']['nbr']<1200 :
        FighterBuildRate = 50
        MiningBuildRate = 30
        FuelReserve = 12000
    else :
        FighterBuildRate = 70
        MiningBuildRate = 30
        FuelReserve = 24000
    log(CONST_LOG_DEBUG, "FighterBuildRate=" + str(int(FighterBuildRate)) +" - MiningBuildRate="+str(int(MiningBuildRate))+" - FuelReserve="+str(int(FuelReserve)), self)
    
    # Effacer la cible ennemi1 avec les rounds
    if me['ennemy1']['t'] != CONST_ENNEMY_VOID and me['ennemy1']['nbc'] == me['ennemy1']['nbv'] and me['info']['nbr']%10 == 0:
        # Decrementer la cible
        me['ennemy1']['nbc'] -= 1
        me['ennemy1']['nbv'] -= me['ennemy1']['nbc']
        # Si la cible est nulle, l'effacer !
        if me['ennemy1']['nbc'] == 0:
            me['x'] = CONST_VOID_POSITION
            me['y'] = CONST_VOID_POSITION
            me['t'] = CONST_ENNEMY_VOID
        compressMyBaseMemory(self, me)
            
    # S'il n'y a plus d'argent dans les caisses, arreter le traitement
    if self.mineralStorage() < aiwar.BASE_MISSILE_PRICE() and self.mineralStorage() < aiwar.FIGHTER_MOVE_CONSO() and self.mineralStorage() < aiwar.MININGSHIP_MOVE_CONSO():
        return


    # S'il existe un ennemi1 localise, creer un guerrier
    log(CONST_LOG_DEBUG, "Creation FIGHTER : me['ennemy1']['t']=" + logEnnemyTypeCible(me['ennemy1']['t']) + " - self.mineralStorage()="+str(int(self.mineralStorage())) +" - FuelReserve="+str(int(FuelReserve))+" - aiwar.BASE_FIGHTER_PRICE()="+str(int(aiwar.BASE_FIGHTER_PRICE())), self)
    if self.mineralStorage() > FuelReserve : 
        log(CONST_LOG_DEBUG, "Creation FIGHTER : FighterBuildRate="+str(int(FighterBuildRate))+" - 100-FighterBuildRate+1+int(10*FIGHTER_PRICE()/(mineralStorage()-FuelReserve))=" + str(int(100-FighterBuildRate+1+int(10*aiwar.BASE_FIGHTER_PRICE()/(self.mineralStorage()-FuelReserve)))), self)
    if me['ennemy1']['t'] != CONST_ENNEMY_VOID and me['ennemy1']['nbc'] > me['ennemy1']['nbv']\
    and (self.mineralStorage() - FuelReserve) > aiwar.BASE_FIGHTER_PRICE() \
    and True \
    or True \
    and self.mineralStorage() > FuelReserve \
    and random.randint( 1, 100-FighterBuildRate+1+int(10*aiwar.BASE_FIGHTER_PRICE()/(self.mineralStorage()-FuelReserve)) ) == 1 \
    or self.mineralStorage() >= (0.9*aiwar.BASE_MAX_MINERAL_STORAGE()) \
    and random.randint(0,1)==0 :
        log(CONST_LOG_WARNING, "Je fabrique un guerrier", self)
        self.createFighter()
    

    # remissile/refuel friend ships
    MiningCouter = 0
    for i in n:
        if ( isinstance(i, aiwar.Fighter) or isinstance(i, aiwar.MiningShip) ) \
        and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() :
            if isinstance(i, aiwar.Fighter) :
                friend = extractFighterMemory(self, i)
                # Donner pour les Fighter qui ont une VRAIE cible
                if friend['ennemy1']['t'] != CONST_ENNEMY_VOID or friend['ennemy2']['t'] != CONST_ENNEMY_VOID:
                    if self.distanceTo(i) <= aiwar.BASE_GIVE_MISSILE_RADIUS():
                        log(CONST_LOG_DEBUG, "je fais le plein de MISSILES de mon ami (FIGHTER)", self)
                        self.giveMissiles(aiwar.FIGHTER_MAX_MISSILE(), i)
                    if self.distanceTo(i) <= aiwar.BASE_REFUEL_RADIUS():
                        log(CONST_LOG_DEBUG, "je fais le plein de mon ami (FIGHTER)", self)
                        self.refuel(aiwar.FIGHTER_MAX_FUEL(), i)
                
            if isinstance(i, aiwar.MiningShip) :
                friend = extractMiningShipMemory(self, i)
                # Donner pour les MiningShip qui ont une VRAIE cible OU s'il n'y a pas de cible en memoire de la BASE pour les X premiers
                if friend['mineral1']['q'] == CONST_MINERAL_NORMAL or friend['mineral2']['q'] == CONST_MINERAL_NORMAL \
                or me['mineral1']['q'] != CONST_MINERAL_NORMAL \
                    and me['mineral2']['q'] != CONST_MINERAL_NORMAL \
                    and me['mineral3']['q'] != CONST_MINERAL_NORMAL \
                    and MiningCouter < CONST_NB_COMMUNICATION_MAX :
                    if self.distanceTo(i) <= aiwar.BASE_REFUEL_RADIUS():
                        log(CONST_LOG_DEBUG, "je fais le plein de mon ami (MINING)", self)
                        self.refuel(aiwar.MININGSHIP_START_FUEL(), i)
                        MiningCouter += 1

    # create new MiningShip
    if True and (self.mineralStorage() - FuelReserve) > (2*aiwar.BASE_FIGHTER_PRICE()) \
    and random.randint( 1, 100 - MiningBuildRate + 1+ int(4*aiwar.BASE_MININGSHIP_PRICE()/self.mineralStorage()) ) == 1 \
    or self.mineralStorage() >= (0.9*aiwar.BASE_MAX_MINERAL_STORAGE()) \
    and random.randint(0,1)==0 :
        log(CONST_LOG_DEBUG, "Je fabrique un mineur", self)
        self.createMiningShip()

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







def play_miningship(self):
    log(CONST_LOG_SHIP_STATE, "***********************", self)
    log(CONST_LOG_SHIP_STATE, "*******MININGSHIP  ({}, {})  ******".format(int(self.pos()[0]), int(self.pos()[1])), self)
    log(CONST_LOG_SHIP_STATE, "Vie: {}".format(self.life()), self)
    log(CONST_LOG_SHIP_STATE, "MineralStorage: {}".format(self.mineralStorage()), self)
    log(CONST_LOG_SHIP_STATE, "Fuel: {}".format(self.fuel()), self)

    n = getSortedNeighbours(self)
    
    logMyMiningShipMemory(self)
    me = extractMyMiningShipMemory(self)

    # Effacer memoire si fuel vide (Limite les interference et le traitement)
    if self.fuel() < aiwar.MININGSHIP_MOVE_CONSO():
        eraseMyMiningShipMemory(self)
        return

    
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
    basePos = (me['base']['x'], me['base']['y'])
    if basePos != (CONST_VOID_POSITION, CONST_VOID_POSITION):
        log(CONST_LOG_DEBUG, "je connais ma base", self)
        baseConnue = True
    else:
        for i in n:
            if isinstance(i, aiwar.Base) and self.isFriend(i):
                px, py = basePos = i.pos()
                me['base']['x'] = px
                me['base']['y'] = py
                compressMyMiningShipMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyMiningShipMemory(self)
                baseConnue = True
                break


    # recherche de minerais visible
    log(CONST_LOG_DEBUG, "recherche de minerais visible : debut", self)
    for i in n:
        if isinstance(i, aiwar.Mineral):
            mpx,mpy = i.pos()
            x,y = mePos = self.pos()
            minPos = {'x': mpx, 'y': mpy}
            
            # Enregistrer la position du minerai
            setMyMineralMemory(self, me, minPos)
    logMyMiningShipMemory(self, CONST_LOG_DEBUG)
    log(CONST_LOG_DEBUG, "recherche de minerais visible : fin", self)
    
    
    
    # NE PLUS FUIR, SAUF LES MISSILES !!
    ennemiEnVue = False
    
    # Remettre a jour la liste en fonction de l'importance de ce qui est visible.
    log(CONST_LOG_DEBUG, "Remettre a jour la liste en fonction de l'importance de ce qui est visible : debut", self)
    Counter = 0
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            Counter += 1
            if me['ennemy1']['t'] == CONST_ENNEMY_VOID \
            or me['ennemy1']['t'] == CONST_ENNEMY_MININGSHIP and me['ennemy1']['nbc'] <= Counter :
                px,py = ennemiPos = i.pos()
                me['ennemy1']['x'] = px
                me['ennemy1']['y'] = py
                me['ennemy1']['t'] = CONST_ENNEMY_MININGSHIP # CONST_ENNEMY_FIGHTER / CONST_ENNEMY_BASE 
                me['ennemy1']['nbc'] = Counter
                me['ennemy1']['nbv'] = 0
                compressMyMiningShipMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyMiningShipMemory(self)
                log(CONST_LOG_DEBUG, "++Ennemy MININGSHIP ("+str(int(Counter))+") spoted: distance="+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)), self)
            

    Counter = 0
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            Counter += 1
            if me['ennemy1']['t'] == CONST_ENNEMY_VOID \
            or me['ennemy1']['t'] == CONST_ENNEMY_MININGSHIP \
            or me['ennemy1']['t'] == CONST_ENNEMY_FIGHTER and me['ennemy1']['nbc'] <= Counter :
                px,py = ennemiPos = i.pos()
                me['ennemy1']['x'] = px
                me['ennemy1']['y'] = py
                me['ennemy1']['t'] = CONST_ENNEMY_FIGHTER # CONST_ENNEMY_MININGSHIP / CONST_ENNEMY_BASE 
                me['ennemy1']['nbc'] = Counter
                me['ennemy1']['nbv'] = 0
                compressMyMiningShipMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyMiningShipMemory(self)
                log(CONST_LOG_DEBUG, "++++Ennemy FIGHTER spoted: "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)), self)


    for i in n:
        if isinstance(i, aiwar.Missile):
            if (isMissileSpotedMe(self, i) == True):
                px,py = ennemiPos = i.pos()
                log(CONST_LOG_WARNING, "++++ MISSILE ON MY WAY !! Distance= "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)), self)
                # Fuite du missile si nous sommes ciblés
                ennemiEnVue = True
            else:
                log(CONST_LOG_WARNING, "++++ MISSILE away and I'm safe ! Distance= "+ str(int(self.distanceTo(i))), self)


    Counter = 0
    for i in n:
        if isinstance(i, aiwar.Base) and not self.isFriend(i):
            Counter += 1
            if me['ennemy1']['t'] == CONST_ENNEMY_VOID \
            or me['ennemy1']['t'] == CONST_ENNEMY_MININGSHIP \
            or me['ennemy1']['t'] == CONST_ENNEMY_FIGHTER \
            or me['ennemy1']['t'] == CONST_ENNEMY_BASE and me['ennemy1']['nbc'] <= Counter :
                px,py = ennemiPos = i.pos()
                me['ennemy1']['x'] = px
                me['ennemy1']['y'] = py
                me['ennemy1']['t'] = CONST_ENNEMY_BASE # CONST_ENNEMY_MININGSHIP / CONST_ENNEMY_FIGHTER 
                me['ennemy1']['nbc'] = Counter
                me['ennemy1']['nbv'] = 0
                compressMyMiningShipMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyMiningShipMemory(self)
                # La vue de la BASE ENNEMIE provoque la fuite à la base pour avertir tout le monde
                ennemiEnVue = True
                log(CONST_LOG_DEBUG, "++++++Ennemy BASE spoted: "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)), self)

    logMyMiningShipMemory(self, CONST_LOG_DEBUG)
    log(CONST_LOG_DEBUG, "Remettre a jour la liste en fonction de l'importance de ce qui est visible : fin", self)


    ############################
    # COMMUNIQUER : friend FIGHTER
    log(CONST_LOG_DEBUG, "Copier memoire Fighter : debut", self)
    Counter = 0
    for i in n:
        if isinstance(i, aiwar.Fighter) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            Counter += 1
            if readFriendMemory(Counter ,CONST_FRIEND_MININGSHIP, CONST_FRIEND_FIGHTER) :
                # Me.0 n'est jamais copié d'un Fighter
                
                # Effacer son "Ennemy" s'il n'est pas vide ou ne designe pas une BASE...
                # S'il est dans un FIGHTER croisé...
                # Qui m'a croisé et qui s'éloigne de moi (donc plus proche de l'ennemi)...
                # Et dont l'ennemi est le meme avec une precision de MININGSHIP_DETECTION_RADIUS()/4
                if me['ennemy1']['t'] != CONST_ENNEMY_VOID and me['ennemy1']['t'] != CONST_ENNEMY_BASE:
                    friend = extractFighterMemory(self, i)
                    if ( (friend['ennemy1']['x'], friend['ennemy1']['y']) != (CONST_VOID_POSITION, CONST_VOID_POSITION) \
                    and friend['ennemy1']['t'] != CONST_ENNEMY_VOID \
                    and friend['info']['active'] == True \
                    and in_circle( friend['ennemy1']['x'], friend['ennemy1']['y'], MiningDistanceProche(), me['ennemy1']['x'], me['ennemy1']['y']) \
                    and not ship_isBack(self, i) \
                    or (friend['ennemy2']['x'], friend['ennemy2']['y']) != (CONST_VOID_POSITION, CONST_VOID_POSITION) \
                    and friend['ennemy2']['t'] != CONST_ENNEMY_VOID \
                    and friend['info']['active'] == True \
                    and in_circle( friend['ennemy2']['x'], friend['ennemy2']['y'], MiningDistanceProche(), me['ennemy1']['x'], me['ennemy1']['y']) ) \
                    and not ship_isBack(self, i):
                        # Effacer l'ennemi de ma memoire
                        me['ennemy1'] = eraseEnnemy(self, me['ennemy1'], False)
                        compressMyMiningShipMemory(self, me)
                        # Mettre a jour mon "Me"
                        me = extractMyMiningShipMemory(self)
    logMyMiningShipMemory(self, CONST_LOG_DEBUG)
    log(CONST_LOG_DEBUG, "Copier memoire Fighter : fin", self)


    ############################
    # COMMUNIQUER : friend Base
    log(CONST_LOG_DEBUG, "Copier memoire Base : debut", self)
    Counter = 0
    for i in n:
        if isinstance(i, aiwar.Base) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            Counter += 1
            if readFriendMemory(Counter ,CONST_FRIEND_MININGSHIP, CONST_FRIEND_BASE) :
                friend = extractBaseMemory(self, i)
                
                # Tester les memoires
                log(CONST_LOG_DEBUG, "Copier memoire Base['mineral1'] : me['mineral1']", self)
                me['mineral1'] = getFriendMineralToMiningShip(self, me['mineral1'], me['mineral2'], friend['mineral1'])
                
                log(CONST_LOG_DEBUG, "Copier memoire Base['mineral2'] : me['mineral1']", self)
                me['mineral1'] = getFriendMineralToMiningShip(self, me['mineral1'], me['mineral2'], friend['mineral2'])
                
                log(CONST_LOG_DEBUG, "Copier memoire Base['mineral3'] : me['mineral1']", self)
                me['mineral1'] = getFriendMineralToMiningShip(self, me['mineral1'], me['mineral2'], friend['mineral3'])
                
                log(CONST_LOG_DEBUG, "Copier memoire Base['mineral1'] : me['mineral2']", self)
                me['mineral2'] = getFriendMineralToMiningShip(self, me['mineral2'], me['mineral1'], friend['mineral1'])
                
                log(CONST_LOG_DEBUG, "Copier memoire Base['mineral2'] : me['mineral2']", self)
                me['mineral2'] = getFriendMineralToMiningShip(self, me['mineral2'], me['mineral1'], friend['mineral2'])
                
                log(CONST_LOG_DEBUG, "Copier memoire Base['mineral3'] : me['mineral2']", self)
                me['mineral2'] = getFriendMineralToMiningShip(self, me['mineral2'], me['mineral1'], friend['mineral3'])
                
                compressMyMiningShipMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyMiningShipMemory(self)



                # Charger une cible aléatoire si je n'ai aucune cible en memoire 
                # et que je viens de croiser la base
    #            if  (me['mineral1']['x'], me['mineral1']['y']) == (CONST_VOID_POSITION, CONST_VOID_POSITION) \
    #            and (me['mineral2']['x'], me['mineral2']['y']) == (CONST_VOID_POSITION, CONST_VOID_POSITION):
    #                target = random_target( (me['base']['x'], me['base']['y']), cpt_friend_mining )
    #                log(CONST_LOG_DEBUG, "Creer cible aléatoire : ("+ str(int(target['x']))+", "+str(int(target['y']))+")", self)
    #                me['mineral1']['x'] = target['x']
    #                me['mineral1']['y'] = target['y']
    #                me['mineral1']['q'] = CONST_MINERAL_NORMAL
    #                me['mineral1']['i'] = False
    #                compressMyMiningShipMemory(self, me)
    #                # Mettre a jour mon "Me"
    #                me = extractMyMiningShipMemory(self)


                # Effacer son "Ennemy" s'il n'est pas vide ou ne designe pas une BASE...
                # S'il est dans la BASE croisée...
                # Et dont l'ennemi est le meme avec une precision de COMMUNICATION_RADIUS()/2
                if me['ennemy1']['t'] != CONST_ENNEMY_VOID and me['ennemy1']['t'] != CONST_ENNEMY_BASE:
                    if friend['ennemy1']['t'] != CONST_ENNEMY_VOID \
                    and in_circle( friend['ennemy1']['x'], friend['ennemy1']['y'], MiningDistanceProche(), me['ennemy1']['x'], me['ennemy1']['y']) :
                    #and in_circle( friend['ennemy1']['x'], friend['ennemy1']['y'], MiningDistanceProche(), me['ennemy1']['x'], me['ennemy1']['y']) \
                    #or (friend['ennemy2']['x'], friend['ennemy2']['y']) != (CONST_VOID_POSITION, CONST_VOID_POSITION) \
                    #and friend['ennemy2']['t'] != CONST_ENNEMY_VOID \
                    #and friend['info']['active'] == True \
                    #and in_circle( friend['ennemy2']['x'], friend['ennemy2']['y'], MiningDistanceProche(), me['ennemy1']['x'], me['ennemy1']['y']) ) :
                        # Effacer l'ennemi de ma memoire
                        me['ennemy1'] = eraseEnnemy(self, me['ennemy1'], False)
                        compressMyMiningShipMemory(self, me)
                        # Mettre a jour mon "Me"
                        me = extractMyMiningShipMemory(self)
                # Inscrire son "Ennemy" dans la BASE croisée s'il n'y etait pas encore
                # Me.2
                if me['ennemy1']['t'] != CONST_ENNEMY_VOID:
                    setEnnemyBaseMemory(self, me['ennemy1'], i)
    logMyMiningShipMemory(self, CONST_LOG_DEBUG)
    log(CONST_LOG_DEBUG, "Copier memoire Base : fin", self)


    ############################
    # COMMUNIQUER : friend MiningShip
    log(CONST_LOG_DEBUG, "Copier memoire MiningShip : debut", self)
    Counter = 0
    for i in n:
        if isinstance(i, aiwar.MiningShip) and self.isFriend(i) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS():
            Counter += 1
            if readFriendMemory(Counter ,CONST_FRIEND_MININGSHIP, CONST_FRIEND_MININGSHIP) :
                friend = extractMiningShipMemory(self, i)
                
                # Tester les memoires
                log(CONST_LOG_DEBUG, "Copier memoire MiningShip['mineral1'] : me['mineral1']", self)
                me['mineral1'] = getFriendMineralToMiningShip(self, me['mineral1'], me['mineral2'], friend['mineral1'])
                
                log(CONST_LOG_DEBUG, "Copier memoire MiningShip['mineral2'] : me['mineral1']", self)
                me['mineral1'] = getFriendMineralToMiningShip(self, me['mineral1'], me['mineral2'], friend['mineral2'])

                log(CONST_LOG_DEBUG, "Copier memoire MiningShip['mineral1'] : me['mineral2']", self)
                me['mineral2'] = getFriendMineralToMiningShip(self, me['mineral2'], me['mineral1'], friend['mineral1'])
                
                log(CONST_LOG_DEBUG, "Copier memoire MiningShip['mineral2'] : me['mineral2']", self)
                me['mineral2'] = getFriendMineralToMiningShip(self, me['mineral2'], me['mineral1'], friend['mineral2'])
                
                compressMyMiningShipMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyMiningShipMemory(self)

                # Me.2 (vide)
                if me['ennemy1']['t'] == CONST_ENNEMY_VOID:
                    if friend['ennemy1']['t'] != CONST_ENNEMY_VOID \
                    and self.distanceTo( (me['base']['x'], me['base']['y']) ) > MiningDistanceCopierEnnemi():
                        log(CONST_LOG_DEBUG, "Copier memoire Minier : Me['ennemy1']", self)
                        log(CONST_LOG_WARNING, "Poto minier (Copy ENNEMY)", self)
                        log(CONST_LOG_WARNING, "++Ennemy MININGSHIP (copy): x="+ str(friend['ennemy1']['x']) +", y="+ str(friend['ennemy1']['y']), self)
                        me['ennemy1'] = dict(friend['ennemy1'])
                        compressMyMiningShipMemory(self, me)
                        # Mettre a jour mon "Me"
                        me = extractMyMiningShipMemory(self)
                
                # Copier la position de BASE si absente de la memoire
                log(CONST_LOG_DEBUG, "Copier memoire MiningShip['base'] : me['base']", self)
                me['base'] = getFriendBasePosition(self, me['base'], friend['base'])
    logMyMiningShipMemory(self, CONST_LOG_DEBUG)
    log(CONST_LOG_DEBUG, "Copier memoire MiningShip : fin", self)
            

    # Rechercher si un mineraux est visible
    minerauxEnVue = False
    for i in n:
        if isinstance(i, aiwar.Mineral):
            minerauxEnVue = True

    # Effacer les mineraux connus qui ont disparus
    log(CONST_LOG_DEBUG, "Effacer mineraux connu : debut", self)
    me['mineral1'] = eraseMineral(self, me['mineral1'], minerauxEnVue)
    me['mineral2'] = eraseMineral(self, me['mineral2'], minerauxEnVue)
    compressMyMiningShipMemory(self, me)
    # Mettre a jour mon "Me"
    me = extractMyMiningShipMemory(self)

    # Decaller le minerai 2 en 1 si le 1 est vide et le 2 ne l'est pas
    if  (me['mineral1']['q'] == CONST_MINERAL_EMPTY or me['mineral1']['q'] == CONST_MINERAL_VOID) \
    and ( me['mineral2']['q'] != CONST_MINERAL_EMPTY and me['mineral2']['q'] != CONST_MINERAL_VOID  ) \
    and self.distanceTo( (me['mineral2']['x'], me['mineral2']['y']) ) < MiningDistanceEffacerMinerai() \
    and minerauxEnVue == True :
        log(CONST_LOG_DEBUG, "Je valide minerai 2 en minerai 1. Youpi !", self)
        # Decaller minerais "espere" en "AVERE"
        tmp = me['mineral1']
        me['mineral1'] = me['mineral2']
        me['mineral2'] = tmp
        compressMyMiningShipMemory(self, me)
        # Mettre a jour mon "Me"
        me = extractMyMiningShipMemory(self)
    logMyMiningShipMemory(self, CONST_LOG_DEBUG)
    log(CONST_LOG_DEBUG, "Effacer mineraux connu : fin", self)



    # Charger une cible aléatoire si je n'ai rien en 'minerai1' et 'minerai2'
    # Et que je ne retourne pas à la base rapporter des mineraux
    if self.mineralStorage() == 0 \
    and ( me['mineral1']['q'] == CONST_MINERAL_EMPTY 
        or me['mineral1']['q'] == CONST_MINERAL_VOID ) \
    and ( me['mineral2']['q'] == CONST_MINERAL_EMPTY 
        or me['mineral2']['q'] == CONST_MINERAL_VOID ) :
        # "Distance max" pour permettre un aller retour à la cible + retour à la base
        distance_max = 0 #(MiningshipInstantRange(self) - 2*self.distanceTo( (me['base']['x'], me['base']['y']) ) - 100 ) / 2
        target = random_target( me['base'], cpt_friend_mining, distance_max )
        log(CONST_LOG_DEBUG, "Creer cible aleatoire : ("+ str(int(target['x']))+", "+str(int(target['y']))+") distance_max="+str(int(distance_max)), self)
        # Calcul nouvelle cible aleatoire
        if random.randint( 1, 2 ) == 1:
            me['mineral1']['x'] = target['x']
            me['mineral1']['y'] = target['y']
            me['mineral1']['q'] = CONST_MINERAL_RANDOM
            me['mineral1']['i'] = False
        else:
            me['mineral2']['x'] = target['x']
            me['mineral2']['y'] = target['y']
            me['mineral2']['q'] = CONST_MINERAL_RANDOM
            me['mineral2']['i'] = False
        compressMyMiningShipMemory(self, me)
        # Mettre a jour mon "Me"
        me = extractMyMiningShipMemory(self)
        logMyMiningShipMemory(self, CONST_LOG_DEBUG)


    # Pas assez de fuel pour rejoindre la cible
    minerauxTropLoin = False
    log(CONST_LOG_DEBUG, "InstantRange = "+ str(int(MiningshipInstantRange(self))) +" - Cible1 = "+ str(int(self.distanceTo( (me['mineral1']['x'], me['mineral1']['y']) )*11/10)) +" - Cible2 = "+ str(int(self.distanceTo( (me['mineral2']['x'], me['mineral2']['y']) )*11/10)), self)

    if me['mineral1']['q'] != CONST_MINERAL_EMPTY \
    and me['mineral1']['q'] != CONST_MINERAL_VOID \
    and MiningshipInstantRange(self) < (self.distanceTo( (me['mineral1']['x'], me['mineral1']['y']) )*11/10 + distance_4_args(me['mineral1']['x'], me['mineral1']['y'], me['base']['x'], me['base']['y']) ) :
        log(CONST_LOG_WARNING, "Le minerai 1 est trop loin", self)
        minerauxTropLoin = True

    if ( me['mineral1']['q'] != CONST_MINERAL_EMPTY \
        or me['mineral1']['q'] != CONST_MINERAL_VOID ) \
    and me['mineral2']['q'] != CONST_MINERAL_EMPTY \
    and me['mineral2']['q'] != CONST_MINERAL_VOID \
    and MiningshipInstantRange(self) < (self.distanceTo( (me['mineral2']['x'], me['mineral2']['y']) )*11/10 + distance_4_args(me['mineral2']['x'], me['mineral2']['y'], me['base']['x'], me['base']['y']) ) :
        log(CONST_LOG_WARNING, "Le minerai 2 est trop loin", self)
        minerauxTropLoin = True


    # Une base oblige a rentrer la declarer
    if me['ennemy1']['t'] == CONST_ENNEMY_BASE :
        ennemiEnVue = True


    # rentrer a la base ?
    log(CONST_LOG_DEBUG, "rentrer a la base ? : debut", self)
    # Rentrer à la base si plus de mine en vue avec cargaison presente
    # OU Si cargaison pleine
    # OU si fuel juste suffisant pour rentrer
    # OU ennemi en vue
    if self.mineralStorage() > 0 and minerauxEnVue == False \
        or self.mineralStorage() == aiwar.MININGSHIP_MAX_MINERAL_STORAGE() \
        or MiningshipInstantRange(self) < (self.distanceTo(basePos)*11/10) \
        or minerauxTropLoin \
        or ennemiEnVue \
        or (me['mineral1']['x'], me['mineral1']['y']) == (CONST_VOID_POSITION, CONST_VOID_POSITION) \
            and (me['mineral2']['x'], me['mineral2']['y']) == (CONST_VOID_POSITION, CONST_VOID_POSITION) :
        if baseConnue or ennemiEnVue:
            if baseConnue or minerauxEnVue == False:
                log(CONST_LOG_WARNING, "je rentre a la base", self)
            if ennemiEnVue:
                # Si ennemi en vue, retourner a la base ou chercher un fighter proche 
                # (mais il faut pouvoir le cibler durablement et l'abandonner s'il n'a pas de fuel)
                # ANNULE TANT QUE LE FUEL et LA CIBLE N'EST PAS DURABLE.

                # ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU
                # ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU
                # ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU
                # ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU
                # ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU
                # ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU ADU
                log(CONST_LOG_WARNING, "je cherche peut-etre un FIGHTER (à coder !!!)", self)

            self.rotateTo(basePos)
            # Se deplacer tant qu'on est loin de la cible
            if self.distanceTo(basePos) > (aiwar.MININGSHIP_MINING_RADIUS()):
                self.move()

            # base en vue et assez proche pour donner le minerai ?
            for i in n:
                if isinstance(i, aiwar.Base) and self.isFriend(i):
                    if self.distanceTo(i) < aiwar.MININGSHIP_MINING_RADIUS():
                        # Deposer les mineraux
                        if self.mineralStorage() > 0 :
                            log(CONST_LOG_WARNING, "je donne mon minerai a ma base", self)
                            self.pushMineral(i, self.mineralStorage())
                        # Enregistrer dans la base les mineraux
                        if me['mineral1']['q'] != CONST_MINERAL_VOID :
                            setMineralBaseMemory(self, me['mineral1'], i)
                    break
            if baseConnue or minerauxEnVue == False:
                log(CONST_LOG_DEBUG, "Fin de traitement MiningShip (rapporter minerais).", self)
            if ennemiEnVue:
                log(CONST_LOG_DEBUG, "Fin de traitement MiningShip (sauve qui peut !).", self)
            danceMiningShip(self)
            return
        else:
            log(CONST_LOG_WARNING, "je cherche ma base", self)
            random_move(self)
            log(CONST_LOG_DEBUG, "Fin de traitement MiningShip (recherche base).", self)
            danceMiningShip(self)
            return
    log(CONST_LOG_DEBUG, "rentrer a la base ? : fin", self)



    # recherche de minerais visible
    log(CONST_LOG_DEBUG, "Go minerais visible : debut", self)
    for i in n:
        if isinstance(i, aiwar.Mineral):
            log(CONST_LOG_WARNING, "je vais au minerai visible", self)
            mpx,mpy = i.pos()
            x,y = mePos = self.pos()
            minPos = {'x': mpx, 'y': mpy}
            
            self.rotateTo( (minPos['x'], minPos['y']) )
            # Se deplacer tant qu'on est loin de la cible
            if self.distanceTo( (minPos['x'], minPos['y']) ) > aiwar.MININGSHIP_MINING_RADIUS():
                self.move()
            if self.distanceTo(i) < aiwar.MININGSHIP_MINING_RADIUS():
                log(CONST_LOG_WARNING, "je mine", self)
                self.extract(i)
            logMyMiningShipMemory(self, CONST_LOG_DEBUG)
            log(CONST_LOG_DEBUG, "Fin de traitement MiningShip (mineral visible).", self)
            danceMiningShip(self)
            return
    log(CONST_LOG_DEBUG, "Go minerais visible : fin", self)


    # recherche de minerai connu
    log(CONST_LOG_DEBUG, "recherche de minerais connu : debut", self)
    moveToMineral(self, me['mineral1'])
    moveToMineral(self, me['mineral2'])
    log(CONST_LOG_DEBUG, "recherche de minerais connu : fin", self)


    danceMiningShip(self)
    log(CONST_LOG_DEBUG, "Fin de traitement MiningShip.", self)





def play_fighter(self):
    log(CONST_LOG_SHIP_STATE, "***********************", self)
    log(CONST_LOG_SHIP_STATE, "********FIGHTER  ({}, {})  ********".format(int(self.pos()[0]), int(self.pos()[1])), self)
    log(CONST_LOG_SHIP_STATE, "Vie: {}".format(self.life()), self)
    log(CONST_LOG_SHIP_STATE, "Fuel: {}".format(self.fuel()), self)
    log(CONST_LOG_SHIP_STATE, "Missiles: {}".format(self.missiles()), self)

    n = self.neighbours()

    logMyFighterMemory(self)
    me = extractMyFighterMemory(self)


# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# ADU ADU ADU
# Limiter les echanges entre FIGHTERs pres de la base.
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

    # ====== PHASE 0 ======
    log(CONST_LOG_WARNING, "=== Phase 0 : debut", self)
    if self.fuel()<aiwar.FIGHTER_MOVE_CONSO():
        eraseMyMiningShipMemory(self)
        if self.missiles() <= 0 :
            return
            # Fin de vie du guerrier (plus de missile et plus de fuel)

    
    # ====== PHASE 1 ======
    # Ordre des cibles :
    #   0 - Missile 
    #   1 - BASE
    #   2 - FIGHTER
    #   3 - MININGSHIP
    log(CONST_LOG_WARNING, "=== Phase 1 : debut", self)
    under_attack=False
    for i in n:
        if isinstance(i, aiwar.Missile):
            if (isMissileSpotedMe(self, i) == True):
                px, py = missilePos = i.pos()
                under_attack=True
                log(CONST_LOG_WARNING, "++++ MISSILE ON MY WAY !! Distance= "+ str(int(self.distanceTo(i))) +"   x="+ str(int(px)) +"   y="+ str(int(py)), self)
                # On evite les missiles Sauf si la base est menacee (avec une marge) : dist(missile,base) > dist(missile, moi)
                if (distance_4_args(px, py, me['base']['x'], me['base']['y']) -20) > distance_4_args(px, py, self.pos()[0], self.pos()[1]) :
                    log(CONST_LOG_WARNING, "++++ Fuir missile : dist(missile,base)-20="+ str(int(distance_4_args(px, py, me['base']['x'], me['base']['y']) -20)) + " > dist(missile, moi)=" + str(int(distance_4_args(px, py, self.pos()[0], self.pos()[1]))), self)
                    # Faire face au missile
                    self.rotateTo(i)
                    # Quand le missile est loin, fuir avec l'angle min/max.
                    # Quand il s'approche, fuir avec zero degres pour aller dans la meme direction que le missile et se maintenir a distance.
                    signe=-1
                    if random.randint(0,1)==0:
                        signe=1
                    angle_facteur = 1 - ( MissileRange()-distance_4_args(px, py, self.pos()[0], self.pos()[1]) ) / ( MissileRange() )
                    angle_min=int( 70* angle_facteur )
                    angle_max=int( 90* angle_facteur )
                    log(CONST_LOG_WARNING, "++++ angle_min= "+ str(int(angle_min)) + "++++ angle_max= "+ str(int(angle_max)), self)
                    self.rotateOf(180+signe*random.randint(angle_min, angle_max))
                    self.move()
            else:
                log(CONST_LOG_WARNING, "++++ MISSILE away and I'm safe ! Distance= "+ str(int(self.distanceTo(i))), self)

    Counter = 0
    for i in n:
        if isinstance(i, aiwar.Base) and not self.isFriend(i):
            log(CONST_LOG_WARNING, "++++++Ennemy BASE: "+ str(self.distanceTo(i)), self)
            Counter += 1
            px,py = Pos = i.pos()
            # Decaller l'ennemi 0 en 1 si l'emplacement 0 etait utilisé
            if me['ennemy1']['t'] != CONST_ENNEMY_VOID \
            and distance_4_args(px, py, me['ennemy1']['x'], me['ennemy1']['y']) >= FighterDistanceLoin():
                me['ennemy2'] = dict(me['ennemy1'])

            if me['ennemy1']['t'] == CONST_ENNEMY_VOID \
            or me['ennemy1']['t'] == CONST_ENNEMY_MININGSHIP \
            or me['ennemy1']['t'] == CONST_ENNEMY_FIGHTER \
            or me['ennemy1']['t'] == CONST_ENNEMY_BASE and me['ennemy1']['nbc'] <= Counter :
                log(CONST_LOG_DEBUG, "++++++Ennemy BASE: Enregistrement de la cible", self)
                me['ennemy1']['x'] = px
                me['ennemy1']['y'] = py
                me['ennemy1']['t'] = CONST_ENNEMY_BASE
                me['ennemy1']['nbc'] = Counter
                me['ennemy1']['nbv'] = 0
                compressMyFighterMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyFighterMemory(self)

            if self.missiles() > 0 and MissileRange() > self.distanceTo(i) :
                log(CONST_LOG_WARNING, "++++++Ennemy BASE: BOOM dans ta face !", self)
                # Tirer sans condition sur la BASE
                self.launchMissile(i)
            else:
                log(CONST_LOG_WARNING, "++++++Ennemy BASE: Plus de munitions/Trop loin ! :'(", self)


    cpt_ship = 0
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            cpt_ship +=1
    Counter = 0
    for i in n:
        if isinstance(i, aiwar.Fighter) and not self.isFriend(i):
            log(CONST_LOG_WARNING, "++++++Ennemy FIGHTER: "+ str(self.distanceTo(i)), self)
            Counter += 1
            px,py = Pos = i.pos()
            # Si aucune cible (1 ou 2) n'avait cette cible en portee => ENREGISTRER
            # Si la cible 1 n'est pas une BASE !!
            if ( me['ennemy1']['t'] == CONST_ENNEMY_VOID 
                or distance_4_args(px, py, me['ennemy1']['x'], me['ennemy1']['y']) >= FighterDistanceLoin() ) \
            and ( me['ennemy2']['t'] == CONST_ENNEMY_VOID 
                or distance_4_args(px, py, me['ennemy2']['x'], me['ennemy2']['y']) >= FighterDistanceLoin() ) \
            and me['ennemy1']['t'] != CONST_ENNEMY_BASE:
                # Decaller l'ennemi 0 en 1 si l'emplacement 0 etait plein
                if me['ennemy1']['t'] != CONST_ENNEMY_VOID :
                    me['ennemy2'] = dict(me['ennemy1'])

                if me['ennemy1']['t'] == CONST_ENNEMY_VOID \
                or me['ennemy1']['t'] == CONST_ENNEMY_MININGSHIP \
                or me['ennemy1']['t'] == CONST_ENNEMY_FIGHTER and me['ennemy1']['nbc'] <= Counter :
                    # Enregistrer la position pour le poursuivre
                    log(CONST_LOG_DEBUG, "++++Ennemy FIGHTER: Enregistrement de la cible", self)
                    me['ennemy1']['x'] = px
                    me['ennemy1']['y'] = py
                    me['ennemy1']['t'] = CONST_ENNEMY_FIGHTER
                    me['ennemy1']['nbc'] = Counter
                    me['ennemy1']['nbv'] = 0
                    compressMyFighterMemory(self, me)
                    # Mettre a jour mon "Me"
                    me = extractMyFighterMemory(self)

            if self.missiles() > 0 and canFighterEscapeMissile(self.distanceTo(i))==True:
                log(CONST_LOG_WARNING, "++++Ennemy FIGHTER: Attrape ca !", self)
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
                    log(CONST_LOG_WARNING, "***************** BOUGEAGE PARASITE **************", self)
                    log(CONST_LOG_JOKE, " La danse de la mort !! Ha ha ha ! :D", self)
            else:
                log(CONST_LOG_WARNING, "++++Ennemy FIGHTER: Plus de munitions/Trop loin ! :'(", self)


    cpt_ship = 0
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            cpt_ship +=1
    Counter = 0
    for i in n:
        if isinstance(i, aiwar.MiningShip) and not self.isFriend(i):
            log(CONST_LOG_WARNING, "++Ennemy MININGSHIP: "+ str(self.distanceTo(i)), self)
            Counter += 1
            px,py = Pos = i.pos()
            # Si aucune cible (1 ou 2) n'avait cette cible en portee => ENREGISTRER
            # Si la cible 1 n'est pas une BASE ou FIGHTER !!
            if me['ennemy1']['t'] == CONST_ENNEMY_VOID \
            or (me['ennemy1']['t'] == CONST_ENNEMY_MININGSHIP \
                and distance_4_args(px, py, me['ennemy1']['x'], me['ennemy1']['y']) >= FighterDistanceLoin() \
                and ( me['ennemy2']['t'] != CONST_ENNEMY_VOID \
                    or distance_4_args(px, py, me['ennemy2']['x'], me['ennemy2']['y']) >= FighterDistanceLoin() ) ) :
                # Decaller l'ennemi 0 en 1 si l'emplacement 0 etait plein
                if me['ennemy1']['t'] != CONST_ENNEMY_VOID :
                    me['ennemy2'] = dict(me['ennemy1'])

                if me['ennemy1']['t'] == CONST_ENNEMY_VOID \
                or (me['ennemy1']['t'] == CONST_ENNEMY_MININGSHIP and me['ennemy1']['nbc'] <= Counter) :
                    # Enregistrer la position pour le poursuivre
                    log(CONST_LOG_DEBUG, "++Ennemy MININGSHIP: Enregistrement de la cible", self)
                    me['ennemy1']['x'] = px
                    me['ennemy1']['y'] = py
                    me['ennemy1']['t'] = CONST_ENNEMY_MININGSHIP
                    me['ennemy1']['nbc'] = Counter
                    me['ennemy1']['nbv'] = 0
                    compressMyFighterMemory(self, me)
                    # Mettre a jour mon "Me"
                    me = extractMyFighterMemory(self)

            if self.missiles() > 0 and canMiningshipEscapeMissile(self.distanceTo(i))==True:
                log(CONST_LOG_WARNING, "++Ennemy MININGSHIP: N'y vois rien de personnel, je fais mon job.", self)
                # Tirer 1 MiningShip sur 4
                if random.randint(1, 4*cpt_ship) == 1:
                    self.launchMissile(i)
            else:
                log(CONST_LOG_WARNING, "++Ennemy MININGSHIP: Plus de munitions/Trop loin ! :'(", self)

    # Si plus de fuel : tirer a vue et ne plus traiter la memoire
    if self.fuel()<aiwar.FIGHTER_MOVE_CONSO():
        return



    # ====== PHASE 2 ======
    # S'il existe un ennemi1 localise dans BASE, je go le combattre
    # Chercher une cible dans mon entourage
    log(CONST_LOG_WARNING, "=== Phase 2 : debut", self)
    log(CONST_LOG_DEBUG, "=== === Recuperer cible de la BASE", self)
    Counter = 0
    for i in n:
        # Recuperer cible de la BASE
        if isinstance(i, aiwar.Base) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() and self.isFriend(i):
            Counter += 1
            if readFriendMemory(Counter ,CONST_FRIEND_FIGHTER, CONST_FRIEND_BASE) :
                # Enregistrer position BASE
                if (me['base']['x'], me['base']['y']) == (CONST_VOID_POSITION, CONST_VOID_POSITION):
                    px,py = basePos = i.pos()
                    me['base']['x'] = px
                    me['base']['y'] = py
                    compressMyFighterMemory(self, me)
                    # Mettre a jour mon "Me"
                    me = extractMyFighterMemory(self)
                
                friend = extractBaseMemory(self, i)
                
                # Tester les memoires
                log(CONST_LOG_DEBUG, "Copier memoire Base['ennemy1'] : me['ennemy1']/me['ennemy2']", self)
                me['ennemy1'] = getFriendEnnemyToFighter(self, me['ennemy1'], me['ennemy2'], i)
                me['ennemy2'] = getFriendEnnemyToFighter(self, me['ennemy2'], me['ennemy1'], i)

                compressMyFighterMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyFighterMemory(self)
    logMyFighterMemory(self, CONST_LOG_DEBUG)



    Counter = 0
    log(CONST_LOG_DEBUG, "=== === Recuperer cible du MININGSHIP", self)
    for i in n:
        # Recuperer cible du MININGSHIP
        if isinstance(i, aiwar.MiningShip) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() and self.isFriend(i):
            Counter += 1
            if readFriendMemory(Counter ,CONST_FRIEND_FIGHTER, CONST_FRIEND_MININGSHIP) :
                friend = extractMiningShipMemory(self, i)
                
                # Tester les memoires
                log(CONST_LOG_DEBUG, "Copier memoire MiningShip['ennemy1'] : me['ennemy1']/me['ennemy2']", self)
                me['ennemy1'] = getFriendEnnemyToFighter(self, me['ennemy1'], me['ennemy2'], i)
                me['ennemy2'] = getFriendEnnemyToFighter(self, me['ennemy2'], me['ennemy1'], i)

                compressMyFighterMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyFighterMemory(self)
    logMyFighterMemory(self, CONST_LOG_DEBUG)



    Counter = 0
    log(CONST_LOG_DEBUG, "=== === Recuperer cible du FIGHTER", self)
    for i in n:
        # Recuperer cible du FIGHTER
        if isinstance(i, aiwar.Fighter) and self.distanceTo(i) <= aiwar.COMMUNICATION_RADIUS() and self.isFriend(i):
            Counter += 1
            if readFriendMemory(Counter ,CONST_FRIEND_FIGHTER, CONST_FRIEND_FIGHTER) :
                friend = extractFighterMemory(self, i)
                
                # Tester les memoires
                log(CONST_LOG_DEBUG, "Copier memoire Fighter['ennemy1'] : me['ennemy1']/me['ennemy2']", self)
                me['ennemy1'] = getFriendEnnemyToFighter(self, me['ennemy1'], me['ennemy2'], i)
                me['ennemy2'] = getFriendEnnemyToFighter(self, me['ennemy2'], me['ennemy1'], i)

                compressMyFighterMemory(self, me)
                # Mettre a jour mon "Me"
                me = extractMyFighterMemory(self)
    logMyFighterMemory(self, CONST_LOG_DEBUG)



    # ====== PHASE 3 ======
    # Initialiser ma cible
    log(CONST_LOG_WARNING, "=== Phase 3 : debut", self)
    
    # S'il ne reste plus de missiles, rentrer a la maison
    if self.missiles() <= 0:
        # Plus de missiles, retourner a la base
        self.rotateTo( (me['base']['x'], me['base']['y']) )
        self.move()
        log(CONST_LOG_WARNING, "++Ennemy: Plus de munitions, retour BASE.", self)
        danceFighter(self)
        return
            
    me['ennemy1'] = moveToEnnemy(self, me['ennemy1'])
    me['ennemy2'] = moveToEnnemy(self, me['ennemy2'])
    compressMyFighterMemory(self, me)
    # Mettre a jour mon "Me"
    me = extractMyFighterMemory(self)
    logMyFighterMemory(self, CONST_LOG_WARNING)
    
    danceFighter(self)

################# FIN ########################
################# FIN ########################
################# FIN ########################
################# FIN ########################





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


# From leguims : Special Effects !
def danceMiningShip(self):
    self.rotateTo( self.pos() )
    self.rotateOf( int(self.pos()[0]+self.pos()[1]) % 360 )
    blinkColor(self)
    return

def danceFighter(self):
    self.rotateTo( self.pos() )
    self.rotateOf( int(self.pos()[0]+self.pos()[1]) % 360 )
    blinkColor(self)
    return

def blinkColor(self):
    if (int(self.pos()[0]+self.pos()[1]) % 3) == 0 :
        self.state(aiwar.LIGHT)
    elif (int(self.pos()[0]+self.pos()[1]) % 3) == 1 :
        self.state(aiwar.DEFAULT)
    else:
        self.state(aiwar.DARK)
    return

# *** Fighter Memory ***

# Plan memoire FIGHTER : 
# 0 : ENNEMY 1 : X (12 bits) / Y (12 bits) / Type cible 1 (2 bits) / Nb Cible 1 (3 bits) / Nb voisins vers cible 1 (3 bits) [RESTE 0 bit]
# 1 : ENNEMY 2 : X (12 bits) / Y (12 bits) / Type cible 1 (2 bits) / Nb Cible 1 (3 bits) / Nb voisins vers cible 1 (3 bits) [RESTE 0 bit]
# 2 : INFO : EMPTY / b0:Vaisseau actif (1 bit) [RESTE 31 bits]
# 3 : BASE POSITION : X (16 bits) / Y (16 bits)  [RESTE 0 bit]

def eraseMyFighterMemory(self):
    log(CONST_LOG_MEMORY, "*** eraseMyFighterMemory :", self)
    
    mem1 = {'x': CONST_VOID_POSITION, 'y': CONST_VOID_POSITION, 't': CONST_ENNEMY_VOID, 'nbc': 0, 'nbv': 0}
    mem2 = {'active': False}
    mem3 = {'x': CONST_VOID_POSITION, 'y': CONST_VOID_POSITION}
    memory = {'ennemy1': mem1,'ennemy2': mem1,'info': mem2,'base': mem3 }
    
    compressMyFighterMemory(self, memory)
    return

def compressMyFighterMemory(self, memory):
    log(CONST_LOG_MEMORY, "*** compressMyFighterMemory :", self)
    mem0 = compressEnnemyPosition(self, memory['ennemy1'], memory['base']['x'], memory['base']['y'])
    mem1 = compressEnnemyPosition(self, memory['ennemy2'], memory['base']['x'], memory['base']['y'])
    mem2 = compressFighterInfo(self, memory['info'])
    mem3 = compress_position_32bits(memory['base']['x'], memory['base']['y'])
    log(CONST_LOG_MEMORY, "   mem0="+ str(hex(mem0)), self)
    log(CONST_LOG_MEMORY, "   mem1="+ str(hex(mem1)), self)
    log(CONST_LOG_MEMORY, "   mem2="+ str(hex(mem2)), self)
    log(CONST_LOG_MEMORY, "   mem3="+ str(hex(mem3)), self)
    self.setMemoryUInt(0, mem0)
    self.setMemoryUInt(1, mem1)
    self.setMemoryUInt(2, mem2)
    self.setMemoryUInt(3, mem3)
    return

def extractMyFighterMemory(self):
    log(CONST_LOG_MEMORY, "*** extractMyFighterMemory :", self)
    mem0 = self.getMemoryUInt(0)
    mem1 = self.getMemoryUInt(1)
    mem2 = self.getMemoryUInt(2)
    mem3 = self.getMemoryUInt(3)
    base = extract_position_32bits(mem3)
    me0 = extractEnnemyPosition(self, mem0, base['x'], base['y'])
    me1 = extractEnnemyPosition(self, mem1, base['x'], base['y'])
    me2 = extractFighterInfo(self, mem2, base['x'], base['y'])
    log(CONST_LOG_MEMORY, "   Ennemy1=("+str(int(me0['x']))+", "+str(int(me0['y']))+") Type="+logEnnemyTypeCible(me0['t'])+" NbCible="+str(int(me0['nbc']))+" NbVoisins="+str(int(me0['nbv'])), self)
    log(CONST_LOG_MEMORY, "   Ennemy2=("+str(int(me1['x']))+", "+str(int(me1['y']))+") Type="+logEnnemyTypeCible(me1['t'])+" NbCible="+str(int(me1['nbc']))+" NbVoisins="+str(int(me1['nbv'])), self)
    log(CONST_LOG_MEMORY, "   Actif="+str(int(me2['active'])), self)
    log(CONST_LOG_MEMORY, "   Base=("+str(int(base['x']))+", "+str(int(base['y']))+")", self)
    tmp = {'ennemy1': me0, 'ennemy2': me1, 'info': me2, 'base': base}
    return tmp

def logMyFighterMemory(self, log_level=CONST_LOG_SHIP_STATE):
    me = extractMyFighterMemory(self)
    log(log_level, "*** Fighter memory :", self)
    log(log_level, "   Ennemy1=("+str(int(me['ennemy1']['x']))+", "+str(int(me['ennemy1']['y']))+") Type="+logEnnemyTypeCible(me['ennemy1']['t'])+" NbCible="+str(int(me['ennemy1']['nbc']))+" NbVoisins="+str(int(me['ennemy1']['nbv'])), self)
    log(log_level, "   Ennemy2=("+str(int(me['ennemy2']['x']))+", "+str(int(me['ennemy2']['y']))+") Type="+logEnnemyTypeCible(me['ennemy2']['t'])+" NbCible="+str(int(me['ennemy2']['nbc']))+" NbVoisins="+str(int(me['ennemy2']['nbv'])), self)
    log(log_level, "   Actif="+str(int(me['info']['active'])), self)
    log(log_level, "   Base=("+str(int(me['base']['x']))+", "+str(int(me['base']['y']))+")", self)
    return

def compressFighterMemory(self, friend, memory):
    log(CONST_LOG_MEMORY, "*** compressFighterMemory(friend) :", self)
    mem0 = compressEnnemyPosition(self, memory['ennemy1'], memory['base']['x'], memory['base']['y'])
    mem1 = compressEnnemyPosition(self, memory['ennemy2'], memory['base']['x'], memory['base']['y'])
    mem2 = compressFighterInfo(self, memory['info'])
    mem3 = compress_position_32bits(memory['base']['x'], memory['base']['y'])
    log(CONST_LOG_MEMORY, "   mem0="+ str(hex(mem0)), self)
    log(CONST_LOG_MEMORY, "   mem1="+ str(hex(mem1)), self)
    log(CONST_LOG_MEMORY, "   mem2="+ str(hex(mem2)), self)
    log(CONST_LOG_MEMORY, "   mem3="+ str(hex(mem3)), self)
    self.setMemoryUInt(0, mem0, friend)
    self.setMemoryUInt(1, mem1, friend)
    self.setMemoryUInt(2, mem2, friend)
    self.setMemoryUInt(3, mem3, friend)
    return

def extractFighterMemory(self, friend):
    log(CONST_LOG_MEMORY, "*** extractFighterMemory(friend) :", self)
    mem0 = self.getMemoryUInt(0, friend)
    mem1 = self.getMemoryUInt(1, friend)
    mem2 = self.getMemoryUInt(2, friend)
    mem3 = self.getMemoryUInt(3, friend)
    base = extract_position_32bits(mem3)
    me0 = extractEnnemyPosition(self, mem0, base['x'], base['y'])
    me1 = extractEnnemyPosition(self, mem1, base['x'], base['y'])
    me2 = extractFighterInfo(self, mem2, base['x'], base['y'])
    log(CONST_LOG_MEMORY, "   Ennemy1=("+str(int(me0['x']))+", "+str(int(me0['y']))+") Type="+logEnnemyTypeCible(me0['t'])+" NbCible="+str(int(me0['nbc']))+" NbVoisins="+str(int(me0['nbv'])), self)
    log(CONST_LOG_MEMORY, "   Ennemy2=("+str(int(me1['x']))+", "+str(int(me1['y']))+") Type="+logEnnemyTypeCible(me1['t'])+" NbCible="+str(int(me1['nbc']))+" NbVoisins="+str(int(me1['nbv'])), self)
    log(CONST_LOG_MEMORY, "   Actif="+str(int(me2['active'])), self)
    log(CONST_LOG_MEMORY, "   Base=("+str(int(base['x']))+", "+str(int(base['y']))+")", self)
    tmp = {'ennemy1': me0, 'ennemy2': me1, 'info': me2, 'base': base}
    return tmp

# *** MiningShip Memory ***

# Plan memoire MININGSHIP : 
# 0 : MINERAL 1 : X (12 bits) / Y (12 bits) / MineralQuantity (2bits) / Informer Fighter (1bit) / [RESTE 5 bits]
# 1 : MINERAL 2 : X (12 bits) / Y (12 bits) / MineralQuantity (2bits) / Informer Fighter (1bit) / [RESTE 5 bits]
# 2 : ENNEMY 1 : X (12 bits) / Y (12 bits) / Type cible 1 (2 bits) / Nb Cible 1 (3 bits) / Nb voisins vers cible 1 (3 bits) [RESTE 0 bit]
# 3 : BASE POSITION : X (16 bits) / Y (16 bits)  [RESTE 0 bit]

def eraseMyMiningShipMemory(self):
    log(CONST_LOG_MEMORY, "*** eraseMyMiningShipMemory :", self)
    
    mem1 = {'x': CONST_VOID_POSITION, 'y': CONST_VOID_POSITION, 'q': CONST_MINERAL_VOID, 'i': False}
    mem2 = {'x': CONST_VOID_POSITION, 'y': CONST_VOID_POSITION, 't': CONST_ENNEMY_VOID, 'nbc': 0, 'nbv': 0}
    mem3 = {'x': CONST_VOID_POSITION, 'y': CONST_VOID_POSITION}
    memory = {'mineral1': mem1, 'mineral2':mem1, 'ennemy1':mem2, 'base': mem3}
    
    compressMyMiningShipMemory(self, memory)
    return

def compressMyMiningShipMemory(self, memory):
    log(CONST_LOG_MEMORY, "*** compressMyMiningShipMemory :", self)
    mem0 = compressMineralPosition(self, memory['mineral1'], memory['base']['x'], memory['base']['y'])
    mem1 = compressMineralPosition(self, memory['mineral2'], memory['base']['x'], memory['base']['y'])
    mem2 = compressEnnemyPosition(self, memory['ennemy1'], memory['base']['x'], memory['base']['y'])
    mem3 = compress_position_32bits(memory['base']['x'], memory['base']['y'])
    log(CONST_LOG_MEMORY, "   mem0="+ str(hex(mem0)), self)
    log(CONST_LOG_MEMORY, "   mem1="+ str(hex(mem1)), self)
    log(CONST_LOG_MEMORY, "   mem2="+ str(hex(mem2)), self)
    log(CONST_LOG_MEMORY, "   mem3="+ str(hex(mem3)), self)
    self.setMemoryUInt(0, mem0)
    self.setMemoryUInt(1, mem1)
    self.setMemoryUInt(2, mem2)
    self.setMemoryUInt(3, mem3)
    return

def extractMyMiningShipMemory(self):
    log(CONST_LOG_MEMORY, "*** extractMyMiningShipMemory :", self)
    mem0 = self.getMemoryUInt(0)
    mem1 = self.getMemoryUInt(1)
    mem2 = self.getMemoryUInt(2)
    mem3 = self.getMemoryUInt(3)
    base = extract_position_32bits(mem3)
    me0 = extractMineralPosition(self, mem0, base['x'], base['y'])
    me1 = extractMineralPosition(self, mem1, base['x'], base['y'])
    me2 = extractEnnemyPosition(self, mem2, base['x'], base['y'])
    log(CONST_LOG_MEMORY, "   Mineral1=("+str(int(me0['x']))+", "+str(int(me0['y']))+") Quantity="+logMineralQuantity(me0['q'])+" Info fighter="+str(int(me0['i'])), self)
    log(CONST_LOG_MEMORY, "   Mineral2=("+str(int(me1['x']))+", "+str(int(me1['y']))+") Quantity="+logMineralQuantity(me1['q'])+" Info fighter="+str(int(me1['i'])), self)
    log(CONST_LOG_MEMORY, "   Ennemy1=("+str(int(me2['x']))+", "+str(int(me2['y']))+") Type="+str(int(me2['t']))+" NbCible="+str(int(me2['nbc']))+" NbVoisins="+str(int(me2['nbv'])), self)
    log(CONST_LOG_MEMORY, "   Base=("+str(int(base['x']))+", "+str(int(base['y']))+")", self)
    tmp = {'mineral1': me0, 'mineral2': me1, 'ennemy1': me2, 'base': base}
    return tmp

def logMyMiningShipMemory(self, log_level=CONST_LOG_SHIP_STATE):
    me = extractMyMiningShipMemory(self)
    log(log_level, "*** MiningShip memory :", self)
    log(log_level, "   Mineral1=("+str(int(me['mineral1']['x']))+", "+str(int(me['mineral1']['y']))+") Quantity="+logMineralQuantity(me['mineral1']['q'])+" Info fighter="+str(int(me['mineral1']['i'])), self)
    log(log_level, "   Mineral2=("+str(int(me['mineral2']['x']))+", "+str(int(me['mineral2']['y']))+") Quantity="+logMineralQuantity(me['mineral2']['q'])+" Info fighter="+str(int(me['mineral2']['i'])), self)
    log(log_level, "   Ennemy1=("+str(int(me['ennemy1']['x']))+", "+str(int(me['ennemy1']['y']))+") Type="+logEnnemyTypeCible(me['ennemy1']['t'])+" NbCible="+str(int(me['ennemy1']['nbc']))+" NbVoisins="+str(int(me['ennemy1']['nbv'])), self)
    log(log_level, "   Base=("+str(int(me['base']['x']))+", "+str(int(me['base']['y']))+")", self)
    return

def compressMiningShipMemory(self, friend, memory):
    log(CONST_LOG_MEMORY, "*** compressMiningShipMemory(friend) :", self)
    mem0 = compressMineralPosition(self, memory['mineral1'], memory['base']['x'], memory['base']['y'])
    mem1 = compressMineralPosition(self, memory['mineral2'], memory['base']['x'], memory['base']['y'])
    mem2 = compressEnnemyPosition(self, memory['ennemy1'], memory['base']['x'], memory['base']['y'])
    mem3 = compress_position_32bits(memory['base']['x'], memory['base']['y'])
    log(CONST_LOG_MEMORY, "   mem0="+ str(hex(mem0)), self)
    log(CONST_LOG_MEMORY, "   mem1="+ str(hex(mem1)), self)
    log(CONST_LOG_MEMORY, "   mem2="+ str(hex(mem2)), self)
    log(CONST_LOG_MEMORY, "   mem3="+ str(hex(mem3)), self)
    self.setMemoryUInt(0, mem0, friend)
    self.setMemoryUInt(1, mem1, friend)
    self.setMemoryUInt(2, mem2, friend)
    self.setMemoryUInt(3, mem3, friend)
    return

def extractMiningShipMemory(self, friend):
    log(CONST_LOG_MEMORY, "*** extractMiningShipMemory(friend) :", self)
    mem0 = self.getMemoryUInt(0, friend)
    mem1 = self.getMemoryUInt(1, friend)
    mem2 = self.getMemoryUInt(2, friend)
    mem3 = self.getMemoryUInt(3, friend)
    base = extract_position_32bits(mem3)
    me0 = extractMineralPosition(self, mem0, base['x'], base['y'])
    me1 = extractMineralPosition(self, mem1, base['x'], base['y'])
    me2 = extractEnnemyPosition(self, mem2, base['x'], base['y'])
    log(CONST_LOG_MEMORY, "   Mineral1=("+str(int(me0['x']))+", "+str(int(me0['y']))+") Quantity="+logMineralQuantity(me0['q'])+" Info fighter="+str(int(me0['i'])), self)
    log(CONST_LOG_MEMORY, "   Mineral2=("+str(int(me1['x']))+", "+str(int(me1['y']))+") Quantity="+logMineralQuantity(me1['q'])+" Info fighter="+str(int(me1['i'])), self)
    log(CONST_LOG_MEMORY, "   Ennemy1=("+str(int(me2['x']))+", "+str(int(me2['y']))+") Type="+logEnnemyTypeCible(me2['t'])+" NbCible="+str(int(me2['nbc']))+" NbVoisins="+str(int(me2['nbv'])), self)
    log(CONST_LOG_MEMORY, "   Base=("+str(int(base['x']))+", "+str(int(base['y']))+")", self)
    tmp = {'mineral1': me0, 'mineral2': me1, 'ennemy1': me2, 'base': base}
    return tmp

# *** Base Memory ***

# Plan memoire BASE : 
# 0 : ENNEMY 1 : X (12 bits) / Y (12 bits) / Type cible 1 (2 bits) / Nb Cible 1 (3 bits) / Nb voisins vers cible 1 (3 bits) [RESTE 0 bit]
# 1 : EMPTY [RESTE 32 bits]
# 2 : MINERAL 1 : X (12 bits) / Y (12 bits) / MineralQuantity (2bits) / Informer Fighter (1bit) / [RESTE 5 bits]
# 3 : MINERAL 2 : X (12 bits) / Y (12 bits) / MineralQuantity (2bits) / Informer Fighter (1bit) / [RESTE 5 bits]
# 4 : MINERAL 3 : X (12 bits) / Y (12 bits) / MineralQuantity (2bits) / Informer Fighter (1bit) / [RESTE 5 bits]
# 5 : INFO : Nb fighters (6bits) / Nb mining (6bits) / Nb round (12bits) [RESTE 8 bits]

def eraseMyBaseMemory(self):
    log(CONST_LOG_MEMORY, "*** eraseMyBaseMemory :", self)
    
    mem1 = {'x': CONST_VOID_POSITION, 'y': CONST_VOID_POSITION, 't': CONST_ENNEMY_VOID, 'nbc': 0, 'nbv': 0}
    mem2 = {'x': CONST_VOID_POSITION, 'y': CONST_VOID_POSITION, 'q': CONST_MINERAL_VOID, 'i': False}
    mem3 = {'nbf': 0, 'nbm': 0, 'nbr': 0}
    memory = {'ennemy1': mem1,'mineral1': mem2,'mineral2': mem2,'mineral3': mem2,'info': mem3 }
    
    compressMyBaseMemory(self, memory)
    return

def compressMyBaseMemory(self, memory):
    log(CONST_LOG_MEMORY, "*** compressMyMiningShipMemory :", self)
    xbase, ybase = self.pos()
    mem0 = compressEnnemyPosition(self, memory['ennemy1'], xbase, ybase)
    mem1 = 0 # "EMPTY"
    mem2 = compressMineralPosition(self, memory['mineral1'], xbase, ybase)
    mem3 = compressMineralPosition(self, memory['mineral2'], xbase, ybase)
    mem4 = compressMineralPosition(self, memory['mineral3'], xbase, ybase)
    mem5 = compressBaseInfo(self, memory['info'])
    log(CONST_LOG_MEMORY, "   mem0="+ str(hex(mem0)), self)
    log(CONST_LOG_MEMORY, "   mem1="+ str(hex(mem1)), self)
    log(CONST_LOG_MEMORY, "   mem2="+ str(hex(mem2)), self)
    log(CONST_LOG_MEMORY, "   mem3="+ str(hex(mem3)), self)
    log(CONST_LOG_MEMORY, "   mem4="+ str(hex(mem4)), self)
    log(CONST_LOG_MEMORY, "   mem5="+ str(hex(mem5)), self)
    self.setMemoryUInt(0, mem0)
    self.setMemoryUInt(1, mem1)
    self.setMemoryUInt(2, mem2)
    self.setMemoryUInt(3, mem3)
    self.setMemoryUInt(4, mem4)
    self.setMemoryUInt(5, mem5)
    return

def extractMyBaseMemory(self):
    log(CONST_LOG_MEMORY, "*** extractMyBaseMemory :", self)
    base = self.pos()
    mem0 = self.getMemoryUInt(0)
    mem1 = self.getMemoryUInt(1)
    mem2 = self.getMemoryUInt(2)
    mem3 = self.getMemoryUInt(3)
    mem4 = self.getMemoryUInt(4)
    mem5 = self.getMemoryUInt(5)
    me0 = extractEnnemyPosition(self, mem0, base[0], base[1])
    me1 = 0#adu, adu = extractAduAdu(self, mem1)
    me2 = extractMineralPosition(self, mem2, base[0], base[1])
    me3 = extractMineralPosition(self, mem3, base[0], base[1])
    me4 = extractMineralPosition(self, mem4, base[0], base[1])
    me5 = extractBaseInfo(self, mem5)
    log(CONST_LOG_MEMORY, "   Ennemy1=("+str(int(me0['x']))+", "+str(int(me0['y']))+") Type="+logEnnemyTypeCible(me0['t'])+" NbCible="+str(int(me0['nbc']))+" NbVoisins="+str(int(me0['nbv'])), self)
    # EMPTY MEM1
    log(CONST_LOG_MEMORY, "   Mineral1=("+str(int(me2['x']))+", "+str(int(me2['y']))+") Quantity="+logMineralQuantity(me2['q'])+" Info fighter="+str(int(me2['i'])), self)
    log(CONST_LOG_MEMORY, "   Mineral2=("+str(int(me3['x']))+", "+str(int(me3['y']))+") Quantity="+logMineralQuantity(me3['q'])+" Info fighter="+str(int(me3['i'])), self)
    log(CONST_LOG_MEMORY, "   Mineral3=("+str(int(me4['x']))+", "+str(int(me4['y']))+") Quantity="+logMineralQuantity(me4['q'])+" Info fighter="+str(int(me4['i'])), self)
    log(CONST_LOG_MEMORY, "   Nb fighters="+str(int(me5['nbf']))+" Nb miningship="+str(int(me5['nbm']))+" Nb round="+str(int(me5['nbr'])), self)
    tmp = {'ennemy1': me0, 'empty': me1, 'mineral1': me2, 'mineral2': me3, 'mineral3': me4, 'info': me5}
    return tmp

def logMyBaseMemory(self, log_level=CONST_LOG_SHIP_STATE):
    me = extractMyBaseMemory(self)
    xbase, ybase = self.pos()
    log(log_level, "*** Base memory :", self)
    log(log_level, "   Ennemy1=("+str(int(me['ennemy1']['x']))+", "+str(int(me['ennemy1']['y']))+") Type="+logEnnemyTypeCible(me['ennemy1']['t'])+" NbCible="+str(int(me['ennemy1']['nbc']))+" NbVoisins="+str(int(me['ennemy1']['nbv'])), self)
    # EMPTY MEM1
    log(log_level, "   Mineral1=("+str(int(me['mineral1']['x']))+", "+str(int(me['mineral1']['y']))+") Quantity="+logMineralQuantity(me['mineral1']['q'])+" Info fighter="+str(int(me['mineral1']['i'])), self)
    log(log_level, "   Mineral2=("+str(int(me['mineral2']['x']))+", "+str(int(me['mineral2']['y']))+") Quantity="+logMineralQuantity(me['mineral2']['q'])+" Info fighter="+str(int(me['mineral2']['i'])), self)
    log(log_level, "   Mineral3=("+str(int(me['mineral3']['x']))+", "+str(int(me['mineral3']['y']))+") Quantity="+logMineralQuantity(me['mineral3']['q'])+" Info fighter="+str(int(me['mineral3']['i'])), self)
    log(log_level, "   Nb fighters="+str(int(me['info']['nbf']))+" Nb miningship="+str(int(me['info']['nbm']))+" Nb round="+str(int(me['info']['nbr'])), self)
    return

def compressBaseMemory(self, friend, memory):
    log(CONST_LOG_MEMORY, "*** compressMiningShipMemory(friend) :", self)
    xbase, ybase = self.pos()
    mem0 = compressEnnemyPosition(self, memory['ennemy1'], xbase, ybase)
    mem1 = 0 # "EMPTY"
    mem2 = compressMineralPosition(self, memory['mineral1'], xbase, ybase)
    mem3 = compressMineralPosition(self, memory['mineral2'], xbase, ybase)
    mem4 = compressMineralPosition(self, memory['mineral3'], xbase, ybase)
    mem5 = compressBaseInfo(self, memory['info'])
    log(CONST_LOG_MEMORY, "   mem0="+ str(hex(mem0)), self)
    log(CONST_LOG_MEMORY, "   mem1="+ str(hex(mem1)), self)
    log(CONST_LOG_MEMORY, "   mem2="+ str(hex(mem2)), self)
    log(CONST_LOG_MEMORY, "   mem3="+ str(hex(mem3)), self)
    log(CONST_LOG_MEMORY, "   mem4="+ str(hex(mem4)), self)
    log(CONST_LOG_MEMORY, "   mem5="+ str(hex(mem5)), self)
    self.setMemoryUInt(0, mem0, friend)
    self.setMemoryUInt(1, mem1, friend)
    self.setMemoryUInt(2, mem2, friend)
    self.setMemoryUInt(3, mem3, friend)
    self.setMemoryUInt(4, mem4, friend)
    self.setMemoryUInt(5, mem5, friend)
    return

def extractBaseMemory(self, friend):
    log(CONST_LOG_MEMORY, "*** extractBaseMemory(friend) :", self)
    base = self.pos()
    mem0 = self.getMemoryUInt(0, friend)
    mem1 = self.getMemoryUInt(1, friend)
    mem2 = self.getMemoryUInt(2, friend)
    mem3 = self.getMemoryUInt(3, friend)
    mem4 = self.getMemoryUInt(4, friend)
    mem5 = self.getMemoryUInt(5, friend)
    me0 = extractEnnemyPosition(self, mem0, base[0], base[1])
    me1 = 0#adu, adu = extractAduAdu(self, mem1)
    me2 = extractMineralPosition(self, mem2, base[0], base[1])
    me3 = extractMineralPosition(self, mem3, base[0], base[1])
    me4 = extractMineralPosition(self, mem4, base[0], base[1])
    me5 = extractBaseInfo(self, mem5)
    log(CONST_LOG_MEMORY, "   Ennemy1=("+str(int(me0['x']))+", "+str(int(me0['y']))+") Type="+logEnnemyTypeCible(me0['t'])+" NbCible="+str(int(me0['nbc']))+" NbVoisins="+str(int(me0['nbv'])), self)
    # EMPTY MEM1
    log(CONST_LOG_MEMORY, "   Mineral1=("+str(int(me2['x']))+", "+str(int(me2['y']))+") Quantity="+logMineralQuantity(me2['q'])+" Info fighter="+str(int(me2['i'])), self)
    log(CONST_LOG_MEMORY, "   Mineral2=("+str(int(me3['x']))+", "+str(int(me3['y']))+") Quantity="+logMineralQuantity(me3['q'])+" Info fighter="+str(int(me3['i'])), self)
    log(CONST_LOG_MEMORY, "   Mineral3=("+str(int(me4['x']))+", "+str(int(me4['y']))+") Quantity="+logMineralQuantity(me4['q'])+" Info fighter="+str(int(me4['i'])), self)
    log(CONST_LOG_MEMORY, "   Nb fighters="+str(int(me5['nbf']))+" Nb miningship=("+str(int(me5['nbm']))+" Nb round=("+str(int(me5['nbr'])), self)
    tmp = {'ennemy1': me0, 'empty': me1, 'mineral1': me2, 'mineral2': me3, 'mineral3': me4, 'info': me5}
    return tmp

# Memory common management

CONST_VOID_POSITION         = 0
CONST_WORLD_SIZE_X          = aiwar.WORLD_SIZE_X()
CONST_WORLD_SIZE_Y          = aiwar.WORLD_SIZE_Y()

# Position sur 24 bits => 8 bits libres
def compress_position_24bits(x, y, bx, by):
    if x==CONST_VOID_POSITION and y==CONST_VOID_POSITION:
        return int(CONST_VOID_POSITION)
    nx=int(CONST_WORLD_SIZE_X + x-bx)
    ny=int(CONST_WORLD_SIZE_Y + y-by)
    tmp = int( (nx & 0xFFF)<<20 ) + int( (ny & 0xFFF)<<8 )
    return tmp

def extract_position_24bits(compressed, bx, by):
    if(compressed==CONST_VOID_POSITION):
        tmp = {'x': CONST_VOID_POSITION,'y': CONST_VOID_POSITION }
        return tmp
    nx=int(compressed)>>20 & 0xFFF
    ny=int(compressed)>>8  & 0xFFF
    x = int(nx - CONST_WORLD_SIZE_X + bx)
    y = int(ny - CONST_WORLD_SIZE_Y + by)
    tmp = {'x': x,'y': y }
    return tmp

# Position sur 32 bits => 0 bit libre
def compress_position_32bits(x, y):
    if x==CONST_VOID_POSITION and y==CONST_VOID_POSITION:
        return int(CONST_VOID_POSITION)
    nx=int(x)
    ny=int(y)
    tmp = int( (nx & 0xFFFF)<<16 ) + int( (ny & 0xFFFF)<<0 )
    return tmp

def extract_position_32bits(compressed):
    if(compressed==CONST_VOID_POSITION):
        tmp = {'x': CONST_VOID_POSITION,'y': CONST_VOID_POSITION }
        return tmp
    nx=int(compressed)>>16 & 0xFFFF
    ny=int(compressed)>>0  & 0xFFFF
    x = int(nx)
    y = int(ny)
    tmp = {'x': x,'y': y }
    return tmp


# 0 : ENNEMY 1 : X (12 bits) / Y (12 bits) / Type cible 1 (2 bits) / Nb Cible 1 (3 bits) / Nb voisins vers cible 1 (3 bits) [RESTE 0 bit]
def compressEnnemyPosition(self, ennemy, xbase, ybase):
    tmp = 0
    tmp = compress_position_24bits(ennemy['x'], ennemy['y'], xbase, ybase)
    tmp = tmp | ((ennemy['t'] & 0x3)<<6) | ((ennemy['nbc'] & 0x7)<<3) | (ennemy['nbv'] & 0x7) 
    return tmp

def extractEnnemyPosition(self, compressed, xbase, ybase):
    if(compressed==CONST_VOID_POSITION):
        tmp = {'x': CONST_VOID_POSITION,'y': CONST_VOID_POSITION,'t': 0,'nbc': 0,'nbv': 0 }
        return tmp
    pos = extract_position_24bits(compressed, xbase, ybase)
    t = (compressed >> 6) & 0x3
    nbc = (compressed >> 3) & 0x7
    nbv = compressed & 0x7
    
    tmp = {'x': pos['x'],'y': pos['y'],'t': t,'nbc': nbc,'nbv': nbv }
    return tmp


# 0 : MINERAL 1 : X (12 bits) / Y (12 bits) / MineralQuantity (2bits) / Informer Fighter (1bit) / [RESTE 5 bits]
def compressMineralPosition(self, mineral, xbase, ybase):
    tmp = 0
    tmp = compress_position_24bits(mineral['x'], mineral['y'], xbase, ybase)
    tmp = tmp | ((mineral['q'] & 0x3)<<6) | ((mineral['i'] & 0x1)<<5) 
    return tmp

def extractMineralPosition(self, compressed, xbase, ybase):
    if(compressed==CONST_VOID_POSITION):
        tmp = {'x': CONST_VOID_POSITION,'y': CONST_VOID_POSITION,'q': 0,'i': 0 }
        return tmp
    pos = extract_position_24bits(compressed, xbase, ybase)
    q = (compressed >> 6) & 0x3
    i = (compressed >> 5) & 0x1
    tmp = {'x': pos['x'],'y': pos['y'],'q': q,'i': i }
    return tmp


# 2 : INFO : EMPTY / b0:Vaisseau actif (1 bit) [RESTE 31 bits]
def compressFighterInfo(self, info):
    tmp = 0
    tmp = tmp | (info['active'] & 0x1) 
    return tmp

def extractFighterInfo(self, compressed, xbase, ybase):
    active = compressed & 0x1
    tmp = {'active': active}
    return tmp


# 5 : INFO : Nb fighters (6bits) / Nb mining (6bits) / Nb round (12bits) [RESTE 8 bits]
def compressBaseInfo(self, info):
    tmp = 0
    tmp = tmp | ((info['nbf'] & 0x3F)<<26) | ((info['nbm'] & 0x3F)<<20) | ((info['nbr'] & 0xFFF)<<8) 
    return tmp

def extractBaseInfo(self, compressed):
    nbf = (compressed >> 26) & 0x3F
    nbm = (compressed >> 20) & 0x3F
    nbr = (compressed >> 8) & 0xFFF
    tmp = {'nbf': nbf,'nbm': nbm,'nbr': nbr }
    return tmp


CONST_MINERAL_RANDOM	= 3
CONST_MINERAL_NORMAL    = 2
CONST_MINERAL_EMPTY 	= 1
CONST_MINERAL_VOID 	    = 0
def logMineralQuantity(quantity):
    log = ""
    if quantity == CONST_MINERAL_RANDOM :
            log += "?RANDOM?"
    elif quantity == CONST_MINERAL_NORMAL :
            log += "Normal"
    elif quantity == CONST_MINERAL_EMPTY :
            log += "-empty-"
    else:
            log += "void"
    return log                

CONST_FRIEND_BASE 	    = CONST_ENNEMY_BASE 	    = 3
CONST_FRIEND_FIGHTER    = CONST_ENNEMY_FIGHTER 	    = 2
CONST_FRIEND_MININGSHIP = CONST_ENNEMY_MININGSHIP	= 1
CONST_FRIEND_VOID 	    = CONST_ENNEMY_VOID 	    = 0
def logEnnemyTypeCible(cible_type):
    log = ""
    if cible_type == CONST_ENNEMY_MININGSHIP :
            log += "Mining"
    elif cible_type == CONST_ENNEMY_FIGHTER :
            log += "Fighter"
    elif cible_type == CONST_ENNEMY_BASE :
            log += "Base"
    else:
            log += "void"
    return log                


# From leguims
def log(level, trace, self):
    if level >= CONST_LOG:
        self.log(trace)
    return
    
def in_circle(center_x, center_y, radius, x, y):
    dist = distance_4_args(center_x, center_y, x, y)
    return dist <= radius

def distance_4_args(x1, y1, x2, y2):
    return ( math.sqrt( math.pow(x1-x2, 2) + math.pow(y1-y2, 2) ) )

def distance_2_args(pos1, pos2):
    return ( math.sqrt( math.pow(pos1[0]-pos2[0], 2) + math.pow(pos1[1]-pos2[1], 2) ) )

def FighterInstantRange(ship):
    return ship.fuel()/aiwar.FIGHTER_MOVE_CONSO()*aiwar.FIGHTER_SPEED()

def MiningshipInstantRange(ship):
    return ship.fuel()/aiwar.MININGSHIP_MOVE_CONSO()*aiwar.MININGSHIP_SPEED()

def MissileRange():
    return aiwar.MISSILE_SPEED()*MissileLifeTime()

def MissileLifeTime():
    return aiwar.MISSILE_START_FUEL()/aiwar.MISSILE_MOVE_CONSO()

def canFighterEscapeMissile(distance):
    # Est-ce que la cible peut s'echaper ?
    portee = MissileRange()
    duree_vie = MissileLifeTime()
        
    # +1 pour le cas le plus defavorable (cible va jouer)
    if (portee-distance) > aiwar.FIGHTER_SPEED()*(duree_vie+1) :
        return True
    else :
        return False

def canMiningshipEscapeMissile(distance):
    # Est-ce que la cible peut s'echaper ?
    portee = MissileRange()
    duree_vie = MissileLifeTime()

    # +1 pour le cas le plus defavorable (cible va jouer)
    if (portee-distance) > aiwar.MININGSHIP_SPEED()*(duree_vie+1) :
        return True
    else :
        return False

def isShipComeBack(self, ship):
    ship_angle = ship.angle()
    sx,sy = ship_pos = ship.pos()
    nx,ny = newship_pos = ( sx + 20*math.cos(math.radians(ship_angle)), sy - 20*math.sin(math.radians(ship_angle)) )
    mx,my = my_pos = self.pos()
    
    if distance_2_args( newship_pos , my_pos ) < distance_2_args( ship_pos , my_pos ):
        return True
    else:
        return False

def isMissileSpotedMe(self, missile):
    log(CONST_LOG_DEBUG, "************************ isMissileSpotedMe : Start", self)
    me_x, me_y = me_pos= self.pos()
    missile_angle = missile.angle()
    mx,my = missile_pos = missile.pos()
    missile_distance = self.distanceTo(missile)
    
    nx,ny = newmissile_pos = ( mx + missile_distance*math.cos(math.radians(missile_angle)), my - missile_distance*math.sin(math.radians(missile_angle)) )
    
    if distance_4_args( nx,ny , me_x,me_y ) < aiwar.WORLD_SIZE_X()/100:
        log(CONST_LOG_DEBUG, "************************ isMissileSpotedMe : True", self)
        return True
    else:
        log(CONST_LOG_DEBUG, "************************ isMissileSpotedMe : False", self)
        return False

def MiningDistanceProche():
    return aiwar.MININGSHIP_DETECTION_RADIUS()/4

def MiningDistanceEffacerMinerai():
    return aiwar.MININGSHIP_DETECTION_RADIUS()*3/5

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

def FighterDistanceEffacerEnnemi():
    return aiwar.FIGHTER_DETECTION_RADIUS()*3/5

def readFriendMemory(Counter = 0, Me = CONST_FRIEND_VOID, Friend = CONST_FRIEND_VOID):
    if Me == CONST_FRIEND_VOID :
        return True
    if Me == CONST_FRIEND_BASE :
        return True
    if Me == CONST_FRIEND_FIGHTER :
        if Counter <= CONST_NB_COMMUNICATION_MAX :
            return True
    if Me == CONST_FRIEND_MININGSHIP :
        if Counter <= CONST_NB_COMMUNICATION_MAX :
            return True
    return False


# Indique s'il faut prendre la cible de l'ami
def getFriendEnnemyToFighter(self, me1, me2, self_friend):
    copy = False
    # Initialisation Friend en fonction de son type
    if isinstance(self_friend, aiwar.Base):
        friend = extractBaseMemory(self, self_friend)
    if isinstance(self_friend, aiwar.Fighter):
        friend = extractFighterMemory(self, self_friend)
    if isinstance(self_friend, aiwar.MiningShip):
        friend = extractMiningShipMemory(self, self_friend)
    # Copier S'il reste assez de cible ou si l'ami est la BASE/Mining 
    # (car ces derniers n'attaquent pas, donc il faut copier leur cible jusqu'à l'épuisement de la cible)
    #log(CONST_LOG_DEBUG, "getFriendEnnemyToFighter : friend['ennemy1']['t']="+logEnnemyTypeCible(friend['ennemy1']['t'])+" - Nb cibles="+str(int(friend['ennemy1']['nbc']))+" >? getNumberTargetByFighter()="+str(int(getNumberTargetByFighter( friend['ennemy1']['t'] )))+" - Base?"+str(int(isinstance(self_friend, aiwar.Base))), self)
    if friend['ennemy1']['t'] != CONST_ENNEMY_VOID \
    and friend['ennemy1']['nbc'] > friend['ennemy1']['nbv'] :
        # Copier la cible amie si la notre est vide et non visible de notre cible2
        if me1['t'] == CONST_ENNEMY_VOID:
            if friend['ennemy1']['t'] != CONST_ENNEMY_VOID \
            and (me2['t'] == CONST_ENNEMY_VOID \
                or distance_4_args(friend['ennemy1']['x'], friend['ennemy1']['y'], me2['x'], me2['y']) >= FighterDistanceLoin() ):
                log(CONST_LOG_DEBUG, "Copier memoire Friend (ennemis)", self)
                copy = True
        # Copier la cible amie si la notre n'est pas vide et non visible de notre cible2
        # ET si elle est supérieur à la notre : BASE >>> FIGHTER >>> MINERALSHIP
        if me1['t'] != CONST_ENNEMY_VOID:
            if friend['ennemy1']['t'] != CONST_ENNEMY_VOID \
                and (me2['t'] == CONST_ENNEMY_VOID \
                    or distance_4_args(friend['ennemy1']['x'], friend['ennemy1']['y'], me2['x'], me2['y']) >= FighterDistanceLoin() ) \
                and (me1['t'] == CONST_ENNEMY_VOID \
                    or distance_4_args(friend['ennemy1']['x'], friend['ennemy1']['y'], me1['x'], me1['y']) >= FighterDistanceLoin() ) \
                and ( friend['ennemy1']['t'] == CONST_ENNEMY_BASE \
                    or friend['ennemy1']['t'] == CONST_ENNEMY_FIGHTER and me1['t'] == CONST_ENNEMY_MININGSHIP ) :
                log(CONST_LOG_DEBUG, "Copier memoire Friend (mineraux épuisés)", self)
                copy = True

        #log(CONST_LOG_DEBUG, "getFriendEnnemyToFighter : copy == "+str(int(copy)), self)
        if copy == True:
            me1 = dict(friend['ennemy1'])
            # Vidage des cible Fighter incrementale. Copie complete de la cible en une fois pour Base/Mining
            if isinstance(self_friend, aiwar.Fighter):
                me1['nbc'] = getNumberTargetByFighter( friend['ennemy1']['t'] )
            else:
                me1['nbc'] = friend['ennemy1']['nbc']
            me1['nbv'] = me1['nbc']
            #log(CONST_LOG_DEBUG, "   Ennemy1=("+str(int(me1['x']))+", "+str(int(me1['y']))+") Type="+logEnnemyTypeCible(me1['t'])+" NbCible="+str(int(me1['nbc']))+" NbVoisins="+str(int(me1['nbv'])), self)
            
            # Decrementer le nombre de cibles de l'ami (sauf si c'est une base)
            if friend['ennemy1']['t'] != CONST_ENNEMY_BASE:
                #log(CONST_LOG_DEBUG, "   friend=("+str(int(friend['ennemy1']['x']))+", "+str(int(friend['ennemy1']['y']))+") Type="+logEnnemyTypeCible(friend['ennemy1']['t'])+" NbCible="+str(int(friend['ennemy1']['nbc']))+" NbVoisins="+str(int(friend['ennemy1']['nbv'])), self)
                
                # Vidage des VOISINS "on the way" Fighter incrementale. Copie complete de la cible en une fois pour Base/Mining
                if isinstance(self_friend, aiwar.Fighter):
                    friend['ennemy1']['nbv'] += getNumberTargetByFighter( friend['ennemy1']['t'] )
                else:
                    friend['ennemy1']['nbv'] = friend['ennemy1']['nbc']
                
                #log(CONST_LOG_DEBUG, "   friend=("+str(int(friend['ennemy1']['x']))+", "+str(int(friend['ennemy1']['y']))+") Type="+logEnnemyTypeCible(friend['ennemy1']['t'])+" NbCible="+str(int(friend['ennemy1']['nbc']))+" NbVoisins="+str(int(friend['ennemy1']['nbv'])), self)
                # INUTILE SI NBC==NBV utilisé  ====>>> A CONFIRMER !!!
                #if friend['ennemy1']['nbc'] <= 0:
                #    # Cible epuisee => l'effacer
                #    friend['ennemy1']['x'] = CONST_VOID_POSITION
                #    friend['ennemy1']['y'] = CONST_VOID_POSITION
                #    friend['ennemy1']['t'] = CONST_ENNEMY_VOID
                #    friend['ennemy1']['nbc'] = 0
                #    friend['ennemy1']['nbv'] = 0
                # Enregistrement Friend en fonction de son type
                if isinstance(self_friend, aiwar.Base):
                    compressBaseMemory(self, self_friend, friend)
                if isinstance(self_friend, aiwar.Fighter):
                    compressFighterMemory(self, self_friend, friend)
                if isinstance(self_friend, aiwar.MiningShip):
                    compressMiningShipMemory(self, self_friend, friend)
                #log(CONST_LOG_DEBUG, "   friend=("+str(int(friend['ennemy1']['x']))+", "+str(int(friend['ennemy1']['y']))+") Type="+logEnnemyTypeCible(friend['ennemy1']['t'])+" NbCible="+str(int(friend['ennemy1']['nbc']))+" NbVoisins="+str(int(friend['ennemy1']['nbv']))+"   Apres compressXxxxMemory().", self)
                
    #log(CONST_LOG_DEBUG, "getFriendEnnemyToFighter : end", self)
    #log(CONST_LOG_DEBUG, "   Ennemy1=("+str(int(me1['x']))+", "+str(int(me1['y']))+") Type="+logEnnemyTypeCible(me1['t'])+" NbCible="+str(int(me1['nbc']))+" NbVoisins="+str(int(me1['nbv'])), self)
    #log(CONST_LOG_DEBUG, "   friend=("+str(int(friend['ennemy1']['x']))+", "+str(int(friend['ennemy1']['y']))+") Type="+logEnnemyTypeCible(friend['ennemy1']['t'])+" NbCible="+str(int(friend['ennemy1']['nbc']))+" NbVoisins="+str(int(friend['ennemy1']['nbv'])), self)
    return me1


def getNumberTargetByFighter( cible_type ):
    if cible_type == CONST_ENNEMY_MININGSHIP :
            return 2
    elif cible_type == CONST_ENNEMY_FIGHTER :
            return 1
    elif cible_type == CONST_ENNEMY_BASE :
            return 1
    return 0


# Retourne la position des mineraux à enregistrer
def getFriendMineralToMiningShip(self, me1, me2, friend):
    # Si mes 2 cibles sont EMPTY, alors considerer me1 VOID (dans ce cas vérifier que friend != me1 en distance)
    # Copier la cible amie si la notre est vide/random (copie uniquement des vraie positions de mineraux)
    if me1['q'] == CONST_MINERAL_VOID or me1['q'] == CONST_MINERAL_RANDOM \
    or (me1['q'] == CONST_MINERAL_EMPTY and me2['q'] == CONST_MINERAL_EMPTY) :
        if friend['q'] == CONST_MINERAL_NORMAL \
            and ( me2['q'] == CONST_MINERAL_VOID or distance_4_args(friend['x'], friend['y'], me2['x'], me2['y']) >= MiningDistanceLoin() ) \
            and (me1['q'] != CONST_MINERAL_EMPTY or distance_4_args(friend['x'], friend['y'], me1['x'], me1['y']) >= MiningDistanceLoin()) :
            log(CONST_LOG_DEBUG, "Copier memoire Friend (mineraux)", self)
            return friend
    # Copier la cible amie si elle est identique (en visibilité) à la notre ET qu'elle est epuisée (EMPTY)
    if me1['q'] != CONST_MINERAL_VOID:
        if friend['q'] != CONST_MINERAL_VOID \
            and distance_4_args(friend['x'], friend['y'], me1['x'], me1['y']) <= MiningDistanceEffacerMinerai() \
            and friend['q'] == CONST_MINERAL_EMPTY \
            and me1['q'] != CONST_MINERAL_EMPTY:
            log(CONST_LOG_DEBUG, "Copier memoire Friend (mineraux épuisés)", self)
            return friend
    return me1


# Retourne la position de la base à enregistrer
def getFriendBasePosition(self, me, friend):
    # Copier la cible amie si la notre est vide
    if (me['x'], me['y']) == (CONST_VOID_POSITION, CONST_VOID_POSITION) \
    and (friend['x'], friend['y']) != (CONST_VOID_POSITION, CONST_VOID_POSITION):
        log(CONST_LOG_DEBUG, "Copier memoire Friend (position BASE)", self)
        return friend
    return me


# Efface les ennemis visibles
def eraseEnnemy(self, ennemy, ennemyEnVue):
    if ennemy['t'] != CONST_ENNEMY_VOID \
    and self.distanceTo( (ennemy['x'], ennemy['y']) ) < FighterDistanceEffacerEnnemi() \
    and ennemyEnVue == False :
        # on aurait du voir l'ennemi -> il est vide
        log(CONST_LOG_WARNING, "J'efface l'ennemi", self)
        ennemy['x'] = CONST_VOID_POSITION
        ennemy['y'] = CONST_VOID_POSITION
        ennemy['t'] = CONST_ENNEMY_VOID
        ennemy['nbc'] = 0
        ennemy['nbv'] = 0
    return ennemy


# Efface les mineraux visibles 'q=EMPTY'
def eraseMineral(self, mineral, minerauxEnVue):
    if (mineral['x'], mineral['y']) != (CONST_VOID_POSITION, CONST_VOID_POSITION) \
    and self.distanceTo( (mineral['x'], mineral['y']) ) < MiningDistanceEffacerMinerai() \
    and minerauxEnVue == False :
        # on aurait du voir le minerai -> il est vide
        log(CONST_LOG_WARNING, "Je passe le minerai 'EMPTY'", self)
        mineral['q'] = CONST_MINERAL_EMPTY
    return mineral


def random_target(base, nb_ships, distance=0):
    # Destination aleatoire relative a la position de la base
    if distance == 0 :
        distance = (aiwar.WORLD_SIZE_X() + aiwar.WORLD_SIZE_Y())/2 - aiwar.MININGSHIP_DETECTION_RADIUS()/2
        
    if(nb_ships == 0):
        angle = random.randint( 1, 360 )
    else:
        angle = 360/nb_ships*random.randint( 0, nb_ships+1 )
    tmp = {'x': int(base['x'] + distance*math.cos(math.radians(angle))) ,'y': int(base['y'] + distance*math.sin(math.radians(angle))) }
    return tmp


def setEnnemyBaseMemory(self, ennemyPosition, Base):
    BaseMemory = extractBaseMemory(self, Base)
    if ennemyPosition['t'] != CONST_ENNEMY_VOID :
        if BaseMemory['ennemy1']['t'] == CONST_ENNEMY_VOID \
        or BaseMemory['ennemy1']['t'] != CONST_ENNEMY_VOID \
            and not in_circle( BaseMemory['ennemy1']['x'], BaseMemory['ennemy1']['y'], MiningDistanceProche(), ennemyPosition['x'], ennemyPosition['y']) :
            # Inscrire le nouvel ennemi dans la BASE
            BaseMemory['ennemy1'] = dict(ennemyPosition)
            compressBaseMemory(self, Base, BaseMemory)
    else :
        # Effacer la cible
        BaseMemory['ennemy1'] = eraseEnnemy(self, BaseMemory['ennemy1'], False)
        compressBaseMemory(self, Base, BaseMemory)


def setMineralBaseMemory(self, mineralPosition, Base):
    BaseMemory = extractBaseMemory(self, Base)
        
    if mineralPosition['q'] == CONST_MINERAL_NORMAL:
        if BaseMemory['mineral3']['q'] == CONST_MINERAL_VOID \
                and not in_circle( BaseMemory['mineral2']['x'], BaseMemory['mineral2']['y'], MiningDistanceProche(), mineralPosition['x'], mineralPosition['y']) \
                and not in_circle( BaseMemory['mineral1']['x'], BaseMemory['mineral1']['y'], MiningDistanceProche(), mineralPosition['x'], mineralPosition['y']) \
            or BaseMemory['mineral2']['q'] == CONST_MINERAL_VOID \
                and not in_circle( BaseMemory['mineral1']['x'], BaseMemory['mineral1']['y'], MiningDistanceProche(), mineralPosition['x'], mineralPosition['y']) \
            or BaseMemory['mineral1']['q'] == CONST_MINERAL_VOID \
            or BaseMemory['mineral1']['q'] != CONST_MINERAL_VOID \
                and BaseMemory['mineral2']['q'] != CONST_MINERAL_VOID \
                and BaseMemory['mineral3']['q'] != CONST_MINERAL_VOID \
                and not in_circle( BaseMemory['mineral3']['x'], BaseMemory['mineral3']['y'], MiningDistanceProche(), mineralPosition['x'], mineralPosition['y']) \
                and not in_circle( BaseMemory['mineral2']['x'], BaseMemory['mineral2']['y'], MiningDistanceProche(), mineralPosition['x'], mineralPosition['y']) \
                and not in_circle( BaseMemory['mineral1']['x'], BaseMemory['mineral1']['y'], MiningDistanceProche(), mineralPosition['x'], mineralPosition['y']) :
            # Decaller la memoire "mineral" de la BASE
            BaseMemory['mineral3'] = dict(BaseMemory['mineral2'])
            BaseMemory['mineral2'] = dict(BaseMemory['mineral1'])
            # Inscrire le nouveau minerai dans la BASE
            BaseMemory['mineral1'] = dict(mineralPosition)
            compressBaseMemory(self, Base, BaseMemory)
            
    elif mineralPosition['q'] == CONST_MINERAL_EMPTY:
        # Copier la cible est deja presente (en visibilité) ET qu'elle est epuisée (EMPTY)
        if BaseMemory['mineral3']['q'] == CONST_MINERAL_NORMAL \
        and distance_4_args(BaseMemory['mineral3']['x'], BaseMemory['mineral3']['y'], mineralPosition['x'], mineralPosition['y']) <= MiningDistanceLoin() :
            BaseMemory['mineral3'] = mineralPosition

        if BaseMemory['mineral2']['q'] == CONST_MINERAL_NORMAL \
        and distance_4_args(BaseMemory['mineral2']['x'], BaseMemory['mineral2']['y'], mineralPosition['x'], mineralPosition['y']) <= MiningDistanceLoin() :
            BaseMemory['mineral2'] = mineralPosition

        if BaseMemory['mineral1']['q'] == CONST_MINERAL_NORMAL \
        and distance_4_args(BaseMemory['mineral1']['x'], BaseMemory['mineral1']['y'], mineralPosition['x'], mineralPosition['y']) <= MiningDistanceLoin() :
            BaseMemory['mineral1'] = mineralPosition

        compressBaseMemory(self, Base, BaseMemory)

    elif mineralPosition['q'] == CONST_MINERAL_RANDOM:
        return
        
    else :
        if BaseMemory['mineral3']['q'] != CONST_MINERAL_VOID:
            BaseMemory['mineral3']['x'] = CONST_VOID_POSITION
            BaseMemory['mineral3']['y'] = CONST_VOID_POSITION
            BaseMemory['mineral3']['q'] = CONST_MINERAL_VOID
            BaseMemory['mineral3']['i'] = False
        elif BaseMemory['mineral2']['q'] != CONST_MINERAL_VOID:
            BaseMemory['mineral2']['x'] = CONST_VOID_POSITION
            BaseMemory['mineral2']['y'] = CONST_VOID_POSITION
            BaseMemory['mineral2']['q'] = CONST_MINERAL_VOID
            BaseMemory['mineral2']['i'] = False
        elif BaseMemory['mineral1']['q'] != CONST_MINERAL_VOID:
            BaseMemory['mineral1']['x'] = CONST_VOID_POSITION
            BaseMemory['mineral1']['y'] = CONST_VOID_POSITION
            BaseMemory['mineral1']['q'] = CONST_MINERAL_VOID
            BaseMemory['mineral1']['i'] = False
        compressBaseMemory(self, Base, BaseMemory)


def setMyMineralMemory(self, me, mineralPosition):
    # ENREGISTER DANS MEMOIRE 1
    # Si memoire 1 et 2 vide => enregistrer dans memoire 1
    # Si memoire 1 vide et 2 non vide et minerai lointain de memoire 2  => enregistrer dans memoire 1
    # Si memoire 1 non-vide et minerai en visibilité de memoire 1 et minerai plus proche BASE que memoire 1 => enregistrer dans memoire 1
    if ( me['mineral1']['q'] == CONST_MINERAL_EMPTY \
            or me['mineral1']['q'] == CONST_MINERAL_VOID) \
        and ( me['mineral2']['q'] == CONST_MINERAL_EMPTY \
            or me['mineral2']['q'] == CONST_MINERAL_VOID) \
        \
        or ( me['mineral1']['q'] == CONST_MINERAL_EMPTY \
            or me['mineral1']['q'] == CONST_MINERAL_VOID ) \
        and ( me['mineral2']['q'] != CONST_MINERAL_EMPTY \
            and me['mineral2']['q'] != CONST_MINERAL_VOID ) \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['mineral2']['x'], me['mineral2']['y']) >= MiningDistanceLoin() \
        \
        or ( me['mineral1']['q'] != CONST_MINERAL_EMPTY \
            and me['mineral1']['q'] != CONST_MINERAL_VOID ) \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['mineral1']['x'], me['mineral1']['y']) < MiningDistanceLoin() \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['base']['x'], me['base']['y']) < distance_4_args(me['mineral1']['x'], me['mineral1']['y'], me['base']['x'], me['base']['y']) :
        log(CONST_LOG_WARNING, "je sauvegarde la position du minerai (cible 1)", self)
        me['mineral1']['x'] = mineralPosition['x']
        me['mineral1']['y'] = mineralPosition['y']
        me['mineral1']['q'] = CONST_MINERAL_NORMAL
        me['mineral1']['i'] = False
        
        compressMyMiningShipMemory(self, me)
        return


    # ENREGISTER DANS MEMOIRE 2
    # Si memoire 1 non-vide et 2 vide et minerai lointain de memoire 1 => enregistrer dans mem2
    # Si memoire 1 non-vide et 2 non-vide et minerai lointain de memoire 1 et minerai plus proche BASE que memoire 2 => enregistrer dans mem2
    elif ( me['mineral1']['q'] != CONST_MINERAL_EMPTY \
            and me['mineral1']['q'] != CONST_MINERAL_VOID ) \
        and ( me['mineral2']['q'] == CONST_MINERAL_EMPTY \
            or me['mineral2']['q'] == CONST_MINERAL_VOID) \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['mineral1']['x'], me['mineral1']['y']) >= MiningDistanceLoin() \
        \
        or ( me['mineral1']['q'] != CONST_MINERAL_EMPTY \
            and me['mineral1']['q'] != CONST_MINERAL_VOID ) \
        and ( me['mineral2']['q'] != CONST_MINERAL_EMPTY \
            and me['mineral2']['q'] != CONST_MINERAL_VOID ) \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['mineral1']['x'], me['mineral1']['y']) >= MiningDistanceLoin() \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['base']['x'], me['base']['y']) < distance_4_args(me['mineral2']['x'], me['mineral2']['y'], me['base']['x'], me['base']['y']) :
        log(CONST_LOG_WARNING, "je sauvegarde la position du minerai (cible 2)", self)
        me['mineral2']['x'] = mineralPosition['x']
        me['mineral2']['y'] = mineralPosition['y']
        me['mineral2']['q'] = CONST_MINERAL_NORMAL
        me['mineral2']['i'] = False
        
        compressMyMiningShipMemory(self, me)
        return


    # DECALLER POUR ENREGISTER DANS MEMOIRE 1
    # Si memoire 1 vide et 2 non vide et minerai en visibilité de memoire 2 et minerai plus proche BASE que memoire 2 => effacer memoire 2 + enregistrer dans memoire 1 = decaller mem1 en mem2 et enregistrer dans mem1
    # Si memoire 1 non-vide et minerai lointain de memoire 1 et minerai plus proche BASE que memoire 1 => decaller mem1 en mem2 et enregistrer dans mem1
    elif ( me['mineral1']['q'] == CONST_MINERAL_EMPTY \
            or me['mineral1']['q'] == CONST_MINERAL_VOID ) \
        and ( me['mineral2']['q'] != CONST_MINERAL_EMPTY \
            and me['mineral2']['q'] != CONST_MINERAL_VOID ) \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['mineral2']['x'], me['mineral2']['y']) < MiningDistanceLoin() \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['base']['x'], me['base']['y']) < distance_4_args(me['mineral2']['x'], me['mineral2']['y'], me['base']['x'], me['base']['y']) \
        \
        or ( me['mineral1']['q'] != CONST_MINERAL_EMPTY \
            and me['mineral1']['q'] != CONST_MINERAL_VOID ) \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['mineral1']['x'], me['mineral1']['y']) >= MiningDistanceLoin() \
        and distance_4_args(mineralPosition['x'], mineralPosition['y'], me['base']['x'], me['base']['y']) < distance_4_args(me['mineral1']['x'], me['mineral1']['y'], me['base']['x'], me['base']['y']) :
        log(CONST_LOG_WARNING, "je sauvegarde la position du minerai (decaller cible 1)", self)
        me['mineral2'] = me['mineral1']
        
        me['mineral1']['x'] = mineralPosition['x']
        me['mineral1']['y'] = mineralPosition['y']
        me['mineral1']['q'] = CONST_MINERAL_NORMAL
        me['mineral1']['i'] = False
        
        compressMyMiningShipMemory(self, me)
        return


def moveToEnnemy(self, ennemy):
    if ennemy['t'] != CONST_ENNEMY_VOID:
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo( (ennemy['x'], ennemy['y']) ) > FighterDistanceProche():
            self.rotateTo( (ennemy['x'], ennemy['y']) )
            self.move()
            log(CONST_LOG_WARNING, "++Ennemy: Go cible 1.("+ str(int(ennemy['x'])) +", "+ str(int(ennemy['y'])) +")", self)
        # Proche de la cible avec des missiles => elle n'est plus là. Passer à la cible suivante.
        else:
            # Effacer la cible
            ennemy = eraseEnnemy(self, ennemy, False)
    return ennemy


def moveToMineral(self, mineral):
    if ( mineral['q'] != CONST_MINERAL_EMPTY \
        and mineral['q'] != CONST_MINERAL_VOID ) :
        log(CONST_LOG_WARNING, "je vais au minerai : x="+ str(mineral['x']) +", y="+ str(mineral['y']), self)
        self.rotateTo( (mineral['x'], mineral['y']) )
        # Se deplacer tant qu'on est loin de la cible
        if self.distanceTo( (mineral['x'], mineral['y']) ) > (aiwar.MININGSHIP_MINING_RADIUS()):
            self.move()


