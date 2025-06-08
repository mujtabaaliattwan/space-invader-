import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size_str='medium'):
        super().__init__()
        self.center = center
        self.size_str = size_str

        if self.size_str == 'small':
            self.max_radius = 20
            self.duration = 200 # ms
        elif self.size_str == 'large':
            self.max_radius = 60
            self.duration = 500 # ms
        else: # medium
            self.max_radius = 40
            self.duration = 300 # ms

        self.spawn_time = pygame.time.get_ticks()
        self.current_radius = 0

        # Create initial image and rect. This will be updated.
        # Image needs to be large enough for max_radius.
        self.image = pygame.Surface([self.max_radius * 2, self.max_radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.center)
        self.update_image()

    def update_image(self):
        self.image.fill((0,0,0,0)) # Transparent
        progress = (pygame.time.get_ticks() - self.spawn_time) / self.duration

        if progress >= 1.0:
            self.current_radius = self.max_radius
        else:
            # Radius grows quickly then slows (ease-out effect)
            self.current_radius = int(self.max_radius * (1 - (1 - progress)**3))

        # Alpha fades out over duration
        alpha = int(255 * (1 - progress))
        if alpha < 0: alpha = 0

        color = (255, 150, 0, alpha) # Orange-yellow, fading out

        if self.current_radius > 0 :
             pygame.draw.circle(self.image, color,
                               (self.max_radius, self.max_radius), # center of the surface
                               self.current_radius)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.duration:
            self.kill()
        else:
            self.update_image()
            # Update rect to ensure it's centered if size changes (though radius changes on fixed surface here)
            self.rect = self.image.get_rect(center=self.center)
