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

#ifndef MININGSHIP_HPP
#define MININGSHIP_HPP

#include <ostream>

#include "item.hpp"
#include "movable.hpp"
#include "living.hpp"
#include "playable.hpp"
#include "memory.hpp"

namespace aiwar {
    namespace core {

        class Mineral;
        class Base;

        class MiningShip : virtual public Item, public Movable, public Living, public Playable, public Memory
        {
        public:
            MiningShip(GameManager& gm, Key k, double xpos, double ypos, Team team, PlayFunction& pf);
            ~MiningShip();

            void update(unsigned int tick);

            unsigned int extract(Mineral *m);
            unsigned int mineralStorage() const;
            unsigned int pushMineral(Base *base, unsigned int mineralPoints);

            // helper function only called by a base item
            unsigned int _release(unsigned int mineralPoint);

            std::string _dump() const;

        private:
            /**
             * \brief Initialize the MiningShip
             *
             * Reset _hasExtracted
             */
            void _preUpdate(unsigned int tick);

            void _setMineralStorage(int n);

            unsigned int _mineralStorage; ///< Number of mineral units stored

            bool _hasExtracted;
        };

    } // namespace aiwar::core
} // namespace aiwar

std::ostream& operator<< (std::ostream& os, const aiwar::core::MiningShip& t);

#endif /* MININGSHIP_HPP */
