#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopColors.sh - launch 'loopMaps.sh' twice and switch colors of players."
    echo ""
    echo "SYNOPSIS : loopColors.sh Player1 Player2 roundToPlay"
    echo ""
    echo "DESCRIPTION : "
    echo "   Player1     : Name of the player 1"
    echo "   Player2     : Name of the player 2"
    echo "   roundToPlay : Number of rounds to play with each colors and each maps"
    echo ""
else
    export blueScoreTotal
    export redScoreTotal

    scorePlayer1=0
    scorePlayer2=0

    echo "Resultat final par map (bi-couleur) :  *** $1 Vs $2 ***"
        . ./loopMaps.sh $1 $2 $3 noheader
        let "scorePlayer1 += blueScoreTotal"
        let "scorePlayer2 += redScoreTotal"
        
        echo

        . ./loopMaps.sh $2 $1 $3 noheader
        let "scorePlayer2 += blueScoreTotal"
        let "scorePlayer1 += redScoreTotal"


    # Resultat total
    if [ $scorePlayer1 -eq $scorePlayer2 ];then
        echo " *** EGALITE *** (par $scorePlayer1 a $scorePlayer2)"
    elif [ $scorePlayer1 -gt $scorePlayer2 ];then
        echo " *** VAINQUEUR === $1 *** (par $scorePlayer1 a $scorePlayer2)"
    else
        echo " *** VAINQUEUR === $2 ***  (par $scorePlayer2 a $scorePlayer1)"
    fi
    echo
fi
