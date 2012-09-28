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

#include <sys/resource.h>

#include "item_manager.hpp"
#include "draw_manager.hpp"
#include "game_manager.hpp"

#include "test_handler.hpp"
#include "python_handler.hpp"

#include "config.hpp"


#define SCREEN_WIDTH 900
#define SCREEN_HEIGHT 800
#define SPEED 400

using namespace aiwar::core;

int main(int argc, char* argv[])
{
    SDL_Surface *screen = NULL;
    SDL_Event e;
    bool done = false;
    bool play = false;
    bool manual = false;
    unsigned int tick = 0;
    Uint32 startTime = 0, ellapsedTime;

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
    
    /*** read configuration ***/
    Config &cfg = Config::instance();

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

    manual = cfg.manual;

    /*** Start handlers ***/

    // Python interpreter init
    PythonHandler ph;
    if(!ph.initialize())
    {
	std::cerr << "FATAL ERROR: fail to initiate Python Interpreter" << std::endl;
	return -1;
    }

    // load handlers for RED team
    if(!ph.load(TEAM_RED, "embtest"))
    {
	std::cerr << "FATAL ERROR: fail to load TEAM_RED python handler" << std::endl;
	return -1;
    }

    // test handler
    TestHandler th;
    th.initialize();


    GameManager gm;
    ItemManager im(gm);

    gm.registerTeam(TEAM_BLUE, th);
    gm.registerTeam(TEAM_RED, ph);

    im.createBase(25,25, TEAM_BLUE);
    im.createFighter(250,250, TEAM_BLUE);

    im.createBase(500,400, TEAM_RED);
    im.createMiningShip(450,400, TEAM_RED);
    im.createFighter(300,200, TEAM_RED);
    im.createFighter(300,220, TEAM_RED);
    im.createFighter(300,240, TEAM_RED);
    im.createFighter(300,180, TEAM_RED);

    im.createMineral(300,300);
    im.createMineral(300,295);
    im.createMineral(305,305);
    im.createMineral(150,35);
    im.createMineral(145,45);
    im.createMineral(165,40);
    im.createMineral(400,200);
    im.createMineral(420,200);
    im.createMineral(410,205);

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
	if(play)
	{
	    if(gm.gameOver())
	    {
		Playable::Team winner = gm.getWinner();
		std::cout << "********** GameOver *********\n";
		if(winner == Playable::NO_TEAM)
		    std::cout << "Egality !\n";
		else
		    std::cout << "Winner is TEAM: " << ((winner == TEAM_BLUE) ? "BLUE" : "RED") << std::endl;
		done = true;
	    }
	    else
	    {
		im.update(tick);
		tick++;

		gm.printStat();
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
 

    // Handlers exit
    th.finalize();
    ph.finalize();

    return 0;
}
