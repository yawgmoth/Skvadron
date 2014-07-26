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
        if x > self.position[0] and x < self.position[1] + self.size[0] and y > self.position[1] and y < self.position[1] + self.size[1]:
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
    def render(self, screen):
        if self.selected:
            pygame.draw.circle(screen, (0,255,0), (self.position[0] + GRID_SIZE/2,self.position[1]+GRID_SIZE/2), GRID_SIZE/2, 4)
            for i,c in enumerate(self.unit.components):
                icon, area = graphman.get_graphic_for_ability(engine.components[c].icon)
                screen.blit(icon, (100+i*GRID_SIZE, 400), area)
        img, area = graphman.get_graphic_for_unit(self.index)
        screen.blit(img, self.position, area)
        if self.unit.health <= 0:
            self.expired = True
        width = max(1,int(round((26*self.unit.health)/self.unit.max_health)))
        pygame.draw.rect(screen, (0,255,0), Rect(self.position[0]+3,self.position[1]+GRID_SIZE-4, width, 4), 0)
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
        self.selected = False
        if x > self.position[0] and x < self.position[0] + GRID_SIZE and y > self.position[1] and y < self.position[1] + GRID_SIZE:
            if btn == 1:
                self.selected = True
                self.sourced = True
                for i,c in enumerate(self.unit.components):
                    print c
            elif btn == 3:
                self.targeted = True
    

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

        
class GuiGame(Scene):
    def __init__(self, guihandler, players, human_players=[0], target_storage=TargetStorage()):
        self.guihandler = guihandler
        self.players = players
        self.guihandler.objects.append(Background())
        self.guiunits = []
        self.last_turn = time.time()
        self.source = None
        self.target_storage = target_storage
        self.current_player = 0
        self.human_players = human_players
        
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
            if self.game_ended():
                if not self.get_winner():
                    self.guihandler.objects.append(Text("Game ended in a draw", (25, 25)))
                else:
                    self.guihandler.objects.append(Text(self.get_winner().name + " has won the game", (25, 25)))
        font = pygame.font.Font(None, 16)
        img = font.render("Current delay: %.2f seconds"%(speed), True, (255,0,0))
        self.guihandler.screen.blit(img, (10,10))    
        
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
            if self.source and self.target_storage.target:
                 self.players[self.current_player].make_attack(self.source, enemy_units)
                 self.source = None
                 self.target_storage.target = None
            else:
                 turndone = False
        else:
            self.players[self.current_player].make_turn(enemy_units)
        if turndone:
            self.current_player += 1
            self.current_player %= len(self.players)
    
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
        
        
class MainMenu(Scene):
    def __init__(self, guihandler):
        self.guihandler = guihandler
        self.guihandler.objects.append(MenuBackground())
        self.guihandler.objects.append(Button(position=(100,100), label="Start", fn=self.do_start))
        self.guihandler.objects.append(Button(position=(100,200), label="Quit", fn=self.do_quit))

    def do_start(self, arg):
        global scene
        files = ["team3.skv", "team2.skv"]
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
            players.append(engine.make_player(f, "player %d"%(i+1), mk_component=gui_component_maker(i)))
        self.guihandler.clear()
        scene = GuiGame(self.guihandler, players, human_players=human_players, target_storage=target_storage)
        scene.start()
        
    def do_quit(self, arg):
        pygame.quit()
        sys.exit(0)
        
        

scene = None
        
def main():
    global speed, scene
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
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
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
                #emit(Event(tags=MOUSE_DOWN, where=event.pos, button=event.button))
        scene.update() 
        pygame.display.flip()
        

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
    pygame.quit()

  