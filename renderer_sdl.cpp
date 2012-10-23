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

#include <SDL/SDL.h>

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 800
//#define SPEED 400

using namespace aiwar::renderer;

RendererSDL::RendererSDL()
{
}

RendererSDL::~RendererSDL()
{
}

std::string RendererSDL::getName() const
{
    return "RendererSDL";
}

std::string RendererSDL::getVersion() const
{
    return "0.1.0";
}

bool RendererSDL::initialize(const std::string& params)
{
    // SDL init
    SDL_Init(SDL_INIT_VIDEO);
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);

    /****** TEST HARDWARE ******/
//    const SDL_VideoInfo *info = SDL_GetVideoInfo();
//    printf("hardware surfaces? %d\n", info->hw_available);
//    printf("window manager available ? %d\n", info->wm_available);
    /*******/

    SDL_Surface *screen = SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, 32, SDL_HWSURFACE);
    SDL_WM_SetCaption("AIWar", NULL);

//    aiwar::renderer::DrawManager dm(screen);
//    dm.debug(cfg.debug);




    return true;
}
	    
bool RendererSDL::finalize()
{
    SDL_Quit();
    return true;
}

bool RendererSDL::render(const aiwar::core::ItemManager::ItemMap::const_iterator &cit, const aiwar::core::GameManager::Stat &stats, bool gameover)
{
    SDL_Event e;
    bool cont = true;

    // treat all events
    while(SDL_PollEvent(&e))
    {	
	switch(e.type)
	{
	case SDL_QUIT:
	    cont = false;
	    break;
	    
	case SDL_KEYDOWN:
	    switch(e.key.keysym.sym)
	    {
	    case SDLK_SPACE:
		//play = true;
		break;

	    case SDLK_d:
		//dm.toggleDebug();
		break;

	    case SDLK_m:
		//manual = !manual;
		break;

	    default:
		break;
	    }
	       
	default:
	    break;
	}
    }
	
	/* actualisation de l'écran */
//	SDL_FillRect(screen, NULL, SDL_MapRGB(screen->format,0,0,0));


    return cont;
}
