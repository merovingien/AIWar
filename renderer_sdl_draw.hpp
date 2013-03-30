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

#ifndef RENDERER_SDL_DRAW_HPP
#define RENDERER_SDL_DRAW_HPP

#include <map>
#include <SDL/SDL_ttf.h>

#include "renderer_sdl.hpp" // for RendererSDL::ItemEx

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
        class ItemManager;
        class StatManager;
    }

    namespace renderer {

        class RendererSDLDraw
        {
        public:

            static const int SMALL_FONT_SIZE = 12;
            static const int BIG_FONT_SIZE = 28;
            static const Uint16 STATS_WIDTH = 250;

            RendererSDLDraw(SDL_Surface *s);
            ~RendererSDLDraw();

            void preDraw(bool clicked, int xmouseClick, int ymouseClick, int dxViewPort, int dyViewPort, int dz, int xmousePos, int ymousePos);
            void draw(RendererSDL::ItemEx *itemEx, const aiwar::core::ItemManager &im);
            void drawStats(const aiwar::core::StatManager &sm);
            void postDraw();
            void updateScreen(SDL_Surface *newScreen);
            
            void resetPosition();
            void resetZoom();

            void setWinner(const aiwar::core::Team& winner);

        private:

            enum ItemType {
                BLUE_DEFAULT_BASE, // unused
                BLUE_LIGHT_BASE, // unused
                BLUE_DARK_BASE, // unused
                BLUE_DEFAULT_MININGSHIP,
                BLUE_LIGHT_MININGSHIP,
                BLUE_DARK_MININGSHIP,
                BLUE_DEFAULT_FIGHTER,
                BLUE_LIGHT_FIGHTER,
                BLUE_DARK_FIGHTER,
                RED_DEFAULT_BASE,
                RED_LIGHT_BASE,
                RED_DARK_BASE,
                RED_DEFAULT_MININGSHIP,
                RED_LIGHT_MININGSHIP,
                RED_DARK_MININGSHIP,
                RED_DEFAULT_FIGHTER,
                RED_LIGHT_FIGHTER,
                RED_DARK_FIGHTER,
                SELECTED_BASE, // unused
                SELECTED_MININGSHIP,
                SELECTED_FIGHTER,
                MISSILE, // unused
                MINERAL // unused
            };

            void _drawMineral(const RendererSDL::ItemEx *m, const aiwar::core::ItemManager &im);
            void _drawMissile(const RendererSDL::ItemEx *m, const aiwar::core::ItemManager &im);
            void _drawMiningShip(const RendererSDL::ItemEx *m, const aiwar::core::ItemManager &im);
            void _drawBase(const RendererSDL::ItemEx *b, const aiwar::core::ItemManager &im);
            void _drawFighter(const RendererSDL::ItemEx *f, const aiwar::core::ItemManager &im);

            void _drawText(SDL_Surface* surface, const std::string &str, int x, int y, TTF_Font* font, const SDL_Color &fgColor, const SDL_Color &bgColor, bool centered = false);

            // return the position of a point in the screen coords considering the current viewport
            // return true if the point is in the world Rect
            bool _getPosOnScreen(const double &px, const double &py, Sint16 &screenPx, Sint16 &screenPy) const;
            // return the position of the mouse pointer (mouseX, mouseY) in the world coords
            // return true if the mouse is in the world Rect
            bool _getMousePos(const int &mouseX, const int &mouseY, double &px, double &py) const;

            SDL_Surface* _createBase(const SDL_Color& color) const;
            SDL_Surface* _createMiningShip(const SDL_Color& color) const;
            SDL_Surface* _createFighter(const SDL_Color& color) const;

            void _addSurface(ItemType, SDL_Surface* surf);
            SDL_Surface* _getSurface(ItemType) const;

            const aiwar::core::Config& _cfg;

            SDL_Surface *_screen;
            SDL_Rect _worldRect;
            SDL_Surface *_worldSurface;
            double _vpX, _vpY; // center of the viewport
            double _zoom;
            std::map<ItemType, SDL_Surface*> _surfaceMap;

            SDL_Rect _statsRect;
            SDL_Surface *_statsSurface;

            // Fonts
            TTF_Font *_statsFont;
            TTF_Font *_aiwarFont;

            // context
            bool _clicked;
            int _xmouseClick, _ymouseClick;
            int _xmousePos, _ymousePos;

            // teams name
            std::string _blueName;
            std::string _redName;

            bool _gameover;
            aiwar::core::Team _winner;
        };
        
    }
}

#endif /* RENDERER_SDL_DRAW_HPP */
