import pygame
import random
from bullet import Bullet # Import Bullet class

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, speed=2, shoot_chance=0.002):
        super().__init__()
        try:
            self.image_orig = pygame.image.load("images/enemy1.png").convert_alpha()
        except pygame.error as e:
            print(f"Warning: Could not load images/enemy1.png: {e}. Using fallback.")
            self.image_orig = pygame.Surface([35, 25])
            self.image_orig.fill((255, 0, 0)) # Red fallback
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.screen_width = screen_width
        self.speed = speed
        self.direction = 1  # 1 for right, -1 for left
        self.shoot_chance = shoot_chance

    def shoot(self):
        # Enemy shoots downwards
        return Bullet(self.rect.centerx, self.rect.bottom, speed_y=5, bullet_type='enemy')

    def hit(self):
        """Called when the enemy is hit by a bullet."""
        self.kill() # Default behavior: kill on one hit

    def update(self):
        self.rect.x += self.speed * self.direction

        # Basic side-to-side movement: reverse direction at screen edges
        if self.rect.right > self.screen_width or self.rect.left < 0:
            self.direction *= -1
            self.rect.y += self.rect.height + 5 # Move down when changing direction (optional)

        # Randomly shoot
        # This will be checked in main.py to add bullet to groups
        # For now, this method just decides if a shot should be made
        # and returns a bullet object if so.
        if random.random() < self.shoot_chance:
            return self.shoot()
        return None

class FastEnemy(Enemy):
    def __init__(self, x, y, screen_width, speed_override=None, shoot_chance_override=None):
        # FastEnemy has its own defaults if overrides are not provided
        default_speed = 4
        default_shoot_chance = 0.003

        current_speed = speed_override if speed_override is not None else default_speed
        current_shoot_chance = shoot_chance_override if shoot_chance_override is not None else default_shoot_chance

        super().__init__(x, y, screen_width, speed=current_speed, shoot_chance=current_shoot_chance)
        try:
            self.image_orig = pygame.image.load("images/enemy2.png").convert_alpha()
        except pygame.error as e:
            print(f"Warning: Could not load images/enemy2.png for FastEnemy: {e}. Using fallback.")
            self.image_orig = pygame.Surface([35, 25]) # Fallback size
            self.image_orig.fill((255, 100, 0)) # Brighter Red/Orange fallback
        self.image = self.image_orig.copy()
        # self.speed and self.shoot_chance are set by super() call. Rect needs to be updated if size changes.
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))


class StrongEnemy(Enemy):
    def __init__(self, x, y, screen_width, speed_override=None, shoot_chance_override=None):
        # StrongEnemy defaults to base Enemy stats if overrides not provided
        default_speed = 2
        default_shoot_chance = 0.002

        current_speed = speed_override if speed_override is not None else default_speed
        current_shoot_chance = shoot_chance_override if shoot_chance_override is not None else default_shoot_chance

        super().__init__(x, y, screen_width, speed=current_speed, shoot_chance=current_shoot_chance)
        try:
            self.image_orig = pygame.image.load("images/enemy3.png").convert_alpha()
        except pygame.error as e:
            print(f"Warning: Could not load images/enemy3.png for StrongEnemy: {e}. Using fallback.")
            self.image_orig = pygame.Surface([40, 30]) # Slightly larger fallback
            self.image_orig.fill((200, 0, 0)) # Darker Red fallback
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) # Update rect if size changed

        self.health = 3
        self.hit_flash_timer = 0 # For timed flash effect

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            # Visual feedback for hit: flash
            self.image = self.image_orig.copy() # Revert to original before applying tint
            self.image.fill((200,100,100, 120), special_flags=pygame.BLEND_RGBA_ADD) # Reddish tint
            self.hit_flash_timer = 3 # Flash for 3 frames (same as Boss)

    def update(self):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            if self.hit_flash_timer == 0:
                self.image = self.image_orig.copy() # Revert to original image
        # Potentially different movement or shooting pattern for strong enemy
        return super().update() # Use base class update for now

class BossEnemy(Enemy):
    def __init__(self, x, y, screen_width, speed_override=None, shoot_chance_override=None):
        # Boss has its own defaults
        default_speed = 1
        default_shoot_chance = 0.02

        current_speed = speed_override if speed_override is not None else default_speed
        current_shoot_chance = shoot_chance_override if shoot_chance_override is not None else default_shoot_chance

        super().__init__(x, y, screen_width, speed=current_speed, shoot_chance=current_shoot_chance)
        try:
            self.image_orig = pygame.image.load("images/boss.png").convert_alpha()
        except pygame.error as e:
            print(f"Warning: Could not load images/boss.png: {e}. Using fallback.")
            self.image_orig = pygame.Surface([100,70])
            self.image_orig.fill((150,0,150)) # Purple fallback
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(centerx=x, top=y)

        self.health = 20
        self.hit_flash_timer = 0 # For timed flash effect

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
            print("Boss Defeated!")
        else:
            # Visual feedback for hit: flash
            self.image = self.image_orig.copy() # Revert to original before applying tint
            self.image.fill((200,50,50, 150), special_flags=pygame.BLEND_RGBA_ADD) # Red tint
            self.hit_flash_timer = 3 # Flash for 3 frames
            print(f"Boss health: {self.health}")

    def update(self):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            if self.hit_flash_timer == 0:
                self.image = self.image_orig.copy() # Revert to original image

        # Boss specific movement (e.g. slow side to side, stop and shoot)
        # For now, same as base enemy but slower
        self.rect.x += self.speed * self.direction
        if self.rect.right > self.screen_width - 50 or self.rect.left < 50: # Keep some margin
            self.direction *= -1
            # No y-axis movement for now, keeps it simpler

        # Boss specific shooting pattern
        if random.random() < self.shoot_chance:
            # Could return a list of bullets for special attacks (e.g., spread shot)
            # For now, single bullet like other enemies, but more frequent
            return self.shoot()
        return None
