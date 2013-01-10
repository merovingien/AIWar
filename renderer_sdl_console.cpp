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

#include <iostream>
#include <sstream>

#include "renderer_sdl_console.hpp"

using namespace aiwar::renderer;

// colors
const SDL_Color BLACK_COLOR = { 0x00, 0x00, 0x00, 0 };

RendererSDLConsole::RendererSDLConsole(SDL_Surface *s) : _screen(s), _show(false)
{
    // console surface
    _consoleRect = new SDL_Rect();
    _consoleRect->x = 0;
    _consoleRect->y = 0;
    _consoleRect->w = _screen->w;
    _consoleRect->h = _screen->h;

    _consoleSurface = SDL_CreateRGBSurface(_screen->flags, _consoleRect->w, _consoleRect->h, _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);
    SDL_SetAlpha(_consoleSurface, SDL_SRCALPHA | SDL_RLEACCEL, 128);

    _consoleFont = TTF_OpenFont("./fonts/Jura-Medium.ttf", 18);
    _FONT_LINE_SKIP = TTF_FontLineSkip(_consoleFont);
}

RendererSDLConsole::~RendererSDLConsole()
{
    TTF_CloseFont(_consoleFont);

    SDL_FreeSurface(_consoleSurface);
    delete _consoleRect;
}

void RendererSDLConsole::preDraw()
{
    if(_show)
    {
        SDL_FillRect(_consoleSurface, NULL, SDL_MapRGB(_screen->format,0xFF,0xFF,0xFF));
    }
}

void RendererSDLConsole::draw()
{
    if(_show)
    {
        // compute max number of lines to print
        unsigned int maxNbLine = _consoleRect->h / _FONT_LINE_SKIP;
        if(_queue.size() < maxNbLine)
            maxNbLine = _queue.size();

        unsigned int i;
        std::deque<std::string>::const_iterator cit = _queue.begin();
        for(i = maxNbLine-1 ; i < maxNbLine ; --i)
        {
            _drawText(*cit, i);
            cit++;
        }
    }
}

void RendererSDLConsole::postDraw()
{
    if(_show)
    {
        SDL_BlitSurface(_consoleSurface, NULL, _screen, _consoleRect);
    }
}

bool RendererSDLConsole::isShow() const
{
    return _show;
}

void RendererSDLConsole::show(bool b)
{
    _show = b;
}

void RendererSDLConsole::appendText(const std::string& txt)
{
    static unsigned long n = 0;

    std::ostringstream oss;

    if(!txt.empty())
    {
        std::string::size_type b = 0, e = 0;
        while((e = txt.find('\n', b)) != std::string::npos)
        {
            oss << n++ << " - " << txt.substr(b, e-b);
            _queue.push_front(oss.str());
            b = e+1;
            oss.str("");
        }
        oss << n++ << " - " << txt.substr(b);
        _queue.push_front(oss.str());
    }
}

void RendererSDLConsole::_drawText(const std::string& txt, int line)
{
    SDL_Surface* textSurface = TTF_RenderText_Solid(_consoleFont, txt.c_str(), BLACK_COLOR);
    SDL_Rect textLocation;

    textLocation.x = 0;
    textLocation.y = line * _FONT_LINE_SKIP;

    SDL_BlitSurface(textSurface, NULL, _consoleSurface, &textLocation);
    SDL_FreeSurface(textSurface);
}
