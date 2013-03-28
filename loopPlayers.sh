#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopPlayers.sh - launch 'loopColors.sh' for each players in the configuration file 'config.xml' without the player itself."
    echo ""
    echo "SYNOPSIS : loopPlayers.sh Player roundToPlay"
    echo ""
    echo "DESCRIPTION : "
    echo "   Player      : Name of the player"
    echo "   roundToPlay : Number of rounds to play with each colors and each maps and against each players"
    echo ""
else
    for player in `grep -A 1 "<player>" config.xml | grep "<name>" | cut -f 2 -d ">" | cut -f 1 -d "<"`;
    do
        if [ "$1" != "$player" ];then
            . ./loopColors.sh $1 $player $2
        fi
    done
fi
