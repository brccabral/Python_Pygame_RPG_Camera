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

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2

        # camera box setup
        self.camera_borders = {'left': 200,
                               'right': 200, 'top': 100, 'bottom': 100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size(
        )[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size(
        )[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l, t, w, h)

        # camera speed
        self.keyboard_speed = 5
        self.mouse_speed = 0.4

        # zoom
        self.zoom_scale = 1
        # too large surface can reduce pygame speed
        self.internal_surface_size = (2500, 2500)
        # new surface needs Alpha channel
        self.internal_surface = pygame.Surface(
            self.internal_surface_size, pygame.SRCALPHA)
        # new surface need to have same center as screen
        self.intenal_surface_rect = self.internal_surface.get_rect(
            center=(self.half_width, self.half_height))
        self.internal_surface_size_vector = pygame.math.Vector2(
            self.internal_surface_size)

        # ground
        self.ground_surface = pygame.image.load(
            'graphics/ground.png').convert_alpha()
        self.ground_rect = self.ground_surface.get_rect()

    def center_target_camera(self, target: pygame.sprite.Sprite):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def box_target_camera(self, target: pygame.sprite.Sprite):
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def keyboard_camera_control(self):
        # to use box and keyboard at the same time need to
        # set the camera_rect first, and then the offset
        # the player never leaves the screen, and
        # the camera never moves away from player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.camera_rect.x -= self.keyboard_speed
        if keys[pygame.K_d]:
            self.camera_rect.x += self.keyboard_speed
        if keys[pygame.K_w]:
            self.camera_rect.y -= self.keyboard_speed
        if keys[pygame.K_s]:
            self.camera_rect.y += self.keyboard_speed

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def mouse_camera_control(self):
        # mouse.set_pos() can only be called once per frame
        # so, we need to set conditions not only for all 4 sides,
        # but also for all 4 corners

        mouse = pygame.math.Vector2(pygame.mouse.get_pos())
        mouse_offset_vector = pygame.math.Vector2()

        left_border = self.camera_borders['left']
        top_border = self.camera_borders['top']
        right_border = self.display_surface.get_size(
        )[0] - self.camera_borders['right']
        bottom_border = self.display_surface.get_size(
        )[1] - self.camera_borders['bottom']

        # to check left and right, mouse needs to be between top and bottom
        if top_border < mouse.y < bottom_border:
            # move mouse to the left, moves the map
            if mouse.x < left_border:
                mouse_offset_vector.x = mouse.x - left_border
                pygame.mouse.set_pos((left_border, mouse.y))
            # move mouse to the RIGH, moves the map
            if mouse.x > right_border:
                mouse_offset_vector.x = mouse.x - right_border
                pygame.mouse.set_pos((right_border, mouse.y))
        # check for top corners
        elif mouse.y < top_border:
            # topleft corner
            if mouse.x < left_border:
                mouse_offset_vector = mouse - \
                    pygame.math.Vector2(left_border, top_border)
                pygame.mouse.set_pos((left_border, top_border))
            # top right corner
            if mouse.x > right_border:
                mouse_offset_vector = mouse - \
                    pygame.math.Vector2(right_border, top_border)
                pygame.mouse.set_pos((right_border, top_border))

        # to check top and bottom, mouse needs to be between left and right
        if left_border < mouse.x < right_border:
            # move mouse to the top, moves the map
            if mouse.y < top_border:
                mouse_offset_vector.y = mouse.y - top_border
                pygame.mouse.set_pos((mouse.x, top_border))
            # move mouse to the bottom, moves the map
            if mouse.y > bottom_border:
                mouse_offset_vector.y = mouse.y - bottom_border
                pygame.mouse.set_pos((mouse.x, bottom_border))
        # check for top corners
        elif mouse.y > bottom_border:
            # topleft corner
            if mouse.x < left_border:
                mouse_offset_vector = mouse - \
                    pygame.math.Vector2(left_border, bottom_border)
                pygame.mouse.set_pos((left_border, bottom_border))
            # top right corner
            if mouse.x > right_border:
                mouse_offset_vector = mouse - \
                    pygame.math.Vector2(right_border, bottom_border)
                pygame.mouse.set_pos((right_border, bottom_border))

        self.offset += mouse_offset_vector * self.mouse_speed

    def zoom_keyboard_camera_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.zoom_scale += 0.1
        if keys[pygame.K_e]:
            self.zoom_scale -= 0.1
            if self.zoom_scale < 0:
                self.zoom_scale = 0

    def custom_draw(self, player):

        # self.center_target_camera(player)

        # using box and keyboard at the same time
        # self.box_target_camera(player)
        # self.keyboard_camera_control()

        self.mouse_camera_control()
        self.zoom_keyboard_camera_control()

        # draw everything on internal surface,
        # scale the internal surface with zoom
        # and then draw scaled surface on screen
        self.internal_surface.fill('#71ddee')

        # ground - draw it first
        ground_offset = self.ground_rect.topleft - self.offset
        self.internal_surface.blit(self.ground_surface, ground_offset)

        # active elements - draw after background stuff
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.internal_surface.blit(sprite.image, offset_pos)

        scaled_surface = pygame.transform.scale(
            self.internal_surface, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surface.get_rect(
            center=(self.half_width, self.half_height))
        self.display_surface.blit(scaled_surface, scaled_rect)
        # box_rect = pygame.Rect(self.camera_rect.left - self.offset.x, self.camera_rect.top -
        #                        self.offset.y, self.camera_rect.width, self.camera_rect.height)
        # pygame.draw.rect(self.display_surface, 'yellow', box_rect, 5)


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# grab mouse to keep it inside Pygame window
# this is used to avoid mouse going to fast outside the window
pygame.event.set_grab(True)

# setup
camera_group = CameraGroup()
player = Player((640, 360), camera_group)

for i in range(20):
    random_x = randint(1000, 2000)
    random_y = randint(1000, 2000)
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

        if event.type == pygame.MOUSEWHEEL:
            camera_group.zoom_scale += event.y * 0.03
            if camera_group.zoom_scale < 0:
                camera_group.zoom_scale = 0

    screen.fill('#71ddee')

    camera_group.update()
    camera_group.custom_draw(player)

    pygame.display.update()
    clock.tick(60)
