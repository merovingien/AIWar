#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopAIWar.sh - launch AIWar for many rounds."
    echo ""
    echo "SYNOPSIS : loopAIWar.sh [bluePlayer redPlayer mapFile] roundToPlay"
    echo "           (take configuration of 'config.xml' if all [bluePlayer redPlayer mapFile] missing)"
    echo ""
    echo "DESCRIPTION : "
    echo "   bluePlayer  : Name of the blue player"
    echo "   redPlayer   : Name of the red player"
    echo "   mapFile     : Name of the map"
    echo "   roundToPlay : Number of rounds to play"
    echo ""
else
    blueScore=0
    redScore=0
    draw=0
    error=0

    if [ $# = "1" ];then
        boucle=let"$1"
    else
        boucle=let"$4"
    fi

    for i in `seq 1 $4`;
    do
        if [ "$#" = "1" ];then
            ./AIWar --file config.xml --renderer dummy  >/dev/null 2>&1
        else
            ./AIWar --blue $1 --red $2 --map $3 --renderer dummy  >/dev/null 2>&1
        fi
        resultat=$?
        #echo $resultat

        if [ $resultat = "0" ];then
                let "draw += 1"
        elif [ $resultat = "1" ];then
                let "blueScore += 1"
        elif [ $resultat = "2" ];then
                let "redScore += 1"
        elif [ $resultat = "255" ];then
                let "error += 1"
        fi
    done

    # Afficher les logs
    if [ "$#" -lt "5" ] || [ "$5" != "nolog" ];then
        echo "Resultat final:  *** $1 Vs $2 ***"
        echo "   Map          : $3"
        echo "   Joueur bleu  : $1 = $blueScore"
        echo "   Joueur rouge : $2 = $redScore"
        echo ""
        echo "   Egalite = $draw"
        echo "   Erreur  = $error"
    fi

    #echo "blueScore=$blueScore - redScore=$redScore - draw=$draw - error=$error"
fi

