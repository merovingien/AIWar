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

#include "renderer_sdl.hpp"

#include "renderer_sdl_draw.hpp"
#include "renderer_sdl_console.hpp"

#include "item.hpp"
#include "playable.hpp"

#include <iostream>
#include <SDL/SDL.h>
#include <SDL/SDL_ttf.h>

#define SCREEN_WIDTH 1050
#define SCREEN_HEIGHT 800
//#define SPEED 400

// ms between each event treatment and draw (20 ms -> 50 FPS)
#define FRAME_DELAY 20

// ms between each play round
#define PLAY_DELAY 500

using namespace aiwar::renderer;

RendererSDL::RendererSDL() : _console(NULL), _drawer(NULL)
{
}

RendererSDL::~RendererSDL()
{
    finalize();
}

std::string RendererSDL::getName() const
{
    return "RendererSDL";
}

std::string RendererSDL::getVersion() const
{
    return "0.4.0";
}

bool RendererSDL::initialize(const std::string& params)
{
    std::cout << "SDL: params (untreated): '" << params << "'\n";

    // SDL init
    SDL_Init(SDL_INIT_VIDEO);
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);
    TTF_Init();

    /****** TEST HARDWARE ******/
//    const SDL_VideoInfo *info = SDL_GetVideoInfo();
//    printf("hardware surfaces? %d\n", info->hw_available);
//    printf("window manager available ? %d\n", info->wm_available);
    /*******/

    _screen = SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, 32, SDL_HWSURFACE | SDL_DOUBLEBUF | SDL_RESIZABLE);
    SDL_WM_SetCaption("AIWar", NULL);

    _console = new RendererSDLConsole(_screen);

    _drawer = new RendererSDLDraw(_screen);
    _drawer->debug(aiwar::core::Config::instance().debug);

    _manual = aiwar::core::Config::instance().manual;

    _frameDelay = FRAME_DELAY;
    _playDelay = PLAY_DELAY;

    _startTimeFrame = SDL_GetTicks() - _frameDelay; // to force process and draw at the first call of render()
    _startTimePlay = SDL_GetTicks();

    return true;
}

bool RendererSDL::finalize()
{
    delete _drawer;
    _drawer = NULL;

    delete _console;
    _console = NULL;

    TTF_Quit();
    SDL_Quit();
    return true;
}

bool RendererSDL::render(const aiwar::core::ItemManager &itemManager, const aiwar::core::StatManager &statManager, bool gameover)
{
    SDL_Event e;
    bool cont = true;
    Uint32 ellapsedTimeFrame, ellapsedTimePlay;
    Sint32 remainingTimeFrame, remainingTimePlay;

    bool play = false; // shall we return to play

    // update itemExMap at each round
    _updateItemEx(itemManager);

    // new round
    std::ostringstream oss;
    oss << "********************* Round #" << statManager.round() << " *********************";
    _console->appendText(oss.str());

    while(cont && (gameover || !play))
    {
        bool process = false; // shall we process events and draw

        Uint32 currentTime = SDL_GetTicks();

        /* FPS */
        ellapsedTimeFrame = currentTime - _startTimeFrame; // ellapsed time since the last event processing and draw
        remainingTimeFrame = _frameDelay - ellapsedTimeFrame; // remaining time for the next event processing and draw

        /* Play */
        if(!_manual)
        {
            ellapsedTimePlay = currentTime - _startTimePlay; // ellapsed time since the last play
            remainingTimePlay = _playDelay - ellapsedTimePlay;  // remaining time for the next play
        }
        else
        {
            remainingTimePlay = (remainingTimeFrame > 0) ? remainingTimeFrame+1 : 1;
            // so remainingTimePlay is always positive and bigger than remainingTimeFrame -> never play and never wait for playing
        }

        // shall we process ?
        if(remainingTimeFrame <= 0)
            process = true;

        // shall we draw ?
        if(remainingTimePlay <= 0)
            play = true;

        // shall we wait ?
        if(!process && !play)
        {
            if(remainingTimeFrame <= remainingTimePlay)
            {
                // we must wait to process
                SDL_Delay(remainingTimeFrame);
                process = true;
            }
            else
            {
                // we must wait to play
                SDL_Delay(remainingTimePlay);
                play = true;
            }
        }

        // shall we process ?
        if(process)
        {
            bool click = false;
            int mcx, mcy;
            int dx = 0, dy = 0;
            int dz = 0;

            _startTimeFrame = SDL_GetTicks();

            // treat all events
            while(SDL_PollEvent(&e))
            {
                switch(e.type)
                {
                case SDL_QUIT:
                    cont = false; // exit
                    break;

                case SDL_KEYDOWN:
                    switch(e.key.keysym.sym)
                    {
                    case SDLK_ESCAPE:
                        cont = false; // exit
                        break;

                    case SDLK_F1: // help
                        _console->help(!_console->isHelp());
                        break;

                    case SDLK_SPACE: // force play
                        play = true;
                        break;

                    case SDLK_d: // toggle debug
                        _drawer->toggleDebug();
                        break;

                    case SDLK_m: // toggle manual
                    case SDLK_p: // <=> pause
                        _manual = !_manual;
                        break;

                    case SDLK_s: // toggle full speed play
                        _playDelay = PLAY_DELAY - _playDelay;
                        break;

                    case SDLK_c: // togle console display
                        _console->show(!_console->isShow());
                        break;

                    case SDLK_r: // reset viewport position
                        _drawer->resetPosition();
                        break;

                    case SDLK_z: // reset zoom
                        _drawer->resetZoom();
                        break;

                    case SDLK_UP:   // console scrolling
                    case SDLK_DOWN:
                    case SDLK_HOME:
                    case SDLK_END:
                        _console->scroll(e.key.keysym.sym);
                        break;

                    case SDLK_a: // zoom
                        dz++;
                        break;

                    case SDLK_q: // dezoom
                        dz--;
                        break;

                    default:
                        break;
                    }
                    break;

                case SDL_MOUSEBUTTONDOWN:
                    switch(e.button.button)
                    {
                    case SDL_BUTTON_LEFT: // manage clicks. Should be a list of clicks
                        click = true;
                        mcx = e.button.x;
                        mcy = e.button.y;
                        break;

                    case SDL_BUTTON_WHEELUP: // zoom
                        dz++;
                        break;

                    case SDL_BUTTON_WHEELDOWN: // dezoom
                        dz--;
                        break;

                    default:
                        break;
                    }
                    break;

                case SDL_MOUSEMOTION: // screen sliding
                    if(e.motion.state)
                    {
                        dx += e.motion.xrel;
                        dy += e.motion.yrel;
                    }
                    break;

                case SDL_VIDEORESIZE:
                    // can be optimised by doing it only at draw time
                    _screen = SDL_SetVideoMode(e.resize.w, e.resize.h, 32, SDL_HWSURFACE | SDL_DOUBLEBUF | SDL_RESIZABLE);
                    _drawer->updateScreen(_screen);
                    _console->updateScreen(_screen);
                    break;

                default:
                    break;
                }
            }

            /* screen update */

            int mx, my;
            SDL_GetMouseState(&mx, &my);

            _drawer->preDraw(click, mcx, mcy, dx, dy, dz, mx, my);
            _console->preDraw();

            ItemExMap::iterator it;
            for(it = _itemExMap.begin() ; it != _itemExMap.end() ; ++it)
            {
                // draw
                _drawer->draw(&it->second, itemManager);

                // print log if selected
                if(it->second.selected)
                {
//                    std::cout << it->second.logStream.str();
                    _console->appendText(it->second.logStream.str());
                }

                // flush logStream
                it->second.logStream.str("");
            }

            _drawer->drawStats(statManager);

            _console->draw();

            _drawer->postDraw();
            _console->postDraw();

            SDL_Flip(_screen);
        }

    } // end while(!play)

    _startTimePlay = SDL_GetTicks();

    return cont;
}

/// \todo improve it by reading each map only once: they are sorted !!!
void RendererSDL::_updateItemEx(const aiwar::core::ItemManager& itemManager)
{
    aiwar::core::ItemManager::ItemMap::const_iterator it_src;
    ItemExMap::iterator it_loc, it_del;
/*
    std::cout << "avant: \nItemMap:   [";
    for(it_src = itemManager.begin() ; it_src != itemManager.end() ; ++it_src)
        std::cout << it_src->first << ", ";
    std::cout << "]\nItemExMap: [";
    for(it_loc = _itemExMap.begin() ; it_loc != _itemExMap.end() ; ++it_loc)
        std::cout << it_loc->first << ", ";
    std::cout << "]\n";
*/
    for(it_src = itemManager.begin() ; it_src != itemManager.end() ; ++it_src)
    {
        ItemEx &ite = _itemExMap[it_src->first];
        ite.item = it_src->second;
        const aiwar::core::Playable* p = dynamic_cast<const aiwar::core::Playable*>(it_src->second);
        if(p)
            ite.logStream << p->getLog();
    }

    for(it_loc = _itemExMap.begin() ; it_loc != _itemExMap.end() ; )
    {
        it_del = it_loc;
        ++it_loc;

        if(!itemManager.exists(it_del->first))
            _itemExMap.erase(it_del);
    }
}

RendererSDL::ItemEx::ItemEx() : item(NULL), selected(false), logStream()
{
}

RendererSDL::ItemEx::ItemEx(const ItemEx& o) : item(o.item), selected(o.selected), logStream()
{
    logStream << o.logStream.str();
}

RendererSDL::ItemEx::~ItemEx()
{
}
