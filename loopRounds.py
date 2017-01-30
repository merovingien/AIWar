from __future__ import print_function
import sys          # argv
import os           # listdir(), path.join()
import subprocess   # Popen()
import time         # time(), sleep()
import logging
import xml.etree.ElementTree as ET
import json         # dump(), load()
import datetime     # date.today().isoformat()

import multiprocessing  # cpu_count()

class AIwarError(Exception):
    pass

# Reading 'config.xml' to extract blue/red players and map name.
# Use global var 'readConfig_static' to prevent multiple XML parsing
readConfig_static = None
def readConfig( config ):
    "Read the config file to return players and map name as a tuple."
    global readConfig_static
    tree = ET.parse(config)
    root = tree.getroot()
    if(readConfig_static == None or readConfig_static['ref'] != config):
        blue = root.find("options/blue").text
        red = root.find("options/red").text
        mapName = root.find("options/map").text
        players = tuple(p.text for p in root.findall('players/player/name'))
        playersParams = tuple(p.text for p in root.findall('players/player/params'))
        renderers = tuple(p.text for p in root.findall('renderers/renderer/name'))
        logging.info(
            'Reading config file "{config}" : players(blue/red): "{blue}"/"{red}" on map "{mapName}".'.format(
            config=config, blue=blue, red=red, mapName=mapName ) )
        logging.info(
            'Reading config file "{config}" : list of players "{players}".'.format(
            config=config, players=players ) )
        readConfig_static = dict()
        readConfig_static['ref'] = config
        readConfig_static['data'] = (blue, red, mapName, players, playersParams, renderers)
    return readConfig_static['data']

# Use global var 'readMaps_static' to prevent multiple os.listdir()
readMaps_static = None
def readMaps( mapDirectory ):
    "Read the list of map and return as a tuple."
    global readMaps_static
    if(readMaps_static == None or readMaps_static['ref'] != mapDirectory):
        readMaps_static = dict()
        readMaps_static['ref'] = mapDirectory
        readMaps_static['data'] = tuple(m for m in os.listdir(mapDirectory) if m[-4:].lower() == '.xml')
        logging.info( 'Reading list of maps : {}'.format(mapDirectory) )
        logging.info( 'Map directory : {}'.format(readMaps_static['ref']) )
        for i, m in enumerate(readMaps_static['data']):
            logging.info( 
                'Map {index} : {mapName}.'.format(
                index=i, mapName=m ) )
    return readMaps_static['data']

def verifyArgs( args ):
    "Verify arguments to launch a job. Raise exception if error."
    # Verify players exist
    if not args[2] in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(args[2]) )
        raise AIwarError('Unknown player', args[2])
    if not args[4] in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(args[4]) )
        raise AIwarError('Unknown player', args[4])
    
    # Verify map exists
    if not os.path.basename(args[6]) in readMaps(configMapDirectory):
        logging.critical( 'Unknown map : {}'.format(os.path.basename(args[6])) )
        raise AIwarError('Unknown map', os.path.basename(args[6]))
    
    # Verify renderer exists
    if not args[8] in readConfig(configFile)[5]:
        logging.critical( 'Unknown renderer : {}'.format(i['args'][8]) )
        raise AIwarError('Unknown renderer', i['args'][8])

def newJob( blue, red, mapName ):
    "Create 1 new job to add to the job list. Returns dictionnary for job without 'number'"
    # Verify players exist
    if not blue in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(blue) )
        raise AIwarError('Unknown player', blue)
    if not red in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(red) )
        raise AIwarError('Unknown player', red)
    
    # Verify map exists
    if not mapName in readMaps(configMapDirectory):
        logging.critical( 'Unknown map : {}'.format(mapName) )
        raise AIwarError('Unknown map', mapName)
    
    return {'blue': blue, 'red':red, 'mapName': mapName}

def createArgs( blue, red, mapName ):
    "Create list of args to launch 'AIWar' subprocess"
    args = ( "AIWar",
             "--blue", blue,
             "--red", red,
             "--map", os.path.join(configMapDirectory, mapName),
             "--renderer", "dummy" )
    return args


def newRounds( blue, red, mapName, repeat = 1 ):
    "Create N rounds to add to the job list. Returns list of dictionnary for job without 'number'"
    return [newJob( blue, red, mapName ) for r in range(repeat)]

def newMaps( blue, red, repeat = 1):
    "Create N rounds by map to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for m in readMaps(configMapDirectory):
        r += newRounds( blue, red, m, repeat )
    return r

def newColors( blue, red, repeat = 1):
    "Create N rounds by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    return newMaps( blue, red, repeat ) + newMaps( red, blue, repeat )

def newPlayers( player, repeat = 1 ):
    "Create N rounds for 1 player against the world by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for p in readConfig(configFile)[3]:
        if p != player:
            r += newColors( player, p, repeat )
    return r

def newComplete( repeat = 1 ):
    "Create N rounds for all players by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for p in readConfig(configFile)[3]:
        r += newPlayers( p, repeat )
    return r

def createResultName( blue, red ):
    "Create a result_name list by customisation of 'result_txt' list with players names. return dict."
    # insert player name in result_txt to have result_name
    name = dict()
    for k, v in result_txt.iteritems():
        if 'blue' in v:
            name[k] = v.replace('blue', blue) + " against " + red
        elif 'red' in v:
            name[k] = v.replace('red', red) + " against " + blue
        else:
            name[k] = v
    logging.debug( 'result_name={}'.format(name) )
    return name


#############
# Multiprocessing function
def processJob( keywords ):
    "Launch a job, wait the end and update the Result-file. Return nothing"
        
    # Init
    #logging = keywords['logging']
    args    = createArgs( keywords['blue'], keywords['red'], keywords['mapName'] )
    try:
        verifyArgs(args)
    except AIwarError as e:
        txt = 'job {number} : Error when launching job "{args}". Ignoring and go to next one.'.format( number=keywords['number'], args=" ".join( args ) )
        logging.exception( txt )
        # End of job !
        return

    # Sleep to randomize each game
    time.sleep(keywords['number']%10)
    # Launch
    popen = subprocess.Popen(args)
    start = time.time()
    end = None
    txt = 'job {number} : Starting "{blue}" Vs "{red}" on map "{mapName}".'.format(
        number=keywords['number'], blue=keywords['blue'], red=keywords['red'], mapName=keywords['mapName'] )
    logging.info( txt )
    print( txt )

    # Wait end of fight
    while(not end):
        logging.debug( 'keywords={} ### args = {} ### i["popen"].poll()={}'.format(keywords, args, popen.poll()) )
        if popen.poll() is None:
            # Job not over.
            if int(time.time()-start) % 10 == 0:
                logging.debug( "popen.poll()={} ; popen.returncode={}".format( popen.poll(), popen.returncode) )
                txt = 'job {number} : T={time} sec. : still fighting...'.format( number=keywords['number'], time=int(time.time()-start) )
                logging.info( txt )
                print( txt )
        else:
            returncode = popen.returncode
            end = time.time()
            result_name = createResultName(blue=keywords['blue'], red=keywords['red'])
            logging.debug( "popen.returncode={}".format( returncode ) )
            txt = 'job {number} : T={time} sec. : {result}'.format( number=keywords['number'], result=result_name[ returncode ], time=int(end-start) )
            logging.info( txt )
            print( txt )
        # Sleep each loop WHILE
        time.sleep(1)

    try:
        # Delete job from "Resume file"
        keywords['mutexResumeFile'].acquire()
        removeJobFromResumeFile( keywords['blue'], keywords['red'], keywords['mapName'] )
        keywords['mutexResumeFile'].release()

        # Add job to "Results file"
        keywords['mutexResultFile'].acquire()
        addJobToResultFile( keywords['blue'], keywords['red'], keywords['mapName'], returncode, start, end )
        keywords['mutexResultFile'].release()
    except ValueError as e:
        txt = 'job {number} : Error when removing job "{args}" from Resume-File. Ignoring and do not add result to Result-File.'.format(
           number=keywords['number'], args=" ".join( args ) )
        logging.exception( txt )

    # Return number
    return keywords['number']

def removeJobFromResumeFile( blue, red, mapName ):
    "Remove a job of Resume-file. Return nothing"
    jobs_resume = list()
    # Initialize jobs_resume with file
    if os.path.isfile(resumeFilename):
        with open(resumeFilename, 'r') as jobListFile:
            jobs_resume = json.load(jobListFile)
            txt = 'Resume file "{name}" : {jobs} job{plural}.'.format( name=resumeFilename, jobs=len(jobs_resume), plural='s' if len(jobs_resume) else '' )
            logging.info( txt )
            print(txt)
    # Update jobs_resume
    jobs_resume.remove( {'blue': blue, 'red': red, 'mapName': mapName} )
    # Write jobs_resume in file
    with open(resumeFilename, 'w') as jobListFile:
        json.dump(jobs_resume, jobListFile)
        txt = 'Resume file "{name}" completed : {jobs} job{plural}.'.format( name=resumeFilename, jobs=len(jobs_resume), plural='s' if len(jobs_resume) else '' )
        logging.info( txt )
        print(txt)

def addJobToResultFile( blue, red, mapName, returncode, start, end ):
    "Add a job to Result-file. Return nothing"
    jobs_results = list()
    resultsFilename = prefixFileName+'results-list-'+datetime.date.today().isoformat()+'.json'
    # Read results already saved from file
    if os.path.isfile(resultsFilename):
        with open(resultsFilename, 'r') as resultsFileIO:
            jobs_results = json.load(resultsFileIO)
            txt = 'Result file "{name}" completed : {jobs} job{plural}.'.format( name=resultsFilename, jobs=len(jobs_results), plural='s' if len(jobs_results) else '' )
            logging.info( txt )
            print(txt)
            #import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(jobs_resume)
    # Update jobs_results
    jobs_results.append(
        {
            'blue': {'name': blue, 'params': playerName_params[ blue ]},
            'red': {'name': red, 'params': playerName_params[ red ]},
            'map': mapName,
            'result': result_txt[ returncode ],
            'start' : start,
            'end' : end,
        })
    # Save to file results list
    with open(resultsFilename, 'w') as resultsFileIO:
        json.dump(jobs_results, resultsFileIO)
        txt = 'Result file "{name}" completed : {jobs} job{plural}.'.format( name=resultsFilename, jobs=len(jobs_results), plural='s' if len(jobs_results) else '' )
        logging.info( txt )
        print(txt)
# Multiprocessing function
#############



#############
# Init
configFile = 'config.xml'
configMapDirectory = './maps'
prefixFileName = os.path.splitext(os.path.basename(sys.argv[0]))[0]+'_'
resumeFilename = prefixFileName+'job-list.json'
logsFilename = prefixFileName+'logs-'+datetime.date.today().isoformat()+'.log'
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename=logsFilename, level=logging.INFO)
#logging.basicConfig(filename=logsFilename, level=logging.ERROR)


result_txt = {0: "draw", 1: "blue wins", 2: "red wins",
              11: "blue error", 12: "red error", 255: "error"}
result_int = {value: key for (key, value) in result_txt.iteritems()}
result_int = {value: key for (key, value) in result_txt.iteritems()}

bluePlayer, redPlayer, mapName, players, playersParams, _ = readConfig(configFile)
playerName_params = {name: params for name, params in zip(players, playersParams)}

if __name__ == '__main__':
    nbProcesses = multiprocessing.cpu_count()/2

    
    #msg='test'
    #logging.info(msg)
    #logging.warning(msg)
    #logging.error(msg)
    #logging.critical(msg)
    #logging.exception(msg)
    #logging.log(level, msg)

    logging.debug( 'result_txt={}'.format(result_txt) )
    logging.debug( 'result_int={}'.format(result_int) )


    # Reading of arguments
    #
    # TROUVER MODULE DEDIE ET IMPLEMENTER
    #

    #############
    # Build list of jobs

    jobs_resume = list()

    # Resume undone jobs from file
    if os.path.isfile(resumeFilename):
        with open(resumeFilename, 'r') as jobListFile:
            jobs_resume = json.load(jobListFile)
            txt = 'Resume file "{name}" : {jobs} job{plural}.'.format( name=resumeFilename, jobs=len(jobs_resume), plural='s' if len(jobs_resume) else '' )
            logging.info( txt )
            print(txt)
            #import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(jobs_resume)
    else:
        txt = 'Resume file "{name}" : empty.'.format( name=resumeFilename )
        logging.info( txt )
        print( txt )
        

    try:
        pass
        jobs_resume += newRounds('GuiGui', 'Shuriken', 'map.xml', 1 )
        jobs_resume += newRounds('Merovingien', 'Clement', 'map_FollowTheWhiteRabbit.xml', 2 )

        #jobs_resume += newMaps( 'GuiGui', 'Shuriken' )
        #jobs_resume += newMaps('Merovingien', 'Clement', 2 )

        #jobs_resume += newColors( 'GuiGui', 'Shuriken' )
        #jobs_resume += newColors('Merovingien', 'Clement', 2 )

        #jobs_resume += newPlayers( 'GuiGui' )
        #jobs_resume += newPlayers( 'Clement', 2 )

        #jobs_resume += newComplete(1)
        #jobs_resume += newComplete(3)
    except AIwarError as e:
        txt = 'Error when create new jobs. Stopping work.' + str(e)
        logging.exception( txt )
        print( txt )
        exit()

    # Save to file the job's list
    with open(resumeFilename, 'w') as jobListFile:
        json.dump(jobs_resume, jobListFile)


    # Add data used for manage job processing
    jobs_launcher = list()
    for enum, i in enumerate(jobs_resume):
        jobs_launcher.append(
            {
                'number': enum,
                'resume': i,
                'popen': None,
                'launching': None,
                'ret': None,
                'start' : 0,
                'end' : 0,
                'args': createArgs( i['blue'], i['red'], i['mapName'] )
            })


    #logging.debug( 'jobs_resume={}'.format(jobs_resume) )
    #logging.debug( 'jobs_launcher={}'.format(jobs_launcher) )

    txt = 'Resume file "{name}" completed : {jobs} job{plural}.'.format( name=resumeFilename, jobs=len(jobs_resume), plural='s' if len(jobs_resume) else '' )
    logging.info( txt )
    print(txt)
    #import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(jobs_resume)
    #import pprint; pp = pprint.PrettyPrinter(indent=4); print('jobs_launcher = '); pp.pprint(jobs_launcher)
    #exit()



    #############
    # Dispatch job to multiprocessing
    m = multiprocessing.Manager()
    mutexResumeFile = m.Lock()
    mutexResultFile = m.Lock()
    pool = multiprocessing.Pool(processes=nbProcesses)
    # Add data used for manage job processing
    jobs_launcher = list()
    for enum, i in enumerate(jobs_resume):
        jobs_launcher.append(
            {
                'number':           enum,
                'mutexResumeFile':  mutexResumeFile,
                'mutexResultFile':  mutexResultFile,
                'blue':             i['blue'],
                'red':              i['red'],
                'mapName':          i['mapName']
            })

    
    #print( pool.map(processJob, jobs_launcher) )
    #pool.close()
    #pool.join()
    
    if jobs_launcher:
        for x in pool.imap_unordered(processJob, jobs_launcher):
            print("Job {} is over.".format(x) )
    
    #exit()

    #############
    # Build charts


    txt = '...End'
    logging.info( txt )
    print(txt)
