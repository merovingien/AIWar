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

#define SMALL_FONT_SIZE 10
#define BIG_FONT_SIZE 20

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
            RendererSDLDraw(SDL_Surface *s);
            ~RendererSDLDraw();

            void preDraw(bool clicked, int xmouse, int ymouse);
            void draw(RendererSDL::ItemEx *itemEx, const aiwar::core::ItemManager &im);
            void drawStats(const aiwar::core::StatManager &sm);
            void postDraw();
            void updateScreen(SDL_Surface *newScreen);
            
            void debug(bool active);
            void toggleDebug();

        private:

            enum ItemType {
                BLUE_BASE,
                BLUE_MININGSHIP,
                BLUE_FIGHTER,
                RED_BASE,
                RED_MININGSHIP,
                RED_FIGHTER,
                SELECTED_BASE,
                SELECTED_MININGSHIP,
                SELECTED_FIGHTER,
                MISSILE,
                MINERAL
            };

            void _drawMineral(const RendererSDL::ItemEx *m, const aiwar::core::ItemManager &im);
            void _drawMissile(const RendererSDL::ItemEx *m, const aiwar::core::ItemManager &im);
            void _drawMiningShip(const RendererSDL::ItemEx *m, const aiwar::core::ItemManager &im);
            void _drawBase(const RendererSDL::ItemEx *b, const aiwar::core::ItemManager &im);
            void _drawFighter(const RendererSDL::ItemEx *f, const aiwar::core::ItemManager &im);

            void _drawText(SDL_Surface* surface, const std::string &str, int x, int y, TTF_Font* font, const SDL_Color &fgColor, const SDL_Color &bgColor, bool centered = false);

            void _addSurface(ItemType, SDL_Surface* surf);
            SDL_Surface* _getSurface(ItemType) const;

            const aiwar::core::Config& _cfg;

            bool _debug;
            SDL_Surface *_screen;
            SDL_Rect *_worldRect;
            SDL_Surface *_worldSurface;
            std::map<ItemType, SDL_Surface*> _surfaceMap;

            SDL_Surface *_statsSurface;
            SDL_Rect *_statsRect;

            // Fonts
            TTF_Font* _statsFont;
            TTF_Font* _aiwarFont;

            // context
            bool _clicked;
            int _xmouse, _ymouse;
        };
        
    }
}

#endif /* RENDERER_SDL_DRAW_HPP */
