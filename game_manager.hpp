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

#ifndef GAME_MANAGER_HPP
#define GAME_MANAGER_HPP

#include "config.hpp"
#include "playable.hpp"

#include <map>

namespace aiwar {
    namespace core {

        class ItemManager;
        class StatManager;

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

            bool init();

            ItemManager& getItemManager();
            const ItemManager& getItemManager() const;

            StatManager& getStatManager();
            const StatManager& getStatManager() const;

            PlayFunction& getBasePF(Team team) const;
            PlayFunction& getMiningShipPF(Team team) const;
            PlayFunction& getFighterPF(Team team) const;

            void update(unsigned int ticks);

            bool gameOver() const;
            Team getWinner() const;

        private:
            class TeamInfo;

            typedef std::map<Team, TeamInfo> TeamMap;

            const TeamInfo& _getTeamInfo(Team team) const;

            TeamMap _teamMap;
            ItemManager *_im;
            StatManager *_sm;
        };


        class GameManager::TeamInfo
        {
        public:
            TeamInfo(PlayFunction& pfb = Playable::playNoOp, PlayFunction& pfm = Playable::playNoOp, PlayFunction& pff = Playable::playNoOp);

            PlayFunction& play_base;
            PlayFunction& play_miningShip;
            PlayFunction& play_fighter;
        };

    } // aiwar::core
} // aiwar

#endif /* GAME_MANAGER_HPP */
