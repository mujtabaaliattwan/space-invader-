import pygame
import random

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center_pos, type):
        super().__init__()
        self.type = type

        image_name = None
        fallback_color = (200, 200, 200) # Default fallback color

        if self.type == 'rapid_fire':
            image_name = "images/powerup_rapidfire.png"
            fallback_color = (0, 255, 255)  # Cyan for rapid fire
        elif self.type == 'shield':
            image_name = "images/powerup_shield.png"
            fallback_color = (0, 0, 255) # Blue for shield
        # Add more types later if needed

        if image_name:
            try:
                self.image = pygame.image.load(image_name).convert_alpha()
            except FileNotFoundError:
                print(f"Warning: PowerUp image file not found: {image_name}. Using fallback surface.")
                self.image = pygame.Surface([20, 20])
                self.image.fill(fallback_color)
            except pygame.error as e:
                print(f"Warning: Could not load PowerUp image {image_name} (pygame error): {e}. Using fallback surface.")
                self.image = pygame.Surface([20, 20])
                self.image.fill(fallback_color)
        else:
            # This case handles if a type is passed that doesn't have a defined image_name
            print(f"Warning: No image_name for PowerUp type '{self.type}'. Using fallback surface.")
            self.image = pygame.Surface([20, 20])
            self.image.fill(fallback_color)

        self.rect = self.image.get_rect(center=center_pos)
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 10000 # Power-up disappears after 10 seconds if not collected
        self.speed_y = 2 # Power-ups slowly fall down

    def update(self):
        self.rect.y += self.speed_y
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.kill()
        if self.rect.top > pygame.display.get_surface().get_height(): # If it falls off screen
            self.kill()

# Example specific power-up related data (could be expanded)
POWERUP_SETTINGS = {
    'rapid_fire': {'duration': 5000, 'cooldown_reduction': 0.5}, # 5 seconds, halves cooldown
    'shield': {'duration': 10000} # 10 seconds of shield
}
