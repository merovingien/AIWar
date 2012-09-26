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

#include <Python.h>

#include <SDL/SDL.h>

#include <iostream>

#include "base.hpp"
#include "miningship.hpp"
#include "mineral.hpp"
#include "missile.hpp"
#include "fighter.hpp"

#include "item_manager.hpp"
#include "draw_manager.hpp"
#include "game_manager.hpp"

#include "python_wrapper.hpp"
#include "python_handler.hpp"

#include "config.hpp"

#define SCREEN_WIDTH 900
#define SCREEN_HEIGHT 800
#define SPEED 400

using namespace aiwar::core;

static void play_miningship(Playable*);
static void play_base(Playable*);
static void play_fighter(Playable*);

int main(int , char* [])
{
    SDL_Surface *screen = NULL;
    SDL_Event e;
    bool done = false;
    bool play = false;
    bool manual = false;
    unsigned int tick = 0;
    Uint32 startTime, ellapsedTime;

    SDL_Init(SDL_INIT_VIDEO);
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);

    // Python interpreter init
    PythonHandler ph;
    if(!ph.initialize())

//    Py_Initialize();
//    if(!initPythonInterpreter(argc, argv))
    {
	std::cerr << "FATAL ERROR: fail to initiate Python Interpreter" << std::endl;
	SDL_Quit();
	return -1;
    }

//    initAiwarModule();

    ph.load(TEAM_RED, "embtest");

    GameManager gm;
    ItemManager im(gm);

    // todo : create a handler
    DefaultPlayFunction base_pf(play_base);
    DefaultPlayFunction miningShip_pf(play_miningship);
    DefaultPlayFunction fighter_pf(play_fighter);

    gm.registerTeam(TEAM_BLUE, base_pf, miningShip_pf, fighter_pf);
    gm.registerTeam(TEAM_RED, ph.get_BaseHandler(TEAM_RED), ph.get_MiningShipHandler(TEAM_RED), ph.get_FighterHandler(TEAM_RED));

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

  

    /****** TEST HARDWARE ******/
//    const SDL_VideoInfo *info = SDL_GetVideoInfo();
//    printf("hardware surfaces? %d\n", info->hw_available);
//    printf("window manager available ? %d\n", info->wm_available);
    /*******/


    screen = SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, 32, SDL_HWSURFACE);
    SDL_WM_SetCaption("AIWar", NULL);

    aiwar::renderer::DrawManager dm(screen);
  
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
	
	if(play)
	{
	    im.update(tick);
	    tick++;

	    gm.printStat();
	}

	std::set<Item*>::const_iterator cit;
	for(cit = im.begin() ; cit != im.end() ; cit++)
	    dm.draw(*cit);

	dm.postDraw();
	SDL_Flip(screen);

	SDL_Delay(16); // about 60 FPS
    }
  
//    Py_Finalize();
    ph.finalize();

    SDL_Quit();
  
    return 0;
}

void play_miningship(Playable *item)
{
    using std::cout;
    using std::endl;

    aiwar::core::MiningShip *self = dynamic_cast<aiwar::core::MiningShip*>(item);

    Item::ItemSet neighbours = self->neighbours();
    cout << *self <<  ": Number of neighbours: " << neighbours.size() << endl;

    Item::ItemSet::iterator it;
    for(it = neighbours.begin() ; it != neighbours.end() ; it++)
    {
	Mineral *m = dynamic_cast<Mineral*>(*it);
	if(m) // m is a Mineral
	{
	    double d = self->distanceTo(m);
	    if(d <= MININGSHIP_MINING_RADIUS)
	    {
		unsigned int e = self->extract(m);
		cout << *self << ": Meet a Mineral, extracted: " << e << endl;
	    }
	    else
	    {
		self->rotateTo(m);
		self->move();
	    }
	}
    }

    self->rotateOf(15);
    self->move();

    cout << *self << ": Life: " << self->life() << endl;
}

void play_base(Playable *item)
{
    using std::cout;
    using std::endl;

    Base *self = dynamic_cast<Base*>(item);

    Item::ItemSet neighbours = self->neighbours();
    cout << *self << ": Number of neighbours: " << neighbours.size() << endl;

    Item::ItemSet::iterator it;
    for(it = neighbours.begin() ; it != neighbours.end() ; ++it)
    {
	aiwar::core::MiningShip *s = dynamic_cast<aiwar::core::MiningShip*>(*it);
	if(s)
	{
	    if(! self->isFriend(s))
	    {
		self->launchMissile(s);
		cout << *self << ": launch a missile to " << *s << endl;
	    }
	    else
	    {
		self->setMemory(0, 5, s);
		int i = self->getMemory<int>(0, s);
		cout << *self << ": get Memory from " << *s << ": " << i << endl;
	    }
	}
    }

    if(self->mineralStorage() > BASE_MININGSHIP_PRICE*2)
    {
	self->createMiningShip();
	cout << *self << ": create a new MiningShip" << endl;
    }

    cout << *self << ": Life: " << self->life() << endl;

    self->setMemory(1, 1);
    cout << *self << ": getMemory<float>(self, 1): " << self->getMemory<float>(1, self) << endl;
}

void play_fighter(Playable* item)
{
    using std::cout;
    using std::endl;

    aiwar::core::Fighter * self = dynamic_cast<aiwar::core::Fighter*>(item);

    Item::ItemSet neighbours = self->neighbours();
//    cout << *self << ": Number of neighbours: " << neighbours.size() << endl;

    Item::ItemSet::iterator it;
    for(it = neighbours.begin() ; it != neighbours.end() ; ++it)
    {
	aiwar::core::MiningShip *s = dynamic_cast<aiwar::core::MiningShip*>(*it);
	if(s)
	{
	    if(! self->isFriend(s))
	    {
		self->launchMissile(s);
//		cout << *self << ": launch a missile to " << *s << endl;
	    }
	}
    }  
}
