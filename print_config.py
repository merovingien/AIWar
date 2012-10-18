import aiwar

########

def play_miningship(ship):
    pass

def play_base(base):
    print_config()
    

def play_fighter(fighter):
    pass

########

def print_config():
    print "Config:"
    for i in dir(aiwar):
        if i.isupper():
            print "aiwar."+i+"() =", getattr(aiwar, i)(), ":", getattr(aiwar, i).__doc__
