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

#ifndef GAME_MANAGER_HPP
#define GAME_MANAGER_HPP

#include "playable.hpp"

#include <map>

namespace aiwar {
    namespace core {

	class Item;
	class Base;
	class MiningShip;
	class Fighter;
	class Missile;
	class Mineral;


	class GameManager
	{
	public:
	    GameManager();
	    ~GameManager();
	    
	    void registerTeam(Playable::Team, Playable::PlayFunction pfBase, Playable::PlayFunction pfMiningShip, Playable::PlayFunction pfFighter);

	    Playable::PlayFunction getBasePF(Playable::Team team) const;
	    Playable::PlayFunction getMiningShipPF(Playable::Team team) const;
	    Playable::PlayFunction getFighterPF(Playable::Team team) const;

	    // slots
	    void baseCreated(const Base*);
	    void baseDestroyed(const Base*);
	    void miningShipCreated(const MiningShip*);
	    void miningShipDestroyed(const MiningShip*);
	    void fighterCreated(const Fighter*);
	    void fighterDestroyed(const Fighter*);
	    void missileCreated(const Missile*);
	    void missileDestroyed(const Missile*);
	    void mineralCreated(const Mineral*);
	    void mineralDestroyed(const Mineral*);
	    void itemDestroyed(const Item*);

	    void printStat() const;

	private:
	    class TeamInfo;

	    typedef std::map<Playable::Team, TeamInfo> TeamMap;

	    const TeamInfo& _getTeamInfo(Playable::Team team) const;

	    TeamMap _teamMap;    
	};

	class GameManager::TeamInfo
	{
	public:
	    TeamInfo();

	    Playable::PlayFunction play_base;
	    Playable::PlayFunction play_miningShip;
	    Playable::PlayFunction play_fighter;

	    unsigned int nb_base;
	    unsigned int nb_base_max;
	    unsigned int nb_miningShip;
	    unsigned int nb_miningShip_max;
	    unsigned int nb_fighter;
	    unsigned int nb_fighter_max;
	};

    } // aiwar::core
} // aiwar


#endif /* GAME_MANAGER_HPP */
