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

#include "renderer_sdl.hpp"

#include "renderer_sdl_draw.hpp"

#include <iostream>
#include <SDL/SDL.h>
#include <SDL/SDL_ttf.h>

#define SCREEN_WIDTH 1000
#define SCREEN_HEIGHT 800
//#define SPEED 400

// ms between each event treatment and draw (20 ms -> 50 FPS)
#define FRAME_DELAY 20

// ms between each play round
#define PLAY_DELAY 500

using namespace aiwar::renderer;

RendererSDL::RendererSDL() : _drawer(NULL)
{
}

RendererSDL::~RendererSDL()
{
    finalize();
}

std::string RendererSDL::getName() const
{
    return "RendererSDL";
}

std::string RendererSDL::getVersion() const
{
    return "0.2.0";
}

bool RendererSDL::initialize(const std::string& params)
{
    std::cout << "SDL: params (untreated): '" << params << "'\n";

    // SDL init
    SDL_Init(SDL_INIT_VIDEO);
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);
    TTF_Init();

    /****** TEST HARDWARE ******/
//    const SDL_VideoInfo *info = SDL_GetVideoInfo();
//    printf("hardware surfaces? %d\n", info->hw_available);
//    printf("window manager available ? %d\n", info->wm_available);
    /*******/

    _screen = SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, 32, SDL_HWSURFACE);
    SDL_WM_SetCaption("AIWar", NULL);

    _drawer = new RendererSDLDraw(_screen);
    _drawer->debug(aiwar::core::Config::instance().debug);

    _manual = aiwar::core::Config::instance().manual;

    _frameDelay = FRAME_DELAY;
    _playDelay = PLAY_DELAY;

    _startTimeFrame = SDL_GetTicks() - _frameDelay; // to force process and draw at the first call of render()
    _startTimePlay = SDL_GetTicks();

    return true;
}
	    
bool RendererSDL::finalize()
{
    if(_drawer)
    {
	delete _drawer;
	_drawer = NULL;
    }
    
    TTF_Quit();
    SDL_Quit();
    return true;
}

bool RendererSDL::render(const aiwar::core::ItemManager &itemManager, const aiwar::core::GameManager::Stat &stats, bool gameover)
{
    SDL_Event e;
    bool cont = true;
    Uint32 ellapsedTimeFrame, ellapsedTimePlay;
    Sint32 remainingTimeFrame, remainingTimePlay;

    bool play = false; // shall we return to play
    
    while(cont && (gameover || !play))
    {
	bool process = false; // shall we process events and draw

	Uint32 currentTime = SDL_GetTicks();

	/* FPS */
	ellapsedTimeFrame = currentTime - _startTimeFrame; // ellapsed time since the last event processing and draw
	remainingTimeFrame = _frameDelay - ellapsedTimeFrame; // remaining time for the next event processing and draw

	/* Play */
	if(!_manual)
	{
	    ellapsedTimePlay = currentTime - _startTimePlay; // ellapsed time since the last play
	    remainingTimePlay = _playDelay - ellapsedTimePlay;  // remaining time for the next play
	}
	else
	{
	    remainingTimePlay = (remainingTimeFrame > 0) ? remainingTimeFrame+1 : 1; 
            // so remainingTimePlay is always positive and bigger than remainingTimeFrame -> never play and never wait for playing
	}

	// shall we process ?
	if(remainingTimeFrame <= 0)
	    process = true;

	// shall we draw ?
	if(remainingTimePlay <= 0)
	    play = true;

	// shall we wait ?
	if(!process && !play)
	{
	    if(remainingTimeFrame <= remainingTimePlay)
	    {
		// we must wait to process
		SDL_Delay(remainingTimeFrame);
		process = true;
	    }
	    else
	    {
		// we must wait to play
		SDL_Delay(remainingTimePlay);
		play = true;
	    }
	}

	// shall we process ?
	if(process)
	{
	    _startTimeFrame = SDL_GetTicks();

	    // treat all events
	    while(SDL_PollEvent(&e))
	    {	
		switch(e.type)
		{
		case SDL_QUIT:
		    cont = false; // exit
		    break;
	    
		case SDL_KEYDOWN:
		    switch(e.key.keysym.sym)
		    {
		    case SDLK_ESCAPE:
			cont = false; // exit
			break;

		    case SDLK_SPACE: // force play
			play = true;
			break;

		    case SDLK_d: // toggle debug
			_drawer->toggleDebug();
			break;

		    case SDLK_m: // toggle manual
			_manual = !_manual;
			break;
			
		    case SDLK_s: // toggle full speed play
			_playDelay = PLAY_DELAY - _playDelay;
			break;

		    default:
			break;
		    }
	       
		default:
		    break;
		}
	    }

	    /* actualisation de l'écran */
	    // SDL_FillRect(_screen, NULL, SDL_MapRGB(_screen->format,0,0,0)); not necessary ?

	    _drawer->preDraw();
    
	    aiwar::core::ItemManager::ItemMap::const_iterator cit;
	    for(cit = itemManager.begin() ; cit != itemManager.end() ; ++cit)
		_drawer->draw(cit->second, itemManager);

	    _drawer->drawStats();

	    _drawer->postDraw();

	    SDL_Flip(_screen);
	}

    } // end while(!play)

    _startTimePlay = SDL_GetTicks();

    return cont;
}
