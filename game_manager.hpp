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

#include "config.hpp"
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
	    
	    void registerTeam(Team team, PlayFunction& pfBase, PlayFunction& pfMiningShip, PlayFunction& pfFighter);

	    PlayFunction& getBasePF(Team team) const;
	    PlayFunction& getMiningShipPF(Team team) const;
	    PlayFunction& getFighterPF(Team team) const;

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
        void mineralSaved(const Team, const  unsigned int);
        void mineralSpent(const Team, const  unsigned int);
	    void itemDestroyed(const Item*);

	    void printStat() const;

	    bool gameOver() const;
	    Team getWinner() const;

	private:
	    class TeamInfo;

	    typedef std::map<Team, TeamInfo> TeamMap;

	    const TeamInfo& _getTeamInfo(Team team) const;

	    TeamMap _teamMap;
	};

	class GameManager::TeamInfo
	{
	public:
	    TeamInfo(PlayFunction& pfb = Playable::playNoOp, PlayFunction& pfm = Playable::playNoOp, PlayFunction& pff = Playable::playNoOp);

	    PlayFunction& play_base;
	    PlayFunction& play_miningShip;
	    PlayFunction& play_fighter;

	    unsigned int nb_base;
	    unsigned int nb_base_max;
	    unsigned int nb_miningShip;
	    unsigned int nb_miningShip_max;
	    unsigned int nb_fighter;
	    unsigned int nb_fighter_max;
	    unsigned int nb_mineral_spent;
	    unsigned int nb_mineral_saved;
	};

    } // aiwar::core
} // aiwar


#endif /* GAME_MANAGER_HPP */
