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

#include <Python.h>

#include "python_handler.hpp"
#include "python_wrapper.hpp"

#include "miningship.hpp"
#include "base.hpp"
#include "fighter.hpp"

#include <stdexcept>



PythonHandler::PythonHandler() : _initFlag(false)
{
}

PythonHandler::~PythonHandler()
{
    if(_initFlag)
    {
	// do unload for each team, or do it in team map

	
	finalize();
    }

    // clean memory, should not be there but in finalyse or unload
    TeamMap::iterator it;
    for(it = _teamMap.begin() ; it != _teamMap.end() ; ++it)
	delete it->second;
}

bool PythonHandler::initialize()
{
    // initialize Python interpreter
    Py_Initialize();

    // insert "." to the python path
    char *p = strdup("path");
    PyObject *path = PySys_GetObject(p);  // path is a borrowed ref, do not call Py_DECREF on it
    free(p);
    if(!path)
    {
	PyErr_Print();
	return false;
    }
    
    PyObject *point = PyString_FromString(".");
    if(!point)
    {
	PyErr_Print();
	return false;
    }

    int ret = PyList_Insert(path, 0, point);
    Py_DECREF(point);
    if(ret != 0)
    {
	PyErr_Print();
	return false;
    }

    // init aiwar module
    if(!initAiwarModule())
	return false;

    _initFlag = true;

    return true;
}

bool PythonHandler::finalize()
{
    // todo do some clean action before finalizing python interpreter

    // unload every team

    Py_Finalize();
    return true;
}

bool PythonHandler::load(T team, const std::string &moduleName)
{
    // load module
    PyObject *pName = PyString_FromString(moduleName.c_str());
    if(!pName)
    {
	PyErr_Print();
	return false;
    }

    PyObject *pModule = PyImport_Import(pName);
    Py_DECREF(pName);
    if(!pModule)
    {
	PyErr_Print();
	return false;
    }

    // load and check MiningShipHandler
    PyObject *pMiningShip_Handler = PyObject_GetAttrString(pModule, "play_miningship");
    if(!pMiningShip_Handler)
    {
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    if(!PyCallable_Check(pMiningShip_Handler))
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    // load and check Base Handler
    PyObject *pBase_Handler = PyObject_GetAttrString(pModule, "play_base");
    if(!pBase_Handler)
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    if(!PyCallable_Check(pMiningShip_Handler))
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_CLEAR(pBase_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    // load and check Fighter Handler
    PyObject *pFighter_Handler = PyObject_GetAttrString(pModule, "play_fighter");
    if(!pFighter_Handler)
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_CLEAR(pBase_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    if(!PyCallable_Check(pFighter_Handler))
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_CLEAR(pBase_Handler);
	Py_CLEAR(pFighter_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    // add handlers to team map
    TeamInfo *info = new TeamInfo(pBase_Handler, pMiningShip_Handler, pFighter_Handler);
    info->moduleName = moduleName;
    info->module = pModule;
    _teamMap[team] = info;

    return true;
}


bool PythonHandler::unload(T)
{
    // todo

    return false;
}

PF& PythonHandler::get_BaseHandler(T team)
{
    TeamMap::iterator it = _teamMap.find(team);
    if(it != _teamMap.end())
    {
	return it->second->baseHandler;
    }
    else
    {
	throw std::runtime_error("Team not registered");
    }
}

PF& PythonHandler::get_MiningShipHandler(T team)
{
    TeamMap::iterator it = _teamMap.find(team);
    if(it != _teamMap.end())
    {
	return it->second->miningShipHandler;
    }
    else
    {
	throw std::runtime_error("Team not registered");
    }
}

PF& PythonHandler::get_FighterHandler(T team)
{
    TeamMap::iterator it = _teamMap.find(team);
    if(it != _teamMap.end())
    {
	return it->second->fighterHandler;
    }
    else
    {
	throw std::runtime_error("Team not registered");
    }
}

/*

static PyObject *pMiningShip_Handler = NULL;
static PyObject *pBase_Handler = NULL;
static PyObject *pFighter_Handler = NULL;

static bool loadHandlers()
{
    // load module 'embtest'
    PyObject *pName = PyString_FromString("embtest");
    if(!pName)
    {
	PyErr_Print();
	return false;
    }

    PyObject *pModule = PyImport_Import(pName);
    Py_DECREF(pName);
    if(!pModule)
    {
	PyErr_Print();
	return false;
    }
    
    // load and check MiningShipHandler
    pMiningShip_Handler = PyObject_GetAttrString(pModule, "play_miningship");
    if(!pMiningShip_Handler)
    {
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    if(!PyCallable_Check(pMiningShip_Handler))
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }


    // load and check Base Handler
    pBase_Handler = PyObject_GetAttrString(pModule, "play_base");
    if(!pBase_Handler)
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    if(!PyCallable_Check(pMiningShip_Handler))
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_CLEAR(pBase_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    // load and check Fighter Handler
    pFighter_Handler = PyObject_GetAttrString(pModule, "play_fighter");
    if(!pFighter_Handler)
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_CLEAR(pBase_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }

    if(!PyCallable_Check(pFighter_Handler))
    {
	Py_CLEAR(pMiningShip_Handler);
	Py_CLEAR(pBase_Handler);
	Py_CLEAR(pFighter_Handler);
	Py_DECREF(pModule);
	PyErr_Print();
	return false;
    }
    
    std::cout << "Python handlers found" << std::endl;

    return true;
}
*/

void PythonHandler::play_miningShip(PyObject *pHandler, aiwar::core::Playable *item)
{
    // create the MiningShip PyObject*
    aiwar::core::MiningShip *m = dynamic_cast<aiwar::core::MiningShip*>(item);
    if(!m)
    {
	std::cerr << "Bad cast error : play_miningShip_py expects MiningShip* argument" << std::endl;
	return;
    }

    PyObject *pM = MiningShip_New(m);
    if(!pM)
    {
	std::cerr << "Error while creating new MiningShip python object" << std::endl;
	PyErr_Print();
	return;
    }

    PyObject *pResult = PyObject_CallFunctionObjArgs(pHandler, pM, NULL);
    Py_DECREF(pM);
    if(!pResult)
    {
	std::cerr << "Error while calling pMiningShip_Handler" << std::endl;
	PyErr_Print();
	return;
    }
    Py_DECREF(pResult);
}

void PythonHandler::play_base(PyObject *pHandler, aiwar::core::Playable *item)
{
    // create the Base PyObject*
    aiwar::core::Base *b = dynamic_cast<aiwar::core::Base*>(item);
    if(!b)
    {
	std::cerr << "Bad cast error: play_base expects Base* argument" << std::endl;
	return;
    }

    PyObject *pB = Base_New(b);
    if(!pB)
    {
	std::cerr << "Error while creating new Base python object" << std::endl;
	PyErr_Print();
	return;
    }

    // call the python function
    PyObject *pResult = PyObject_CallFunctionObjArgs(pHandler, pB, NULL);
    Py_DECREF(pB);
    if(!pResult)
    {
	std::cerr << "Error while calling pBase_Handler" << std::endl;
	PyErr_Print();
	return;
    }
    Py_DECREF(pResult);
}

void PythonHandler::play_fighter(PyObject *pHandler, aiwar::core::Playable *item)
{
    // create the Fighter PyObject*
    aiwar::core::Fighter *f = dynamic_cast<aiwar::core::Fighter*>(item);
    if(!f)
    {
	std::cerr << "Bad cast error : play_fighter expects Fighter* argument" << std::endl;
	return;
    }

    PyObject *pF = Fighter_New(f);
    if(!pF)
    {
	std::cerr << "Error while creating new Fighter python object" << std::endl;
	PyErr_Print();
	return;
    }

    // call the python function
    PyObject *pResult = PyObject_CallFunctionObjArgs(pHandler, pF, NULL);
    Py_DECREF(pF);
    if(!pResult)
    {
	std::cerr << "Error while calling pFighter_Handler" << std::endl;
	PyErr_Print();
	return;
    }
    Py_DECREF(pResult);
}

PythonHandler::TeamInfo::TeamInfo(PyObject *bh, PyObject *mh, PyObject *fh)
    : baseHandler(&PythonHandler::play_base, bh),
      miningShipHandler(&PythonHandler::play_miningShip, mh),
      fighterHandler(&PythonHandler::play_fighter, fh)
{
}








/*

PF get_MiningShip_PyHandler()
{
    if(!pMiningShip_Handler)
	if(!loadHandlers())
	    return NULL;

    return &play_miningShip_py;
}

PF get_Base_PyHandler()
{
    if(!pBase_Handler)
	if(!loadHandlers())
	    return NULL;

    return &play_base_py;
}

PF get_Fighter_PyHandler()
{
    if(!pFighter_Handler)
	if(!loadHandlers())
	    return NULL;

    return &play_fighter_py;
}

*/
