import pygame
from player import Player
from enemy import Enemy, FastEnemy, StrongEnemy, BossEnemy
from bullet import Bullet
from powerup import PowerUp, POWERUP_SETTINGS
from effects import Explosion
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders - The Clone Wars")

# Game States
MENU = 0
PLAYING = 1
GAME_OVER_SCREEN = 2
game_state = MENU
game_over_internal_flag = False # Internal flag for game over condition

# Sound Effects
sound_files = {
    "player_shoot": "sounds/player_shoot.wav",
    "enemy_shoot": "sounds/enemy_shoot.wav",
    "enemy_explode": "sounds/enemy_explode.wav",
    "player_explode": "sounds/player_explode.wav",
    "powerup_collect": "sounds/powerup_collect.wav",
    "boss_hit": "sounds/boss_hit.wav",
    "game_over": "sounds/game_over.wav"
}
sounds = {}
for name, path in sound_files.items():
    try:
        sounds[name] = pygame.mixer.Sound(path)
    except FileNotFoundError:
        print(f"Warning: Sound file not found: {path}. '{name}' sound will be disabled.")
        sounds[name] = None
    except pygame.error as e: # Catch other pygame specific errors e.g. format issues
        print(f"Warning: Could not load sound file {path} (pygame error): {e}. '{name}' sound will be disabled.")
        sounds[name] = None


# Background Music
music_loaded = False
try:
    # Attempt to load .wav first as per file creation plan, then .ogg as original fallback
    pygame.mixer.music.load("sounds/background_music.wav")
    music_loaded = True
except pygame.error as e_wav:
    print(f"Warning: 'sounds/background_music.wav' could not be loaded: {e_wav}. Trying .ogg.")
    try:
        pygame.mixer.music.load("music/background_music.ogg") # Original fallback path
        music_loaded = True
    except pygame.error as e_ogg:
        print(f"Warning: Background music 'music/background_music.ogg' also could not be loaded: {e_ogg}")

if music_loaded:
    pygame.mixer.music.play(-1)

# Font
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y, color=(255,255,255)):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x,y))
    surf.blit(text_surface, text_rect)

# Global game variables (will be reset in reset_game_state)
player = None
all_sprites = None
enemies = None
player_bullets = None
enemy_bullets = None
powerups_group = None
score = 0
player_lives = 0
wave_number = 0
boss_battle_active = False
boss_spawned = False
base_enemy_count = 8
BOSS_SPAWN_SCORE_THRESHOLD = 50
boss_defeat_score_bonus = 100

# --- Reset Game Function ---
def reset_game_state_vars():
    global player, all_sprites, enemies, player_bullets, enemy_bullets, powerups_group
    global score, player_lives, wave_number, boss_battle_active, boss_spawned, game_over_internal_flag

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups_group = pygame.sprite.Group()

    player = Player(screen_width, screen_height)
    all_sprites.add(player)

    score = 0
    player_lives = 3
    wave_number = 1
    boss_battle_active = False
    boss_spawned = False
    game_over_internal_flag = False

    spawn_new_wave()

# --- Spawn New Wave Function ---
def spawn_new_wave():
    global wave_number
    print(f"Spawning wave {wave_number}.")
    number_of_enemies = base_enemy_count + (wave_number -1) * 2

    speed_multiplier = min(1 + (wave_number - 1) * 0.1, 2.5)
    shoot_chance_multiplier = min(1 + (wave_number - 1) * 0.05, 2.0)

    for i in range(number_of_enemies):
        if boss_battle_active: continue
        enemy_type_choice = random.choice([Enemy, FastEnemy, StrongEnemy])

        default_speed, default_shoot_chance = 2, 0.002
        if enemy_type_choice == FastEnemy: default_speed, default_shoot_chance = 4, 0.003
        elif enemy_type_choice == StrongEnemy: default_speed, default_shoot_chance = 2, 0.002

        current_speed = default_speed * speed_multiplier
        current_shoot_chance = default_shoot_chance * shoot_chance_multiplier

        x_pos = 50 + (i % 10) * 70; y_pos = 50 + (i // 10) * 50
        enemy = enemy_type_choice(x=x_pos, y=y_pos, screen_width=screen_width,
                                  speed_override=current_speed, shoot_chance_override=current_shoot_chance)
        all_sprites.add(enemy); enemies.add(enemy)

# --- Menu Screen Function ---
def show_menu_screen():
    global game_state, running

    screen.fill((0,0,20))
    draw_text(screen, "SPACE INVADERS: THE CLONE WARS", 40, screen_width / 2, screen_height / 5)

    start_button_rect = pygame.Rect(screen_width/2 - 120, screen_height/2 - 60, 240, 50)
    quit_button_rect = pygame.Rect(screen_width/2 - 120, screen_height/2 + 10, 240, 50)

    button_color = (0, 100, 0); hover_color = (0,180,0)
    quit_button_color = (100,0,0); quit_hover_color = (180,0,0)

    mx, my = pygame.mouse.get_pos()

    if start_button_rect.collidepoint((mx,my)): pygame.draw.rect(screen, hover_color, start_button_rect, border_radius=5)
    else: pygame.draw.rect(screen, button_color, start_button_rect, border_radius=5)
    draw_text(screen, "Start Game", 28, start_button_rect.centerx, start_button_rect.centery)

    if quit_button_rect.collidepoint((mx,my)): pygame.draw.rect(screen, quit_hover_color, quit_button_rect, border_radius=5)
    else: pygame.draw.rect(screen, quit_button_color, quit_button_rect, border_radius=5)
    draw_text(screen, "Quit", 28, quit_button_rect.centerx, quit_button_rect.centery)

    draw_text(screen, "Arrows to move, Space to shoot", 20, screen_width / 2, screen_height * 0.70)
    draw_text(screen, "Destroy all enemies and the boss!", 20, screen_width / 2, screen_height * 0.75)
    draw_text(screen, "Collect power-ups for an advantage.", 20, screen_width/2, screen_height*0.80)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_button_rect.collidepoint(event.pos):
                reset_game_state_vars(); game_state = PLAYING
            elif quit_button_rect.collidepoint(event.pos): running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                 reset_game_state_vars(); game_state = PLAYING
            if event.key == pygame.K_ESCAPE: running = False

# --- Game Over Screen Function ---
def show_game_over_screen():
    global game_state, running

    screen.fill((20,0,0)) # Dark Red background
    draw_text(screen, "GAME OVER", 70, screen_width/2, screen_height/4, color=(200,0,0))
    draw_text(screen, f"Final Score: {score}", 45, screen_width/2, screen_height/2 - 50)

    play_again_rect = pygame.Rect(screen_width/2 - 120, screen_height/2 + 20, 240, 50)
    menu_button_rect = pygame.Rect(screen_width/2 - 120, screen_height/2 + 80, 240, 50) # Back to Menu
    # quit_button_rect = pygame.Rect(screen_width/2 - 120, screen_height/2 + 140, 240, 50) # Optional Quit

    button_color = (80, 80, 0) # Dark Yellow
    hover_color = (150, 150, 0) # Brighter Yellow

    mx, my = pygame.mouse.get_pos()

    # Play Again Button
    if play_again_rect.collidepoint((mx,my)): pygame.draw.rect(screen, hover_color, play_again_rect, border_radius=5)
    else: pygame.draw.rect(screen, button_color, play_again_rect, border_radius=5)
    draw_text(screen, "Play Again", 28, play_again_rect.centerx, play_again_rect.centery)

    # Main Menu Button
    if menu_button_rect.collidepoint((mx,my)): pygame.draw.rect(screen, hover_color, menu_button_rect, border_radius=5)
    else: pygame.draw.rect(screen, button_color, menu_button_rect, border_radius=5)
    draw_text(screen, "Main Menu", 28, menu_button_rect.centerx, menu_button_rect.centery)

    draw_text(screen, "Press ESC to Quit", 20, screen_width/2, screen_height * 0.85)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if play_again_rect.collidepoint(event.pos):
                reset_game_state_vars()
                game_state = PLAYING
            elif menu_button_rect.collidepoint(event.pos):
                game_state = MENU
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: # Play Again on Enter
                reset_game_state_vars()
                game_state = PLAYING
            if event.key == pygame.K_ESCAPE: # Quit on Escape
                running = False
            if event.key == pygame.K_m: # Back to menu on M
                game_state = MENU


# --- Main Game Loop ---
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000.0

    if game_state == MENU:
        show_menu_screen()

    elif game_state == PLAYING:
        if game_over_internal_flag:
            game_state = GAME_OVER_SCREEN
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.alive():
                        p_bullet = player.shoot()
                if p_bullet:
                    all_sprites.add(p_bullet); player_bullets.add(p_bullet)
                    if sounds.get("player_shoot"): sounds["player_shoot"].play()
                elif event.key == pygame.K_ESCAPE: game_state = MENU

        keys = pygame.key.get_pressed()
        if player.alive(): player.update(keys)

        for enemy_sprite in list(enemies):
            e_bullet = enemy_sprite.update()
            if e_bullet:
                all_sprites.add(e_bullet); enemy_bullets.add(e_bullet)
                if sounds.get("enemy_shoot"): sounds["enemy_shoot"].play()

        hit_enemies_dict = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for enemy_hit, bullets_that_hit in hit_enemies_dict.items():
            for _ in bullets_that_hit:
                enemy_hit.hit() # hit() method handles health decrease and self.kill()
                if isinstance(enemy_hit, BossEnemy) and enemy_hit.alive(): # Boss was hit but not killed
                    if sounds.get("boss_hit"): sounds["boss_hit"].play()

                if not enemy_hit.alive():
                    score += 10
                    if sounds.get("enemy_explode"): sounds["enemy_explode"].play()
                    expl_size = 'large' if isinstance(enemy_hit, BossEnemy) else 'medium'
                    all_sprites.add(Explosion(enemy_hit.rect.center, expl_size))
                    if isinstance(enemy_hit, BossEnemy): # Boss was defeated by this hit
                        boss_battle_active = False; score += boss_defeat_score_bonus; print("Boss defeated!")
                        # Enemy explode sound already played. Could have a specific boss_defeat_sound.
                    elif not boss_battle_active and random.random() < 0.15:
                        powerup_type = random.choice(['rapid_fire', 'shield'])
                        new_powerup = PowerUp(enemy_hit.rect.center, powerup_type)
                        all_sprites.add(new_powerup); powerups_group.add(new_powerup)
                        print(f"Spawned {powerup_type} powerup")

        if not boss_battle_active and not boss_spawned and score >= (BOSS_SPAWN_SCORE_THRESHOLD * wave_number):
            boss_battle_active = True; boss_spawned = True
            for es in list(enemies):
                if not isinstance(es, BossEnemy): es.kill()
            boss_s = 1 + (wave_number-1)*0.2; boss_sc = 0.02 + (wave_number-1)*0.005
            boss = BossEnemy(screen_width//2, 50, screen_width, speed_override=boss_s, shoot_chance_override=boss_sc)
            all_sprites.add(boss); enemies.add(boss); print("Boss incoming!")

        coll_powerups = pygame.sprite.spritecollide(player, powerups_group, True)
        for pu in coll_powerups:
            player.activate_powerup(pu.type)
            if sounds.get("powerup_collect"): sounds["powerup_collect"].play()

        if player.alive():
            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                if player.is_shielded: player.is_shielded = False; player.remove_shield_visual(); print("Shield absorbed bullet!")
                else: player_lives -= 1
            # Corrected: Enemy collision should also decrement lives by number of enemies hit if that's the design
            # For now, it's one life per colliding enemy because the enemy is killed.
            colliding_enemies_direct = pygame.sprite.spritecollide(player, enemies, True)
            if colliding_enemies_direct: # Enemies themselves collide
                if player.is_shielded:
                    player.is_shielded = False; player.remove_shield_visual();
                    print("Shield absorbed enemy collision!")
                    # Kill the specific enemies that collided if shield absorbs them without player damage
                    for shielded_enemy_hit in colliding_enemies_direct: shielded_enemy_hit.kill()
                else:
                    player_lives -= len(colliding_enemies_direct) # Lose life for each colliding enemy
                    for _ in colliding_enemies_direct:
                        if sounds.get("enemy_explode"): sounds["enemy_explode"].play() # Enemy explodes on player

            if player_lives <= 0:
                if not game_over_internal_flag:
                    if sounds.get("player_explode"): sounds["player_explode"].play()
                    all_sprites.add(Explosion(player.rect.center, 'large'))
                game_over_internal_flag = True; player.kill(); print("Game Over internal flag set!")

        all_sprites.update()

        screen.fill((0,0,0))
        all_sprites.draw(screen)
        draw_text(screen, f"Score: {score}", 18, screen_width / 2, 10)
        draw_text(screen, f"Lives: {max(0, player_lives)}", 18, screen_width - 70, 10)
        if boss_battle_active:
            active_boss = next((e for e in enemies if isinstance(e, BossEnemy) and e.alive()), None)
            if active_boss: draw_text(screen, f"Boss Health: {active_boss.health}", 18, screen_width/2, 40)
        pygame.display.flip()

        if not game_over_internal_flag and not boss_battle_active and boss_spawned and not any(e.alive() for e in enemies):
            wave_number += 1; boss_spawned = False
            print(f"Starting Wave {wave_number}"); spawn_new_wave()

    elif game_state == GAME_OVER_SCREEN:
        show_game_over_screen()

pygame.quit()
