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

#include <sstream>
#include <cmath>

#include <SDL/SDL.h>
#include <SDL/SDL_gfxPrimitives.h>
#include <SDL/SDL_rotozoom.h>

using namespace aiwar::renderer;
using aiwar::core::BLUE_TEAM;
using aiwar::core::RED_TEAM;
using aiwar::core::NO_TEAM;

// FONT_COLOR
const SDL_Color BLACK_COLOR = { 0x00, 0x00, 0x00, 0 };
const SDL_Color BLUE_COLOR = { 0x00, 0x00, 0xFF, 0 };
const SDL_Color RED_COLOR = { 0xFF, 0x00, 0x00, 0 };
const SDL_Color WHITE_COLOR = { 0xFF, 0xFF, 0xFF, 0 };
const SDL_Color BG_COLOR = BLACK_COLOR;

RendererSDLDraw::RendererSDLDraw(SDL_Surface *screen) : _cfg(core::Config::instance()), _screen(screen), _gameover(false), _winner(NO_TEAM)
{
    // playground surface
    _worldRect.x = 0;
    _worldRect.y = 0;
    _worldRect.w = _screen->w - STATS_WIDTH;
    _worldRect.h = _screen->h;

    _worldSurface = SDL_CreateRGBSurface(_screen->flags, _worldRect.w, _worldRect.h, _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);

    // viewport
    resetPosition();
    resetZoom();

    // stat surface
    _statsRect.x = _worldRect.w;
    _statsRect.y = 0;
    _statsRect.w = STATS_WIDTH;
    _statsRect.h = _screen->h;

    _statsSurface = SDL_CreateRGBSurface(_screen->flags, _statsRect.w, _statsRect.h, _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);

    // team names
    _blueName = _cfg.players.find(_cfg.blue)->second.name;
    _redName = _cfg.players.find(_cfg.red)->second.name;

    // create item surfaces

    // ***red miningShip***
    SDL_Surface* tmp = SDL_CreateRGBSurface(_worldSurface->flags, static_cast<int>(_cfg.MININGSHIP_SIZE_X), static_cast<int>(_cfg.MININGSHIP_SIZE_Y), _worldSurface->format->BitsPerPixel, _worldSurface->format->Rmask, _worldSurface->format->Gmask, _worldSurface->format->Bmask, _worldSurface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_worldSurface->format, 0,0,0,255));
    // red triangle
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y), static_cast<Sint16>(_cfg.MININGSHIP_SIZE_X),static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y)/2, 255,0,0,255);
    _addSurface(RED_MININGSHIP, tmp);

    // ***blue miningShip***
    tmp = SDL_CreateRGBSurface(_worldSurface->flags, static_cast<int>(_cfg.MININGSHIP_SIZE_X), static_cast<int>(_cfg.MININGSHIP_SIZE_Y), _worldSurface->format->BitsPerPixel, _worldSurface->format->Rmask, _worldSurface->format->Gmask, _worldSurface->format->Bmask, _worldSurface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_worldSurface->format, 0,0,0,255));
    // blue triangle
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y), static_cast<Sint16>(_cfg.MININGSHIP_SIZE_X),static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y)/2, 0,0,255,255);
    _addSurface(BLUE_MININGSHIP, tmp);

    // ***selected miningShip***
    tmp = SDL_CreateRGBSurface(_worldSurface->flags, static_cast<int>(_cfg.MININGSHIP_SIZE_X), static_cast<int>(_cfg.MININGSHIP_SIZE_Y), _worldSurface->format->BitsPerPixel, _worldSurface->format->Rmask, _worldSurface->format->Gmask, _worldSurface->format->Bmask, _worldSurface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_worldSurface->format, 0,0,0,255));
    // yellow triangle
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y), static_cast<Sint16>(_cfg.MININGSHIP_SIZE_X),static_cast<Sint16>(_cfg.MININGSHIP_SIZE_Y)/2, 255,255,0,255);
    _addSurface(SELECTED_MININGSHIP, tmp);

    // ***red fighter***
    tmp = SDL_CreateRGBSurface(_worldSurface->flags, static_cast<int>(_cfg.FIGHTER_SIZE_X), static_cast<int>(_cfg.FIGHTER_SIZE_Y), _worldSurface->format->BitsPerPixel, _worldSurface->format->Rmask, _worldSurface->format->Gmask, _worldSurface->format->Bmask, _worldSurface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_worldSurface->format, 0,0,0,255));
    // red triangles
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),0, 255,0,0,255);
    filledTrigonRGBA(tmp, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3*2, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 255,0,0,255);
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), static_cast<Sint16>(_cfg.FIGHTER_SIZE_X)/2,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/2, 255,0,0,255);
    _addSurface(RED_FIGHTER, tmp);

    // ***blue fighter***
    tmp = SDL_CreateRGBSurface(_worldSurface->flags, static_cast<int>(_cfg.FIGHTER_SIZE_X), static_cast<int>(_cfg.FIGHTER_SIZE_Y), _worldSurface->format->BitsPerPixel, _worldSurface->format->Rmask, _worldSurface->format->Gmask, _worldSurface->format->Bmask, _worldSurface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_worldSurface->format, 0,0,0,255));
    // blue triangles
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),0, 0,0,255,255);
    filledTrigonRGBA(tmp, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3*2, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 0,0,255,255);
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), static_cast<Sint16>(_cfg.FIGHTER_SIZE_X)/2,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/2, 0,0,255,255);
    _addSurface(BLUE_FIGHTER, tmp);

    // ***selected fighter***
    tmp = SDL_CreateRGBSurface(_worldSurface->flags, static_cast<int>(_cfg.FIGHTER_SIZE_X), static_cast<int>(_cfg.FIGHTER_SIZE_Y), _worldSurface->format->BitsPerPixel, _worldSurface->format->Rmask, _worldSurface->format->Gmask, _worldSurface->format->Bmask, _worldSurface->format->Amask);

    // transparent background
    SDL_FillRect(tmp, NULL, SDL_MapRGBA(_worldSurface->format, 0,0,0,255));
    // yellow triangles
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),0, 255,255,0,255);
    filledTrigonRGBA(tmp, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/3*2, static_cast<Sint16>(_cfg.FIGHTER_SIZE_X),static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), 255,255,0,255);
    filledTrigonRGBA(tmp, 0,0, 0,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y), static_cast<Sint16>(_cfg.FIGHTER_SIZE_X)/2,static_cast<Sint16>(_cfg.FIGHTER_SIZE_Y)/2, 255,255,0,255);
    _addSurface(SELECTED_FIGHTER, tmp);


    /// \todo add test to check OpenFont
    _statsFont = TTF_OpenFont("./fonts/Jura-Medium.ttf", SMALL_FONT_SIZE);
    _aiwarFont = TTF_OpenFont("./fonts/DouarOutline.ttf", BIG_FONT_SIZE);
}

RendererSDLDraw::~RendererSDLDraw()
{
    // fonts
    TTF_CloseFont(_aiwarFont);
    TTF_CloseFont(_statsFont);

    // item surfaces
    std::map<ItemType, SDL_Surface*>::iterator it;
    for(it = _surfaceMap.begin() ; it != _surfaceMap.end() ; ++it)
        SDL_FreeSurface(it->second);

    SDL_FreeSurface(_worldSurface);

    SDL_FreeSurface(_statsSurface);
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

bool RendererSDLDraw::_getPosOnScreen(const double &itemPx, const double &itemPy, Sint16 &screenPx, Sint16 &screenPy) const
{
    screenPx = static_cast<Sint16>((static_cast<double>(_worldRect.w) / 2.0) - (_vpX - itemPx) * _zoom);
    screenPy = static_cast<Sint16>((static_cast<double>(_worldRect.h) / 2.0) - (_vpY - itemPy) * _zoom);

    return (screenPx > 0 && screenPx < _worldRect.w && screenPy > 0 && screenPy < _worldRect.h);
}

bool RendererSDLDraw::_getMousePos(const int &mouseX, const int &mouseY, double &px, double &py) const
{
    px = _vpX - ( (static_cast<double>(_worldRect.w) / 2.0) - static_cast<double>(mouseX) ) / _zoom;
    py = _vpY - ( (static_cast<double>(_worldRect.h) / 2.0) - static_cast<double>(mouseY) ) / _zoom;

    return (mouseX > 0 && mouseX < _worldRect.w && mouseY > 0 && mouseY < _worldRect.h);
}

void RendererSDLDraw::setWinner(const aiwar::core::Team& winner)
{
    _gameover = true;
    _winner = winner;
}

void RendererSDLDraw::preDraw(bool clicked, int xmc, int ymc, int dxViewPort, int dyViewPort, int dz, int xm, int ym)
{
    _clicked = clicked;
    _xmouseClick = xmc;
    _ymouseClick = ymc;

    _xmousePos = xm;
    _ymousePos = ym;

    _vpX -= static_cast<double>(dxViewPort) / _zoom;
    _vpY -= static_cast<double>(dyViewPort) / _zoom;

    if(dz > 0)
        _zoom *= std::pow(1.15, dz);
    else if(dz < 0)
        _zoom /= std::pow(1.15, -dz);

    SDL_FillRect(_worldSurface, NULL, SDL_MapRGB(_screen->format,0,0,0));
    SDL_FillRect(_statsSurface, NULL, SDL_MapRGB(_screen->format,0,0,0));
}

void RendererSDLDraw::draw(RendererSDL::ItemEx *itemEx, const aiwar::core::ItemManager &im)
{
    const aiwar::core::Mineral *mineral;
    const aiwar::core::Missile *missile;
    const aiwar::core::MiningShip *miningShip;
    const aiwar::core::Base *base;
    const aiwar::core::Fighter *fighter;

    if(_clicked)
    {
        double px = itemEx->item->xpos();
        double py = itemEx->item->ypos();
        im.undoOffset(px, py);

        double mxc, myc;
        _getMousePos(_xmouseClick, _ymouseClick, mxc, myc);

        // check if this item is clicked
        if(px - itemEx->item->_xSize()/2.0 / _zoom <= mxc &&
           px + itemEx->item->_xSize()/2.0 / _zoom >= mxc &&
           py - itemEx->item->_ySize()/2.0 / _zoom <= myc &&
           py + itemEx->item->_xSize()/2.0 / _zoom >= myc)
        {
            itemEx->selected = !itemEx->selected;
        }
    }

    if((mineral = dynamic_cast<const aiwar::core::Mineral*>(itemEx->item)))
        _drawMineral(itemEx, im);
    else if((missile = dynamic_cast<const aiwar::core::Missile*>(itemEx->item)))
        _drawMissile(itemEx, im);
    else if((miningShip = dynamic_cast<const aiwar::core::MiningShip*>(itemEx->item)))
        _drawMiningShip(itemEx, im);
    else if((base = dynamic_cast<const aiwar::core::Base*>(itemEx->item)))
        _drawBase(itemEx, im);
    else if((fighter = dynamic_cast<const aiwar::core::Fighter*>(itemEx->item)))
        _drawFighter(itemEx, im);

    if(_gameover)
    {
        // draw winner
        int y = (_worldRect.h - TTF_FontHeight(_aiwarFont)) / 2;
        std::ostringstream oss;
        if(_winner == BLUE_TEAM)
            oss << "Winner  is  " << _blueName;
        else if(_winner == RED_TEAM)
            oss << "Winner  is  " << _redName;
        else
            oss << "Equality";
        _drawText(_worldSurface, oss.str(), _worldRect.w / 2, y, _aiwarFont, WHITE_COLOR, BG_COLOR, true);
    }
}

void RendererSDLDraw::drawStats(const aiwar::core::StatManager &sm)
{
    std::ostringstream statsText;
    const int FONT_HEIGHT = TTF_FontLineSkip(_statsFont);

    // compute cursor position
    double mx, my;
    bool printMouse = _getMousePos(_xmousePos, _ymousePos, mx, my);
    int y = 0;

    // draw

    statsText << "AIWar";
    _drawText(_statsSurface, statsText.str(), STATS_WIDTH/2, 20, _aiwarFont, WHITE_COLOR, BG_COLOR, true);
    y += FONT_HEIGHT;

    y += 4 * FONT_HEIGHT;

    // round
    statsText.str("");
    statsText << "Round #" << sm.round();
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, WHITE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    //BLUE team y pos
    y += FONT_HEIGHT;

    statsText.str(_blueName);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, BLUE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Bases (current/max):  " << sm.baseCurrent(BLUE_TEAM) << " / " << sm.baseMax(BLUE_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, BLUE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Fighters (current/max):  " << sm.fighterCurrent(BLUE_TEAM) << " / " << sm.fighterMax(BLUE_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, BLUE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "MiningShips (current/max):  " << sm.miningShipCurrent(BLUE_TEAM) << " / " << sm.miningShipMax(BLUE_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, BLUE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Missiles (launched/created): " << sm.missileLaunched(BLUE_TEAM) << " / " << sm.missileCreated(BLUE_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, BLUE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Minerals (spent/saved):  " << sm.mineralSpent(BLUE_TEAM) << " / " << sm.mineralSaved(BLUE_TEAM);
    _drawText(_statsSurface, statsText.str(), 10,  y, _statsFont, BLUE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    // RED team
    y += FONT_HEIGHT;

    statsText.str(_redName);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, RED_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Bases (current/max):  " << sm.baseCurrent(RED_TEAM) << " / " << sm.baseMax(RED_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, RED_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Fighters (current/max):  " << sm.fighterCurrent(RED_TEAM) << " / " << sm.fighterMax(RED_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, RED_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "MiningShips (current/max):  " << sm.miningShipCurrent(RED_TEAM) << " / " << sm.miningShipMax(RED_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, RED_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Missiles (launched/created): " << sm.missileLaunched(RED_TEAM) << " / " << sm.missileCreated(RED_TEAM);
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, RED_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    statsText.str("");
    statsText << "Minerals (spent/saved):  " << sm.mineralSpent(RED_TEAM) << " / " << sm.mineralSaved(RED_TEAM);
    _drawText(_statsSurface, statsText.str(), 10,  y, _statsFont, RED_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    y += FONT_HEIGHT * 4;

    // print zoom
    statsText.str("");
    statsText << "Zoom: " << _zoom;
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, WHITE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    // print mouse position
    statsText.str("");
    if(printMouse)
        statsText << "Cursor: " << mx << "x" << my;
    else
        statsText << "Cursor: - x -";
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, WHITE_COLOR, BG_COLOR);
    y += FONT_HEIGHT;

    // Show help
    y = _statsRect.h - FONT_HEIGHT - 5;
    statsText.str("");
    statsText << "Press F1 for help";
    _drawText(_statsSurface, statsText.str(), 10, y, _statsFont, WHITE_COLOR, BG_COLOR);
}

void RendererSDLDraw::postDraw()
{
    SDL_BlitSurface(_worldSurface, NULL, _screen, &_worldRect);
    SDL_BlitSurface(_statsSurface, NULL, _screen, &_statsRect);
}

void RendererSDLDraw::updateScreen(SDL_Surface *newScreen)
{
    SDL_Surface *tmp;

    _screen = newScreen;

    // playground surface
    _worldRect.x = 0;
    _worldRect.y = 0;
    _worldRect.w = _screen->w - STATS_WIDTH;
    _worldRect.h = _screen->h;

    tmp = SDL_CreateRGBSurface(_screen->flags, _worldRect.w, _worldRect.h, _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);
    if(tmp)
    {
        SDL_FreeSurface(_worldSurface);
        _worldSurface = tmp;
    }

    // zoom
    resetZoom();

    // stat surface
    _statsRect.x = _worldRect.w;
    _statsRect.y = 0;
    _statsRect.w = STATS_WIDTH;
    _statsRect.h = _screen->h;

    tmp = SDL_CreateRGBSurface(_screen->flags, _statsRect.w, _statsRect.h, _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);
    if(tmp)
    {
        SDL_FreeSurface(_statsSurface);
        _statsSurface = tmp;
    }
}

void RendererSDLDraw::resetPosition()
{
    _vpX = _cfg.WORLD_SIZE_X / 2.0;
    _vpY = _cfg.WORLD_SIZE_Y / 2.0;
}

void RendererSDLDraw::resetZoom()
{
    double zx = static_cast<double>(_worldRect.w) / _cfg.WORLD_SIZE_X;
    double zy = static_cast<double>(_worldRect.h) / _cfg.WORLD_SIZE_Y;

    _zoom = zx < zy ? zx : zy;
}

void RendererSDLDraw::_drawMineral(const RendererSDL::ItemEx *ite, const aiwar::core::ItemManager &im)
{
    const aiwar::core::Mineral *m = dynamic_cast<const aiwar::core::Mineral*>(ite->item);

    double px = m->xpos();
    double py = m->ypos();
    im.undoOffset(px, py);

    Sint16 sx, sy;
    _getPosOnScreen(px, py, sx, sy);

    SDL_Rect r;
    r.x = sx - static_cast<Sint16>(_cfg.MINERAL_SIZE_X/2.0);
    r.y = sy - static_cast<Sint16>(_cfg.MINERAL_SIZE_Y/2.0);
    r.w = static_cast<Uint16>(_cfg.MINERAL_SIZE_X);
    r.h = static_cast<Uint16>(_cfg.MINERAL_SIZE_Y);
    SDL_FillRect(_worldSurface, &r, SDL_MapRGB(_worldSurface->format, 0,255,128));
}

void RendererSDLDraw::_drawBase(const RendererSDL::ItemEx *ite, const aiwar::core::ItemManager &im)
{
    const aiwar::core::Base *b = dynamic_cast<const aiwar::core::Base*>(ite->item);

    double px = b->xpos();
    double py = b->ypos();
    im.undoOffset(px, py);

    Sint16 sx, sy;
    _getPosOnScreen(px, py, sx, sy);

    if (ite->selected)
    {
        // draw vision circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.BASE_DETECTION_RADIUS * _zoom), 255,255,0,255);

        // draw mining circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.MININGSHIP_MINING_RADIUS * _zoom), 190,192,192,255);

        // draw communication circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.COMMUNICATION_RADIUS * _zoom) , 0,192,128,255);
    }

    SDL_Rect r;
    r.x = sx - static_cast<Sint16>(_cfg.BASE_SIZE_X/2.0);
    r.y = sy - static_cast<Sint16>(_cfg.BASE_SIZE_Y/2.0);
    r.w = static_cast<Uint16>(_cfg.BASE_SIZE_X);
    r.h = static_cast<Uint16>(_cfg.BASE_SIZE_Y);

    Uint32 color = SDL_MapRGB(_worldSurface->format, 0,255,0);
    if(ite->selected)
        color = SDL_MapRGB(_worldSurface->format, 255,255,0);
    else if(b->team() == BLUE_TEAM)
        color = SDL_MapRGB(_worldSurface->format, 0,0,255);
    else if(b->team() == RED_TEAM)
        color = SDL_MapRGB(_worldSurface->format, 255,0,0);

    SDL_FillRect(_worldSurface, &r, color);
}

void RendererSDLDraw::_drawMiningShip(const RendererSDL::ItemEx *ite, const aiwar::core::ItemManager &im)
{
    const aiwar::core::MiningShip *m = dynamic_cast<const aiwar::core::MiningShip*>(ite->item);

    double px = m->xpos();
    double py = m->ypos();
    im.undoOffset(px, py);
    Sint16 sx, sy;
    _getPosOnScreen(px, py, sx, sy);

    if (ite->selected)
    {
        // draw vision circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.MININGSHIP_DETECTION_RADIUS * _zoom), 255,255,0,255);

        // draw mining circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.MININGSHIP_MINING_RADIUS * _zoom), 190,192,192,255);

        // draw communication circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.COMMUNICATION_RADIUS * _zoom) , 0,192,128,255);
    }

    SDL_Surface *rs = NULL;

    // rotate the ship
    if(ite->selected)
        rs = rotozoomSurface(_getSurface(SELECTED_MININGSHIP), m->angle(), 1.0, SMOOTHING_OFF);
    else if(m->team() == RED_TEAM)
        rs = rotozoomSurface(_getSurface(RED_MININGSHIP), m->angle(), 1.0, SMOOTHING_OFF);
    else if(m->team() == BLUE_TEAM)
        rs = rotozoomSurface(_getSurface(BLUE_MININGSHIP), m->angle(), 1.0, SMOOTHING_OFF);

    SDL_Rect r;
    r.x = sx - rs->w/2;
    r.y = sy - rs->h/2;
    r.w = rs->w;
    r.h = rs->h;

    SDL_BlitSurface(rs, NULL, _worldSurface, &r);
    SDL_FreeSurface(rs);
}

void RendererSDLDraw::_drawMissile(const RendererSDL::ItemEx *ite, const aiwar::core::ItemManager &im)
{
    const aiwar::core::Missile *m = dynamic_cast<const aiwar::core::Missile*>(ite->item);

    double px = m->xpos();
    double py = m->ypos();
    im.undoOffset(px, py);
    Sint16 sx, sy;
    _getPosOnScreen(px, py, sx, sy);

    SDL_Surface* tmp = SDL_CreateRGBSurface(_worldSurface->flags, static_cast<int>(_cfg.MISSILE_SIZE_X), static_cast<int>(_cfg.MISSILE_SIZE_Y), _worldSurface->format->BitsPerPixel, _worldSurface->format->Rmask, _worldSurface->format->Gmask, _worldSurface->format->Bmask, _worldSurface->format->Amask);

    SDL_FillRect(tmp, NULL, SDL_MapRGB(_worldSurface->format, 255,0,255));

    // rotate the missile
    SDL_Surface *rs = rotozoomSurface(tmp, m->angle(), 1.0, SMOOTHING_OFF);

    SDL_Rect r;
    r.x = sx - rs->w/2;
    r.y = sy - rs->h/2;
    r.w = rs->w;
    r.h = rs->h;
    SDL_BlitSurface(rs, NULL, _worldSurface, &r);

    SDL_FreeSurface(rs);
    SDL_FreeSurface(tmp);
}

void RendererSDLDraw::_drawFighter(const RendererSDL::ItemEx *ite, const aiwar::core::ItemManager &im)
{
    const aiwar::core::Fighter *f = dynamic_cast<const aiwar::core::Fighter*>(ite->item);

    double px = f->xpos();
    double py = f->ypos();
    im.undoOffset(px, py);
    Sint16 sx, sy;
    _getPosOnScreen(px, py, sx, sy);

    if(ite->selected)
    {
        // draw vision circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.FIGHTER_DETECTION_RADIUS * _zoom), 255,255,0,255);

        // draw communication circle
        circleRGBA(_worldSurface, sx, sy, static_cast<Sint16>(_cfg.COMMUNICATION_RADIUS * _zoom), 0,192,128,255);
    }

    SDL_Surface *rs = NULL;

    // rotate the ship
    if(ite->selected)
        rs = rotozoomSurface(_getSurface(SELECTED_FIGHTER), f->angle(), 1.0, SMOOTHING_OFF);
    else if(f->team() == RED_TEAM)
        rs = rotozoomSurface(_getSurface(RED_FIGHTER), f->angle(), 1.0, SMOOTHING_OFF);
    else if(f->team() == BLUE_TEAM)
        rs = rotozoomSurface(_getSurface(BLUE_FIGHTER), f->angle(), 1.0, SMOOTHING_OFF);

    SDL_Rect r;
    r.x = sx - rs->w/2;
    r.y = sy - rs->h/2;
    r.w = rs->w;
    r.h = rs->h;

    SDL_BlitSurface(rs, NULL, _worldSurface, &r);
    SDL_FreeSurface(rs);
}

void RendererSDLDraw::_drawText(SDL_Surface* surface, const std::string &str, int x, int y, TTF_Font* font, const SDL_Color &fgColor, const SDL_Color &bgColor, bool centered)
{
    SDL_Surface* textSurface = TTF_RenderText_Shaded(font, str.c_str(), fgColor, bgColor);
    SDL_Rect textLocation;

    if(centered)
    {
        textLocation.x = x - textSurface->w / 2;
        textLocation.y = y - textSurface->h / 2;
    }
    else
    {
        textLocation.x = x;
        textLocation.y = y;
    }
    textLocation.w =  0;
    textLocation.h = 0;

    SDL_BlitSurface(textSurface, NULL, surface, &textLocation);
    SDL_FreeSurface(textSurface);
}
