import engine

TYPE_NAMES = {engine.SELECTOR: "Target Selector", engine.ATTACK: "Attack", engine.DEFENSE: "Defense", engine.SPECIAL: "Special", engine.DEBUG: "Debug"}

comps = engine.components.keys()[:]
comps.sort(key=lambda c: engine.components[c].type)
for c in comps:
    print c, "(%s)"%(TYPE_NAMES[engine.components[c].type])
    print "\t", engine.components[c].description
    print
