from pygame import *
import random
from random import randint


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (80, 80))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
    
class Player(GameSprite):
    def __init__(self, image_path, x, y, speed):
        super().__init__(image_path, x, y, speed)
        self.speed = speed
        self.last_shot = 0
        self.shots_fired = 0
        self.reloading = False
        self.reload_start_time = 0

    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < 1190 - self.rect.width:
            self.rect.x += self.speed
        if keys[K_SPACE]:
            self.fire()
    
    def fire(self):
        global ammo
        current_time = time.get_ticks()

        if self.reloading:
            if current_time - self.reload_start_time >= 5000:
                self.reloading = False
                self.shots_fired = 0
            else:
                return

        if current_time - self.last_shot > 300 and ammo > 0:
            bullet = Bullet('bullet.png', self.rect.centerx, self.rect.top, -5)
            bullets.add(bullet)

            firel = mixer.Sound('fire.ogg')
            firel.play()

            self.last_shot = current_time
            self.shots_fired += 1
            ammo -= 1

            if self.shots_fired >= 10:
                self.reloading = True
                self.reload_start_time = current_time

class Enemy(GameSprite):
    def __init__(self, image_path, x, y, speed):
        super().__init__(image_path, x, y, speed)

    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > 900:
            self.rect.y = 0
            self.rect.x = randint(80, 1120)
            lost = lost + 1

class Bullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.image = transform.scale(image.load(player_image), (10, 20))
    def update(self):
        self.rect.y += self.speed
        global win
        if self.rect.y < 0:
            self.kill()
        if sprite.groupcollide(monsters, bullets, True, True):
            win += 1
            monster1 = Enemy('ufo.png', randint(80, 1120), 0, randint(1, 4))
            monsters.add(monster1)
        if sprite.groupcollide(asteroids, bullets, True, True):
            win += 1
            asteroid1 = Asteroid('asteroid.png', randint(80, 1120), 0, randint(1, 4))
            asteroids.add(asteroid1)

class Asteroid(GameSprite):
    def __init__(self, image_path, x, y, speed):
        super().__init__(image_path, x, y, speed)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > 900:
            self.rect.y = 0
            self.rect.x = randint(80, 1120)

monsters = sprite.Group()
for _ in range(7):
    monster = Enemy('ufo.png', randint(80, 1120), 0, randint(1, 4))
    monsters.add(monster)

bullets = sprite.Group()

asteroids = sprite.Group()
for _ in range(3):
    asteroid = Asteroid('asteroid.png', randint(80, 1120), 0, randint(1, 4))
    asteroids.add(asteroid)

backgrounds = [
    'galaxy-night-panoramic.jpg',
    'galaxy-space-scene.jpg',
    'galaxy-night-view.jpg',
    'galaxy-background-with-fictional-planets.jpg'
]
fon = random.choice(backgrounds)

window = display.set_mode((1200, 900))
display.set_caption('Супер мега крутое название')
background = transform.scale(image.load(fon), (1200, 900))

mixer.init()
mixer.music.load('Galactic-Rap.ogg')
mixer.music.set_volume(0.05)
mixer.music.play()

player = Player('rocket.png', 600, 750, 10)

run = True
finish = False
clock = time.Clock()
FPS = 60
lost = 0
win = 0
ammo = 70  # общее количество патронов

font.init()
font1 = font.Font(None, 36)
font2 = font.Font(None, 36)
font3 = font.Font(None, 128)
lose = font3.render('YOU LOSE', True,(255,0,0))
winner = font3.render('YOU WIN', True,(124,252,0))
font = font.SysFont('Arial', 40)
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                player.fire() 

    if not finish:
        text_lose = font1.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        text_win = font2.render("Повержено: " + str(win), 1, (255, 255, 255))
        text_ammo = font2.render("Патроны: " + str(ammo), 1, (255, 255, 255))

        clock.tick(FPS)
        window.blit(background, (0, 0))
        window.blit(text_lose, (10, 40))
        window.blit(text_win, (10, 10))
        window.blit(text_ammo, (10, 70))

        player.reset()
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        player.update()
        monsters.update()
        bullets.update()
        asteroids.update()

        if lost >= 10 or sprite.spritecollide(player, monsters, False) or sprite.spritecollide(player, asteroids, False):
            finish = True
            window.blit(lose, (400, 400))
        elif win >= 20:
            finish = True
            window.blit(winner, (400, 400))

        display.update()
