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

#include "handler_example.hpp"

#include "base.hpp"
#include "miningship.hpp"
#include "fighter.hpp"
#include "mineral.hpp"

#include <cstdlib>

static void random_move(aiwar::core::Movable*);

HandlerExample::HandlerExample()
    : _pf_Base(&play_base), _pf_MiningShip(&play_miningship), _pf_Fighter(&play_fighter)
{
}

bool HandlerExample::initialize()
{
    return true;
}

bool HandlerExample::finalize()
{
    return true;
}

bool HandlerExample::load(P, const std::string&)
{
    return true;
}

bool HandlerExample::unload(P)
{
    return true;
}

HandlerExample::PF& HandlerExample::get_BaseHandler(P)
{
    return _pf_Base;
}

HandlerExample::PF& HandlerExample::get_MiningShipHandler(P)
{
    return _pf_MiningShip;
}

HandlerExample::PF& HandlerExample::get_FighterHandler(P)
{
    return _pf_Fighter;
}

// implementations of play functions

void HandlerExample::play_base(aiwar::core::Playable* base)
{
    using namespace aiwar::core;
    Item::ItemList::iterator it;
    std::ostringstream oss;

    const Config& CFG = Config::instance();

    Base *self = dynamic_cast<Base*>(base);


    self->log("*********BASE**********");
    oss << "Vie: " << self->life();
    self->log(oss.str()); oss.str("");
    oss << "MineralStorage: " << self->mineralStorage();
    self->log(oss.str()); oss.str("");

    Item::ItemList n = self->neighbours();

    // refuel friend ships
    for (it = n.begin() ; it != n.end() ; ++it)
    {
        MiningShip* i = dynamic_cast<MiningShip*>(*it);
        if (i && self->isFriend(i) && self->distanceTo(i) <= CFG.BASE_REFUEL_RADIUS)
        {
            oss << "mon ami a encore " << self->fuel(i) << " fuel";
            self->log(oss.str()); oss.str("");
            self->log("je fais le plein de mon ami");
            self->refuel(CFG.MININGSHIP_START_FUEL, i);
        }
    }

    // create new MiningShip
    if (self->mineralStorage() > CFG.BASE_MININGSHIP_PRICE && (std::rand() % 20) == 1)
    {
        self->log("Je cree un MiningShip");
        self->createMiningShip();
    }

    // communiquer avec les copains
    for (it = n.begin() ; it != n.end() ; ++it)
    {
        MiningShip* i = dynamic_cast<MiningShip*>(*it);
        if (i && self->isFriend(i) && self->distanceTo(i) <= CFG.COMMUNICATION_RADIUS)
        {
            // si on connait la position du mineral
            float posMineralSelf_x = self->getMemory<float>(2);
            float posMineralSelf_y = self->getMemory<float>(3);
            if (posMineralSelf_x != 0.0 || posMineralSelf_y != 0.0)
            {
                // envoi de la position du mineral s'il ne la connait pas
                float posMineralCopain_x = self->getMemory<float>(2,i);
                float posMineralCopain_y = self->getMemory<float>(3,i);
                if (posMineralCopain_x == 0.0 && posMineralCopain_y == 0.0)
                {
                    self->setMemory<float>(2, posMineralSelf_x, i);
                    self->setMemory<float>(3, posMineralSelf_y, i);
                    self->log("J'ai donne la position de mon minerais a mon copain");
                }
            }
        }
    }
}

void HandlerExample::play_miningship(aiwar::core::Playable* miningship)
{
    using namespace aiwar::core;
    Item::ItemList::iterator it;
    std::ostringstream oss;

    const Config& CFG = Config::instance();

    MiningShip *self = dynamic_cast<MiningShip*>(miningship);


    self->log("*******MININGSHIP******");
    oss << "Vie: " << self->life();
    self->log(oss.str()); oss.str("");
    oss << "MineralStorage: " << self->mineralStorage();
    self->log(oss.str()); oss.str("");
    oss << "Fuel: " << self->Movable::fuel();
    self->log(oss.str()); oss.str("");

    Item::ItemList n = self->neighbours();
    
    // recherche de la base amie
    bool baseConnue = false;
    float basePos_x = self->getMemory<float>(0);
    float basePos_y = self->getMemory<float>(1);
    if (basePos_x != 0.0 || basePos_y != 0.0)
    {
        self->log("je connais ma base");
        baseConnue = true;
    }
    else
    {
        for (it = n.begin() ; it != n.end() ; ++it)
        {
            Base* i = dynamic_cast<Base*>(*it);
            if (i && self->isFriend(i))
            {
                self->log("base trouvee");
                basePos_x = i->xpos();
                basePos_y = i->ypos();
                self->setMemory<float>(0, basePos_x);
                self->setMemory<float>(1, basePos_y);
                baseConnue = true;
                break;
            }
        }
    }

    // communiquer avec les copains
    for (it = n.begin() ; it != n.end() ; ++it)
    {
        Base* bi = dynamic_cast<Base*>(*it);
        MiningShip* mi = dynamic_cast<MiningShip*>(*it);
        Memory* i = NULL;
        if (bi && self->isFriend(bi)) i = bi;
        else if (mi && self->isFriend(mi)) i = mi;

        if (i && self->distanceTo(i) <= CFG.COMMUNICATION_RADIUS)
        {
            // si on connait la position du mineral
            float posMineralSelf_x = self->getMemory<float>(2);
            float posMineralSelf_y = self->getMemory<float>(3);
            if (posMineralSelf_x != 0.0 || posMineralSelf_y != 0.0)
            {
                // envoi de la position du mineral s'il ne la connait pas
                float posMineralCopain_x = self->getMemory<float>(2,i);
                float posMineralCopain_y = self->getMemory<float>(3,i);
                if (posMineralCopain_x == 0.0 && posMineralCopain_y == 0.0)
                {
                    self->setMemory<float>(2, posMineralSelf_x, i);
                    self->setMemory<float>(3, posMineralSelf_y, i);
                    self->log("J'ai donne la position de mon minerais a mon copain");
                }
            }
        }
    }

    // rentrer a la base ?
    if (self->mineralStorage() == CFG.MININGSHIP_MAX_MINERAL_STORAGE || self->Movable::fuel() < (baseConnue ? self->distanceTo(basePos_x, basePos_y) : 170))
    {
        if (baseConnue)
        {
            self->log("je rentre a la base");
            self->state(DARK);
            self->rotateTo(basePos_x, basePos_y);
            self->move();
            // base en vue et assez proche pour donner le minerai ?
            for (it = n.begin() ; it != n.end() ; ++it)
            {
                Base* i = dynamic_cast<Base*>(*it);
                if (i && self->isFriend(i))
                {
                    if (self->distanceTo(i) <= CFG.MININGSHIP_MINING_RADIUS)
                    {
                        self->log("je donne mon minerai a ma base");
                        self->pushMineral(i, self->mineralStorage());
                    }
                    break;
                }
            }
            return;
        }
        else
        {
            self->log("je cherche ma base");
            random_move(self);
            return;
        }
    }

    // recherche de minerais visible
    for (it = n.begin() ; it != n.end() ; ++it)
    {
        Mineral* i = dynamic_cast<Mineral*>(*it);
        if (i)
        {
            self->log("je sauvegarde la position du minerai");
            float mpx = i->xpos();
            float mpy = i->ypos();
            self->setMemory<float>(2, mpx);
            self->setMemory<float>(3, mpy);
            self->log("je vais au minerais visible");
            self->state(DEFAULT);
            self->rotateTo(i);
            self->move();
            if (self->distanceTo(i) <= CFG.MININGSHIP_MINING_RADIUS-1)
            {
                self->log("je mine");
                self->state(LIGHT);
                self->extract(i);
            }
            return;
        }
    }

    // recherche de minerai connu
    float minPos_x = self->getMemory<float>(2);
    float minPos_y = self->getMemory<float>(3);
    if (minPos_x != 0.0 || minPos_y != 0.0)
    {
        self->log("je connais un minerai");
        if (self->distanceTo(minPos_x, minPos_y) < CFG.MININGSHIP_DETECTION_RADIUS) // on aurait du voir le minerai -> il est vide
        {
            // reset de la position
            self->setMemory<float>(2, 0.0);
            self->setMemory<float>(3, 0.0);
        }
        else
        {
            self->log("je vais au minerais connus");
            self->state(DEFAULT);
            self->rotateTo(minPos_x, minPos_y);
            self->move();
            return;
        }
    }

    // deplacement aleatoire
    self->log("je cherche du minerais");
    self->state(DEFAULT);
    random_move(self);
}

void HandlerExample::play_fighter(aiwar::core::Playable*)
{
}


// helpers
static void random_move(aiwar::core::Movable* self)
{
    int a = (std::rand() % 91) - 45;
    self->rotateOf(a);
    self->move();
}
