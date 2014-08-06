
class Unit(object):
    def __init__(self, name, icon=0, components=[]):
        self.name = name
        self.icon = icon
        self.components = components
        
def make_unit(s):
    tokens = map(lambda s: s.strip(), l.split())
    index = 0
    comps = tokens[1:]
    try:
        index = int(tokens[1])
        comps = tokens[2:]
    except Exception:
        pass
    return Unit(tokens[0], index, comps)
    