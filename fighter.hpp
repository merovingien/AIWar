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

#ifndef FIGHTER_HPP
#define FIGHTER_HPP

#include "item.hpp"
#include "movable.hpp"
#include "living.hpp"
#include "playable.hpp"
#include "memory.hpp"

namespace aiwar {
    namespace core {

        class Fighter : virtual public Item, public Movable, public Living, public Playable, public Memory
        {
        public:
            Fighter(GameManager &gm, Key k, double px, double py, Team team, PlayFunction& pf);
            ~Fighter();

            void update(unsigned int tick);

            unsigned int missiles() const;
            void launchMissile(Living* target);

            unsigned int _addMissiles(unsigned int nb);

            std::string _dump() const;

        private:
            void _preUpdate(unsigned int tick);

            unsigned int _missiles;
            bool _hasLaunch;
        };

    } // namespace core
} // namespace aiwar

#endif /* FIGHTER_HPP */
