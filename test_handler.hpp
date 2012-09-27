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

#ifndef TEST_HANDLER_HPP
#define TEST_HANDLER_HPP

#include "handler_interface.hpp"

class TestHandler : public aiwar::core::HandlerInterface
{
public:
    typedef aiwar::core::Playable::Team T;
    typedef aiwar::core::PlayFunction PF;

    TestHandler();

    bool initialize();
    bool finalize();

    PF& get_BaseHandler(T team);
    PF& get_MiningShipHandler(T team);
    PF& get_FighterHandler(T team);

private:
    aiwar::core::DefaultPlayFunction _pf_Base;
    aiwar::core::DefaultPlayFunction _pf_MiningShip;
    aiwar::core::DefaultPlayFunction _pf_Fighter;

    static void play_miningship(aiwar::core::Playable*);
    static void play_base(aiwar::core::Playable*);
    static void play_fighter(aiwar::core::Playable*);
};



#endif /* TEST_HANDLER_HPP */
