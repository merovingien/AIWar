/*
 * Copyright (C) 2012 Paul Grégoire
 *
 * This file is part of AIWar.
 *
 * AIWar is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * AIWar is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with AIWar.  If not, see <http://www.gnu.org/licenses/>. 
 */

#include <Python.h> // to define some constant before everything else

#include <SDL/SDL.h>
#include <iostream>

#ifndef _WIN32
#	include <sys/resource.h>
#endif

#include "item_manager.hpp"
#include "draw_manager.hpp"
#include "game_manager.hpp"

#include "test_handler.hpp"
#include "python_handler.hpp"

#include "config.hpp"


#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 800
#define SPEED 400

using namespace aiwar::core;

int main(int argc, char* argv[])
{
    SDL_Surface *screen = NULL;
    SDL_Event e;
    bool done = false, gameover = false;
    bool play = false;
    bool manual = false;
    unsigned int tick = 0;
    Uint32 startTime = 0, ellapsedTime;

#ifndef _WIN32
    /***** rlimit *****/
    rlimit rlim;
    if(getrlimit(RLIMIT_CORE, &rlim) == -1)
	std::cerr << "Cannot get CORE rlimit: " << strerror(errno) << std::endl;
    else
    {
	rlim.rlim_cur = rlim.rlim_max;
	if(setrlimit(RLIMIT_CORE, &rlim) == -1)
	    std::cerr << "Cannot set new CORE rlimit: " << strerror(errno) << std::endl;
    }
    /******************/
#endif

    /*** read configuration ***/
    aiwar::core::Config &cfg = aiwar::core::Config::instance();

    if(!cfg.parseCmdLine(argc, argv))
    {
	std::cerr << "Bad options\n" << cfg.usage();
	return 1;
    }
    
    if(cfg.help)
    {
	std::cout << cfg.usage();
	return 0;
    }

    if(!cfg.loadConfigFile())
    {
	std::cerr << "Bad config file\n";
	return 1;
    }

//    std::cout << cfg.dump();

    manual = cfg.manual;

    /*** Start handlers ***/

    TestHandler th;
    if(!th.initialize())
    {
	std::cerr << "Fail to initialize test handler\n";
	return -1;
    }

    PythonHandler ph;
    if(!ph.initialize())
    {
	std::cerr << "Fail to initialize python handler\n";
	th.finalize();
	return -1;
    }

    /*** Load teams ***/

    // load blue Team
    aiwar::core::Config::PlayerInfo &pblue = cfg.players[cfg.blue];
    HandlerInterface *hblue = NULL;
    if(pblue.handler == "test")
	hblue = &th;
    else if(pblue.handler == "python")
	hblue = &ph;
    else
    {
	std::cerr << "Unknown handler name for blue player: " << pblue.handler << std::endl;
	th.finalize();
	ph.finalize();
	return -1;
    }

    if(!hblue->load(cfg.blue, pblue.params))
    {
	std::cerr << "Fail to load blue handler\n";
	th.finalize();
	ph.finalize();
	return -1;
    }

    // load red Team
    aiwar::core::Config::PlayerInfo &pred = cfg.players[cfg.red];
    HandlerInterface *hred = NULL;
    if(pred.handler == "test")
	hred = &th;
    else if(pred.handler == "python")
	hred = &ph;
    else
    {
	std::cerr << "Unknown handler name for red team: " << pred.handler << std::endl;
	th.finalize();
	ph.finalize();
	return -1;
    }

    if(!hred->load(cfg.red, pred.params))
    {
	std::cerr << "Fail to load red handler\n";
	th.finalize();
	ph.finalize();
	return -1;
    }
    
    /*** Init the game ***/

    GameManager gm;

    gm.registerTeam(BLUE_TEAM, hblue->get_BaseHandler(cfg.blue), hblue->get_MiningShipHandler(cfg.blue), hblue->get_FighterHandler(cfg.blue));
    gm.registerTeam(RED_TEAM, hred->get_BaseHandler(cfg.red), hred->get_MiningShipHandler(cfg.red), hred->get_FighterHandler(cfg.red));

    ItemManager im(gm);

    if(!im.loadMap(cfg.mapFile))
    {
	std::cerr << "Error while loading map file\n";
	th.finalize();
	ph.finalize();
	return -1;
    }

    // SDL init
    SDL_Init(SDL_INIT_VIDEO);
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);

    /****** TEST HARDWARE ******/
//    const SDL_VideoInfo *info = SDL_GetVideoInfo();
//    printf("hardware surfaces? %d\n", info->hw_available);
//    printf("window manager available ? %d\n", info->wm_available);
    /*******/

    screen = SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, 32, SDL_HWSURFACE);
    SDL_WM_SetCaption("AIWar", NULL);

    aiwar::renderer::DrawManager dm(screen);
    dm.debug(cfg.debug);

    while(!done)
    {
	play = false;
	if(!manual)
	{
	    ellapsedTime = SDL_GetTicks();
	    if((ellapsedTime - startTime) >= SPEED)
	    {
		play = true;
		startTime = ellapsedTime;
	    }
	}

	// treat all events
	while(SDL_PollEvent(&e))
 	{	
	    switch(e.type)
	    {
	    case SDL_QUIT:
		done = true;
		break;
		
	    case SDL_KEYDOWN:
		switch(e.key.keysym.sym)
		{
		case SDLK_SPACE:
		    play = true;
		    break;

		case SDLK_d:
		    dm.toggleDebug();
		    break;

		case SDLK_m:
		    manual = !manual;
		    break;

		default:
		    break;
		}
	       
	    default:
		break;
	    }
	}
	
	/* actualisation de l'écran */
	SDL_FillRect(screen, NULL, SDL_MapRGB(screen->format,0,0,0));
	dm.preDraw();

	// update game
	if(play && !gameover)
	{
	    if(gm.gameOver())
	    {
		Team winner = gm.getWinner();
		std::cout << "********** GameOver *********\n";
		if(winner == NO_TEAM)
		    std::cout << "Egality !\n";
		else
		    std::cout << "Winner is: " << ((winner == BLUE_TEAM) ? cfg.players[cfg.blue].name : cfg.players[cfg.red].name) << std::endl;
		gameover = true;
	    }
	    else
	    {
		try
		{
		    im.update(tick++);
		    gm.printStat();
		}
		catch(const aiwar::core::HandlerError &e)
		{
		    std::cout << "********** GameOver *********\n";
		    std::string name = (e.team() == BLUE_TEAM) ? cfg.players[cfg.blue].name : cfg.players[cfg.red].name;
		    std::cout << "Team " << name << " has lost because an error occured in his play handler: " << e.what() << std::endl;
		    gameover = true;
		}
	    }
	}

	ItemManager::ItemMap::const_iterator cit;
	for(cit = im.begin() ; cit != im.end() ; cit++)
	    dm.draw(cit->second);

	dm.postDraw();
	SDL_Flip(screen);

	SDL_Delay(16); // about 60 FPS
    }

    // SDL exit
    SDL_Quit();
 

    // unload teams
    hred->unload(cfg.red);
    hblue->unload(cfg.blue);

    // finalize handlers
    th.finalize();
    ph.finalize();

    std::cout << "Exiting gracefully...\n";
	
    return 0;
}
