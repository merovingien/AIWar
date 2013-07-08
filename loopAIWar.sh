#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopAIWar.sh - launch 'loopPlayers.sh' for each players in the configuration file 'config.xml'. Every players will fight each others."
    echo ""
    echo "SYNOPSIS : loopAIWar.sh roundToPlay"
    echo ""
    echo "DESCRIPTION : "
    echo "   roundToPlay : Number of rounds to play with each colors and each maps and against each players"
    echo ""
else
    # Variables externes
    export descriptionAIWarVersion_Rounds
    
    # Variables exportees
    
    # Variables locales
    rounds_AIWar=$1
    
    for player_AIWar in `grep -A 1 "<player>" config.xml | grep "<name>" | cut -f 2 -d ">" | cut -f 1 -d "<"`;
    do
        echo "<== Start to play ${player_AIWar} at `date +%d/%m/%Y` `date +%Hh%M`."
        echo "    Currently playing ${player_AIWar}..."
        . ./loopPlayers.sh ${player_AIWar} $rounds_AIWar onlyFileName
        echo "==> Playing ${player_AIWar} is over since `date +%d/%m/%Y` `date +%Hh%M`."
        echo ""
    done
    
    echo ""
    echo "   Ver.AIWar = $descriptionAIWarVersion_Rounds"
fi
