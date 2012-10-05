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

#ifndef DRAW_MANAGER_HPP
#define DRAW_MANAGER_HPP

#include <map>

struct SDL_Surface;
struct SDL_Rect;

namespace aiwar {

    namespace core {
	class Config;
	class Item;
	class Mineral;
	class Missile;
	class MiningShip;
	class Base;
	class Fighter;
    }
    
    namespace renderer {

	class DrawManager
	{
	public:
	    DrawManager(SDL_Surface *s);
	    ~DrawManager();

	    void preDraw();
	    void draw(const core::Item *item);
	    void postDraw();

	    void debug(bool active);
	    void toggleDebug();

	private:

	    enum ItemType {
		BLUE_MININGSHIP,
		BLUE_BASE,
		RED_MININGSHIP,
		RED_BASE,
		BLUE_FIGHTER,
		RED_FIGHTER,
		MISSILE,
		MINERAL
	    };

	    void _drawMineral(const core::Mineral *m);
	    void _drawMissile(const core::Missile *m);
	    void _drawMiningShip(const core::MiningShip *m);
	    void _drawBase(const core::Base *b);
	    void _drawFighter(const core::Fighter *f);

	    void _addSurface(ItemType, SDL_Surface* surf);
	    SDL_Surface* _getSurface(ItemType) const;

	    core::Config& _cfg;

	    bool _debug;
	    SDL_Surface *_screen;
	    SDL_Rect *_world_rect;
	    SDL_Surface *_world_surface;
	    std::map<ItemType, SDL_Surface*> _surfaceMap;
	};

    }
}

#endif /* DRAW_MANAGER_HPP */
