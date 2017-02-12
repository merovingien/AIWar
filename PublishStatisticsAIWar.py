from __future__ import print_function
import os           # listdir(), path.join()
import subprocess   # Popen()
import logging
import json         # dump(), load()
import datetime     # date.today().isoformat()
import copy         # deepcopy()


class AIwarError(Exception):
    pass

def readFile(filepath):
    "Read file"
    data = list()
    if filepath and os.path.isfile(filepath):
        with open(filepath, 'r') as rf:
            data = rf.read()
    return data
    
def writeFile(filepath, data):
    "Write file"
    if filepath and os.path.exists(os.path.dirname(filepath)):
        with open(filepath, 'w') as rf:
            rf.write(data)
    
def readJSONFile(filepath):
    data = list()
    # Read file
    if filepath and os.path.isfile(filepath):
        with open(filepath, 'r') as rf:
            data = json.load(rf)
    return data
    
def readResultFile(filepath):
    "Read jobs of Result-file of the current day. Return list and Result-file name."
    jobs_results = list()
    # Read results already saved from file
    if filepath and os.path.isfile(filepath):
        jobs_results = readJSONFile(filepath)
        txt = 'Result file "{name}" : {jobs} job{plural}.'.format( name=os.path.basename(filepath), jobs=len(jobs_results), plural='s' if len(jobs_results) else '' )
        #logging.info( txt )
        print(txt)
    elif filepath:
        txt = 'Result file "{name}" : empty.'.format( name=os.path.basename(filepath) )
        #logging.info( txt )
        print(txt)
    return jobs_results

def readStatisticsFile(filepath):
    "Read jobs of Result-file of the current day. Return list and Result-file name."
    statistics = list()
    # Read results already saved from file
    if filepath and os.path.isfile(filepath):
        statistics = readJSONFile(filepath)
        txt = 'Statistics file "{name}" : {jobs} data{plural}.'.format( name=os.path.basename(filepath), jobs=len(statistics), plural='s' if len(statistics) else '' )
        #logging.info( txt )
        print(txt)
    elif filepath:
        txt = 'Statistics file "{name}" : empty.'.format( name=os.path.basename(filepath) )
        #logging.info( txt )
        print(txt)
    return statistics

def writeStatisticsOverview(filepath, data):
    "Write statistics to file. Return nothing."
    # Save to file
    if filepath and data:
        with open(filepath, 'w') as f:
            json.dump(data, f)

def publish(args):
    "Create all statistics. return nothing."
    #print('publish() : ',args)
    
    # Args:
    #'list-results-files': list_results_files
    #'list-players': list_players
    #'list-maps': list_maps
    #'statistics-path': statistics_path
    #'template-path': template_path
    #'output-path': output_path
    
    # Publish statistics : overview
    statistics = createStatistics_overview(args)
    publishStatistics_overview(args, statistics)
    
    # Publish statistics : maps
    statistics = createStatistics_maps(args)
    publishStatistics_maps(args, statistics)
    
    # Publish statistics : players
    statistics = createStatistics_players(args)
    publishStatistics_players(args, statistics)

def TU_overview():
    listOfResultFile = ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json']
    args = { \
        'list-results-files': ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json'], \
        'statistics-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar', \
        'template-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\template', \
        'output-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\results', \
        'list-maps': ('map.xml', 'map_BackToBack.xml', 'map_FollowTheWhiteRabbit.xml', 'map_NoRulZ.xml', 'map_test.xml', 'map_ToInfinityAndBeyond.xml'), \
        'list-players': ('TEAM_DUMMY', 'PYTHON_TEAM', 'Merovingien-3', 'Merovingien-2', 'Antoine', 'Clement', 'Shuriken-0', 'GuiGui-6', 'GuiGui-1', 'GuiGui-2', 'GuiGui-3', 'GuiGui-4', 'GuiGui-5') \
        }
    statistics = createStatistics_overview(args)
    print(statistics)
    publishStatistics_overview(args, statistics)
    return statistics
    
def TU_maps():
    listOfResultFile = ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json']
    args = { \
        'list-results-files': ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json'], \
        'statistics-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar', \
        'template-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\template', \
        'output-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\results', \
        'list-maps': ('map.xml', 'map_BackToBack.xml', 'map_FollowTheWhiteRabbit.xml', 'map_NoRulZ.xml', 'map_test.xml', 'map_ToInfinityAndBeyond.xml'), \
        'list-players': ('TEAM_DUMMY', 'PYTHON_TEAM', 'Merovingien-3', 'Merovingien-2', 'Antoine', 'Clement', 'Shuriken-0', 'GuiGui-6', 'GuiGui-1', 'GuiGui-2', 'GuiGui-3', 'GuiGui-4', 'GuiGui-5') \
        }
    statistics = createStatistics_maps(args)
    print(statistics)
    publishStatistics_maps(args, statistics)
    return statistics
    
def TU_players():
    listOfResultFile = ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json']
    args = { \
        'list-results-files': ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json'], \
        'statistics-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar', \
        'template-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\template', \
        'output-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\results', \
        'list-maps': ('map.xml', 'map_BackToBack.xml', 'map_FollowTheWhiteRabbit.xml', 'map_NoRulZ.xml', 'map_test.xml', 'map_ToInfinityAndBeyond.xml'), \
        'list-players': ('TEAM_DUMMY', 'PYTHON_TEAM', 'Merovingien-3', 'Merovingien-2', 'Antoine', 'Clement', 'Shuriken-0', 'GuiGui-6', 'GuiGui-1', 'GuiGui-2', 'GuiGui-3', 'GuiGui-4', 'GuiGui-5') \
        }
    statistics = createStatistics_players(args)
    print(statistics)
    publishStatistics_players(args, statistics)
    return statistics
    
def createStatistics_overview(args):
    "Create statistics 'overview'. return list of statistics."
    sp = dict()
    # Read each Result-File
    for f in args['list-results-files']:
        if f:
            resultFile = readResultFile(f);
            #print('for f in args[list-results-files]: resultFile : ',resultFile[0],resultFile[-1])
            
            # Count win/lose for each player
            for name in args['list-players']:
                #print('for p in args[list-players]: name : {}'.format(name))
                playerGames = [g for g in resultFile if g['blue']['name'] == name or g['red']['name'] == name ]
                win = 0
                lose = 0
                draw = 0
                for g in playerGames:
                    if g['blue']['name'] == name and 'blue wins' in g['result']    \
                       or g['blue']['name'] == name and 'red error' in g['result'] \
                       or g['red']['name'] == name and 'red wins' in g['result']   \
                       or g['red']['name'] == name and 'blue error' in g['result']:
                        win += 1
                    elif g['blue']['name'] == name and 'red wins' in g['result']    \
                       or g['blue']['name'] == name and 'blue error' in g['result'] \
                       or g['red']['name'] == name and 'blue wins' in g['result']   \
                       or g['red']['name'] == name and 'red error' in g['result']:
                         lose += 1
                    elif 'draw' in g['result']:
                         draw += 1
                if name not in sp.keys():
                    sp[name] = {'name': name, 'win':0, 'lose':0, 'draw':0}
                sp[name]['win'] += win
                sp[name]['lose'] += lose
                sp[name]['draw'] += draw

    # (rank, {name, win, lose, draw})
    overview = [(n, infos) for n, (name, infos) in enumerate(sorted(
        sp.items(),key=lambda kv: 10*kv[1]['win']+kv[1]['lose']+3*kv[1]['draw'],reverse=True), 1)]

    # Write to file Statistics-Overview
    statFile = os.path.join( args['statistics-path'], 'statistics-Overview.json')
    writeStatisticsOverview(statFile, overview)
##    print('overview : ',overview)
##    for k, v in overview['Top-Players'].iteritems():
##        print("overview['Top-Players'] = ", k,':',v)
    return overview
    


def createStatistics_maps(args):
    "Create statistics 'maps'. return list of statistics."
    
    # Blue/Red ratio winner
    # {mapName, blue, red}
    brRatio = dict()
    
    # Duration of game
    # {mapName, samples:[{duration, number}]}
    duration = dict()
    
    # ranking of players
    # {mapName, players:[{playerName, rank, blue, red}]}
    ranking = dict()
    sp = dict()
    
    # Read each Result-File
    for f in args['list-results-files']:
        if f:
            resultFile = readResultFile(f);
            
            # Count win/lose for each player
            for map_ in args['list-maps']:
                if map_ not in brRatio.keys():
                    brRatio[map_] = {'mapName': map_, 'blue':0, 'red':0}
                if map_ not in duration.keys():
                    duration[map_] = {'mapName': map_, 'samples': list()}
                    # '[{duration, number}]' added later
                if map_ not in ranking.keys():
                    ranking[map_] = {'mapName': map_, 'players': list()}
                    # '[{playerName, rank, blue, red}]' added later
                
                # Blue/Red ratio winner
                brRatio[map_]['blue'] += len([g for g in resultFile if g['map'] == map_ and (g['result'] == 'blue wins' or g['result'] == 'red error') ])
                brRatio[map_]['red'] += len([g for g in resultFile if g['map'] == map_ and (g['result'] == 'red wins' or g['result'] == 'blue error') ])
                
                # Duration of game
                durationList = [int(g['end']-g['start']) for g in resultFile if g['map'] == map_]
                duration[map_]['samples'] += [{'duration': d, 'number': durationList.count(d)} for d in set(durationList)]
                
                # loop on each player
                for name in args['list-players']:
                    #print('for p in args[list-players]: name : {}'.format(name))
                    playerGames = [g for g in resultFile if g['map'] == map_ and (g['blue']['name'] == name or g['red']['name'] == name) ]
                    win = 0
                    lose = 0
                    draw = 0
                    for g in playerGames:
                        if g['blue']['name'] == name and 'blue wins' in g['result']    \
                           or g['blue']['name'] == name and 'red error' in g['result'] \
                           or g['red']['name'] == name and 'red wins' in g['result']   \
                           or g['red']['name'] == name and 'blue error' in g['result']:
                            win += 1
                        elif g['blue']['name'] == name and 'red wins' in g['result']    \
                           or g['blue']['name'] == name and 'blue error' in g['result'] \
                           or g['red']['name'] == name and 'blue wins' in g['result']   \
                           or g['red']['name'] == name and 'red error' in g['result']:
                            lose += 1
                        elif 'draw' in g['result']:
                            draw += 1
                    if map_ not in sp.keys():
                        sp[map_] = dict()
                    if name not in sp[map_].keys():
                        sp[map_][name] = {'map': map_, 'name': name, 'win':0, 'lose':0, 'draw':0}
                    sp[map_][name]['win'] += win
                    sp[map_][name]['lose'] += lose
                    sp[map_][name]['draw'] += draw
    
    for map_ in args['list-maps']:
        # {map:(rank, {name, win, lose, draw})}
        ranking[map_]['players'] = [(n, infos) for n, (name, infos) in enumerate(sorted(
            sp[map_].items(),key=lambda kv: kv[1]['win']-kv[1]['lose']+(kv[1]['draw'])/(1+kv[1]['win']+kv[1]['lose']),reverse=True), 1)]

    # Write to file Statistics-Overview
    overview = {'ratio-blue-red': brRatio, 'duration': duration, 'ranking': ranking}
    statFile = os.path.join( args['statistics-path'], 'statistics-Maps.json')
    writeStatisticsOverview(statFile, overview)
    return overview

def createStatistics_players(args):
    "Create statistics 'players'. return list of statistics."
    
    # Blue/Red ratio winner
    # {playerName, blue, red}
    brRatio = dict()
    
    # Overview win/lose/draw ratio
    # {playerName, win, draw, lose}
    overRatio = dict()
    
    # Map win/lose/draw ratio
    # {playerName, maps:[{playerName, mapName, win, draw, lose}]}
    mapRatio = dict()
    
    # Player win/lose/draw ratio
    # {playerName, players:[{playerName, opponentName, win, draw, lose}]}
    playerRatio = dict()
    
    # Duration of game
    # {playerName, samples:[{duration, number}]}
    duration = dict()
    
    # Read each Result-File
    for f in args['list-results-files']:
        if f:
            resultFile = readResultFile(f);
            
            # loop on each player
            for playerName in args['list-players']:
                if playerName not in brRatio.keys():
                    brRatio[playerName] = {'playerName': playerName, 'blue':0, 'red':0}
                if playerName not in overRatio.keys():
                    overRatio[playerName] = {'playerName': playerName, 'win':0, 'lose':0, 'draw':0}
                if playerName not in mapRatio.keys():
                    mapRatio[playerName] = dict()
                    # '[{playerName, mapName, win, draw, lose}]' added later
                if playerName not in playerRatio.keys():
                    playerRatio[playerName] = dict()
                    # '[{playerName, opponentName, win, draw, lose}]' added later
                if playerName not in duration.keys():
                    duration[playerName] = {'playerName': playerName, 'samples': list()}
                    # '[{duration, number}]' added later
                
                # Blue/Red ratio winner
                brRatio[playerName]['blue'] += len([g for g in resultFile if g['blue']['name'] == playerName and (g['result'] == 'blue wins' or g['result'] == 'red error') ])
                brRatio[playerName]['red'] += len([g for g in resultFile if g['red']['name'] == playerName and (g['result'] == 'red wins' or g['result'] == 'blue error') ])
                
                # Overview win/lose/draw ratio
                # {playerName, win, draw, lose}
                overRatio[playerName]['win'] += len([g for g in resultFile 
                                                     if (g['blue']['name'] == playerName and (g['result'] == 'blue wins' or g['result'] == 'red error')) 
                                                     or (g['red']['name'] == playerName and (g['result'] == 'red wins' or g['result'] == 'blue error')) ])
                overRatio[playerName]['draw'] += len([g for g in resultFile if (g['red']['name'] == playerName or g['blue']['name'] == playerName) and g['result'] == 'draw' ])
                overRatio[playerName]['lose'] += len([g for g in resultFile 
                                                     if (g['blue']['name'] == playerName and (g['result'] == 'red wins' or g['result'] == 'blue error')) 
                                                     or (g['red']['name'] == playerName and (g['result'] == 'blue wins' or g['result'] == 'red error')) ])
                
                # Duration of game
                # {playerName, samples:[{duration, number}]}
                durationList = [int(g['end']-g['start']) for g in resultFile if g['blue']['name'] == playerName or g['red']['name'] == playerName]
                duration[playerName]['samples'] += [{'duration': d, 'number': durationList.count(d)} for d in set(durationList)]

                # Player win/lose/draw ratio
                # {playerName, players:[{playerName, opponentName, win, draw, lose}]}
                for on in args['list-players']:
                    if on != playerName:
                        # Stats against other players
                        w = len([g for g in resultFile 
                                 if (g['blue']['name'] == playerName and g['red']['name'] == on and (g['result'] == 'blue wins' or g['result'] == 'red error')) 
                                 or (g['red']['name'] == playerName and g['blue']['name'] == on and (g['result'] == 'red wins' or g['result'] == 'blue error')) ])
                        d = len([g for g in resultFile 
                                 if (g['blue']['name'] == playerName and g['red']['name'] == on and g['result'] == 'draw') 
                                 or (g['red']['name'] == playerName and g['blue']['name'] == on and g['result'] == 'draw') ])
                        l = len([g for g in resultFile 
                                 if (g['blue']['name'] == playerName and g['red']['name'] == on and (g['result'] == 'red wins' or g['result'] == 'blue error')) 
                                 or (g['red']['name'] == playerName and g['blue']['name'] == on and (g['result'] == 'blue wins' or g['result'] == 'red error')) ])
                        if on not in playerRatio[playerName].keys():
                            # add new player in list
                            playerRatio[playerName][on] = {'playerName': playerName, 'opponentName': on, 'win': w, 'draw': d, 'lose': l}
                        else:
                            # update player in list
                            playerRatio[playerName][on]['win'] += w
                            playerRatio[playerName][on]['draw'] += d
                            playerRatio[playerName][on]['lose'] += l
                
                # Map win/lose/draw ratio
                # {playerName, maps:[{playerName, mapName, win, draw, lose}]}
                for map_ in args['list-maps']:
                    w = len([g for g in resultFile 
                                                 if (g['blue']['name'] == playerName and g['map'] == map_ and (g['result'] == 'blue wins' or g['result'] == 'red error')) 
                                                 or (g['red']['name'] == playerName and g['map'] == map_ and (g['result'] == 'red wins' or g['result'] == 'blue error')) ])
                    d = len([g for g in resultFile 
                                                 if (g['blue']['name'] == playerName and g['map'] == map_ and g['result'] == 'draw') 
                                                 or (g['red']['name'] == playerName and g['map'] == map_ and g['result'] == 'draw') ])
                    l = len([g for g in resultFile 
                                                 if (g['blue']['name'] == playerName and g['map'] == map_ and (g['result'] == 'red wins' or g['result'] == 'blue error')) 
                                                 or (g['red']['name'] == playerName and g['map'] == map_ and (g['result'] == 'blue wins' or g['result'] == 'red error')) ])
                    if map_ not in mapRatio[playerName].keys():
                        # add new map in list
                        mapRatio[playerName][map_] = {'playerName': playerName, 'mapName': map_, 'win': w, 'draw': d, 'lose': l}
                    else:
                        # update map in list
                        mapRatio[playerName][map_]['win'] += w
                        mapRatio[playerName][map_]['draw'] += d
                        mapRatio[playerName][map_]['lose'] += l
    
    for playerName in args['list-players']:
        playerRatio[playerName] = [(n, infos) for n, (name, infos) in enumerate(sorted(
            playerRatio[playerName].items(),key=lambda kv: kv[1]['win']-kv[1]['lose']+(kv[1]['draw'])/(1+kv[1]['win']+kv[1]['lose']),reverse=True), 1)]
        mapRatio[playerName] = [(n, infos) for n, (name, infos) in enumerate(sorted(
            mapRatio[playerName].items(),key=lambda kv: kv[1]['win']-kv[1]['lose']+(kv[1]['draw'])/(1+kv[1]['win']+kv[1]['lose']),reverse=True), 1)]
        
    # Write to file Statistics-Overview
    overview = {'ratio-blue-red': brRatio, 'ratio-win-lose-draw': overRatio, 'ratio-maps': mapRatio, 'ratio-players': playerRatio, 'duration': duration}
    statFile = os.path.join( args['statistics-path'], 'statistics-Players.json')
    writeStatisticsOverview(statFile, overview)
    return overview


def publishStatistics_overview(args, statistics):
    "Create HTML output of 'overview' statistics. return nothing."
    # Read 'overview' template File
    template = readFile( os.path.join(args['template-path'],'template_RGraph_statistics-Overview.html') )
    
    # Replace '##...##' by value in argument 'statistics'
    # '##heightHBAR##', '##PlayersList##', '##PlayersWinDrawLoseList##'
    template = template.replace('##heightHBAR##', str(int(len(statistics)*30+80)) )
    template = template.replace('##PlayersList##', json.dumps([infos['name'] for rank, infos in statistics]) )
    template = template.replace('##PlayersWinDrawLoseList##', json.dumps([ [infos['win'],infos['draw'],infos['lose']] for rank, infos in statistics ]) )
    
    # Write to file
    writeFile( os.path.join(args['output-path'],'RGraph_statistics-Overview.html'), template)
    
def publishStatistics_maps(args, statistics):
    "Create HTML output of 'maps' statistics. return nothing."
    # Read 'maps' template File
    template = readFile( os.path.join(args['template-path'],'template_RGraph_statistics-Maps.html') )
    
    # Iterate on all maps in argument 'statistics'
    for map_ in args['list-maps']:
        # # Copy deeply template in local variable
        c = copy.deepcopy(template)
        # # Replace '##...##' by value in argument 'statistics'
        # ##MapName##   ##heightHBAR##   ##WinColor##   ##DurationList##   ##NumberList##   
        # ##PlayersList##   ##PlayersWinDrawLoseList##
        c = c.replace('##MapName##', os.path.splitext(map_)[0] )
        c = c.replace('##heightHBAR##', str(int(len(statistics['ranking'][map_]['players'])*30+80)) )
        c = c.replace('##WinColor##', json.dumps([statistics['ratio-blue-red'][map_]['blue'], statistics['ratio-blue-red'][map_]['red']]) )
        # RGraph.Line bugs if data are void list '[]', so I add '[0]' to fix it.
        tmp_duration, tmp_number = [sample['duration'] for sample in statistics['duration'][map_]['samples']], [sample['number'] for sample in statistics['duration'][map_]['samples']]
        if not len(tmp_duration):
            tmp_duration.append(0)
            tmp_number.append(0)
        c = c.replace('##DurationList##', json.dumps(tmp_duration) )
        c = c.replace('##NumberList##', json.dumps(tmp_number) )
        c = c.replace('##PlayersList##', json.dumps([player['name'] for rank, player in statistics['ranking'][map_]['players']]) )
        c = c.replace('##PlayersWinDrawLoseList##', json.dumps([ [player['win'],player['draw'],player['lose']] for rank, player in statistics['ranking'][map_]['players'] ]) )
        # # Write to file for this map
        writeFile( os.path.join(args['output-path'],'RGraph_statistics-Maps-'+ os.path.splitext(map_)[0] +'.html'), c)
        
def publishStatistics_players(args, statistics):
    "Create HTML output of 'players' statistics. return nothing."
    # Read 'players' template File
    template = readFile( os.path.join(args['template-path'],'template_RGraph_statistics-Players.html') )
    
    # Iterate on all players in argument 'statistics'
    for player in args['list-players']:
        # # Copy deeply template in local variable
        c = copy.deepcopy(template)
        # # Replace '##...##' by value in argument 'statistics'
        # ##PlayerName##   ##heightHBAR-Player##   ##heightHBAR-Maps##   
        # ##WinColor##   ##WinDrawLose##   ##PlayersList##   ##PlayersWinDrawLoseList##
        # ##MapsList##   ##MapsWinDrawLoseList##   ##DurationList##   ##NumberList##
        c = c.replace('##PlayerName##', player )
        c = c.replace('##heightHBAR-Player##', str(int(len(statistics['ratio-players'][player])*30+80)) )
        c = c.replace('##heightHBAR-Maps##', str(int(len(statistics['ratio-maps'][player])*30+80)) )
        c = c.replace('##WinColor##', json.dumps([statistics['ratio-blue-red'][player]['blue'], statistics['ratio-blue-red'][player]['red']]) )
        c = c.replace('##WinDrawLose##', json.dumps([statistics['ratio-win-lose-draw'][player]['win'], statistics['ratio-win-lose-draw'][player]['draw'], statistics['ratio-win-lose-draw'][player]['lose']]) )
        c = c.replace('##PlayersList##', json.dumps([infos['opponentName'] for rank, infos in statistics['ratio-players'][player]]) )
        c = c.replace('##PlayersWinDrawLoseList##', json.dumps([ [infos['win'],infos['draw'],infos['lose']] for rank, infos in statistics['ratio-players'][player]]) )
        c = c.replace('##MapsList##', json.dumps([infos['mapName'] for rank, infos in statistics['ratio-maps'][player]]) )
        c = c.replace('##MapsWinDrawLoseList##', json.dumps([ [infos['win'],infos['draw'],infos['lose']] for rank, infos in statistics['ratio-maps'][player]]) )
        # RGraph.Line bugs if data are void list '[]', so I add '[0]' to fix it.
        tmp_duration, tmp_number = [sample['duration'] for sample in statistics['duration'][player]['samples']], [sample['number'] for sample in statistics['duration'][player]['samples']]
        if not len(tmp_duration):
            tmp_duration.append(0)
            tmp_number.append(0)
        c = c.replace('##DurationList##', json.dumps(tmp_duration) )
        c = c.replace('##NumberList##', json.dumps(tmp_number) )
        # # Write to file for this player
        writeFile( os.path.join(args['output-path'],'RGraph_statistics-Players-'+ player +'.html'), c)
    

#TU_createStatistics_overview()
#TU_createStatistics_maps()
#TU_createStatistics_players()