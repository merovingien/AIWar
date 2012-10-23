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
#include <stdexcept>
#include <list>
#include <string>
#include <tinyxml.h>

using namespace aiwar::core;

/*** Parse Error ***/
class ParseError : public std::runtime_error
{
public:
    ParseError(const std::string &key): std::runtime_error(key) {}
};

/*** Cast helpers ***/
template<typename T>
static T convert(const std::string&);

template<>
std::string convert(const std::string& value)
{
    return value;
}

template<>
unsigned int convert(const std::string& value)
{
    unsigned int val;
    std::istringstream iss(value);
    iss >> val;
    if(!iss)
	throw ParseError("not a valid unsigned int");
    return val;
}

template<>
double convert(const std::string& value)
{
    double val;
    std::istringstream iss(value);
    iss >> val;
    if(!iss)
	throw ParseError("not a valid double");
    return val;
}

template<>
bool convert(const std::string& value)
{
    bool val;
    std::istringstream iss(value);
    iss >> std::boolalpha;
    iss >> val;
    if(!iss)
	throw ParseError("not a valid bool");
    return val;
}

template<typename T>
static T get(const TiXmlHandle &pHandle, const std::string& key)
{
    // parse key
    std::list<std::string> elements;
    std::string::size_type idx_start = 0, idx_end;
    while( (idx_end = key.find('/', idx_start)) != std::string::npos)
    {
	if(idx_start != idx_end)
	    elements.push_back(key.substr(idx_start, idx_end-idx_start));
	idx_start = idx_end + 1;
    }
    if(idx_start != key.size())
	elements.push_back(key.substr(idx_start));

    // get key value
    TiXmlHandle pH(pHandle);
    std::list<std::string>::const_iterator cit;
    for(cit = elements.begin() ; cit != elements.end() ; cit++)
    {
	pH = pH.FirstChild(*cit);
    }
    TiXmlElement *pElem = pH.ToElement();
    if(!pElem)
	throw ParseError(std::string("Key error: ")+key);
    TiXmlText *pText = pH.FirstChild().ToText();
    std::string sval;
    if(!pText)
	sval = "";
    else
	sval = pText->ValueStr();

    // cast
    T val;
    try
    {
	val = convert<T>(sval);
    }
    catch(const ParseError& e)
    {
	std::ostringstream oss;
	oss << "Cast error: key='" << key << "' value='" << sval << "' error='" << e.what() << "'";
	throw ParseError(oss.str());
    }

    return val;
}

/*** Config class ***/

Config Config::_instance; // singleton instance

Config& Config::instance()
{
    return _instance;
}

Config::Config()
    : help(false),
      blue(0),
      red(0),
      _programName("AIWar"),
      _configFile("config.xml"),
      _cl_debug(false),
      _cl_manual(false)
{
}
      

std::string Config::usage() const
{
    std::ostringstream oss;
    oss << "usage: " << _programName << " [OPTIONS]\n"
	<< "OPTIONS:\n"
	<< "\t--help\t\t\tPrint this message\n"
	<< "\t--debug\t\t\tRun in debug mode\n"
	<< "\t--manual\t\tDo not automatically play\n"
	<< "\t--file config_file\tConfiguration file [config.xml]\n"
	<< "\t--map map_file\t\tMap file [map.xml]\n"
	<< "\t--blue player_name\tBlue player name\n"
	<< "\t--red player_name\tRed player name\n"
	<< "\t--renderer name\t\tRenderer name\n";
    
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
	    _cl_debug = true;
	else if(arg == "manual")
	    _cl_manual = true;
	else if(arg == "file")
	{
	    if(i == argc-1)
		return false;
	    _configFile = argv[++i];
	}
	else if(arg == "map")
	{
	    if(i == argc-1)
		return false;
	    _cl_mapFile = argv[++i];
	}
	else if(arg == "blue")
	{
	    if(i == argc-1)
		return false;
	    _cl_blue = argv[++i];
	}
	else if(arg == "red")
	{
	    if(i == argc-1)
		return false;
	    _cl_red = argv[++i];
	}
	else if(arg == "renderer")
	{
	    if(i == argc-1)
		return false;
	    _cl_renderer = argv[++i];
	}
	else
	{
	    std::cerr << "Bad option: " << arg << "\n";
	    return false;
	}
    }

    return true;
}

bool Config::loadConfigFile()
{
    std::string blue_name;
    std::string red_name;
    std::string renderer_name;

    TiXmlDocument doc(_configFile.c_str());
    if(!doc.LoadFile())
    {
	std::cerr << "Cannot load config file: \"" << _configFile << "\"\n";
	return false;
    }

    TiXmlHandle hDoc(0), hPlayer(0), hRenderer(0);
    TiXmlElement *pElem, *pPlayers, *pParams, *pRenderers;
    TiXmlNode *pNode;

    // root: aiwar
    pElem=doc.RootElement();
    // should always have a valid root but handle gracefully if it does
    if (!pElem || pElem->ValueStr() != "aiwar")
	return false;

    // read file
    hDoc = TiXmlHandle(pElem);
    try
    {
	// options
	debug = get<bool>(hDoc, "options/debug");
	manual = get<bool>(hDoc, "options/manual");
	mapFile = get<std::string>(hDoc, "options/map");

	blue_name = get<std::string>(hDoc, "options/blue");
	red_name = get<std::string>(hDoc, "options/red");

	renderer_name = get<std::string>(hDoc, "options/renderer");

	// players
	pPlayers = hDoc.FirstChildElement("players").ToElement();
	if(!pPlayers)
	    throw(ParseError("Key error: players"));
	pElem = 0;
	Player player_id = 1;
	for(pElem=pPlayers->FirstChildElement("player") ; pElem ; pElem=pElem->NextSiblingElement("player"))
	{
	    hPlayer = pElem;

	    PlayerInfo tf;
	    tf.name = get<std::string>(hPlayer, "name");
	    tf.handler = get<std::string>(hPlayer, "handler");
	    
	    // params (keep whole content)
	    pParams = hPlayer.FirstChildElement("params").ToElement();
	    if(!pParams)
		throw ParseError("Key error: player/params");
	    
	    std::ostringstream oss;
	    for(pNode=pParams->FirstChild() ; pNode ; pNode=pNode->NextSibling())
	    {
		oss << *pNode;
	    }
	    tf.params = oss.str();

	    players[player_id] = tf;
	    player_id++;
	}

	// renderers
	pRenderers = hDoc.FirstChildElement("renderers").ToElement();
	if(!pRenderers)
	    throw(ParseError("Key error: renderers"));
	Renderer renderer_id = 1;
	for(pElem=pRenderers->FirstChildElement("renderer") ; pElem ; pElem=pElem->NextSiblingElement("renderer"))
	{
	    hRenderer = pElem;

	    RendererInfo tf;
	    tf.name = get<std::string>(hRenderer, "name");
	    
	    // params (keep whole content)
	    pParams = hRenderer.FirstChildElement("params").ToElement();
	    if(!pParams)
		throw ParseError("Key error: renderer/params");
	    std::ostringstream oss;
	    for(pNode=pParams->FirstChild() ; pNode ; pNode=pNode->NextSibling())
	    {
		oss << *pNode;
	    }
	    tf.params = oss.str();

	    renderers[renderer_id] = tf;
	    renderer_id++;
	}

	// constants
	WORLD_SIZE_X = get<double>(hDoc, "constants/WORLD_SIZE_X");
	WORLD_SIZE_Y = get<double>(hDoc, "constants/WORLD_SIZE_Y");

	MINERAL_SIZE_X = get<double>(hDoc, "constants/MINERAL_SIZE_X");
	MINERAL_SIZE_Y = get<double>(hDoc, "constants/MINERAL_SIZE_Y");
	MINERAL_LIFE = get<unsigned int>(hDoc, "constants/MINERAL_LIFE");

	MININGSHIP_SIZE_X = get<double>(hDoc, "constants/MININGSHIP_SIZE_X");
	MININGSHIP_SIZE_Y = get<double>(hDoc, "constants/MININGSHIP_SIZE_Y");
	MININGSHIP_SPEED = get<double>(hDoc, "constants/MININGSHIP_SPEED");
	MININGSHIP_DETECTION_RADIUS = get<double>(hDoc, "constants/MININGSHIP_DETECTION_RADIUS");
	MININGSHIP_MAX_LIFE = get<unsigned int>(hDoc, "constants/MININGSHIP_MAX_LIFE");
	MININGSHIP_START_LIFE = get<unsigned int>(hDoc, "constants/MININGSHIP_START_LIFE");
	MININGSHIP_START_FUEL = get<unsigned int>(hDoc, "constants/MININGSHIP_START_FUEL");
	MININGSHIP_MAX_FUEL = get<unsigned int>(hDoc, "constants/MININGSHIP_MAX_FUEL");
	MININGSHIP_MOVE_CONSO = get<unsigned int>(hDoc, "constants/MININGSHIP_MOVE_CONSO");
	MININGSHIP_MINING_RADIUS = get<double>(hDoc, "constants/MININGSHIP_MINING_RADIUS");
	MININGSHIP_MINERAL_EXTRACT = get<unsigned int>(hDoc, "constants/MININGSHIP_MINERAL_EXTRACT");
	MININGSHIP_MAX_MINERAL_STORAGE = get<unsigned int>(hDoc, "constants/MININGSHIP_MAX_MINERAL_STORAGE");
	MININGSHIP_MEMORY_SIZE = get<unsigned int>(hDoc, "constants/MININGSHIP_MEMORY_SIZE");

	FIGHTER_SIZE_X = get<double>(hDoc, "constants/FIGHTER_SIZE_X");
	FIGHTER_SIZE_Y = get<double>(hDoc, "constants/FIGHTER_SIZE_Y");
	FIGHTER_SPEED = get<double>(hDoc, "constants/FIGHTER_SPEED");
	FIGHTER_DETECTION_RADIUS = get<double>(hDoc, "constants/FIGHTER_DETECTION_RADIUS/");
	FIGHTER_MAX_LIFE = get<unsigned int>(hDoc, "constants/FIGHTER_MAX_LIFE");
	FIGHTER_START_LIFE = get<unsigned int>(hDoc, "constants/FIGHTER_START_LIFE");
	FIGHTER_MOVE_CONSO = get<unsigned int>(hDoc, "constants/FIGHTER_MOVE_CONSO");
	FIGHTER_START_FUEL = get<unsigned int>(hDoc, "constants/FIGHTER_START_FUEL");
	FIGHTER_MAX_FUEL = get<unsigned int>(hDoc, "constants/FIGHTER_MAX_FUEL");
	FIGHTER_MEMORY_SIZE = get<unsigned int>(hDoc, "constants/FIGHTER_MEMORY_SIZE");
	FIGHTER_START_MISSILE = get<unsigned int>(hDoc, "constants/FIGHTER_START_MISSILE");
	FIGHTER_MAX_MISSILE = get<unsigned int>(hDoc, "constants/FIGHTER_MAX_MISSILE");

	MISSILE_SIZE_X = get<double >(hDoc, "constants/MISSILE_SIZE_X");
	MISSILE_SIZE_Y = get<double>(hDoc, "constants/MISSILE_SIZE_Y");
	MISSILE_LIFE = get<unsigned int>(hDoc, "constants/MISSILE_LIFE");
	MISSILE_MOVE_CONSO = get<unsigned int>(hDoc, "constants/MISSILE_MOVE_CONSO");
	MISSILE_START_FUEL = get<unsigned int>(hDoc, "constants/MISSILE_START_FUEL");
	MISSILE_MAX_FUEL = get<unsigned int>(hDoc, "constants/MISSILE_MAX_FUEL");
	MISSILE_SPEED = get<double>(hDoc, "constants/MISSILE_SPEED");
	MISSILE_DAMAGE = get<unsigned int>(hDoc, "constants/MISSILE_DAMAGE");

	BASE_SIZE_X = get<double>(hDoc, "constants/BASE_SIZE_X");
	BASE_SIZE_Y = get<double>(hDoc, "constants/BASE_SIZE_Y");
	BASE_DETECTION_RADIUS = get<double>(hDoc, "constants/BASE_DETECTION_RADIUS");
	BASE_MAX_LIFE = get<unsigned int>(hDoc, "constants/BASE_MAX_LIFE");
	BASE_START_LIFE = get<unsigned int>(hDoc, "constants/BASE_START_LIFE");
	BASE_MISSILE_PRICE = get<unsigned int>(hDoc, "constants/BASE_MISSILE_PRICE");
	BASE_MININGSHIP_PRICE = get<unsigned int>(hDoc, "constants/BASE_MININGSHIP_PRICE");
	BASE_FIGHTER_PRICE = get<unsigned int>(hDoc, "constants/BASE_FIGHTER_PRICE");
	BASE_START_MINERAL_STORAGE = get<unsigned int>(hDoc, "constants/BASE_START_MINERAL_STORAGE");
	BASE_MAX_MINERAL_STORAGE = get<unsigned int>(hDoc, "constants/BASE_MAX_MINERAL_STORAGE");
	BASE_MEMORY_SIZE = get<unsigned int>(hDoc, "constants/BASE_MEMORY_SIZE");
	BASE_REPAIR_RADIUS = get<double>(hDoc, "constants/BASE_REPAIR_RADIUS");
	BASE_REFUEL_RADIUS = get<double>(hDoc, "constants/BASE_REFUEL_RADIUS");
	BASE_GIVE_MISSILE_RADIUS = get<double>(hDoc, "constants/BASE_GIVE_MISSILE_RADIUS");

	COMMUNICATION_RADIUS = get<double>(hDoc, "constants/COMMUNICATION_RADIUS");
    }
    catch(const ParseError& e)
    {
	std::cerr << "Parsing config file '" << _configFile << "' failed\n"
		  << e.what() << std::endl;
	return false;
    }

    // set players id
    if(!_cl_blue.empty())
	blue_name = _cl_blue;
    if(!_cl_red.empty())
	red_name = _cl_red;

    PlayerMap::const_iterator cit;
    for(cit=players.begin() ; cit!=players.end() ; ++cit)
    {
	if(cit->second.name == blue_name)
	    blue = cit->first;

	if(cit->second.name == red_name)
	    red = cit->first;
    }

    if(blue == 0)
    {
	std::cerr << "Player not found in config file: " << blue_name << std::endl;
	return false;
    }
    if(red == 0)
    {
	std::cerr << "Player not found in config file: " << red_name << std::endl;
	return false;
    }

    // set renderers id
    if(!_cl_renderer.empty())
	renderer_name = _cl_renderer;

    RendererMap::const_iterator cit_r;
    for(cit_r=renderers.begin() ; cit_r!=renderers.end() ; ++cit_r)
    {
	if(cit_r->second.name == renderer_name)
	    renderer = cit_r->first;
    }

    if(renderer == 0)
    {
	std::cerr << "Renderer not found in config file: " << renderer_name << std::endl;
	return false;
    }

    // replace options with command line values
    if(_cl_debug) debug = _cl_debug;
    if(_cl_manual) manual = _cl_manual;
    if(!_cl_mapFile.empty()) mapFile = _cl_mapFile;

    return true;
}

std::string Config::dump() const
{
    std::ostringstream oss;
    
    // options
    oss << "options\n"
	<< "\thelp: " << help << "\n"
	<< "\tdebug: " << debug << "\n"
	<< "\tmanual: " << manual << "\n"
	<< "\tconfig file: " << _configFile << "\n"
	<< "\tmap file: " << mapFile << "\n"
	<< "\tblue: " << blue << "\n"
	<< "\tred: " << red << "\n"
	<< "\trenderer: " << renderer << "\n";

    // teams
    oss << "players\n";
    PlayerMap::const_iterator cit;
    for(cit = players.begin() ; cit != players.end() ; ++cit)
    {
	oss << "\tplayer: " << cit->first << "\n"
	    << "\t\tname: " << cit->second.name << "\n"
	    << "\t\thandler: " << cit->second.handler << "\n"
	    << "\t\tparams: " << cit->second.params << "\n";
    }

    // renderers
    oss << "renderers\n";
    RendererMap::const_iterator cit_r;
    for(cit_r = renderers.begin() ; cit_r != renderers.end() ; ++cit_r)
    {
	oss << "\trenderer: " << cit_r->first << "\n"
	    << "\t\tname: " << cit_r->second.name << "\n"
	    << "\t\tparams: " << cit_r->second.params << "\n";
    }

    // constants
    oss << "constants\n"
	<< "\tWORLD_SIZE_X: " << WORLD_SIZE_X << "\n"
	<< "\tWORLD_SIZE_Y: " << WORLD_SIZE_Y << "\n"
	<< "\tMINERAL_SIZE_X: " << MINERAL_SIZE_X << "\n"
	<< "\tMINERAL_SIZE_Y: " << MINERAL_SIZE_Y << "\n"
	<< "\tMINERAL_LIFE: " << MINERAL_LIFE << "\n"
	<< "\tMININGSHIP_SIZE_X: " << MININGSHIP_SIZE_X << "\n"
	<< "\tMININGSHIP_SIZE_Y: " << MININGSHIP_SIZE_Y << "\n"
	<< "\tMININGSHIP_SPEED: " << MININGSHIP_SPEED << "\n"
	<< "\tMININGSHIP_DETECTION_RADIUS: " << MININGSHIP_DETECTION_RADIUS << "\n"
	<< "\tMININGSHIP_MAX_LIFE: " << MININGSHIP_MAX_LIFE << "\n"
	<< "\tMININGSHIP_START_LIFE: " << MININGSHIP_START_LIFE << "\n"
	<< "\tMININGSHIP_START_FUEL: " << MININGSHIP_START_FUEL << "\n"
	<< "\tMININGSHIP_MAX_FUEL: " << MININGSHIP_MAX_FUEL << "\n"
	<< "\tMININGSHIP_MOVE_CONSO: " << MININGSHIP_MOVE_CONSO << "\n"
	<< "\tMININGSHIP_MINING_RADIUS: " << MININGSHIP_MINING_RADIUS << "\n"
	<< "\tMININGSHIP_MINERAL_EXTRACT: " << MININGSHIP_MINERAL_EXTRACT << "\n"
	<< "\tMININGSHIP_MAX_MINERAL_STORAGE: " << MININGSHIP_MAX_MINERAL_STORAGE << "\n"
	<< "\tMININGSHIP_MEMORY_SIZE: " << MININGSHIP_MEMORY_SIZE << "\n"
	<< "\tFIGHTER_SIZE_X: " << FIGHTER_SIZE_X << "\n"
	<< "\tFIGHTER_SIZE_Y: " << FIGHTER_SIZE_Y << "\n"
	<< "\tFIGHTER_SPEED: " << FIGHTER_SPEED << "\n"
	<< "\tFIGHTER_DETECTION_RADIUS: " << FIGHTER_DETECTION_RADIUS << "\n"
	<< "\tFIGHTER_MAX_LIFE: " << FIGHTER_MAX_LIFE << "\n"
	<< "\tFIGHTER_START_LIFE: " << FIGHTER_START_LIFE << "\n"
	<< "\tFIGHTER_MOVE_CONSO: " << FIGHTER_MOVE_CONSO << "\n"
	<< "\tFIGHTER_START_FUEL: " << FIGHTER_START_FUEL << "\n"
	<< "\tFIGHTER_MAX_FUEL: " << FIGHTER_MAX_FUEL << "\n"
	<< "\tFIGHTER_MEMORY_SIZE: " << FIGHTER_MEMORY_SIZE << "\n"
	<< "\tFIGHTER_START_MISSILE: " << FIGHTER_START_MISSILE << "\n"
	<< "\tFIGHTER_MAX_MISSILE: " << FIGHTER_MAX_MISSILE << "\n"
	<< "\tMISSILE_SIZE_X: " << MISSILE_SIZE_X << "\n"
	<< "\tMISSILE_SIZE_Y: " << MISSILE_SIZE_Y << "\n"
	<< "\tMISSILE_LIFE: " << MISSILE_LIFE << "\n"
	<< "\tMISSILE_MOVE_CONSO: " << MISSILE_MOVE_CONSO << "\n"
	<< "\tMISSILE_START_FUEL: " << MISSILE_START_FUEL << "\n"
	<< "\tMISSILE_MAX_FUEL: " << MISSILE_MAX_FUEL << "\n"
	<< "\tMISSILE_SPEED: " << MISSILE_SPEED << "\n"
	<< "\tMISSILE_DAMAGE: " << MISSILE_DAMAGE << "\n"
	<< "\tBASE_SIZE_X: " << BASE_SIZE_X << "\n"
	<< "\tBASE_SIZE_Y: " << BASE_SIZE_Y << "\n"
	<< "\tBASE_DETECTION_RADIUS: " << BASE_DETECTION_RADIUS << "\n"
	<< "\tBASE_MAX_LIFE: " << BASE_MAX_LIFE << "\n"
	<< "\tBASE_START_LIFE: " << BASE_START_LIFE << "\n"
	<< "\tBASE_MISSILE_PRICE: " << BASE_MISSILE_PRICE << "\n"
	<< "\tBASE_MININGSHIP_PRICE: " << BASE_MININGSHIP_PRICE << "\n"
	<< "\tBASE_FIGHTER_PRICE: " << BASE_FIGHTER_PRICE << "\n"
	<< "\tBASE_START_MINERAL_STORAGE: " << BASE_START_MINERAL_STORAGE << "\n"
	<< "\tBASE_MAX_MINERAL_STORAGE: " << BASE_MAX_MINERAL_STORAGE << "\n"
	<< "\tBASE_MEMORY_SIZE: " << BASE_MEMORY_SIZE << "\n"
	<< "\tBASE_REPAIR_RADIUS: " << BASE_REPAIR_RADIUS << "\n"
	<< "\tBASE_REFUEL_RADIUS: " << BASE_REFUEL_RADIUS << "\n"
	<< "\tBASE_GIVE_MISSILE_RADIUS: " << BASE_GIVE_MISSILE_RADIUS << "\n"
	<< "\tCOMMUNICATION_RADIUS: " << COMMUNICATION_RADIUS << "\n";

    return oss.str();
}
