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

// font size
const int FONT_SIZE = 16;

// colors
const SDL_Color BLACK_COLOR = { 0x00, 0x00, 0x00, 0 };

RendererSDLConsole::RendererSDLConsole(SDL_Surface *s) : _screen(s), _consoleSurface(NULL), _show(false), _firstLine(0), _help(false), _helpFirstLine(0)
{
    // console surface
    _consoleRect.x = 0;
    _consoleRect.y = 0;
    _consoleRect.w = _screen->w;
    _consoleRect.h = _screen->h;

    _consoleSurface = SDL_CreateRGBSurface(_screen->flags, _consoleRect.w, _consoleRect.h, _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);
    SDL_SetAlpha(_consoleSurface, SDL_SRCALPHA | SDL_RLEACCEL, 128);

    _consoleFont = TTF_OpenFont("./fonts/Jura-Medium.ttf", FONT_SIZE);
    _FONT_LINE_SKIP = TTF_FontLineSkip(_consoleFont);

    _helpQueue.push_back(" ----- AIWar -----");
    _helpQueue.push_back(" ");
    _helpQueue.push_back(" ");
    _helpQueue.push_back(" * Keyboard shortcuts *");
    _helpQueue.push_back(" ");
    _helpQueue.push_back(" F1     - Close this menu");
    _helpQueue.push_back(" Escape - Quit the game");
    _helpQueue.push_back(" Space  - Play one round");
    _helpQueue.push_back(" P      - Pause / Unpause");
    _helpQueue.push_back(" S      - Play without pause (full speed)");
    _helpQueue.push_back(" D      - Active/Deactive debug mode");
    _helpQueue.push_back(" Z      - Reset zoom");
    _helpQueue.push_back(" R      - Reset postition");
    _helpQueue.push_back(" C      - Show/Hide console");
    _helpQueue.push_back(" UP     - Scroll up console or help");
    _helpQueue.push_back(" DOWN   - Scroll down console or help");
    _helpQueue.push_back(" ");
    _helpQueue.push_back(" * Mouse *");
    _helpQueue.push_back(" ");
    _helpQueue.push_back(" Click  - Select/Unselect item");
    _helpQueue.push_back(" Wheel  - Zoom/Dezoom");

    _helpFirstLine = _helpQueue.size() - 1;
}

RendererSDLConsole::~RendererSDLConsole()
{
    TTF_CloseFont(_consoleFont);

    SDL_FreeSurface(_consoleSurface);
}

void RendererSDLConsole::preDraw()
{
    if(_show || _help)
    {
        SDL_FillRect(_consoleSurface, NULL, SDL_MapRGB(_screen->format,0xFF,0xFF,0xFF));
    }
}

void RendererSDLConsole::draw()
{
    if(_help)
    {
        // compute max number of lines to print
        unsigned int maxNbLine = _consoleRect.h / _FONT_LINE_SKIP;
        if(_helpQueue.size() < maxNbLine)
            maxNbLine = _helpQueue.size();

        // compute first line
        if(_helpFirstLine + maxNbLine > _helpQueue.size())
            _helpFirstLine = _helpQueue.size() - maxNbLine;

        unsigned int i;
        for(i = 0 ; i < maxNbLine ; ++i)
        {
            _drawText(_helpQueue.at(i + _helpFirstLine), i);
        }
    }
    else if(_show)
    {
        // compute max number of lines to print
        unsigned int maxNbLine = _consoleRect.h / _FONT_LINE_SKIP;
        if(_queue.size() < maxNbLine)
            maxNbLine = _queue.size();

        // compute first line
        if(_firstLine + maxNbLine > _queue.size())
            _firstLine = _queue.size() - maxNbLine;

        unsigned int i;
        for(i = 0 ; i < maxNbLine ; ++i)
        {
            _drawText(_queue.at(i + _firstLine), i);
        }
    }
}

void RendererSDLConsole::postDraw()
{
    if(_show || _help)
    {
        SDL_BlitSurface(_consoleSurface, NULL, _screen, &_consoleRect);
    }
}

void RendererSDLConsole::updateScreen(SDL_Surface *newScreen)
{
    SDL_Surface *tmp;

    _screen = newScreen;

    // console surface
    _consoleRect.x = 0;
    _consoleRect.y = 0;
    _consoleRect.w = _screen->w;
    _consoleRect.h = _screen->h;

    tmp = SDL_CreateRGBSurface(_screen->flags, _consoleRect.w, _consoleRect.h, _screen->format->BitsPerPixel, _screen->format->Rmask, _screen->format->Gmask, _screen->format->Bmask, _screen->format->Amask);
    if(tmp)
    {
        SDL_FreeSurface(_consoleSurface);
        _consoleSurface = tmp;
        SDL_SetAlpha(_consoleSurface, SDL_SRCALPHA | SDL_RLEACCEL, 128);
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

bool RendererSDLConsole::isHelp() const
{
    return _help;
}

void RendererSDLConsole::help(bool b)
{
    _help = b;
}

void RendererSDLConsole::scroll(SDLKey k)
{
    if(_show || _help)
    {
        switch(k)
        {
        case SDLK_UP:
            if(_help)
            {
                if(_helpFirstLine > 0)
                    _helpFirstLine--;
            }
            else if(_show)
            {
                if(_firstLine > 0)
                    _firstLine--;
            }
            break;

        case SDLK_DOWN:
            if(_help)
            {
                if(_helpFirstLine < _helpQueue.size() - 1)
                    _helpFirstLine++;
            }
            else if(_show)
            {
                if(_firstLine < _queue.size() - 1)
                    _firstLine++;
            }
            break;

        case SDLK_HOME:
            if(_help)
                _helpFirstLine = 0;
            else if(_show)
                _firstLine = 0;
            break;

        case SDLK_END:
            if(_help)
                _helpFirstLine = _helpQueue.size() - 1;
            else if(_show)
                _firstLine = _queue.size() - 1;
            break;

        default:
            break;
        }
    }
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
            oss << n++ << " | " << txt.substr(b, e-b);
            _queue.push_back(oss.str());
            b = e+1;
            oss.str("");
        }
        std::string last = txt.substr(b);
        if(!last.empty())
        {
            oss << n++ << " | " << last;
            _queue.push_back(oss.str());
        }

        // update _firstLine
        _firstLine = _queue.size() - 1;
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
