#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopMaps.sh - launch 'loopRounds.sh' for all maps in directory './maps'."
    echo ""
    echo "SYNOPSIS : loopMaps.sh Player1 Player2 roundToPlay [verbose]"
    echo ""
    echo "DESCRIPTION : "
    echo "   Player1  : Name of the blue player"
    echo "   Player2   : Name of the red player"
    echo "   roundToPlay : Number of rounds to play on each map"
    echo "   verbose     : Customize the trace on terminal."
    echo "                 This is used when loopMaps.sh is called from a parent bash script."
    echo "                 If missing, everything is written to the terminal."
    echo "                 Can be 2 values : 'nolog' or 'noheader'."
    echo "                  - nolog    = nothing is written to the terminal"
    echo "                  - noheader = no header and no tailer written to the terminal"
    echo ""
else
    # Variables externes
    export templatePath_Rounds
    export filePath_Rounds
    export blueScore_Rounds
    export redScore_Rounds
    export blueError_Rounds
    export redError_Rounds
    export draw_Rounds
    export error_Rounds
    export descriptionVersionPlayer1_Rounds
    export descriptionVersionPlayer2_Rounds
    export descriptionAIWarVersion_Rounds
    export installerRGraph_Rounds
    export jsonBody_Rounds
    export jsonTail_Rounds
    

    # Variables exportees
    blueScoreTotal_Maps=0
    redScoreTotal_Maps=0
    drawScoreTotal_Maps=0
    blueScore_Maps[0]=0
    redScore_Maps[0]=0
    DrawScore_Maps[0]=0
    mapName_Maps[0]=""
    mapsList1_Maps=""
    mapsList2_Maps=""
    mapsScoreList_Maps_RGraph=""
    mapsScoreList_Maps_ChartJs_Player1=""
    mapsScoreList_Maps_ChartJs_Player2=""
    mapsScoreList_Maps_ChartJs_Draw=""
    heightHBAR_Maps=0
    jsonHead_Maps=""
    jsonBody_Maps=""

    # Variables locales
    player1_Maps=$1
    player2_Maps=$2
    rounds=$3
    fileName=""
    descriptionDate=""
    descriptionHour=""
    descriptionType=""

    # Afficher les logs
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        echo "Resultat final par map :  *** ${player1_Maps} Vs ${player2_Maps} ***"
    fi

    indice=0
    for map in `ls maps/*.xml`;
    do
        . ./loopRounds.sh $1 $2 $map $3 nolog
        blueScore_Maps[indice]=$blueScore_Rounds
        redScore_Maps[indice]=$redScore_Rounds
        DrawScore_Maps[indice]=$draw_Rounds
        mapName_Maps[indice]=`echo "$map" | cut -f 2 -d "/"`
        let "blueScoreTotal_Maps += blueScore_Rounds"
        let "redScoreTotal_Maps += redScore_Rounds"
        let "drawScoreTotal_Maps += draw_Rounds"
        
        if [ "$#" -lt "4" ] || [ "$4" != "nolog" ];then
            echo "   [Bleu]$1=$blueScore_Rounds  [Rouge]$2=$redScore_Rounds  Egalite=$draw_Rounds  Bug(Bleu/Rouge/Config)=$blueError_Rounds/$redError_Rounds/$error_Rounds  [Map]$map"
        fi

        # Enregistrer le resultat JSON
        if [ -n "$jsonBody_Maps" ];then
            jsonBody_Maps=`echo "${jsonBody_Maps},"; echo "${jsonBody_Rounds}"`
        else
            jsonBody_Maps=`echo "${jsonBody_Rounds}"`
        fi

        let "indice += 1"
    done

    # Resultat total
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        if [ $blueScoreTotal_Maps -eq $redScoreTotal_Maps ];then
            echo " *** EGALITE *** (par $blueScoreTotal_Maps a $redScoreTotal_Maps)"
        elif [ $blueScoreTotal_Maps -gt $redScoreTotal_Maps ];then
            echo " *** VAINQUEUR === ${player1_Maps} *** (par $blueScoreTotal_Maps a $redScoreTotal_Maps)"
        else
            echo " *** VAINQUEUR === ${player2_Maps} ***  (par $redScoreTotal_Maps a $blueScoreTotal_Maps)"
        fi
        echo ""
        echo "   Ver.AIWar = $descriptionAIWarVersion_Rounds"
        echo "$installerRGraph_Rounds"
    fi


    # Initialiser les listes de resultats
    for i in `seq 0 $indice`; do
        if [ -n "${mapName_Maps[*]}" ] && [ -n "${mapName_Maps[$i]}" ];then
            if [ -n "$mapsList1_Maps" ];then
                mapsList1_Maps=`echo "$mapsList1_Maps, (${i})${mapName_Maps[$i]}"`
                mapsList2_Maps=`echo "$mapsList2_Maps,'map_${i}'"`
                mapsScoreList_Maps_RGraph=`echo "$mapsScoreList_Maps_RGraph,[${blueScore_Maps[$i]},${redScore_Maps[$i]},${DrawScore_Maps[$i]}]"`
                mapsScoreList_Maps_ChartJs_Player1=`echo "$mapsScoreList_Maps_ChartJs_Player1, ${blueScore_Maps[$i]}"`
                mapsScoreList_Maps_ChartJs_Player2=`echo "$mapsScoreList_Maps_ChartJs_Player2, ${redScore_Maps[$i]}"`
                mapsScoreList_Maps_ChartJs_Draw=`echo "$mapsScoreList_Maps_ChartJs_Draw, ${DrawScore_Maps[$i]}"`

            else
                mapsList1_Maps=`echo "(${i})${mapName_Maps[$i]}"`
                mapsList2_Maps=`echo "'map_${i}'"`
                mapsScoreList_Maps_RGraph=`echo "[${blueScore_Maps[$i]},${redScore_Maps[$i]},${DrawScore_Maps[$i]}]"`
                mapsScoreList_Maps_ChartJs_Player1=`echo "${blueScore_Maps[$i]}"`
                mapsScoreList_Maps_ChartJs_Player2=`echo "${redScore_Maps[$i]}"`
                mapsScoreList_Maps_ChartJs_Draw=`echo "${DrawScore_Maps[$i]}"`
            fi
        fi
    done
    #echo "mapsList1_Maps=$mapsList1_Maps - mapsList2_Maps=$mapsList2_Maps"
    #echo "mapsScoreList_Maps_RGraph=$mapsScoreList_Maps_RGraph"
    
    # Hauteur du barGraphe
    let "heightHBAR_Maps = indice *70"
    
    
    # Initialisation de la description pour les fichier resultat HTML
    descriptionDate="`date +%d-%m-%Y`"
    descriptionHour="`date +%Hh%M`"
    descriptionType="X rounds, all maps, 1 color, 1 opponent."
    fileName="loopMaps_`date +%Y%m%d`_${descriptionHour}_${player1_Maps}_Vs_${player2_Maps}"

    # Creation du fichier resultat HTML **RGraph**
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        cat "${templatePath_Rounds}template_RGraph_loopMaps.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Rounds/g" | sed "s/##DescriptionVersionPlayer2##/$descriptionVersionPlayer2_Rounds/g" | sed "s/##Player1##/${player1_Maps}/g" | sed "s/##Player2##/${player2_Maps}/g" | sed "s/##Rounds##/$rounds/g" | sed "s/##BlueScoreTotal##/$blueScoreTotal_Maps/g" | sed "s/##RedScoreTotal##/$redScoreTotal_Maps/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Maps/g" | sed "s/##MapsScoreList##/$mapsScoreList_Maps_RGraph/g" | sed "s/##MapsList1##/$mapsList1_Maps/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" | sed "s/##heightHBAR##/$heightHBAR_Maps/g" >> ${filePath_Rounds}RGraph_${fileName}.html
        
        echo "Fichier HTML RGraph = file://`pwd`/${filePath_Rounds}RGraph_${fileName}.html"
    fi



    # Creation du fichier resultat HTML **ChartJs**
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        cat "${templatePath_Rounds}template_ChartJs_loopMaps.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Rounds/g" | sed "s/##DescriptionVersionPlayer2##/$descriptionVersionPlayer2_Rounds/g" | sed "s/##Player1##/${player1_Maps}/g" | sed "s/##Player2##/${player2_Maps}/g" | sed "s/##Rounds##/$rounds/g" | sed "s/##BlueScoreTotal##/$blueScoreTotal_Maps/g" | sed "s/##RedScoreTotal##/$redScoreTotal_Maps/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Maps/g" | sed "s/##MapsScoreList_Player1##/$mapsScoreList_Maps_ChartJs_Player1/g" | sed "s/##MapsScoreList_Player2##/$mapsScoreList_Maps_ChartJs_Player2/g" | sed "s/##MapsScoreList_Draw##/$mapsScoreList_Maps_ChartJs_Draw/g" | sed "s/##MapsList1##/$mapsList1_Maps/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" | sed "s/##heightHBAR##/$heightHBAR_Maps/g" >> ${filePath_Rounds}ChartJs_${fileName}.html
        
        echo "Fichier HTML ChartJs = file://`pwd`/${filePath_Rounds}ChartJs_${fileName}.html"
    fi



    # Creation de la structure JSON
    jsonHead_Maps=`cat "${templatePath_Rounds}template_JSON_head.json" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionAIWarVersion##/$descriptionAIWarVersion_Rounds/g"`


    # Creation du fichier resultat JSON
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        echo "$jsonHead_Maps" >> ${filePath_Rounds}JSON_${fileName}.json
        echo "$jsonBody_Maps"  >> ${filePath_Rounds}JSON_${fileName}.json
        echo "$jsonTail_Rounds" >> ${filePath_Rounds}JSON_${fileName}.json
        
        echo "Fichier JSON = file://`pwd`/${filePath_Rounds}JSON_${fileName}.json"
    fi

fi
