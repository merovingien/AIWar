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

#ifndef HANDLER_INTERFACE_HPP
#define HANDLER_INTERFACE_HPP

#include "config.hpp" // for Config::Player
#include "playable.hpp" // for Playable::PlayFunction

#include <string>
#include <stdexcept>

namespace aiwar {
    namespace core {

        class HandlerInterface
        {
        public:
            virtual ~HandlerInterface() {}

            virtual bool initialize() = 0;
            virtual bool finalize() = 0;

            virtual bool load(Config::Player player, const std::string& params) = 0;
            virtual bool unload(Config::Player player) = 0;

            virtual PlayFunction& get_BaseHandler(Config::Player player) = 0;
            virtual PlayFunction& get_MiningShipHandler(Config::Player player) = 0;
            virtual PlayFunction& get_FighterHandler(Config::Player player) = 0;
        };

        class HandlerError : public std::runtime_error
        {
        public:
            HandlerError(Team team, const std::string &what) : std::runtime_error(what), _team(team) {}
            const Team& team() const { return _team; }

        private:
            Team _team;
        };

    } // aiwar::core
} // aiwar

#endif /* HANDLER_INTERFACE_HPP */
