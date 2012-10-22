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

using namespace aiwar::renderer;

std::string RendererSDL::getName() const
{
    return "RendererSDL";
}

std::string RendererSDL::getVersion() const
{
    return "0.1.0";
}

bool RendererSDL::initialize(const std::string& params)
{
    return true;
}
	    
bool RendererSDL::finalize()
{
    return true;
}

bool RendererSDL::render(const aiwar::core::ItemManager::ItemMap::const_iterator &cit, const aiwar::core::GameManager::Stat &stats, bool gameover)
{
    return true;
}
