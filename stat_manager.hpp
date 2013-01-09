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

#ifndef STAT_MANAGER_HPP
#define STAT_MANAGER_HPP

#include "config.hpp"

namespace aiwar {
    namespace core {

        class Item;
        class Base;
        class MiningShip;
        class Fighter;
        class Missile;
        class Mineral;

        class StatManager
        {
        public:
            StatManager();
            ~StatManager();

            // slots
            void nextRound();
            unsigned int round() const;
            void baseCreated(const Base*);
            void baseDestroyed(const Base*);
            unsigned int baseCurrent(const Team&) const;
            unsigned int baseMax(const Team&) const;
            void miningShipCreated(const MiningShip*);
            void miningShipDestroyed(const MiningShip*);
            unsigned int miningShipCurrent(const Team&) const;
            unsigned int miningShipMax(const Team&) const;
            void fighterCreated(const Fighter*);
            void fighterDestroyed(const Fighter*);
            unsigned int fighterCurrent(const Team&) const;
            unsigned int fighterMax(const Team&) const;
            void missileCreated(const Team&, unsigned int);
            void missileLaunched(const Team&, unsigned int);
            unsigned int missileCreated(const Team&) const;
            unsigned int missileLaunched(const Team&) const;
            void mineralSaved(const Team&, unsigned int);
            void mineralSpent(const Team&, unsigned int);
            unsigned int mineralSaved(const Team&) const;
            unsigned int mineralSpent(const Team&) const;

            void itemDestroyed(const Item*);

            std::string dump() const;
            void print() const;

        private:
            class TeamInfo;

            typedef std::map<Team, TeamInfo> TeamMap;

            unsigned int _round;
            TeamMap _teamMap;
        };


        class StatManager::TeamInfo
        {
        public:
            TeamInfo();

            unsigned int nb_base;
            unsigned int nb_base_max;
            unsigned int nb_miningShip;
            unsigned int nb_miningShip_max;
            unsigned int nb_fighter;
            unsigned int nb_fighter_max;
            unsigned int nb_missile_created;
            unsigned int nb_missile_launched;
            unsigned int nb_mineral_saved;
            unsigned int nb_mineral_spent;
        };

    } // aiwar::core
} // aiwar

#endif /* STAT_MANAGER_HPP */
