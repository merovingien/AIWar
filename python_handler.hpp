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

#ifndef PYHTON_HANDLER_HPP
#define PYTHON_HANDLER_HPP

#include "handler_interface.hpp"

#include <map>

class PythonHandler : public HandlerInterface
{
public:
    PythonHandler();
    ~PythonHandler();

    bool initialize();
    bool finalize();

    bool load(T team, const std::string &file);
    bool unload(T team);

    PF& get_BaseHandler(T team);
    PF& get_MiningShipHandler(T team);
    PF& get_FighterHandler(T team);

private:
    class TeamInfo;

    typedef std::map<T, TeamInfo*> TeamMap;

    PythonHandler(const PythonHandler&);
    PythonHandler& operator= (const PythonHandler&);

    static void play_base(PyObject *pHandler, aiwar::core::Playable *item);
    static void play_miningShip(PyObject *pHandler, aiwar::core::Playable *item);
    static void play_fighter(PyObject *pHandler, aiwar::core::Playable *item);


    bool _initFlag;
    TeamMap _teamMap;
};

typedef void (*PH_PF)(PyObject *h, aiwar::core::Playable *p);

class PythonHandlerPlayFunction : public aiwar::core::PlayFunction
{
public:
    PythonHandlerPlayFunction(PH_PF fn, PyObject *handler) : _fun(fn), _h(handler) {}
    void operator()(aiwar::core::Playable* p) { _fun(_h, p); }
    
private:
    PH_PF _fun;
    PyObject *_h;
};


class PythonHandler::TeamInfo
{
public:
    TeamInfo(PyObject *bh, PyObject *mh, PyObject *fh);

    std::string moduleName;
    PyObject* module;
    PythonHandlerPlayFunction baseHandler;
    PythonHandlerPlayFunction miningShipHandler;
    PythonHandlerPlayFunction fighterHandler;
};

//PF get_MiningShip_PyHandler();

//PF get_Base_PyHandler();

//PF get_Fighter_PyHandler();

#endif /* PYTHON_HANDLER_HPP */
