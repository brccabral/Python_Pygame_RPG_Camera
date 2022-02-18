import pygame
import sys
from random import randint


class Tree(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('graphics/tree.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # ground
        self.ground_surface = pygame.image.load(
            'graphics/ground.png').convert_alpha()
        self.ground_rect = self.ground_surface.get_rect()

    def custom_draw(self):

        # ground - draw it first
        self.display_surface.blit(self.ground_surface, self.ground_rect)

        # active elements - draw after background stuff
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            self.display_surface.blit(sprite.image, sprite.rect)


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# setup
camera_group = CameraGroup()
player = Player((640, 360), camera_group)

for i in range(20):
    random_x = randint(0, 1000)
    random_y = randint(0, 1000)
    Tree((random_x, random_y), camera_group)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.fill('#71ddee')

    camera_group.update()
    camera_group.custom_draw()

    pygame.display.update()
    clock.tick(60)
