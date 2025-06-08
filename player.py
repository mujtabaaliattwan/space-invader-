import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        image_path = "images/player.png"
        try:
            # Load the base image for the player
            self.image_orig = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print(f"Warning: Player image file not found: {image_path}. Using fallback surface.")
            self.image_orig = pygame.Surface([50, 30])
            self.image_orig.fill((0, 255, 0)) # Green fallback
        except pygame.error as e:
            print(f"Warning: Could not load player image {image_path} (pygame error): {e}. Using fallback surface.")
            self.image_orig = pygame.Surface([50, 30])
            self.image_orig.fill((0, 255, 0)) # Green fallback

        self.image = self.image_orig.copy() # self.image is what's drawn
        self.rect = self.image.get_rect()
        self.rect.x = (screen_width - self.rect.width) // 2
        self.rect.y = screen_height - self.rect.height - 10  # Position at the bottom
        self.screen_width = screen_width
        self.speed = 5

        # Shooting cooldown attributes
        self.shoot_cooldown_base = 500 # Milliseconds
        self.shoot_cooldown_current = self.shoot_cooldown_base
        self.last_shot_time = 0

        # Power-up attributes
        self.active_powerups = {} # e.g. {'rapid_fire': expiry_time, 'shield': expiry_time}
        self.is_shielded = False


    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_cooldown_current:
            self.last_shot_time = now
            from bullet import Bullet
            return Bullet(self.rect.centerx, self.rect.top, bullet_type='player')
        return None

    def activate_powerup(self, type):
        from powerup import POWERUP_SETTINGS # Import here to access settings
        if type in POWERUP_SETTINGS:
            duration = POWERUP_SETTINGS[type]['duration']
            self.active_powerups[type] = pygame.time.get_ticks() + duration
            print(f"Activated {type} for {duration/1000}s")

            if type == 'rapid_fire':
                self.shoot_cooldown_current = self.shoot_cooldown_base * POWERUP_SETTINGS[type]['cooldown_reduction']
            elif type == 'shield':
                self.is_shielded = True
                self.apply_shield_visual()

    def apply_shield_visual(self):
        self.image = self.image_orig.copy()
        # Apply a simple tint;
        shield_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        shield_overlay.fill((70, 70, 180, 120)) # Bluish, semi-transparent
        self.image.blit(shield_overlay, (0,0))


    def remove_shield_visual(self):
        # Only copy if it's not already the original (e.g. if no shield was ever active)
        if self.image is not self.image_orig:
            self.image = self.image_orig.copy()

    def update_powerups(self):
        now = pygame.time.get_ticks()
        # Check for expired power-ups
        expired_powerups = [type for type, expiry_time in self.active_powerups.items() if now > expiry_time]
        for type in expired_powerups:
            print(f"Deactivated {type}")
            del self.active_powerups[type]
            if type == 'rapid_fire':
                self.shoot_cooldown_current = self.shoot_cooldown_base
            elif type == 'shield':
                self.is_shielded = False
                self.remove_shield_visual()

    def update(self, keys):
        self.update_powerups()

        # Ensure shield visual is active if shield is on, and removed if shield was consumed (not by timeout)
        if self.is_shielded and 'shield' in self.active_powerups:
            # This might be redundant if apply_shield_visual is robust, but ensures it if image is manipulated elsewhere
            self.apply_shield_visual()
        elif not self.is_shielded and 'shield' not in self.active_powerups: # Shield is off (either expired or consumed)
            # This check ensures that if shield was consumed (is_shielded = False by main.py)
            # and also not in active_powerups (expired), visual is removed.
            # If shield was consumed, main.py sets is_shielded to False.
            # update_powerups() would remove it from active_powerups if it timed out.
            self.remove_shield_visual()


        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Keep player within screen bounds
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > self.screen_width - self.rect.width:
            self.rect.x = self.screen_width - self.rect.width
