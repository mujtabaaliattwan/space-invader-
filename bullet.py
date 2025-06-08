import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y=-8, bullet_type='player'): # bullet_type can be 'player' or 'enemy'
        super().__init__()

        image_path = "images/bullet_player.png" if bullet_type == 'player' else "images/bullet_enemy.png"
        color_fallback = (255,255,255) if bullet_type == 'player' else (255,200,0)

        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print(f"Warning: Bullet image file not found: {image_path}. Using fallback surface.")
            self.image = pygame.Surface([5, 10])
            self.image.fill(color_fallback)
        except pygame.error as e:
            print(f"Warning: Could not load bullet image {image_path} (pygame error): {e}. Using fallback surface.")
            self.image = pygame.Surface([5, 10])
            self.image.fill(color_fallback)

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = speed_y

    def update(self):
        self.rect.y += self.speed_y
        # Kill bullet if it goes off screen (top)
        if self.rect.bottom < 0:
            self.kill()
