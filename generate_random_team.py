import engine
import sys
import random

types = {}

for c in engine.components:
    if engine.components[c].type != engine.DEBUG:
        if engine.components[c].type not in types:
            types[engine.components[c].type] = []
        types[engine.components[c].type].append(c)
    
f = open(sys.argv[1], 'w')
for i in xrange(5):
    f.write('unit%d %d '%(i+1, random.randint(1,25))) 
    for t in types:
        f.write(random.choice(types[t]) + " ")
    f.write("\n")
        
f.close()