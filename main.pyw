import math
import random
import sys #so you can quit the game
import pygame

pygame.init()


display = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

heart = pygame.image.load('assets/fx/hp.png')
notheart = pygame.image.load('assets/fx/-hp.png')

weps = {0:pygame.image.load('assets/fx/paper.png'),
        1:pygame.image.load('assets/fx/rock.png'),
        2:pygame.image.load('assets/fx/scissors.png')}

my_font = pygame.font.SysFont('Comic Sans MS', 30)

#WEAPONS
class Paper_Weapon:
    def __init__(self):
        self.pic = pygame.image.load('assets/weapons/paper.png')
        self.hitbox = pygame.Rect(0,0,0,0)

    def handle_weapon(self, display):
        mx, my = pygame.mouse.get_pos()

        relx, rely = mx - you.hitbox.x, my - you.hitbox.y
        angle = math.atan2(relx, rely)

        #allows orbit
        offset = 50
        coords = [you.hitbox.x + offset*math.sin(angle), you.hitbox.y + offset*math.cos(angle)]
        #hitbox stuff
        wep = pygame.transform.rotate(pygame.transform.scale(self.pic, (64,64)), angle*180/math.pi)
        temp = pygame.Rect(wep.get_rect(topleft=coords))
        #make hitbox actually fit weapon
        self.hitbox = temp.inflate(-50 * abs(math.sin(angle)), -50 * abs(math.cos(angle)))

        #pygame.draw.rect(display,(0,0,255), self.hitbox)

        display.blit(wep, (coords[0], coords[1]))

class Rock_Weapon:
    def __init__(self):
        pass
        
    def attack(self):
        global urbullets
        urbullets.append(Rock_Weapon_Projectile(you.hitbox.x+32, you.hitbox.y+32))

class Rock_Weapon_Projectile:
    def __init__(self, x, y):
        #self.x = x
        #self.y = y
        self.hitbox = pygame.Rect(x,y,16,16)
        self.spd = 10

        mx, my = pygame.mouse.get_pos()

        self.angle = math.atan2(y-my, x-mx)
        self.xv = math.cos(self.angle) * self.spd
        self.yv = math.sin(self.angle) * self.spd
    
    def main(self,display):#this function replaces handle_weapon as there are multiple projectiles
        self.hitbox.x -= int(self.xv)
        self.hitbox.y -= int(self.yv)

        pygame.draw.circle(display, (128,128,128), (self.hitbox.x+5, self.hitbox.y+5), 8)

class Scissor_Weapon:
    def __init__(self):
        self.anims = [pygame.image.load('assets/weapons/scissors_0.png'),
                      pygame.image.load('assets/weapons/scissors_1.png'),
                      pygame.image.load('assets/weapons/scissors_2.png')]
        self.curanim = 0

        self.hitbox = pygame.Rect(2,2,64,64)
        self.attacking = False

        self.angle = 0
        
    def attack(self):
        mx, my = pygame.mouse.get_pos()
        relx, rely = mx - you.hitbox.x, my - you.hitbox.y
        self.angle = math.atan2(relx, rely)

        self.attacking = True
    
    def handle_weapon(self, display):
        if self.attacking:
            #actually attack
            #allows orbit
            offset = 50
            coords = [you.hitbox.x + offset*math.sin(self.angle), you.hitbox.y + offset*math.cos(self.angle)]
            #hitbox stuff
            wep = pygame.transform.rotate(pygame.transform.scale(self.anims[self.curanim//5], (64,64)), self.angle*180/math.pi)
            temp = pygame.Rect(wep.get_rect(topleft=coords))
            #make hitbox actually fit weapon
            self.hitbox = temp.inflate(-25 * abs(math.cos(self.angle)), -25 * abs(math.sin(self.angle)))

            display.blit(wep, (coords[0], coords[1]))
            #pygame.draw.rect(display, (255,0,0), self.hitbox, 2)

            self.curanim += 1

            if self.curanim == 15:
                self.curanim = 0
                self.attacking = False
        else:
            self.hitbox = pygame.Rect(0,0,0,0)

#YOU
class Player:
    def __init__(self, x, y):
        self.spd = 3.5
        self.hp = 3
        self.immune = False
        self.last_hit = 0.0

        self.hitbox = pygame.Rect(x+10, y, 50, 64)

        self.walkanim = [pygame.image.load('assets/you_walk_0.png'),
                        pygame.image.load('assets/you_walk_1.png')]
        self.still = pygame.image.load('assets/you_still.png')

        self.curanim = 0
        self.moving = False

        self.weapons = [Paper_Weapon(), Rock_Weapon(), Scissor_Weapon()]
        self.curwep = 0
    
    def main(self, display):
        #animation and stuff
        self.curanim += 1
        self.curanim = 0 if self.curanim >= len(self.walkanim)*5 else self.curanim
        
        if self.moving:
            display.blit(pygame.transform.scale(self.walkanim[self.curanim//5], (64,64)), (self.hitbox.x, self.hitbox.y))
        else:
            display.blit(pygame.transform.scale(self.still, (64,64)), (self.hitbox.x, self.hitbox.y))
        
        try:
            #rock weapon cannot handle_weapon so try except to prevent game from breaking
            self.weapons[self.curwep].handle_weapon(display)
        except:
            pass
        self.moving = False
        
        #immunity
        if self.immune:
            now = pygame.time.get_ticks()
            if now - self.last_hit > 700:#change cooldown here!!
                self.immune = False
    
    def move(self, xmove, ymove):
        self.hitbox.x += xmove * self.spd
        self.hitbox.y += ymove * self.spd

        if self.hitbox.x > 750:
            self.hitbox.x = 750
        if self.hitbox.x < 0:
            self.hitbox.x = 0
        if self.hitbox.y > 536:
            self.hitbox.y = 536
        if self.hitbox.y < 0:
            self.hitbox.y = 0

        self.moving = True

#ENEMIES
class Rock:
    def __init__(self, x, y):
        self.hitbox = pygame.Rect(x, y, 64, 64)
        self.die = False
        self.immune = False
        self.last_hit = 0.0

        self.cooldown = 500
        self.last_target = pygame.time.get_ticks()

        self.tx = 50
        self.ty = 50
        self.spd = 12
        self.angle = math.atan2(y-self.ty, x-self.tx)
        self.xv = math.cos(self.angle) * self.spd
        self.yv = math.sin(self.angle) * self.spd

        self.anims = [pygame.image.load('assets/rock_enemy/rock_0.png'),
                      pygame.image.load('assets/rock_enemy/rock_1.png'),
                      pygame.image.load('assets/rock_enemy/rock_2.png'),
                      pygame.image.load('assets/rock_enemy/rock_3.png'),
                      pygame.image.load('assets/rock_enemy/rock_4.png')]
        
        self.dieanim = [pygame.image.load('assets/rock_enemy/rock_die_0.png'),
                        pygame.image.load('assets/rock_enemy/rock_die_1.png'),
                        pygame.image.load('assets/rock_enemy/rock_die_2.png')]

        self.curanim = 0

    def set_target(self):
        self.tx = you.hitbox.centerx
        self.ty = you.hitbox.centery

        self.angle = math.atan2(self.hitbox.y-self.ty, self.hitbox.x-self.tx)
        self.xv = math.cos(self.angle) * self.spd
        self.yv = math.sin(self.angle) * self.spd

    def move(self):
        self.curanim = 0 if self.curanim >= len(self.anims*5) else self.curanim

        now = pygame.time.get_ticks()
        if now - self.last_target >= self.cooldown:
            #moving
            self.hitbox.x -= int(self.xv)
            self.hitbox.y -= int(self.yv)

            if self.hitbox.x > 736 or self.hitbox.x < 1 or self.hitbox.y > 536 or self.hitbox.y < 1:
                self.last_target = now
            
            anim = self.curanim//5

        else:
            #retargeting
            self.set_target()
            anim = 0

        #player damage checks
        if self.hitbox.colliderect(you.hitbox) and self.die == False:
            you.hp -= 1 if you.immune == False else 0
            self.immune = True

            if not you.immune:
                you.immune = True
                you.last_hit = pygame.time.get_ticks()

        #self damage checks
        if type(you.weapons[you.curwep])==Paper_Weapon and self.immune == False:
            if self.hitbox.colliderect(you.weapons[you.curwep].hitbox):
                self.die = True
                self.curanim = 0
        
        #make immunity wear off
        if self.immune:
            now = pygame.time.get_ticks()
            if now - self.last_hit > 2500:
                self.immune = False

        d = self.tx < self.hitbox.x
        display.blit(pygame.transform.scale(pygame.transform.flip(self.anims[anim], d ,False), (64,64)), (self.hitbox.x, self.hitbox.y))

    def main(self, display):
        self.curanim += 1

        if self.die == True:
            anim = self.curanim//10
            display.blit(pygame.transform.scale(pygame.transform.flip(self.dieanim[anim], False ,False), (64,64)), (self.hitbox.x, self.hitbox.y))
                
            if anim == len(self.dieanim)-1:
                #permadie
                global enemies
                global score
                score += 100
                enemies.remove(self)

        else:
            self.move()

class Paper:
    def __init__(self, x, y):
        self.hitbox = pygame.Rect(x,y,32,60)
        self.die = False

        self.tx = 0
        self.ty = 0
        self.spd = 3

        self.angle = math.atan2(y-self.ty, x-self.tx)
        self.xv = math.cos(self.angle) * self.spd
        self.yv = math.sin(self.angle) * self.spd

        self.anims = [pygame.image.load('assets/paper_enemy/paper_0.png'),
                      pygame.image.load('assets/paper_enemy/paper_1.png'),
                      pygame.image.load('assets/paper_enemy/paper_2.png'),
                      pygame.image.load('assets/paper_enemy/paper_1.png')]
        
        self.dieanim = [pygame.image.load('assets/paper_enemy/paper_die_0.png'),
                        pygame.image.load('assets/paper_enemy/paper_die_1.png'),
                        pygame.image.load('assets/paper_enemy/paper_die_2.png')]

        self.curanim = 0
    
    def set_target(self):
        self.tx = you.hitbox.centerx
        self.ty = you.hitbox.centery

        self.angle = math.atan2(self.hitbox.y-self.ty, self.hitbox.x-self.tx)
        self.xv = math.cos(self.angle) * self.spd
        self.yv = math.sin(self.angle) * self.spd

    def move(self, display):
        #pygame.draw.rect(display,(255,0,0), self.hitbox,3)

        self.curanim = 0 if self.curanim >= len(self.anims*5) else self.curanim

        self.set_target()

        self.hitbox.x -= int(self.xv)
        self.hitbox.y -= int(self.yv)
            
        anim = self.curanim//5

        #player damage checks
        if self.hitbox.colliderect(you.hitbox) and self.die == False:
            you.hp -= 1 if you.immune == False else 0
            self.immune = True

            if not you.immune:
                you.immune = True
                you.last_hit = pygame.time.get_ticks()

        #self damage checks
        if type(you.weapons[you.curwep]) == Scissor_Weapon:
            if self.hitbox.colliderect(you.weapons[you.curwep].hitbox):
                self.die = True
                self.curanim = 0

        d = self.tx < self.hitbox.x
        display.blit(pygame.transform.scale(pygame.transform.flip(self.anims[anim], d ,False), (64,64)), (self.hitbox.x-20, self.hitbox.y))

    def main(self, display):
        self.curanim += 1

        if self.die == True:
            anim = self.curanim//10
            display.blit(pygame.transform.scale(pygame.transform.flip(self.dieanim[anim], False ,False), (64,64)), (self.hitbox.x, self.hitbox.y))
                
            if anim == len(self.dieanim)-1:
                #permadie
                global enemies
                global score
                score += 100
                enemies.remove(self)

        else:
            self.move(display)

class Scissors:
    def __init__(self, x, y):
        self.hitbox = pygame.Rect(x,y,48,64)
        self.die = False

        self.tx = 0
        self.ty = 0
        self.spd = 3
        self.set_target()

        self.moveanim = [pygame.image.load('assets/scissors_enemy/scissors_walk_0.png'),
                         pygame.image.load('assets/scissors_enemy/scissors_walk_1.png')]
        
        self.atkanim = [pygame.image.load('assets/scissors_enemy/scissors_walk_1.png'),
                        pygame.image.load('assets/scissors_enemy/scissors_attack_1.png'),
                        pygame.image.load('assets/scissors_enemy/scissors_attack_2.png'),
                        pygame.image.load('assets/scissors_enemy/scissors_walk_1.png'),
                        pygame.image.load('assets/scissors_enemy/scissors_attack_1.png'),
                        pygame.image.load('assets/scissors_enemy/scissors_attack_2.png'),
                        pygame.image.load('assets/scissors_enemy/scissors_walk_1.png')]
        
        self.dieanim = [pygame.image.load('assets/scissors_enemy/scissors_walk_0.png'),
                        pygame.image.load('assets/scissors_enemy/scissors_die_0.png')]

        self.curanim = 0

        self.attacking = False

        self.last_move = 0
        self.dirx = 0
        self.diry = 0

    def attack(self, display):
        #anims
        if self.curanim >= 35:
            self.curanim = 0
            self.attacking = False

        display.blit(pygame.transform.scale(self.atkanim[self.curanim//5], (64,64)), (self.hitbox.x-10, self.hitbox.y))

        #if player in attacking range
        r = 100
        pygame.draw.circle(display, (255,0,0), (self.hitbox.x+22, self.hitbox.y+32), r, 5)

        if not you.immune:
            #attacking player effect
            if math.hypot(abs(self.hitbox.x + 22 - you.hitbox.x), abs(self.hitbox.y + 32 - you.hitbox.y)) < r:
                you.hp -= 1
                you.immune = True
                you.last_hit = pygame.time.get_ticks()

    def set_target(self):
        self.tx = random.randint(10, 730)
        self.ty = random.randint(10, 530)

    def move(self, display):
        self.curanim = 0 if self.curanim >= len(self.moveanim*5) else self.curanim

        dx, dy = self.tx - self.hitbox.x, self.ty - self.hitbox.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.hitbox.x += dx / dist * min(self.spd, dist)
            self.hitbox.y += dy / dist * min(self.spd, dist)
        else:
            self.set_target()
            self.attacking = True

        display.blit(pygame.transform.scale(self.moveanim[self.curanim//5], (64,64)), (self.hitbox.x-10, self.hitbox.y))
    
    def main(self, display):
        self.curanim += 1

        #death checks
        global urbullets
        for b in urbullets:
            if b.hitbox.colliderect(self.hitbox):
                #no bullet piercing
                urbullets.remove(b)
                #die for realsies
                self.curanim = 0 if self.die == False else self.curanim
                self.die = True
            
        if self.die == True:
            if self.curanim == 10:
                global enemies
                global score
                score += 100
                enemies.remove(self)
            else:
                display.blit(pygame.transform.scale(self.dieanim[self.curanim//5], (64,64)), (self.hitbox.x, self.hitbox.y))

        else:
            #actions n stuff
            if self.attacking:
                self.attack(display)
            else:
                self.move(display)

                #time to change directions
                now = pygame.time.get_ticks()
                if now - self.last_move > 2000:
                    self.dirx = random.randint(-1,1)
                    self.diry = random.randint(-1,1)
                    self.last_move = now

def spawn_enemy():
    global enemies
    toadd = random.randint(0,2)

    posx = random.randint(0,1) * 733 + 2#like this so rock enemy can actually move
    posy = random.randint(0,1) * 533 + 2#also like this so rock enemy can actually move

    if toadd == 0:
        enemies.append(Paper(posx, posy))
    if toadd == 1:
        enemies.append(Rock(posx, posy))
    if toadd == 2:
        enemies.append(Scissors(posx, posy))

def replay_prompt():
    #background
    display.fill((200,200,200))

    #score show
    scoretext = my_font.render(f'Score: {score}', False, (0, 0, 0))
    display.blit(scoretext, (300,200))

    #replay button show
    replaytext = my_font.render('Click HERE to play again!', False, (0,0,0))
    display.blit(replaytext, (10,300))
    replayrect = replaytext.get_rect(topleft=(10, 300))

    #quit button show
    quittext = my_font.render('click here to quit :(', False, (0,0,0))
    display.blit(quittext, (400,400))
    quitrect = quittext.get_rect(topleft=(400, 400))

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                    point = pygame.mouse.get_pos()
                    #quit
                    if quitrect.collidepoint(point):
                        pygame.QUIT = True
                        sys.exit()
                    #replay
                    if replayrect.collidepoint(point):
                        game_init()

def game_init():
    global you, urbullets, enemies, score, last_spawn
    you = Player(400,300)
    urbullets = []
    enemies = [Scissors(100,100), Rock(400,400)]
    score = 0
    last_spawn = 0

def gaming():
    global last_spawn
    if you.immune:
        display.fill((200,0,0))
    else:
        display.fill((200,200,200))

    #healthbar
    display.blit(heart, (1,600-32)) if you.hp > 0 else display.blit(notheart, (1,600-32))
    display.blit(heart, (33,600-32)) if you.hp > 1 else display.blit(notheart, (33,600-32))
    display.blit(heart, (65,600-32)) if you.hp > 2 else display.blit(notheart, (65,600-32))

    #current weapon
    display.blit(pygame.transform.scale(weps[you.curwep], (64,64)), (20,500))

    for event in pygame.event.get():
        #so you can actually quit (code will not run without this bit)
        if event.type == pygame.QUIT:
            sys.exit()
            pygame.QUIT

        #activate weapon
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                #try and except incase weapon is paper
                try:
                    you.weapons[you.curwep].attack()
                except:
                    pass
    
    #get player inputs
    keys = pygame.key.get_pressed()
    #movement
    if keys[pygame.K_a]:
        you.move(-1,0)
    if keys[pygame.K_d]:
        you.move(1,0)
    if keys[pygame.K_s]:
        you.move(0,1)
    if keys[pygame.K_w]:
        you.move(0,-1)
    #weapon change
    if keys[pygame.K_1]:
        you.curwep = 0
    if keys[pygame.K_2]:
        you.curwep = 1
    if keys[pygame.K_3]:
        you.curwep = 2
    
    #spawn enemies
    now = pygame.time.get_ticks()
    cooldown = 2000 - score//2 if score < 3001 else 500
    if now - last_spawn > cooldown:
        last_spawn = now
        spawn_enemy()

    #more drawing
    you.main(display)
    
    for b in urbullets:
        b.main(display)
    
    for e in enemies:
        e.main(display)

    #clock.tick(60)#make sure fps is constant
    #pygame.display.update()

#MAIN
game_init()
while True:
    if you.hp < 1:
        replay_prompt()
    else:
        gaming()

    clock.tick(60)#make sure fps is constant
    pygame.display.update()
