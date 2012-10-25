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

#include "renderer_sdl_draw.hpp"

#include "item.hpp"
#include "mineral.hpp"
#include "missile.hpp"
#include "miningship.hpp"
#include "base.hpp"
#include "fighter.hpp"

#include "config.hpp"

#include <SDL/SDL.h>
#include <SDL/SDL_gfxPrimitives.h>
#include <SDL/SDL_rotozoom.h>

using namespace aiwar::renderer;
using aiwar::core::BLUE_TEAM;
using aiwar::core::RED_TEAM;

RendererSDLDraw::RendererSDLDraw(SDL_Surface *screen) : _cfg(core::Config::instance()), _debug(_cfg.debug), _screen(screen)
{
    _world_rect = new SDL_Rect();
    _world_rect->x = 0;
    _world_rect->y = 0;
    _world_rect->w = static_cast<Uint16>(_cfg.WORLD_SIZE_X);
    _world_rect->h = static_cast<Uint16>(_cfg.WORLD_SIZE_Y);

    _world_surface = SDL_CreateRGBSurface(_screen->flags, static_cast<int>(_cfg.WORLD_SIZE_X), static_cast<int>(_cfg.WORLD_SIZE_Y), _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);

    // create item surfaces

    // red miningShip
    SDL_Surface* tmp = SDL_CreateRGBSurface(_world_surface->flags, static_cast<int>(_cfg.MININGSHIP_SIZE_X), static_cast<int>(_cfg.MININGSHIP_SIZE_Y), _world_surface->format->BitsPerPixel, _world_surface->format->Rmask, _world_surface->format->Gmask, _world_surface->format->Bmask, _world_surface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_world_surface->format, 0,0,0,255));
    // red triangle
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y), static_cast<Sint16>(_cfg.MININGSHIP_SIZE_X),static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y)/2, 255,0,0,255);
    _addSurface(RED_MININGSHIP, tmp);

    // blue miningShip
    tmp = SDL_CreateRGBSurface(_world_surface->flags, static_cast<int>(_cfg.MININGSHIP_SIZE_X), static_cast<int>(_cfg.MININGSHIP_SIZE_Y), _world_surface->format->BitsPerPixel, _world_surface->format->Rmask, _world_surface->format->Gmask, _world_surface->format->Bmask, _world_surface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_world_surface->format, 0,0,0,255));
    // blue triangle
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y), static_cast<Sint16>(_cfg.MININGSHIP_SIZE_X),static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y)/2, 0,0,255,255);
    _addSurface(BLUE_MININGSHIP, tmp);

    // red fighter
    tmp = SDL_CreateRGBSurface(_world_surface->flags, static_cast<int>(_cfg.FIGHTER_SIZE_X), static_cast<int>(_cfg.FIGHTER_SIZE_Y), _world_surface->format->BitsPerPixel, _world_surface->format->Rmask, _world_surface->format->Gmask, _world_surface->format->Bmask, _world_surface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_world_surface->format, 0,0,0,255));
    // red triangle
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),0, 255,0,0,255);
    filledTrigonRGBA(tmp, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3*2, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 255,0,0,255);
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), static_cast<Sint16>(_cfg.FIGHTER_SIZE_X)/2,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/2, 255,0,0,255);
    _addSurface(RED_FIGHTER, tmp);

    // blue fighter
    tmp = SDL_CreateRGBSurface(_world_surface->flags, static_cast<int>(_cfg.FIGHTER_SIZE_X), static_cast<int>(_cfg.FIGHTER_SIZE_Y), _world_surface->format->BitsPerPixel, _world_surface->format->Rmask, _world_surface->format->Gmask, _world_surface->format->Bmask, _world_surface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_world_surface->format, 0,0,0,255));
    // red triangle
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),0, 0,0,255,255);
    filledTrigonRGBA(tmp, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 0,0, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 0,0,255,255);
    _addSurface(BLUE_FIGHTER, tmp);


}

RendererSDLDraw::~RendererSDLDraw()
{
    std::map<ItemType, SDL_Surface*>::iterator it;
    for(it = _surfaceMap.begin() ; it != _surfaceMap.end() ; ++it)
	SDL_FreeSurface(it->second);

    SDL_FreeSurface(_world_surface);
    delete _world_rect;
}

void RendererSDLDraw::_addSurface(ItemType t, SDL_Surface* s)
{
    _surfaceMap[t] = s;
}

SDL_Surface* RendererSDLDraw::_getSurface(ItemType t) const
{
    std::map<ItemType, SDL_Surface*>::const_iterator cit = _surfaceMap.find(t);
    if(cit != _surfaceMap.end())
	return cit->second;
    return NULL;
}

void RendererSDLDraw::preDraw()
{
    SDL_FillRect(_world_surface, NULL, SDL_MapRGB(_screen->format,0,0,0));
}

void RendererSDLDraw::draw(const aiwar::core::Item *item)
{
    const aiwar::core::Mineral *mineral;
    const aiwar::core::Missile *missile;
    const aiwar::core::MiningShip *miningShip;
    const aiwar::core::Base *base;
    const aiwar::core::Fighter *fighter;

    if((mineral = dynamic_cast<const aiwar::core::Mineral*>(item)))
	_drawMineral(mineral);
    else if((missile = dynamic_cast<const aiwar::core::Missile*>(item)))
	_drawMissile(missile);
    else if((miningShip = dynamic_cast<const aiwar::core::MiningShip*>(item)))
	_drawMiningShip(miningShip);
    else if((base = dynamic_cast<const aiwar::core::Base*>(item)))
	_drawBase(base);
    else if((fighter = dynamic_cast<const aiwar::core::Fighter*>(item)))
	_drawFighter(fighter);
}

void RendererSDLDraw::postDraw()
{
    SDL_BlitSurface(_world_surface, NULL, _screen, _world_rect);
}

void RendererSDLDraw::debug(bool active)
{
    _debug = active;
}

void RendererSDLDraw::toggleDebug()
{
    _debug = !_debug;
}

void RendererSDLDraw::_drawMineral(const aiwar::core::Mineral *m)
{
    SDL_Rect r;
    r.x = static_cast<Sint16>(m->xpos() - _cfg.MINERAL_SIZE_X/2);
    r.y = static_cast<Sint16>(m->ypos() - _cfg.MINERAL_SIZE_Y/2);
    r.w = static_cast<Uint16>(_cfg.MINERAL_SIZE_X);
    r.h = static_cast<Uint16>(_cfg.MINERAL_SIZE_Y);
    SDL_FillRect(_world_surface, &r, SDL_MapRGB(_world_surface->format, 0,255,128));
}

void RendererSDLDraw::_drawBase(const aiwar::core::Base *b)
{
    SDL_Rect r;
    r.x = static_cast<Sint16>(b->xpos() - _cfg.BASE_SIZE_X/2);
    r.y = static_cast<Sint16>(b->ypos() - _cfg.BASE_SIZE_Y/2);
    r.w = static_cast<Uint16>(_cfg.BASE_SIZE_X);
    r.h = static_cast<Uint16>(_cfg.BASE_SIZE_Y);

    Uint32 color = SDL_MapRGB(_world_surface->format, 0,255,0);
    if(b->team() == BLUE_TEAM)
	color = SDL_MapRGB(_world_surface->format, 0,0,255);
    else if(b->team() == RED_TEAM)
	color = SDL_MapRGB(_world_surface->format, 255,0,0);

    SDL_FillRect(_world_surface, &r, color);
}

void RendererSDLDraw::_drawMiningShip(const aiwar::core::MiningShip *m)
{
    SDL_Surface *rs = NULL;

    // rotate the ship
    if(m->team() == RED_TEAM)
	rs = rotozoomSurface(_getSurface(RED_MININGSHIP), m->angle(), 1.0, SMOOTHING_OFF);
    else if(m->team() == BLUE_TEAM)
	rs = rotozoomSurface(_getSurface(BLUE_MININGSHIP), m->angle(), 1.0, SMOOTHING_OFF);

    SDL_Rect r;
    r.x = static_cast<Sint16>(m->xpos()) - rs->w/2;
    r.y = static_cast<Sint16>(m->ypos()) - rs->h/2;
    r.w = rs->w;
    r.h = rs->h;

//    std::cout << "MiningShip size: (" << r.w << "," << r.h << ")\n"; 

    SDL_BlitSurface(rs, NULL, _world_surface, &r);
    SDL_FreeSurface(rs);

    if(_debug)
    {
	// draw vision circle
	circleRGBA(_world_surface, static_cast<Sint16>(m->xpos()), static_cast<Sint16>(m->ypos()), static_cast<Sint16>(_cfg.MININGSHIP_DETECTION_RADIUS), 255,255,0,255);

	// draw mining circle
	circleRGBA(_world_surface, static_cast<Sint16>(m->xpos()), static_cast<Sint16>(m->ypos()), static_cast<Sint16>(_cfg.MININGSHIP_MINING_RADIUS), 190,192,192,255);

	// draw communication circle
	circleRGBA(_world_surface, static_cast<Sint16>(m->xpos()), static_cast<Sint16>(m->ypos()), static_cast<Sint16>(_cfg.COMMUNICATION_RADIUS), 0,192,128,255);
    }
}

void RendererSDLDraw::_drawMissile(const aiwar::core::Missile *m)
{
    SDL_Surface* tmp = SDL_CreateRGBSurface(_world_surface->flags, static_cast<int>(_cfg.MISSILE_SIZE_X), static_cast<int>(_cfg.MISSILE_SIZE_Y), _world_surface->format->BitsPerPixel, _world_surface->format->Rmask, _world_surface->format->Gmask, _world_surface->format->Bmask, _world_surface->format->Amask);

    SDL_FillRect(tmp, NULL, SDL_MapRGB(_world_surface->format, 255,0,255));
  
    // rotate the missile
    SDL_Surface *rs = rotozoomSurface(tmp, m->angle(), 1.0, SMOOTHING_OFF);

    SDL_Rect r;
    r.x = static_cast<Sint16>(m->xpos()) - rs->w/2;
    r.y = static_cast<Sint16>(m->ypos()) - rs->h/2;
    r.w = rs->w;
    r.h = rs->h;
    SDL_BlitSurface(rs, NULL, _world_surface, &r);

    SDL_FreeSurface(rs);
    SDL_FreeSurface(tmp);
}

void RendererSDLDraw::_drawFighter(const aiwar::core::Fighter *f)
{
    SDL_Surface *rs = NULL;

    // rotate the ship
    if(f->team() == RED_TEAM)
	rs = rotozoomSurface(_getSurface(RED_FIGHTER), f->angle(), 1.0, SMOOTHING_OFF);
    else if(f->team() == BLUE_TEAM)
	rs = rotozoomSurface(_getSurface(BLUE_FIGHTER), f->angle(), 1.0, SMOOTHING_OFF);

    SDL_Rect r;
    r.x = static_cast<Sint16>(f->xpos()) - rs->w/2;
    r.y = static_cast<Sint16>(f->ypos()) - rs->h/2;
    r.w = rs->w;
    r.h = rs->h;

    SDL_BlitSurface(rs, NULL, _world_surface, &r);
    SDL_FreeSurface(rs);

    if(_debug)
    {
	// draw vision circle
	circleRGBA(_world_surface, static_cast<Sint16>(f->xpos()), static_cast<Sint16>(f->ypos()), static_cast<Sint16>(_cfg.FIGHTER_DETECTION_RADIUS), 255,255,0,255);

	// draw communication circle
	circleRGBA(_world_surface, static_cast<Sint16>(f->xpos()), static_cast<Sint16>(f->ypos()), static_cast<Sint16>(_cfg.COMMUNICATION_RADIUS), 0,192,128,255);
    }
}
