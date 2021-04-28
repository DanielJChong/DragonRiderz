import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 1000, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DragonRiderz")

# Load images
# Player 
DRAKE = pygame.image.load(os.path.join("img", "purple_dragon.png"))
# Enemies
ENEMY_DRAKE = pygame.image.load(os.path.join("img", "enemy_dragon.png"))
BLUE_DRAKE = pygame.image.load(os.path.join("img", "blue_dragon.png"))
RED_DRAKE = pygame.image.load(os.path.join("img", "red_dragon.png"))

#Fireballs
FIREBALL = pygame.image.load(os.path.join("img", "fireball.png"))

#Enemy Fireballs
BLUE_FIREBALL = pygame.image.load(os.path.join("img", "enemy_fireball.png"))

#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("img", "sky_background.png")), (WIDTH, HEIGHT))


#class for all drakes
class Drake:
    COOLDOWN = 30
    
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.drake_img = None
        self.fireball_img = None
        self.fireballs = []
        self.cool_down_counter = 0

    def draw(self, window):
        # pygame.draw.rect(window, (202, 44, 146), (self.x, self.y, 50,50))
        window.blit(self.drake_img, (self.x, self.y))
        for fireball in self.fireballs:
            fireball.draw(window)

    def move_fireballs(self, vel, obj):
        self.cooldown()
        for fireball in self.fireballs:
            fireball.move(vel)
            if fireball.off_screen(HEIGHT):
                self.fireballs.remove(fireball)
            elif fireball.collision(obj):
                obj.health -= 10  #if enemy fireball hits player, health goes down by 10
                self.fireballs.remove(fireball)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            fireball = Fireball(self.x, self.y, self.fireball_img)
            self.fireballs.append(fireball)
            self.cool_down_counter = 1

    def get_width(self):
        return self.drake_img.get_width()

    def get_height(self):
        return self.drake_img.get_height()


#class for player that inherits player qualities
class Player(Drake):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.drake_img = DRAKE
        self.fireball_img = FIREBALL
        self.mask = pygame.mask.from_surface(self.drake_img)
        self.max_health = health
#controll where fireballs from player comes from and other aspects of fireballs
    def shoot(self):
        if self.cool_down_counter == 0:
            fireball = Fireball(self.x+45, self.y, self.fireball_img)
            self.fireballs.append(fireball)
            self.cool_down_counter = 1

    def move_fireballs(self, vel, objs):
        self.cooldown()
        for fireball in self.fireballs:
            fireball.move(vel)
            if fireball.off_screen(HEIGHT):
                self.fireballs.remove(fireball)
            else:
                for obj in objs:
                    if fireball.collision(obj):
                        objs.remove(obj)
                        self.fireballs.remove(fireball)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
#healthbar for player's drake
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.drake_img.get_height() + 10, self.drake_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.drake_img.get_height() + 10, self.drake_img.get_width() * (self.health/self.max_health), 10))


#class for enemy drakes
class Enemy(Drake):
    COLOR_MAP = {
        "red": (RED_DRAKE, BLUE_FIREBALL),
        "green": (ENEMY_DRAKE, BLUE_FIREBALL),
        "blue": (BLUE_DRAKE, BLUE_FIREBALL),
    }

    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health)
        self.drake_img, self.fireball_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.drake_img)

    def move(self, vel):
        self.y += vel
#controll where fireballs from enemy comes from and other aspects of fireballs
    def shoot(self):
        if self.cool_down_counter == 0:
            fireball = Fireball(self.x+35, self.y, self.fireball_img)
            self.fireballs.append(fireball)
            self.cool_down_counter = 1


#class for fireballs
class Fireball:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


#how game reads object collision such as fireballs hitting player drake
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



#main info
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
#what font and size of font
    main_font = pygame.font.SysFont("comicsans", 50)
#what font for game over screen
    lost_font = pygame.font.SysFont("comicsans", 70)
#store where enemies are
    enemies = []
    wave_length = 5
    enemy_vel = 1
#speed of player movement
    player_vel = 5
#speed of fireball movement
    fireball_vel = 5
#where player location starts 
    player = Player(450, 700)

    clock = pygame.time.Clock()
#defining game over
    lost = False
    lost_count = 0


#drawing everything on the screen
    def redraw_window():
        WIN.blit(BG, (0,0))
#draw text for lives and level
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,255,0))
        level_label = main_font.render(f"Level: {level}", 1, (0,0,0))
#where on screen lives and level is displayed
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
#draw enemies
        for enemy in enemies:
            enemy.draw(WIN)
#drawing player
        player.draw(WIN)
#when game over, what happens
        if lost:
            lost_label = lost_font.render("You Lost!! Game Over!!", 1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 550))

        pygame.display.update()


    while run:
        clock.tick(FPS)

        redraw_window()

#if player health goes down to 0, you lose a life
        if player.health <= 0:
            lives -= 1
            player.health == 100
#if player lives reach 0, game over
        if lives <= 0:
            lost = True
            lost_count += 1
#this is what happens when game over (show game over message for 8 secs and exit)
        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                continue

#how enemies spawn randomly and how levels go up
        if len(enemies) == 0:
            level += 1
#how many enemies spawn
            wave_length += 8
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
#how to quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
#moving the player            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  #left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:  #right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  #up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < HEIGHT:  #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_fireballs(fireball_vel, player)

            if random.randrange(0, 1*60) == 1: #how often enemy shoots
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)

        player.move_fireballs(-fireball_vel, enemies)


#main menu
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title = title_font.render("DragonRiderz", 1, (185,59,217))
        WIN.blit(title, (WIDTH/2 - title.get_width()/2, 200))
        title_label = title_font.render("Press the mouse to begin...", 1, (0,0,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
