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

#ifndef RENDERER_SDL_HPP
#define RENDERER_SDL_HPP

#include "renderer_interface.hpp"

#include <SDL/SDL.h>

namespace aiwar {
    namespace renderer {

        class RendererSDLDraw;

        class RendererSDL : public RendererInterface
        {
        public:
            RendererSDL();
            ~RendererSDL();

            std::string getName() const;
            std::string getVersion() const;

            bool initialize(const std::string& params);

            bool finalize();

            bool render(const aiwar::core::ItemManager &itemManager,
                        const aiwar::core::StatManager &statManager,
                        bool gameover);

        private:
            SDL_Surface *_screen;
            RendererSDLDraw *_drawer;
            bool _manual;

            Uint32 _frameDelay;
            Uint32 _playDelay;

            Uint32 _startTimeFrame;
            Uint32 _startTimePlay;
        };

    } // aiwar::renderer
} // aiwar

#endif
