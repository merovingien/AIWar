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

#include "config.hpp"

#include <sstream>

Config Config::_instance; // singleton instance

Config& Config::instance()
{
    return _instance;
}

Config::Config()
    : help(false),
      debug(false),
      manual(false),
      _programName("AIWar")
{
}
      

std::string Config::usage() const
{
    std::ostringstream oss;
    oss << "usage: " << _programName << " [OPTIONS]\n"
	<< "OPTIONS:\n"
	<< "\t--help\t\tPrint this message\n"
	<< "\t--debug\t\tRun in debug mode\n"
	<< "\t--manual\tDo not automatically play\n";

    return oss.str();
}

bool Config::parseCmdLine(int argc, char* argv[])
{
    int i;
    std::string arg;

    if(argc == 0)
	return false;

    _programName = argv[0];

    for(i = 1 ; i < argc ; i++)
    {
	arg = argv[i];
	
	if(arg[0] != '-' || arg[1] != '-')
	    return false;

	arg = arg.substr(2);

	if(arg == "help")
	    help = true;
	else if(arg == "debug")
	    debug = true;
	else if(arg == "manual")
	    manual = true;
	else
	    return false;
    }

    return true;
}
