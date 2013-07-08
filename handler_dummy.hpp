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

#ifndef HANDLER_DUMMY_HPP
#define HANDLER_DUMMY_HPP

#include "handler_interface.hpp"

class HandlerDummy : public aiwar::core::HandlerInterface
{
public:
    typedef aiwar::core::Config::Player P;
    typedef aiwar::core::PlayFunction PF;

    HandlerDummy();

    bool initialize();
    bool finalize();

    bool load(P player, const std::string& params);
    bool unload(P player);

    PF& get_BaseHandler(P player);
    PF& get_MiningShipHandler(P player);
    PF& get_FighterHandler(P player);

private:
    aiwar::core::DefaultPlayFunction _pf_Base;
    aiwar::core::DefaultPlayFunction _pf_MiningShip;
    aiwar::core::DefaultPlayFunction _pf_Fighter;

    static void play_miningship(aiwar::core::Playable*);
    static void play_base(aiwar::core::Playable*);
    static void play_fighter(aiwar::core::Playable*);
};



#endif /* HANDLER_DUMMY_HPP */
