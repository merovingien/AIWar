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

#include "renderer_summary.hpp"

#include <iostream>

using namespace aiwar::renderer;

RendererSummary::RendererSummary()
{
}

RendererSummary::~RendererSummary()
{
}

std::string RendererSummary::getName() const
{
    return "RendererSummary";
}

std::string RendererSummary::getVersion() const
{
    return "0.1.0";
}

bool RendererSummary::initialize(const std::string&)
{
    return true;
}

bool RendererSummary::finalize()
{
    return true;
}

bool RendererSummary::render(const aiwar::core::ItemManager&, const aiwar::core::StatManager& sm, bool gameover, const aiwar::core::Team& winner)
{
    if(gameover)
    {
        std::cout << "winner: ";
        switch(winner)
        {
        case aiwar::core::BLUE_TEAM:
            std::cout << "blue";
            break;
        case aiwar::core::RED_TEAM:
            std::cout << "red";
            break;
        case aiwar::core::NO_TEAM:
        default:
            std::cout << "draw";
        }
        std::cout << std::endl;

        std::cout << sm.dump();
    }
    return true;
}
