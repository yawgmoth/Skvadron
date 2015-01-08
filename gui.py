import pygame
from pygame.locals import *
import os
import random
import engine
import time
import sys

DATADIR = "data"
IMAGEDIR = "img"

GRID_SIZE = 32

def load_image(name, colorkey=None):
    fullname = os.path.join(DATADIR, IMAGEDIR, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print "Cannot load image:", name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image
    
class GraphicManager:
    def initialize(self):
        self.unit_image = load_image('units1.gif', (255,255,255))
        self.terrain_image = load_image('terrain1.gif')
        self.ability_image = load_image('icons.png', (255,255,255))
        self.edge_image = load_image('edges1.gif', (255,255,255))
    def get_graphic_for_unit(self, nr):
        x = nr*GRID_SIZE
        y = x/self.unit_image.get_width()
        x %= self.unit_image.get_width()
        return (self.unit_image, Rect(x,y,GRID_SIZE,GRID_SIZE))
    def get_graphic_for_terrain(self, nr):
        x = nr*GRID_SIZE
        y = x/self.terrain_image.get_width()
        x %= self.terrain_image.get_width()
        return (self.terrain_image, Rect(x,y*GRID_SIZE,GRID_SIZE,GRID_SIZE))
        
    def get_graphic_for_ability(self, nr):
        x = nr*GRID_SIZE
        y = x/self.ability_image.get_width()
        x %= self.ability_image.get_width()
        return (self.ability_image, Rect(x,y*GRID_SIZE,GRID_SIZE,GRID_SIZE))
        
    def get_graphic_for_edge(self, nr):
        x = nr*GRID_SIZE
        y = x/self.edge_image.get_width()
        x %= self.edge_image.get_width()
        return (self.edge_image, Rect(x,y*GRID_SIZE,GRID_SIZE,GRID_SIZE))
        
graphman = GraphicManager()

class ScreenObject(object):
    def __init__(self):
        self.expired = False
        self.sourced = False
        self.targeted = False
    def handle_click(self, where, btn):
        pass
    def handle_mouse(self, pos, rel):
        pass

class Background(ScreenObject):
    def render(self, screen):
        for i in xrange(300):
            x = i%20
            y = i/20
            #[9,54,57,57,93]
            img, area = graphman.get_graphic_for_terrain([9,54,57,57,93][0 if x%10-(y+2)*i%39 < 0 else (i*x+y)%5])
            screen.blit(img, (x*GRID_SIZE, y*GRID_SIZE), area)
        for i in xrange(20):
            ind = 49
            if i == 0:
                ind = 48
            elif i == 19:
                ind = 50
            img,area = graphman.get_graphic_for_edge(ind)
            screen.blit(img, (i*GRID_SIZE,11*GRID_SIZE), area)
            for j in xrange(3):
                ind = 57
                if i == 0:
                    ind = 56
                elif i == 19:
                    ind = 58
                img, area = graphman.get_graphic_for_edge(ind)
                screen.blit(img, (i*GRID_SIZE,(12+j)*GRID_SIZE), area)
            
class MenuBackground(ScreenObject):
    def render(self, screen):
        for i in xrange(300):
            x = i%20
            y = i/20
            img, area = graphman.get_graphic_for_terrain(9)
            screen.blit(img, (x*GRID_SIZE, y*GRID_SIZE), area)
            
class Text(ScreenObject):
    def __init__(self, text, position = (0,0), color=(255,0,0)):
        super(Text,self).__init__()
        self.text = text
        self.position = position
        self.color = color
    def render(self, screen):
        font = pygame.font.Font(None, 28)
        img = font.render(self.text, True, self.color)
        screen.blit(img, self.position)
        
class Rectangle(ScreenObject):
    def __init__(self, position=(0,0), size=(10,10), color=(255,0,0), width=3):
        super(Rectangle,self).__init__()
        self.position = position
        self.size = size
        self.color = color
        self.width = width
    def render(self, screen):
        pygame.draw.rect(screen, self.color, Rect(self.position[0],self.position[1], self.size[0], self.size[1]), self.width)
        
class Button(ScreenObject):
    def __init__(self, position=(0,0), color=(0,0,255), label="", fn=lambda a: None, arg=None):
        super(Button,self).__init__()
        self.text = Text(label, (position[0]+5,position[1]+5), color=color)
        font = pygame.font.Font(None, 28)
        img = font.render(label, True, (255,0,0))
        self.size = (img.get_width() + 10, img.get_height() + 10)
        self.rect = Rectangle(position, self.size, color=color)
        self.fn = fn
        self.position = position
        self.arg = arg
    def render(self, screen):
        self.rect.render(screen)
        self.text.render(screen)
    def handle_click(self, where, btn):
        x,y = where
        if x > self.position[0] and x < self.position[0] + self.size[0] and y > self.position[1] and y < self.position[1] + self.size[1]:
            self.fn(self.arg)
        
        
DAMAGE_TYPE_COLORS = {engine.PHYSICAL: (255,0,0), engine.MAGICAL: (0,0,255), engine.PURE: (255,255,255)}
        
class GuiUnit(ScreenObject):
    def __init__(self, position, index, unit, xoff=GRID_SIZE+10):
        super(GuiUnit,self).__init__()
        self.index = index
        self.unit = unit
        self.position = position
        self.outdmg = None
        self.indmg = None
        self.xoff = xoff
        self.selected = False
        self.show_hint = None
    def render(self, screen):
        if self.unit.health <= 0:
            img, area = graphman.get_graphic_for_edge(18)
            screen.blit(img, self.position, area)
            return
            #self.expired = True
    
        if self.selected:
            pygame.draw.circle(screen, (0,255,0), (self.position[0] + GRID_SIZE/2,self.position[1]+GRID_SIZE/2), GRID_SIZE/2, 4)
            font = pygame.font.Font(None, 16)
            img = font.render("%.2f/%.2d"%(self.unit.health, self.unit.max_health), True, (0,0,0))
            screen.blit(img, (20,400))
            font = pygame.font.Font(None, 16)
            img = font.render("%.2f/%.2d"%(self.unit.mana, self.unit.max_mana), True, (0,0,0))
            screen.blit(img, (20,420))
            offsetx = 0
            if self.unit.owner.is_human:
                offsetx = -GRID_SIZE
            for i,c in enumerate(self.unit.components):
                if engine.components[c].type == engine.SELECTOR and self.unit.owner.is_human:
                    continue
                icon, area = graphman.get_graphic_for_ability(engine.components[c].icon)
                screen.blit(icon, (100+i*GRID_SIZE+offsetx, 400), area)
                if self.show_hint:
                    x,y = self.show_hint
                    if x > 100+i*GRID_SIZE+offsetx and x < 100 + (i+1)*GRID_SIZE+offsetx and \
                       y > 400 and y < 400 + GRID_SIZE:
                        hx = 100
                        hy = 363
                        font = pygame.font.Font(None, 16)
                        img = font.render(engine.components[c].name, True, (0,0,0))
                        screen.blit(img, (hx,hy))
                        hy = 373
                        img = font.render(engine.components[c].description, True, (0,0,0))
                        if img.get_width() > 400:
                            desc = engine.components[c].description.split()
                            img = font.render(' '.join(desc[:len(desc)/2]), True, (0,0,0))
                            screen.blit(img, (hx,hy))
                            img = font.render(' '.join(desc[len(desc)/2:]), True, (0,0,0))
                            hy = 383
                        screen.blit(img, (hx,hy))
            for i,b in enumerate(self.unit.buffs):
                icon, area = graphman.get_graphic_for_ability(b.icon)
                screen.blit(icon, (300+i*GRID_SIZE, 400), area)
                if b.count:
                    font = pygame.font.Font(None, 16)
                    img = font.render(str(int(round(b.count))), True, (255,0,0))
                    screen.blit(img, (300+(i+1)*GRID_SIZE-img.get_width(),400+GRID_SIZE - img.get_height()))
                if self.show_hint:
                    x,y = self.show_hint
                    if x > 300+i*GRID_SIZE and x < 300 + (i+1)*GRID_SIZE and \
                       y > 400 and y < 400 + GRID_SIZE:
                        hx = 300
                        hy = 363
                        font = pygame.font.Font(None, 16)
                        img = font.render(b.name, True, (0,0,0))
                        screen.blit(img, (hx,hy))
                        hy = 373
                        desc = b.description.replace("%count", str(b.count))
                        img = font.render(desc, True, (0,0,0))
                        if img.get_width() > 400:
                            desc = desc.split()
                            img = font.render(' '.join(desc[:len(desc)/2]), True, (0,0,0))
                            screen.blit(img, (hx,hy))
                            img = font.render(' '.join(desc[len(desc)/2:]), True, (0,0,0))
                            hy = 383
                        screen.blit(img, (hx,hy))
                        
        img, area = graphman.get_graphic_for_unit(self.index)
        
        screen.blit(img, self.position, area)
        
        width = max(1,int(round((26*self.unit.health)/self.unit.max_health)))
        pygame.draw.rect(screen, (0,255,0), Rect(self.position[0]+3,self.position[1]+GRID_SIZE-8, width, 4), 0)
        if width < 26:
            pygame.draw.rect(screen, (255,0,0), Rect(self.position[0]+3+width,self.position[1]+GRID_SIZE-8, 26-width, 4), 0)
        width = max(1,int(round((26*self.unit.mana)/self.unit.max_mana)))
        pygame.draw.rect(screen, (0,0,255), Rect(self.position[0]+3,self.position[1]+GRID_SIZE-4, width, 4), 0)
        if width < 26:
            pygame.draw.rect(screen, (255,0,0), Rect(self.position[0]+3+width,self.position[1]+GRID_SIZE-4, 26-width, 4), 0)
        if self.outdmg is not None:
            dmg,type = self.outdmg
            font = pygame.font.Font(None, 18)
            img = font.render(dmg, True, DAMAGE_TYPE_COLORS[type])
            x,y = self.position
            x += self.xoff
            y += GRID_SIZE/2-12
            screen.blit(img, (x,y))
        if self.indmg is not None:
            dmg,type = self.indmg
            font = pygame.font.Font(None, 18)
            img = font.render(dmg, True, DAMAGE_TYPE_COLORS[type])
            x,y = self.position
            x += self.xoff
            y += GRID_SIZE/2+4
            screen.blit(img, (x,y))
    def add_out_damage(self, dmg, type):
        d = ""
        if self.outdmg:
            d = self.outdmg[0]
        self.outdmg = (d + " + %.2f"%(dmg), type)
    def add_in_damage(self, dmg, type):
        d = ""
        if self.indmg:
            d = self.indmg[0]
        self.indmg = (d + "- %.2f"%(dmg), type)
    def handle_click(self, where, btn):
        x,y = where
        if btn == 1:
            self.selected = False
        if x > self.position[0] and x < self.position[0] + GRID_SIZE and y > self.position[1] and y < self.position[1] + GRID_SIZE:
            if btn == 1:
                self.selected = True
                self.sourced = True
            elif btn == 3:
                self.targeted = True
    def handle_mouse(self, pos, rel):
        self.show_hint = pos
    

class GuiHandler:
    def __init__(self, screen):
        self.objects = []
        self.screen = screen
    def render_frame(self):
        newobjects = []
        for o in self.objects:
            o.render(self.screen)
            if not o.expired:
                newobjects.append(o)
        self.objects = newobjects
    def clear(self):
        self.objects = []
        
class ShowOutgoingDamage(engine.AttackHandler):
    def __init__(self, guigame, guiunit):
        self.guigame = guigame
        self.priority = 1000000
        self.guiunit = guiunit
    def __call__(self, atk, targets):
        self.guiunit.add_out_damage(atk.damage, atk.type)
        return atk
        
class ShowIncomingDamage(engine.DefenseHandler):
    def __init__(self, guigame, guiunit):
        self.guigame = guigame
        self.priority = 1000000
        self.guiunit = guiunit
    def __call__(self, atk, units):
        self.guiunit.add_in_damage(atk.damage, atk.type)
        return atk
        
speed = 1.0

class Scene(object):
    def update(self):
        self.guihandler.render_frame()
        self.do_update()
    def do_update(self):
        pass
    def handle_click(self, where, button):
        for obj in self.guihandler.objects:
            obj.handle_click(where, button)
    def handle_mouse(self, pos, rel):
        for obj in self.guihandler.objects:
            obj.handle_mouse(pos, rel)
                
@engine.component
class HumanTargetSelector(engine.AttackHandler,engine.AHandlerComponent):
    name = "HumanTargetSelector"
    description = "Your choice"
    type = engine.SELECTOR
    icon = 222
    def __init__(self, storage):
        self.priority = 0
        self.storage = storage
    def __call__(self, atk, targets):
        if self.storage.target not in targets:
            print "you chose the wrong thing"
            return atk
        atk.target = self.storage.target
        return atk

class TargetStorage(object):
    def __init__(self):
        self.target = None
        
class UnitEditor(ScreenObject):
    def __init__(self, parent, unit, position):
        self.parent = parent
        self.unit = unit
        self.position = position
        self.components = {}
        self.expired = False
        for c in self.unit[2:]:
            self.components[engine.components[c].type] = c
        self.show_hint = (0,0)
    def render(self, screen):
        if self.parent.selected_unit == self:
            pygame.draw.circle(screen, (0,255,0), (self.position[0] + GRID_SIZE/2,self.position[1]+GRID_SIZE/2), GRID_SIZE/2, 4)
        img, area = graphman.get_graphic_for_unit(int(self.unit[1]))
        screen.blit(img, self.position, area)
        at = GRID_SIZE
        for t in ALL_TYPES:
            hx, hy = (100,5)
            if t in self.components:
                img, area = graphman.get_graphic_for_ability(engine.components[self.components[t]].icon)
                screen.blit(img, (self.position[0], self.position[1]+at), area)
                c = self.components[t]
                if self.show_hint and self.show_hint[0] > self.position[0] and \
                   self.show_hint[0] < self.position[0]+GRID_SIZE and \
                   self.show_hint[1] > self.position[1] + at and \
                   self.show_hint[1] < self.position[1] + at + GRID_SIZE:
                    font = pygame.font.Font(None, 16)
                    img = font.render(engine.components[c].name, True, (0,0,0))
                    screen.blit(img, (hx,hy))
                    hy = 20
                    img = font.render(engine.components[c].description, True, (0,0,0))
                    if img.get_width() > 500:
                        desc = engine.components[c].description.split()
                        img = font.render(' '.join(desc[:len(desc)/2]), True, (0,0,0))
                        screen.blit(img, (hx,hy))
                        img = font.render(' '.join(desc[len(desc)/2:]), True, (0,0,0))
                        hy = 35
                    screen.blit(img, (hx,hy))
                at += GRID_SIZE
        return
    def handle_click(self,where, btn):
        x,y = where
        if x > self.position[0] and x < self.position[0] + GRID_SIZE and \
           y > self.position[1] and y < self.position[1] + GRID_SIZE:
               self.parent.selected_unit = self
        if x > self.position[0] and x < self.position[0] + GRID_SIZE and \
           y > self.position[1] + GRID_SIZE and y < self.position[1] + (len(self.components) +1)*GRID_SIZE:
            at = (y - (self.position[1] + GRID_SIZE))/GRID_SIZE
            for t in ALL_TYPES:
                if t in self.components and at == 0:
                    self.parent.return_component(self.components[t])
                    del self.components[t]
                    break
                elif t in self.components:
                    at -= 1
    def make_unit(self):
        result = self.unit[:2]
        for t in self.components:
            result.append(self.components[t])
        return result
        
    def handle_mouse(self, pos, rel):
        self.show_hint = pos
        
ALL_TYPES = [engine.BODY, engine.ATTACK, engine.DEFENSE, engine.SPECIAL, engine.TRAIT, engine.ABILITY]

class InventoryEditor(ScreenObject):
    def __init__(self, parent, inventory, position):
        self.parent = parent
        self.inventory = inventory
        self.position = position
        self.expired = False
        self.show_hint = (0,0)
    def render(self, screen):
        for i,t in enumerate(ALL_TYPES):
            comps = []
            for c in self.inventory:
                if engine.components[c].type == t:
                    comps.append((c,self.inventory[c]))
            comps.sort(key=lambda (name,cnt): name)
            for j,t in enumerate(comps):
                hx,hy = (100,5)
                img,area = graphman.get_graphic_for_ability(engine.components[t[0]].icon)
                screen.blit(img, (self.position[0]+j*GRID_SIZE,self.position[1] + i*50), area)
                c = t[0]
                if self.show_hint and self.show_hint[0] > self.position[0]+j*GRID_SIZE and \
                   self.show_hint[0] < self.position[0]+(j+1)*GRID_SIZE and \
                   self.show_hint[1] > self.position[1] + i*50 and \
                   self.show_hint[1] < self.position[1] + (i+1)*50:
                    font = pygame.font.Font(None, 16)
                    img = font.render(engine.components[c].name, True, (0,0,0))
                    screen.blit(img, (hx,hy))
                    hy = self.position[1]-30
                    img = font.render(engine.components[c].description, True, (0,0,0))
                    if img.get_width() > 500:
                        desc = engine.components[c].description.split()
                        img = font.render(' '.join(desc[:len(desc)/2]), True, (0,0,0))
                        screen.blit(img, (hx,hy))
                        img = font.render(' '.join(desc[len(desc)/2:]), True, (0,0,0))
                        hy = self.position[1]-15
                    screen.blit(img, (hx,hy))
                if t[1] >= 0:
                    font = pygame.font.Font(None, 16)
                    img = font.render("%d"%(t[1]), True, (255,0,0))
                    screen.blit(img, (self.position[0]+j*GRID_SIZE,self.position[1] + i*50))

    def handle_click(self, where, btn):
        x, y = where
        if not self.parent.selected_unit:
            return
        if x > self.position[0] and y > self.position[1] and y < self.position[1] + len(ALL_TYPES)*50:
            index = (x-self.position[0])/GRID_SIZE
            type = ALL_TYPES[(y-self.position[1])/50]
            comps = []
            for c in self.inventory:
                if engine.components[c].type == type:
                    comps.append((c,self.inventory[c]))
            comps.sort(key=lambda (name,cnt): name)
            if index < len(comps):
                comp = comps[index][0]
                if self.inventory[comp] != 0:
                    if type in self.parent.selected_unit.components:
                        self.parent.return_component(self.parent.selected_unit.components[type])
                    self.parent.selected_unit.components[type] = comp
                    if self.inventory[comp] > 0:
                        self.inventory[comp] -= 1
    def handle_mouse(self, pos, rel):
        self.show_hint = pos
                
                

class UnitBuilder(Scene):
    def __init__(self, guihandler):
        self.guihandler = guihandler
        self.guihandler.objects.append(MenuBackground())
        global player
        self.effective_inventory = {}
        for i in player.inventory:
            self.effective_inventory[i] = player.inventory[i]
        self.selected_unit = None
        self.uniteds = []
        for i, u in enumerate(player.team):
            ue = UnitEditor(self, u, (100+i*50, 250))
            self.guihandler.objects.append(ue)
            self.uniteds.append(ue)
        self.guihandler.objects.append(InventoryEditor(self, self.effective_inventory, (100,50)))
        self.guihandler.objects.append(Button(position=(20,50), label='Save', fn=self.do_save))
        self.guihandler.objects.append(Button(position=(20,100), label='Cancel', fn=self.do_cancel))
    def return_component(self, comp):
        if comp not in self.effective_inventory:
            self.effective_inventory[comp] = 0
        if self.effective_inventory[comp] >= 0:
            self.effective_inventory[comp] += 1
    def do_cancel(self, arg):
        global scene
        self.guihandler.clear()
        scene = LevelSelector(self.guihandler)
    def do_save(self, arg):
        global scene, player
        self.guihandler.clear()
        player.inventory = self.effective_inventory
        newteam = []
        for i, ue in enumerate(self.uniteds):
            newteam.append(ue.make_unit())
        scene = LevelSelector(self.guihandler)
        player.team = newteam
    
def get_drop(chances):
    total = sum(map(lambda item: int(item[1]), chances))
    r = random.randint(0, total-1)
    at = 0
    for i in chances:
        if at <= r and at + int(i[1]) > r:
            return i[0]
        at += int(i[1])
    return chances[-1][0]
    
class Drop(ScreenObject):
    def __init__(self, name, index):
        self.name = name
        dx = index%5
        dy = index/5
        self.position = (150+dx*GRID_SIZE,200+dy*GRID_SIZE)
        self.expired = False
        self.show_hint = (0,0)
        self.targeted = False
        self.sourced = False
        self.show_hint = (0,0)
    def render(self, screen):
        icon, area = graphman.get_graphic_for_ability(engine.components[self.name].icon)
        screen.blit(icon, self.position, area)
        if self.show_hint and self.show_hint[0] > self.position[0] and \
           self.show_hint[0] < self.position[0] + GRID_SIZE and \
           self.show_hint[1] > self.position[1] and \
           self.show_hint[1] < self.position[1] + GRID_SIZE:
            hx = 100
            hy = 363
            c = self.name
            font = pygame.font.Font(None, 16)
            img = font.render(engine.components[c].name, True, (0,0,0))
            screen.blit(img, (hx,hy))
            hy = 373
            img = font.render(engine.components[c].description, True, (0,0,0))
            if img.get_width() > 400:
                desc = engine.components[c].description.split()
                img = font.render(' '.join(desc[:len(desc)/2]), True, (0,0,0))
                screen.blit(img, (hx,hy))
                img = font.render(' '.join(desc[len(desc)/2:]), True, (0,0,0))
                hy = 383
            screen.blit(img, (hx,hy))
    def handle_mouse(self, pos, rel):
        self.show_hint = pos
        
class GuiGame(Scene):
    def __init__(self, guihandler, players, human_players=[0], target_storage=TargetStorage(), lvl=None, past=False):
        self.guihandler = guihandler
        self.players = players
        self.guihandler.objects.append(Background())
        self.guiunits = []
        self.last_turn = time.time()
        self.source = None
        self.target_storage = target_storage
        self.current_player = 0
        self.human_players = human_players
        self.end_reached = False
        self.lvl = lvl
        self.drops = []
        self.past = past
        
    def do_update(self):
        for obj in self.guihandler.objects:
            if obj.targeted and obj.unit.owner != self.players[self.current_player]:
                self.target_storage.target = obj.unit
                obj.targeted = False
            if obj.sourced and obj.unit.owner == self.players[self.current_player]:
                self.source = obj.unit
                obj.sourced = False
        if (time.time() - self.last_turn) > speed and not self.game_ended():
            self.last_turn = time.time()
            self.turn()
            if self.game_ended() and not self.end_reached:
                self.guihandler.clear()
                self.guihandler.objects.append(Background())
                self.guihandler.objects.append(Button(position=(150,100), label="Continue", fn=self.do_continue))
                if self.lvl:
                    if self.get_winner() and self.get_winner().is_human:
                        if not self.past:
                            player.past.append(self.lvl)
                            del player.available_levels[player.available_levels.index(self.lvl)]
                            for n in self.lvl.next:
                                if n.strip() not in map(lambda l: l.fname.strip(), player.available_levels + player.past):
                                    player.available_levels.append(Level(n))
                        for d in self.lvl.drops:
                            drop = get_drop(d)
                            if drop not in player.inventory:
                                player.inventory[drop] = 0
                            player.inventory[drop] += 1
                            self.drops.append(drop)
                self.end_reached = True
                
                if not self.get_winner():
                    self.guihandler.objects.append(Text("Game ended in a draw", (25, 25)))
                else:
                    wname = self.get_winner().name
                    wverb = "has"
                    if wname == "You":
                        wverb = "have"
                    self.guihandler.objects.append(Text("%s %s won the game"%(wname, wverb), (25, 25)))
                if self.drops:
                    self.guihandler.objects.append(Text("You gained:", (120, 150)))
                    for i, d in enumerate(self.drops):
                        self.guihandler.objects.append(Drop(d, i))
        font = pygame.font.Font(None, 16)
        img = font.render("Current delay: %.2f seconds"%(speed), True, (255,0,0))
        self.guihandler.screen.blit(img, (10,10))

    def do_continue(self, arg):
        global scene, player
        self.guihandler.clear()
        if self.lvl:
            scene = LevelSelector(self.guihandler, self.past)
        else:
            scene = MainMenu(self.guihandler)
        
    def game_ended(self):
        has_units = 0
        for p in self.players:
            if p.units:
                has_units += 1
        return has_units <= 1

    def turn(self):
        for gu in self.guiunits:
            gu.outdmg = None
            gu.indmg = None
        enemy_units = []
        for i, p in enumerate(self.players):
            if i != self.current_player:
                enemy_units.extend(p.units)
        turndone = True
        if self.current_player in self.human_players:
            if self.source and self.target_storage.target and self.target_storage.target.health > 0:
                 self.players[self.current_player].make_attack(self.source, enemy_units)
                 self.target_storage.target = None
            else:
                 turndone = False
        else:
            self.players[self.current_player].make_turn(enemy_units)
        if turndone:
            self.current_player += 1
            self.current_player %= len(self.players)
            if self.source and ((self.current_player in self.human_players and self.source.owner != self.players[self.current_player]) or self.source.health <= 0):
                self.source = None
    
    def start(self):
        self.current_player = 0
        x = 3*GRID_SIZE
        for i,p in enumerate(self.players):
            y = 3* GRID_SIZE
            self.guihandler.objects.append(Text(p.name, (x-GRID_SIZE/2,y-GRID_SIZE)))
            for u in p.units:
                index = (i+1)*5
                if hasattr(u, "index"):
                    index = u.index
                xoff = GRID_SIZE + 10
                if i == len(self.players)-1:
                    xoff = -10
                gu = GuiUnit((x,y), index, u)
                self.guiunits.append(gu)
                self.guihandler.objects.append(gu)
                u.add_attack_handler(ShowOutgoingDamage(self, gu))
                u.add_defense_handler(ShowIncomingDamage(self, gu))
                y += GRID_SIZE
            x += 7*GRID_SIZE

    def get_winner(self):
        winner = None
        for i,p in enumerate(self.players):
            if p.units:
                winner = p
        return winner
    
class Level:
    def __init__(self, fname):
        f = open(fname, 'r')
        self.drops = []
        self.next = []
        self.opponent = ""
        self.name = "Level"
        self.fname = fname
        for l in f:
            if l.startswith('opponent'):
                 self.opponent = l.split()[1]
            elif l.startswith('drop'):
                 self.drops.append(map(lambda s: s.strip().split(), l.split(None, 1)[1].split(',')))
            elif l.startswith('next'):
                 self.next.append(l.split()[1].strip())
            elif l.startswith('name'):
                 self.name = l.split(None, 1)[1].strip()
    
class Player:
    def __init__(self, fname=""):
        self.fname = fname
        if fname and os.path.exists(fname):
            f = file(fname, "r")
            self.team = []
            self.inventory = {}
            self.past = []
            self.available_levels = []
            for l in f:
                items = l.split()
                if len(items) > 1:
                    what, line = l.split(None, 1)
                    if what == "unit:":
                        self.team.append(line.strip().split(","))
                    elif what == "levels:":
                        self.available_levels = map(Level, line.strip().split(","))
                    elif what == "inventory:":
                        cnt, item = line.strip().split(None, 1)
                        self.inventory[item] = int(cnt)
                    elif what == "past:":
                        self.past = map(Level, line.strip().split(","))
            f.close()
        else:
            
            self.available_levels = [Level("levels/level_generated_0_0.lvl")]
            self.team = [["unit1", 3, 'RandomTargetSelector', 'BasicPhysicalAttack', 'BasicMagicalDefense'],
                         ["unit2", 8, 'RandomTargetSelector', 'BasicMagicalAttack', 'BasicMagicalDefense'],
                         ["unit3", 11, 'RandomTargetSelector', 'BasicMagicalAttack', 'BasicPhysicalDefense'],
                         ["unit4", 2, 'RandomTargetSelector', 'BasicPhysicalAttack', 'BasicPhysicalDefense'],
                         ["unit5", 14, 'RandomTargetSelector', 'BasicPhysicalAttack', 'BasicMagicalDefense']
                         ]
            self.inventory = {'BasicPhysicalAttack': -1, 'BasicMagicalAttack': -1,
                          'BasicPhysicalDefense': -1, 'BasicMagicalDefense': -1}
            self.past = []
    def save(self):
        f = file(self.fname, "w")
        levels = ",".join(map(lambda l: l.fname, self.available_levels))
        print >> f, "levels:", levels
        for t in self.team:
            print >> f, "unit:", ",".join(map(str, t))
        for i in self.inventory:
            print >> f, "inventory:", self.inventory[i], i
        if self.past:
            print >> f, "past:", ",".join(map(lambda l: l.fname, self.past))
        f.close()
        
        
        
class LevelSelector(Scene):
    def __init__(self, guihandler, past=False):
        self.guihandler = guihandler
        global player
        self.guihandler.objects.append(MenuBackground())
        self.guihandler.objects.append(Button(position=(100, 100), label="Modify team", fn=self.do_build_unit))
        if past:
            for i, lvl in enumerate(player.past):
                self.guihandler.objects.append(Button(position=(100,150+50*i), label=lvl.name, fn=self.start_past_level, arg=lvl))
            self.guihandler.objects.append(Button(position=(100, 150 + 50*len(player.past)), label="Back", fn=self.do_current_levels))
        else:
            for i, lvl in enumerate(player.available_levels):
                self.guihandler.objects.append(Button(position=(100,150+50*i), label=lvl.name, fn=self.start_level, arg=lvl))
            self.guihandler.objects.append(Button(position=(100, 150 + 50*len(player.available_levels)), label="Past Levels", fn=self.do_past_levels))
         
        
    def start_level(self, lvl):
        self.do_start_level(lvl)
    def start_past_level(self, lvl):
        self.do_start_level(lvl, True)
    def do_start_level(self, lvl, past=False):
        global scene, player
        files = ["", lvl.opponent]
        if len(sys.argv) > 2:
            files = sys.argv[1:]
        players = []
        human_players = [0]
        target_storage = TargetStorage()
        def gui_component_maker(i):
            def make_gui_component(name):
                c = engine.components[name]
                if c.type == engine.SELECTOR and i in human_players:
                    return HumanTargetSelector(target_storage)
                return c()
            return make_gui_component
        for i,f in enumerate(files):
            if i in human_players:
                players.append(engine.make_player_from_team(player.team, "You", mk_component=gui_component_maker(i), is_human=True))
            else:
                players.append(engine.make_player(f, "Opponent"))
        self.guihandler.clear()
        scene = GuiGame(self.guihandler, players, human_players=human_players, target_storage=target_storage, lvl=lvl, past=past)
        scene.start()
        
    def do_build_unit(self, arg):
        global scene
        self.guihandler.clear()
        scene = UnitBuilder(self.guihandler)

    def do_quit(self, arg):
        global player
        if player:
            player.save()
        pygame.quit()
        sys.exit(0)
        
    def do_past_levels(self, arg):
        global scene, player
        self.guihandler.clear()
        scene = LevelSelector(self.guihandler, True)
        
    def do_current_levels(self, arg):
        global scene, player
        self.guihandler.clear()
        scene = LevelSelector(self.guihandler, False)
        
class MainMenu(Scene):
    def __init__(self, guihandler):
        self.guihandler = guihandler
        self.guihandler.objects.append(MenuBackground())
        self.guihandler.objects.append(Button(position=(100,100), label="Start", fn=self.do_start))
        self.guihandler.objects.append(Button(position=(100,150), label="Skirmish", fn=self.do_skirmish))
        self.guihandler.objects.append(Button(position=(100,200), label="Quit", fn=self.do_quit))
    

    def do_start(self, arg):
        global scene, player
        player = Player("player.ply")
        self.guihandler.clear()
        scene = LevelSelector(self.guihandler)
        #scene.start()
        
    def do_skirmish(self, arg):
        global scene
        files = ["team3.skv", "teams/team%d.skv"%(random.randint(0,60))]
        if len(sys.argv) > 2:
            files = sys.argv[1:]
        players = []
        human_players = [0]
        target_storage = TargetStorage()
        def gui_component_maker(i):
            def make_gui_component(name):
                c = engine.components[name]
                if c.type == engine.SELECTOR and i in human_players:
                    return HumanTargetSelector(target_storage)
                return c()
            return make_gui_component
        for i,f in enumerate(files):
            players.append(engine.make_player(f, "player %d"%(i+1), mk_component=gui_component_maker(i), is_human=i in human_players))
        self.guihandler.clear()
        scene = GuiGame(self.guihandler, players, human_players=human_players, target_storage=target_storage)
        scene.start()
        
    def do_quit(self, arg):
        pygame.quit()
        sys.exit(0)
        
        

scene = None
player = None
        
def main():
    global speed, scene, player
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Skvadron')
    clock = pygame.time.Clock()
    graphman.initialize()
    
    guihandler = GuiHandler(screen)
    #
    scene = MainMenu(guihandler)
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                if player:
                    player.save()
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                if player:
                    player.save()
                return
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    speed /= 2.0
                elif event.key == K_a:
                    speed *= 2.0
            elif event.type == KEYUP: 
                pass
                #emit(Event(tags=KEY_UP, key=event.key))
            elif event.type == MOUSEBUTTONDOWN:
                scene.handle_click(event.pos, event.button)
                #emit(Event(tags=MOUSE_DOWN, where=event.pos, button=event.button))#
            elif event.type == MOUSEMOTION:
                scene.handle_mouse(event.pos, event.rel)
                
        scene.update() 
        pygame.display.flip()
        

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
    pygame.quit()

  