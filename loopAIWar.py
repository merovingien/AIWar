from __future__ import print_function
import sys          # argv
import os           # listdir(), path.join()
import subprocess   # Popen()
import time         # time(), sleep()
import logging
import xml.etree.ElementTree as ET
import json         # dump(), load()
import datetime     # date.today().isoformat()
import argparse     # ArgumentParser(), add_argument(), parse_args()

import multiprocessing  # cpu_count()

import PublishStatisticsAIWar # publish()

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
             #"--renderer", "sdl" ) # To watch the game. Press "ESC" to close window at end.
    return args


def newRounds( blue, red, mapName, repeat = 1 ):
    "Create N rounds to add to the job list. Returns list of dictionnary for job without 'number'"
    logging.info("blue={} red={}, mapName={}, repeat={}".format(blue, red, mapName, repeat))
    #print("blue={} red={}, mapName={}, repeat={}".format(blue, red, mapName, repeat))
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
def allocateJob(jobs_resume):
    "Allocate jobs to multiprocessing, wait and print the end. Return nothing"
    m = multiprocessing.Manager()
    mutexResumeFile = m.Lock()
    mutexResultFile = m.Lock()
    mutexPrint = m.Lock()
    pool = multiprocessing.Pool(processes=nbProcesses)
    # Add data used for manage job processing
    jobs_launcher = list()
    for enum, i in enumerate(jobs_resume):
        jobs_launcher.append(
            {
                'number':           enum,
                'mutexResumeFile':  mutexResumeFile,
                'mutexResultFile':  mutexResultFile,
                'mutexPrint':       mutexPrint,
                'blue':             i['blue'],
                'red':              i['red'],
                'mapName':          i['mapName'],
                'timeout':          timeout
            })
    
    #print( pool.map(processJob, jobs_launcher) )
    #pool.close()
    #pool.join()
    
    if jobs_launcher:
        for x in pool.imap_unordered(processJob, jobs_launcher):
            mutexPrint.acquire()
            print("Job {} is over.".format(x) )
            mutexPrint.release()

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
    keywords['mutexPrint'].acquire()
    print( txt )
    keywords['mutexPrint'].release()

    # Wait end of fight
    while(not end):
        logging.debug( 'keywords={} ### args = {} ### i["popen"].poll()={}'.format(keywords, args, popen.poll()) )
        if popen.poll() is None:
            # Job not over.
            if int(time.time()-start) % 10 == 0:
                logging.debug( "popen.poll()={} ; popen.returncode={}".format( popen.poll(), popen.returncode) )
                txt = 'job {number} : T={time} sec. : still fighting...'.format( number=keywords['number'], time=int(time.time()-start) )
                logging.info( txt )
                keywords['mutexPrint'].acquire()
                print( txt )
                keywords['mutexPrint'].release()
            # Timeout : Terminate process + move job to end of Resume-File
            if keywords['timeout'] and int(time.time()-start) >= keywords['timeout']:
                # Terminate/Kill
                popen.terminate()
                if popen.poll() is None:
                    popen.kill()
                # Log
                txt = 'job {number} : T={time} sec. : Timeout of {timeout} seconds expired.'.format(
                    number=keywords['number'], time=int(time.time()-start), timeout=keywords['timeout'] )
                logging.warning( txt )
                keywords['mutexPrint'].acquire()
                print( txt )
                keywords['mutexPrint'].release()
                # Delete and add to the end the job from "Resume file"
                keywords['mutexResumeFile'].acquire()
                removeJobFromResumeFile( keywords['blue'], keywords['red'], keywords['mapName'] )
                addJobToResumeFile( keywords['blue'], keywords['red'], keywords['mapName'] )
                keywords['mutexResumeFile'].release()
                return keywords['number']
        else:
            returncode = popen.returncode
            end = time.time()
            result_name = createResultName(blue=keywords['blue'], red=keywords['red'])
            logging.debug( "popen.returncode={}".format( returncode ) )
            txt = 'job {number} : T={time} sec. : {result}'.format( number=keywords['number'], result=result_name[ returncode ], time=int(end-start) )
            logging.info( txt )
            keywords['mutexPrint'].acquire()
            print( txt )
            keywords['mutexPrint'].release()
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

def readJobFromResumeFile():
    "Read jobs of Resume-file. Return list."
    jobs_resume = list()
    # Read jobs_resume with file
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
    return jobs_resume

def writeJobToResumeFile(jobs_resume):
    "Write jobs of Resume-file. Return nothing."
    # Save to file the job's list
    with open(resumeFilename, 'w') as jobListFile:
        json.dump(jobs_resume, jobListFile)

def removeJobFromResumeFile( blue, red, mapName ):
    "Remove a job of Resume-file. Return nothing"
    # Initialize jobs_resume with file
    jobs_resume = readJobFromResumeFile()
    # Update jobs_resume
    jobs_resume.remove( {'blue': blue, 'red': red, 'mapName': mapName} )
    # Write jobs_resume in file
    writeJobToResumeFile(jobs_resume)
    txt = 'Resume file "{name}" completed : {jobs} job{plural}.'.format( name=resumeFilename, jobs=len(jobs_resume), plural='s' if len(jobs_resume) else '' )
    logging.info( txt )
    print(txt)

def addJobToResumeFile( blue, red, mapName ):
    "Add a job to Resume-file. Return nothing"
    # Initialize jobs_resume with file
    jobs_resume = readJobFromResumeFile()
    # Update jobs_resume
    jobs_resume.append(
        {
            'blue': blue,
            'red': red,
            'mapName': mapName
        })
    # Write jobs_resume in file
    writeJobToResumeFile(jobs_resume)
    txt = 'Resume file "{name}" completed : {jobs} job{plural}.'.format( name=resumeFilename, jobs=len(jobs_resume), plural='s' if len(jobs_resume) else '' )
    logging.info( txt )
    print(txt)

def readJobFromResultFile():
    "Read jobs of Result-file of the current day. Return list and Result-file name."
    jobs_results = list()
    resultsFilename = os.path.join(rootPath, prefixFileName+'results-list-'+datetime.date.today().isoformat()+'.json')
    # Read results already saved from file
    if os.path.isfile(resultsFilename):
        with open(resultsFilename, 'r') as resultsFileIO:
            jobs_results = json.load(resultsFileIO)
            txt = 'Result file "{name}" completed : {jobs} job{plural}.'.format( name=os.path.basename(resultsFilename), jobs=len(jobs_results), plural='s' if len(jobs_results) else '' )
            logging.info( txt )
            print(txt)
            #import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(jobs_resume)
    else:
        txt = 'Result file "{name}" : empty.'.format( name=os.path.basename(resultsFilename) )
        logging.info( txt )
        print( txt )
    return jobs_results, resultsFilename

def getListOfResultFile():
    prefix = prefixFileName+'results-list-'
    listOfRsultFile = tuple(m for m in os.listdir(rootPath)
                            if m[:len(prefix)] == prefix
                            and m[-5:].lower() == '.json')
    return listOfRsultFile

def readJobFromAllResultFile():
    "Read jobs of all Result-file. Return list."
    jobs_results = list()
    jobs_results_single = list()
    resultsFilename = getListOfResultFile()
    # Read results already saved from file
    for f in resultsFilename:
        if os.path.isfile( os.path.join(rootPath, f) ):
            with open(os.path.join(rootPath, f), 'r') as resultsFileIO:
                jobs_results_single = json.load(resultsFileIO)
                jobs_results += jobs_results_single
                txt = 'Result file "{name}" completed : {jobs} job{plural}.'.format(
                    name=f, jobs=len(jobs_results_single), plural='s' if len(jobs_results_single) else '' )
                logging.info( txt )
                print(txt)
                #import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(jobs_resume)
        else:
            txt = 'Result file "{name}" : empty.'.format( name=f )
            logging.info( txt )
            print( txt )
    return jobs_results

def addJobToResultFile( blue, red, mapName, returncode, start, end ):
    "Add a job to Result-file. Return nothing"
    jobs_results = list()
    jobs_results, resultsFilename = readJobFromResultFile()
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
        txt = 'Result file "{name}" completed : {jobs} job{plural}.'.format( name=os.path.basename(resultsFilename), jobs=len(jobs_results), plural='s' if len(jobs_results) else '' )
        logging.info( txt )
        print(txt)
# Multiprocessing function
#############



#############
# Init
rootPath = os.path.join(os.getcwd(),'www', os.path.splitext(os.path.basename(sys.argv[0]))[0])
if not os.path.isdir(rootPath):
    os.makedirs(rootPath)
configFile = 'config.xml'
configMapDirectory = './maps'
prefixFileName = os.path.splitext(os.path.basename(sys.argv[0]))[0]+'_'
resumeFilename = os.path.join(rootPath, prefixFileName+'job-list.json')
logsFilename = os.path.join(rootPath, prefixFileName+'logs-'+datetime.date.today().isoformat()+'.log')
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(filename=logsFilename, level=logging.INFO)
logging.basicConfig(filename=logsFilename, level=logging.ERROR)


result_txt = {0: "draw", 1: "blue wins", 2: "red wins",
              11: "blue error", 12: "red error", 255: "error"}
result_int = {value: key for (key, value) in result_txt.iteritems()}
result_int = {value: key for (key, value) in result_txt.iteritems()}

bluePlayer, redPlayer, mapName, players, playersParams, _ = readConfig(configFile)
playerName_params = {name: params for name, params in zip(players, playersParams)}

if __name__ == '__main__':
    #############
    # Reading of arguments
    parser = argparse.ArgumentParser(description="Automation of AIWar game. \
        This script is able to loop all combinations of games between players, maps and colors. \
        [Tips] If you want to stop the current jobs processing, kill first the python script and after AIWar.exe launched. \
        By this way, you prevent bad results to be register in Result-File")

    # Cancelled because defined just before launching the job
    #parser.add_argument("-g", "--gui", action="store_true", help="Show game on graphic user interface")
    parser.add_argument("-p", "--processes", type=int, help="Number of processes to use (maximum by default)")
    parser.add_argument("-t", "--timeout", type=int, default=0, help="Time limit of a job in seconds (infinite by default)")
    
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-v", "--verbose", action="store_true",
                        help="increase console verbosity")
    group1.add_argument("-q", "--quiet", action="store_true",
                        help="decrease console verbosity")
    
    sub_cmd = parser.add_subparsers(help="Select info, resume or deep of loop", dest='subparser_name')
    
    parser_info = sub_cmd.add_parser('info',
                                    help="get info about jobs to resume, cardinality of loops or processes")
    
    parser_resume = sub_cmd.add_parser('resume-jobs',
                                    help="resume jobs in 'Resume-File'")
    
    parser_resume = sub_cmd.add_parser('clean-resume-jobs',
                                    help="clean all jobs in 'Resume-File'")
    
    parser_charts = sub_cmd.add_parser('update-charts',
                                    help="update charts from 'Result-File'")
    
    parser_rounds = sub_cmd.add_parser('loop-rounds',
                                    help="launch AIWar for many rounds between 2 players")
    parser_rounds.add_argument("-n", "--nb-rounds",  type=int, default=1, help="number of rounds to play")
    parser_rounds.add_argument("-b", "--blue",  type=str, help="name of the blue player (from 'config.xml' by default)")
    parser_rounds.add_argument("-r", "--red",   type=str, help="name of the red player (from 'config.xml' by default)")
    parser_rounds.add_argument("-m", "--map",   type=str, help="name of the map (from 'config.xml' by default)")
    
    parser_maps = sub_cmd.add_parser('loop-maps',
                                  help="equivalent to 'loop-rounds' option for all maps in directory './maps'")
    parser_maps.add_argument("-n", "--nb-rounds",  type=int, default=1, help="number of rounds to play")
    parser_maps.add_argument("-b", "--blue",  type=str, help="name of the blue player (from 'config.xml' by default)")
    parser_maps.add_argument("-r", "--red",   type=str, help="name of the red player (from 'config.xml' by default)")
    
    parser_colors = sub_cmd.add_parser('loop-colors',
                                  help="equivalent to 'loop-maps' option and switch colors of players")
    parser_colors.add_argument("-n", "--nb-rounds",  type=int, default=1, help="number of rounds to play")
    parser_colors.add_argument("-b", "--blue",  type=str, help="name of the blue player (from 'config.xml' by default)")
    parser_colors.add_argument("-r", "--red",   type=str, help="name of the red player (from 'config.xml' by default)")
    
    parser_players = sub_cmd.add_parser('loop-players',
                                  help="equivalent to 'loop-colors' option with one player " \
                                  "against all players in the configuration file " \
                                  "'config.xml' without the player itself.")
    parser_players.add_argument("-n", "--nb-rounds",  type=int, default=1, help="number of rounds to play")
    parser_players.add_argument("-b", "--blue",  type=str, help="name of the hero player (blue player from 'config.xml' by default)")

    parser_complete = sub_cmd.add_parser('loop-complete',
                                  help="equivalent to 'loop-players' option for each players " \
                                  "in the configuration file 'config.xml'")
    parser_complete.add_argument("-n", "--nb-rounds",  type=int, default=1, help="number of round to play")
    
    args = parser.parse_args()

    # --verbose/--quiet
    if args.quiet:
        logging.basicConfig(filename=logsFilename, level=logging.ERROR)
    elif args.verbose:
        logging.basicConfig(filename=logsFilename, level=logging.DEBUG)
    else:
        logging.basicConfig(filename=logsFilename, level=logging.INFO)

    # --processes
    if args.processes and args.processes <= multiprocessing.cpu_count():
        nbProcesses = args.processes
    else:
        nbProcesses = multiprocessing.cpu_count()

    # --timeout
    if args.timeout:
        timeout = args.timeout
    else:
        timeout = None

    # info
    if args.subparser_name == 'info':
        # Resume-File size
        readJobFromResumeFile()
        #size = len( readJobFromResumeFile() )
        #print('"Resume-File" size = {}'.format(size))
        
        # Result-File size
        size = len( readJobFromAllResultFile() )
        print('"Result-File" total size = {}'.format(size))
        
        # Player number
        size = len( readConfig(configFile)[3] )
        print('Number of players = {}'.format(size))
        # Map number
        size = len( readMaps(configMapDirectory) )
        print('Number of maps = {}'.format(size))
        # loop-rounds size
        size = len( newRounds( *readConfig(configFile)[0:2], mapName=os.path.basename(readConfig(configFile)[2]) ) )
        print('loop-rounds minimum jobs = {}'.format(size))
        # loop-maps size
        size = len( newMaps( *readConfig(configFile)[0:2] ) )
        print('loop-maps minimum jobs = {}'.format(size))
        # loop-colors size
        size = len( newColors( *readConfig(configFile)[0:2] ) )
        print('loop-colors minimum jobs = {}'.format(size))
        # loop-players size
        size = len( newPlayers( *readConfig(configFile)[0:1] ) )
        print('loop-players minimum jobs = {}'.format(size))
        # loop-complete size
        size = len( newComplete() )
        print('loop-complete minimum jobs = {}'.format(size))
        # Number of processes max
        np_max = multiprocessing.cpu_count()
        print('Number of processes max = {}'.format(np_max))
    
    if args.subparser_name == 'resume-jobs':
        jobs_resume = list()
        # Read ResumeFile
        jobs_resume = readJobFromResumeFile()
        # Launch jobs
        allocateJob(jobs_resume)
        # update charts
        ################ TO DO - TO DO - TO DO - TO DO ##############

    if args.subparser_name == 'clean-resume-jobs':
        # Write void list to Resume-File
        jobs_resume = list()
        writeJobToResumeFile(jobs_resume)

    if args.subparser_name == 'update-charts':
        # update charts
        ################ TO DO - TO DO - TO DO - TO DO ##############
        # Add path to result file
        listOfResultFile = [os.path.join(rootPath, f) for f in getListOfResultFile()]
            
        publish_data = {'list-results-files': listOfResultFile,     \
                        'list-players': readConfig(configFile)[3],  \
                        'list-maps': readMaps(configMapDirectory),  \
                        'statistics-path': rootPath                 \
                        }
        PublishStatisticsAIWar.publish(publish_data)

    if args.subparser_name == 'loop-rounds':
        # Read Resume-File
        jobs_resume = readJobFromResumeFile()
        # Generate loop-rounds list
        nb_rounds = args.nb_rounds
        if args.blue:
            blue = args.blue
        else:
            blue = readConfig(configFile)[0]
        
        if args.red:
            red = args.red
        else:
            red = readConfig(configFile)[1]
        
        if args.map:
            mapName = args.map
        else:
            mapName = os.path.basename(readConfig(configFile)[2])
        
        try:
            jobs_resume += newRounds(blue, red, mapName, nb_rounds)
        except AIwarError as e:
            txt = 'loop-rounds : Error when create new jobs. Stopping work.' + str(e)
            logging.exception( txt )
            print( txt )
            exit()
        # Write Resume-File
        writeJobToResumeFile(jobs_resume)
        # launch jobs
        allocateJob(jobs_resume)
        # update charts
        ################ TO DO - TO DO - TO DO - TO DO ##############

    if args.subparser_name == 'loop-maps':
        # Read Resume-File
        jobs_resume = readJobFromResumeFile()
        # Generate loop-maps list
        nb_rounds = args.nb_rounds
        if args.blue:
            blue = args.blue
        else:
            blue = readConfig(configFile)[0]
        
        if args.red:
            red = args.red
        else:
            red = readConfig(configFile)[1]
        
        try:
            jobs_resume += newMaps(blue, red, nb_rounds)
        except AIwarError as e:
            txt = 'loop-maps : Error when create new jobs. Stopping work.' + str(e)
            logging.exception( txt )
            print( txt )
            exit()
        # Write Resume-File
        writeJobToResumeFile(jobs_resume)
        # launch jobs
        allocateJob(jobs_resume)
        # update charts
        ################ TO DO - TO DO - TO DO - TO DO ##############

    if args.subparser_name == 'loop-colors':
        # Read Resume-File
        jobs_resume = readJobFromResumeFile()
        # Generate loop-colors list
        nb_rounds = args.nb_rounds
        if args.blue:
            blue = args.blue
        else:
            blue = readConfig(configFile)[0]
        
        if args.red:
            red = args.red
        else:
            red = readConfig(configFile)[1]
        
        try:
            jobs_resume += newColors(blue, red, nb_rounds)
        except AIwarError as e:
            txt = 'loop-colors : Error when create new jobs. Stopping work.' + str(e)
            logging.exception( txt )
            print( txt )
            exit()
        # Write Resume-File
        writeJobToResumeFile(jobs_resume)
        # launch jobs
        allocateJob(jobs_resume)
        # update charts
        ################ TO DO - TO DO - TO DO - TO DO ##############

    if args.subparser_name == 'loop-players':
        # Read Resume-File
        jobs_resume = readJobFromResumeFile()
        # Generate loop-players list
        nb_rounds = args.nb_rounds
        if args.blue:
            blue = args.blue
        else:
            blue = readConfig(configFile)[0]
        
        try:
            jobs_resume += newPlayers(blue, nb_rounds)
        except AIwarError as e:
            txt = 'loop-players : Error when create new jobs. Stopping work.' + str(e)
            logging.exception( txt )
            print( txt )
            exit()
        # Write Resume-File
        writeJobToResumeFile(jobs_resume)
        # launch jobs
        allocateJob(jobs_resume)
        # update charts
        ################ TO DO - TO DO - TO DO - TO DO ##############

    if args.subparser_name == 'loop-complete':
        # Read Resume-File
        jobs_resume = readJobFromResumeFile()
        # Generate loop-complete list
        nb_rounds = args.nb_rounds
        
        try:
            jobs_resume += newComplete(nb_rounds)
        except AIwarError as e:
            txt = 'loop-complete : Error when create new jobs. Stopping work.' + str(e)
            logging.exception( txt )
            print( txt )
            exit()
        # Write Resume-File
        writeJobToResumeFile(jobs_resume)
        # launch jobs
        allocateJob(jobs_resume)
        # update charts
        ################ TO DO - TO DO - TO DO - TO DO ##############



    #############
    # Build charts



    txt = '...End'
    logging.info( txt )
    print(txt)
