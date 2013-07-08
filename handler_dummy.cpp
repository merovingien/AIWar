/*
 * Copyright (C) 2012, 2013 Paul Grégoire
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

#include "handler_dummy.hpp"

#include "base.hpp"
#include "miningship.hpp"
#include "fighter.hpp"

HandlerDummy::HandlerDummy()
    : _pf_Base(&play_base), _pf_MiningShip(&play_miningship), _pf_Fighter(&play_fighter)
{
}

bool HandlerDummy::initialize()
{
    return true;
}

bool HandlerDummy::finalize()
{
    return true;
}

bool HandlerDummy::load(P, const std::string&)
{
    return true;
}

bool HandlerDummy::unload(P)
{
    return true;
}

HandlerDummy::PF& HandlerDummy::get_BaseHandler(P)
{
    return _pf_Base;
}

HandlerDummy::PF& HandlerDummy::get_MiningShipHandler(P)
{
    return _pf_MiningShip;
}

HandlerDummy::PF& HandlerDummy::get_FighterHandler(P)
{
    return _pf_Fighter;
}

void HandlerDummy::play_miningship(aiwar::core::Playable*)
{
}

void HandlerDummy::play_base(aiwar::core::Playable*)
{
}

void HandlerDummy::play_fighter(aiwar::core::Playable*)
{
}
