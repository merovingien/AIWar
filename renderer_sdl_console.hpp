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

#ifndef RENDERER_SDL_CONSOLE_HPP
#define RENDERER_SDL_CONSOLE_HPP

#include <vector>

#include <SDL/SDL.h>
#include <SDL/SDL_ttf.h>

namespace aiwar {

    namespace renderer {

        class RendererSDLConsole
        {
        public:
            RendererSDLConsole(SDL_Surface *s);
            ~RendererSDLConsole();

            void preDraw();
            void draw();
            void postDraw();
            void updateScreen(SDL_Surface *newScreen);

            bool isShow() const;
            void show(bool b = true);

            void scroll(SDLKey k);
            
            void appendText(const std::string& txt);

        private:
            void _drawText(const std::string& txt, int line);

            SDL_Surface *_screen;

            SDL_Rect _consoleRect;
            SDL_Surface *_consoleSurface;

            bool _show;
            std::vector<std::string> _queue;
            unsigned long _firstLine;

            TTF_Font *_consoleFont;
            unsigned int _FONT_LINE_SKIP;
        };

    } // aiwar::renderer
} // aiwar

#endif /* RENDERER_SDL_CONSOLE_HPP */
