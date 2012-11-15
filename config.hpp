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

#ifndef CONFIG_HPP
#define CONFIG_HPP

#include <string>
#include <map>

namespace aiwar {
    namespace core {

        /**
         * \brief Team identifiant
         */
        enum Team
        {
            NO_TEAM,
            BLUE_TEAM,
            RED_TEAM
        };

        class Config
        {
        public:
            typedef unsigned int Player;
            class PlayerInfo;
            typedef std::map<Player, PlayerInfo> PlayerMap;

            typedef unsigned int Renderer;
            class RendererInfo;
            typedef std::map<Renderer, RendererInfo> RendererMap;

            static Config& instance();

            std::string usage() const;
            bool parseCmdLine(int argc, char* argv[]);
            bool loadConfigFile();
            std::string dump() const;

            bool help;
            bool debug;
            bool manual;
            std::string mapFile;
            unsigned int seed;

            Player blue;
            Player red;

            Renderer renderer;

            PlayerMap players;
            RendererMap renderers;

            double WORLD_SIZE_X;
            double WORLD_SIZE_Y;

            double MINERAL_SIZE_X;
            double MINERAL_SIZE_Y;
            unsigned int MINERAL_LIFE;

            double MININGSHIP_SIZE_X;
            double MININGSHIP_SIZE_Y;
            double MININGSHIP_SPEED;
            double MININGSHIP_DETECTION_RADIUS;
            unsigned int MININGSHIP_MAX_LIFE;
            unsigned int MININGSHIP_START_LIFE;
            unsigned int MININGSHIP_START_FUEL;
            unsigned int MININGSHIP_MAX_FUEL;
            unsigned int MININGSHIP_MOVE_CONSO;
            double MININGSHIP_MINING_RADIUS;
            unsigned int MININGSHIP_MINERAL_EXTRACT;
            unsigned int MININGSHIP_MAX_MINERAL_STORAGE;
            unsigned int MININGSHIP_MEMORY_SIZE;

            double FIGHTER_SIZE_X;
            double FIGHTER_SIZE_Y;
            double FIGHTER_SPEED;
            double FIGHTER_DETECTION_RADIUS;
            unsigned int FIGHTER_MAX_LIFE;
            unsigned int FIGHTER_START_LIFE;
            unsigned int FIGHTER_MOVE_CONSO;
            unsigned int FIGHTER_START_FUEL;
            unsigned int FIGHTER_MAX_FUEL;
            unsigned int FIGHTER_MEMORY_SIZE;
            unsigned int FIGHTER_START_MISSILE;
            unsigned int FIGHTER_MAX_MISSILE;

            double MISSILE_SIZE_X;
            double MISSILE_SIZE_Y;
            unsigned int MISSILE_LIFE;
            unsigned int MISSILE_MOVE_CONSO;
            unsigned int MISSILE_START_FUEL;
            unsigned int MISSILE_MAX_FUEL;
            double MISSILE_SPEED;
            unsigned int MISSILE_DAMAGE;

            double BASE_SIZE_X;
            double BASE_SIZE_Y;
            double BASE_DETECTION_RADIUS;
            unsigned int BASE_MAX_LIFE;
            unsigned int BASE_START_LIFE;
            unsigned int BASE_MISSILE_PRICE;
            unsigned int BASE_MININGSHIP_PRICE;
            unsigned int BASE_FIGHTER_PRICE;
            unsigned int BASE_START_MINERAL_STORAGE;
            unsigned int BASE_MAX_MINERAL_STORAGE;
            unsigned int BASE_MEMORY_SIZE;
            double BASE_REPAIR_RADIUS;
            double BASE_REFUEL_RADIUS;
            double BASE_GIVE_MISSILE_RADIUS;

            double COMMUNICATION_RADIUS;

        private:
            Config(); // singleton

            static Config _instance;

            // no copy
            Config(const Config&);
            Config& operator=(const Config&);

            std::string _programName;
            std::string _configFile;

            bool _cl_debug;
            bool _cl_manual;
            std::string _cl_mapFile;
            std::string _cl_blue;
            std::string _cl_red;
            std::string _cl_renderer;
        };

        class Config::PlayerInfo
        {
        public:
            std::string name;
            std::string handler;
            std::string params;
        };

        class Config::RendererInfo
        {
        public:
            std::string name;
            std::string params;
        };

    } // aiwar::core
} // aiwar

#endif /* CONFIG_HPP */
