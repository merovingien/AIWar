AIWar
=====

Create your Artificial Intelligence to win the war


AIWar is a game that let you create artificial intelligences to control space ships. The goal is to assemble a fighter army to destroy the ennemy base. To do that, you must get minerals with miningship and create fighters with your ressources. And you should also defend yourself again the ennemy army. The first team that destroes the ennemy base win the match !


*INSTALL*

Dependancies:
- tinyxml
- python (2.7 is the only tested version)
- SDL
- SDL_gfx

Currently AIWar only works on Linux. Windows version is coming soon.

To compile AIWar, just install dev packages of the libraries listed above, and run 'make CPP=gcc LD=gcc' (or just 'make' if you have clang installed).

*RUN*

'./AIWar'

That's it !

More options are available, './AIWar --help' will help you...

To create your own AI, you can create a python file, and provide three functions : play_base(base), play_miningship(miningship) and play_fighter(fighter). See embtest.py for details and examples. Then you add a <player> section in config.xml and set your player name in one of the two teams : blue or red.

*CONTRIBUTE*

If you have suggestions or bug report, do not hesitate to post them in the tracker.

Have fun !
