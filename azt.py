##########################################################
#
#▄▄▄▄   ▓█████  █    ██  ██▀███    ▄████  ██░ ██▓██   ██▓
#▓█████▄ ▓█   ▀  ██  ▓██▒▓██ ▒ ██▒ ██▒ ▀█▒▓██░ ██▒▒██  ██▒
#▒██▒ ▄██▒███   ▓██  ▒██░▓██ ░▄█ ▒▒██░▄▄▄░▒██▀▀██░ ▒██ ██░
#▒██░█▀  ▒▓█  ▄ ▓▓█  ░██░▒██▀▀█▄  ░▓█  ██▓░▓█ ░██  ░ ▐██▓░
#░▓█  ▀█▓░▒████▒▒▒█████▓ ░██▓ ▒██▒░▒▓███▀▒░▓█▒░██▓ ░ ██▒▓░
#░▒▓███▀▒░░ ▒░ ░░▒▓▒ ▒ ▒ ░ ▒▓ ░▒▓░ ░▒   ▒  ▒ ░░▒░▒  ██▒▒▒ 
#▒░▒   ░  ░ ░  ░░░▒░ ░ ░   ░▒ ░ ▒░  ░   ░  ▒ ░▒░ ░▓██ ░▒░ 
# ░    ░    ░    ░░░ ░ ░   ░░   ░ ░ ░   ░  ░  ░░ ░▒ ▒ ░░  
# ░         ░  ░   ░        ░           ░  ░  ░  ░░ ░     
#      ░                                          ░ ░     
##########################################################
import math
import tkinter as tk
import random
import time
from PIL import Image, ImageTk

# Constantes
LARGEUR = 640
HAUTEUR = 480
TAILLE_CASE = 64
FOV = math.pi / 3
DISTANCE_MAX = 8
VITESSE_JOUEUR = 0.1
VITESSE_ROTATION = 0.00

# Carte (1 = mur, 0 = vide)
carte = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,1,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,1,0,1],
    [1,0,1,0,1,1,0,1,0,1],
    [1,0,1,0,1,1,0,1,0,1],
    [1,0,1,0,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
]

class Sprite:
    def __init__(self, x, y, texture, type='enemy', speed=0.03):
        self.x = x
        self.y = y
        self.texture = texture
        self.type = type
        self.speed = speed
        self.angle = 0
        self.health = 100
        self.is_visible = True
        self.animation_frame = 0
        self.last_animation_time = 0
        self.is_hit = False
        self.hit_time = 0
        self.is_dead = False
        self.death_time = 0
    
    def update(self, player_x, player_y, current_time):
        if self.type == 'enemy' and not self.is_dead:
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            if 0.5 < distance < 5:
                norm_dx = dx / distance
                norm_dy = dy / distance
                new_x = self.x + norm_dx * self.speed
                new_y = self.y + norm_dy * self.speed
                if (0 <= int(new_y) < len(carte) and 
                    0 <= int(new_x) < len(carte[0]) and 
                    carte[int(new_y)][int(new_x)] == 0):
                    self.x = new_x
                    self.y = new_y
                self.angle = math.atan2(dy, dx)
            if current_time - self.last_animation_time > 0.2:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.last_animation_time = current_time
            if self.is_hit and current_time - self.hit_time > 0.1:
                self.is_hit = False
    
    def take_damage(self, damage, current_time):
        if not self.is_dead:
            self.health -= damage
            self.is_hit = True
            self.hit_time = current_time
            if self.health <= 0:
                self.is_dead = True
                self.death_time = current_time
                return True
        return False

class Gun:
    def __init__(self):
        try:
            idle_img = Image.open("C:/Users/maxfrossard/Desktop/gun_idle.png").resize((200, 100))
            fire_img = Image.open("C:/Users/maxfrossard/Desktop/gun.png").resize((200, 100))
        except FileNotFoundError:
            # fallback images if not found
            idle_img = Image.new('RGB', (200, 100), (50, 50, 50))
            fire_img = Image.new('RGB', (200, 100), (255, 150, 0))

        self.tk_idle = ImageTk.PhotoImage(idle_img)
        self.tk_fire = ImageTk.PhotoImage(fire_img)

        self.is_firing = False
        self.last_fire_time = 0
        self.fire_cooldown = 0.5
        self.ammo = 12
        self.max_ammo = 12
        self.damage = 25
        self.reload_time = 1.5
        self.is_reloading = False
        self.reload_start_time = 0

    def fire(self, current_time):
        if not self.is_firing and not self.is_reloading and self.ammo > 0:
            if current_time - self.last_fire_time > self.fire_cooldown:
                self.is_firing = True
                self.last_fire_time = current_time
                self.ammo -= 1
                return True
        return False

    def update(self, current_time):
        if self.is_firing and current_time - self.last_fire_time > 0.1:
            self.is_firing = False
        if self.is_reloading and current_time - self.reload_start_time > self.reload_time:
            self.is_reloading = False
            self.ammo = self.max_ammo

    def reload(self, current_time):
        if not self.is_reloading and self.ammo < self.max_ammo:
            self.is_reloading = True
            self.reload_start_time = current_time

    def get_current_image(self):
        return self.tk_fire if self.is_firing else self.tk_idle

# --- la suite complète (FPSGame class + main) est trop longue pour un seul message. Je continue juste après. ---
class FPSGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Wolfenstein Clone")
        self.canvas = tk.Canvas(root, width=LARGEUR, height=HAUTEUR, bg="black")
        self.canvas.pack()

        self.root.focus_set()

        try:
            self.texture_mur = Image.open("C:/Users/maxfrossard/Desktop/wall.png").resize((64, 64))
            self.enemy_texture = Image.open("C:/Users/maxfrossard/Desktop/enemy.png").resize((64, 64))
        except FileNotFoundError:
            self.texture_mur = Image.new('RGB', (64, 64), (128, 128, 128))
            for i in range(64):
                for j in range(64):
                    if (i + j) % 8 == 0:
                        self.texture_mur.putpixel((i, j), (200, 200, 200))
            self.enemy_texture = Image.new('RGB', (64, 64), (200, 50, 50))
            for i in range(64):
                for j in range(64):
                    if 20 < i < 44 and 5 < j < 20:
                        self.enemy_texture.putpixel((i, j), (255, 200, 200))
                    if 25 < i < 39 and 25 < j < 60:
                        self.enemy_texture.putpixel((i, j), (150, 0, 0))

        self.texture_columns = [self.texture_mur.crop((x, 0, x + 1, 64)) for x in range(64)]
        self.enemy_texture_columns = [self.enemy_texture.crop((x, 0, x + 1, 64)) for x in range(64)]

        self.wall_textures_cache = {}
        self.sprite_textures_cache = {}

        self.gun = Gun()

        self.sprites = []
        for _ in range(5):
            while True:
                x = random.uniform(1.5, 8.5)
                y = random.uniform(1.5, 8.5)
                if carte[int(y)][int(x)] == 0:
                    break
            self.sprites.append(Sprite(x, y, self.enemy_texture))

        self.x = 3.5
        self.y = 3.5
        self.angle = 0
        self.vitesse = VITESSE_JOUEUR
        self.rotation = VITESSE_ROTATION
        self.touches = set()
        self.score = 0
        self.last_mouse_x = 0
        self.mouse_sensitivity = 0.003

        self.fps_time = 0
        self.fps_count = 0
        self.fps = 0
        self.current_time = time.time()

        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.bind("<Button-1>", self.mouse_click)
        root.bind("<Motion>", self.mouse_move)
        root.bind("<Escape>", self.toggle_mouse_lock)

        self.mouse_locked = False
        self.center_x = LARGEUR // 2
        self.canvas.config(cursor="none")

        self.boucle_jeu()

    def toggle_mouse_lock(self, event=None):
        self.mouse_locked = not self.mouse_locked
        if self.mouse_locked:
            self.canvas.config(cursor="none")
        else:
            self.canvas.config(cursor="")
    
    def mouse_move(self, event):
        if self.mouse_locked:
            # Calculer le mouvement relatif
            mouse_x = event.x
            if mouse_x != self.center_x:
                delta_x = mouse_x - self.center_x
                self.angle += delta_x * self.mouse_sensitivity
                
                # Repositionner la souris au centre
                self.root.event_generate("<Motion>", warp=True, x=self.center_x, y=HAUTEUR//2)
    
    def mouse_click(self, event):
        # Tir à gauche
        if event.num == 1:
            if self.gun.fire(self.current_time):
                self.shoot()
        
        # Verrouiller/déverrouiller la souris au début
        if not self.mouse_locked:
            self.toggle_mouse_lock()
    
    def shoot(self):
        # Rayon au centre de l'écran
        dist, tex_x, side, sprite_hit = self.raycast(self.angle, True)
        
        if sprite_hit is not None:
            # Toucher un ennemi
            if sprite_hit.take_damage(self.gun.damage, self.current_time):
                self.score += 100  # Points pour avoir tué un ennemi
    
    def key_down(self, e):
        key = e.keysym.lower()
        self.touches.add(key)
        
        # Gestion du rechargement
        if key == 'r':
            self.gun.reload(self.current_time)
    
    def key_up(self, e):
        self.touches.discard(e.keysym.lower())
    
    def boucle_jeu(self):
        self.current_time = time.time()
        self.deplacer_joueur()
        self.update_sprites()
        self.gun.update(self.current_time)
        self.rendu()
        
        self.root.after(16, self.boucle_jeu)
    
    def update_sprites(self):
        for sprite in self.sprites:
            sprite.update(self.x, self.y, self.current_time)
    
    def deplacer_joueur(self):
        if 'q' in self.touches:
            self.angle -= self.rotation
        if 'e' in self.touches:
            self.angle += self.rotation
        
        # Normaliser l'angle
        self.angle %= 2 * math.pi
        
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)
        
        if 'w' in self.touches:
            nx, ny = self.x + dx * self.vitesse, self.y + dy * self.vitesse
            if carte[int(ny)][int(nx)] == 0:
                self.x, self.y = nx, ny
        if 's' in self.touches:
            nx, ny = self.x - dx * self.vitesse, self.y - dy * self.vitesse
            if carte[int(ny)][int(nx)] == 0:
                self.x, self.y = nx, ny
        
        # Mouvements latéraux (strafe)
        if 'a' in self.touches:  # Gauche
            nx = self.x + dy * self.vitesse
            ny = self.y - dx * self.vitesse
            if carte[int(ny)][int(nx)] == 0:
                self.x, self.y = nx, ny
        if 'd' in self.touches:  # Droite
            nx = self.x - dy * self.vitesse
            ny = self.y + dx * self.vitesse
            if carte[int(ny)][int(nx)] == 0:
                self.x, self.y = nx, ny
    
    def raycast(self, angle, check_sprites=False):
        # Direction du rayon
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        # Position initiale
        map_x, map_y = int(self.x), int(self.y)
        
        # Calcul des distances aux bords de la grille
        delta_dist_x = abs(1 / cos_a) if cos_a != 0 else float('inf')
        delta_dist_y = abs(1 / sin_a) if sin_a != 0 else float('inf')
        
        # Direction de pas
        step_x = 1 if cos_a >= 0 else -1
        step_y = 1 if sin_a >= 0 else -1
        
        # Distance au prochain bord x ou y
        side_dist_x = ((map_x + step_x) - self.x) * delta_dist_x if step_x > 0 else (self.x - map_x) * delta_dist_x
        side_dist_y = ((map_y + step_y) - self.y) * delta_dist_y if step_y > 0 else (self.y - map_y) * delta_dist_y
        
        # DDA (Digital Differential Analysis) algorithm
        hit = False
        side = 0  # 0 pour un mur horizontal, 1 pour un mur vertical
        while not hit:
            # Avancer jusqu'au prochain bord de la grille
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            # Vérifier si on a touché un mur
            if 0 <= map_y < len(carte) and 0 <= map_x < len(carte[0]) and carte[map_y][map_x] == 1:
                hit = True
        
        # Calculer la distance perpendiculaire (évite l'effet fish-eye)
        if side == 0:
            perp_wall_dist = (map_x - self.x + (1 - step_x) / 2) / cos_a
            wall_x = self.y + perp_wall_dist * sin_a
        else:
            perp_wall_dist = (map_y - self.y + (1 - step_y) / 2) / sin_a
            wall_x = self.x + perp_wall_dist * cos_a
        
        # Calculer la coordonnée x de la texture (0-63)
        wall_x -= math.floor(wall_x)
        tex_x = int(wall_x * 64)
        if (side == 0 and cos_a < 0) or (side == 1 and sin_a > 0):
            tex_x = 64 - tex_x - 1
        
        # Vérifier collision avec sprites
        sprite_hit = None
        if check_sprites:
            for sprite in self.sprites:
                if not sprite.is_dead and sprite.is_visible:
                    # Vérifier si le rayon touche le sprite
                    dx = sprite.x - self.x
                    dy = sprite.y - self.y
                    
                    # Calculer la distance entre le joueur et le sprite
                    sprite_dist = math.sqrt(dx*dx + dy*dy)
                    
                    if sprite_dist < perp_wall_dist:
                        # Calculer l'angle entre le joueur et le sprite
                        sprite_angle = math.atan2(dy, dx)
                        
                        # Normaliser l'angle
                        diff_angle = (sprite_angle - angle + math.pi) % (2 * math.pi) - math.pi
                        
                        # Vérifier si le sprite est dans la ligne de mire
                        if abs(diff_angle) < 0.1:  # Marge de tolérance
                            sprite_hit = sprite
                            break
        
        return perp_wall_dist, tex_x, side, sprite_hit
    
    def get_wall_texture(self, tex_x, height):
        """Retourne une texture de mur redimensionnée avec mise en cache"""
        # Clé de cache
        cache_key = (tex_x, height)
        
        # Vérifier si la texture est dans le cache
        if cache_key in self.wall_textures_cache:
            return self.wall_textures_cache[cache_key]
        
        # Redimensionner la colonne de texture
        column = self.texture_columns[tex_x]
        if height < 64:
            resized = column.resize((1, height), Image.NEAREST)
        else:
            # Pour les murs très proches, on prend une partie de la texture
            crop_height = min(64, int(64 * 64 / height))
            start = (64 - crop_height) // 2
            cropped = column.crop((0, start, 1, start + crop_height))
            resized = cropped.resize((1, height), Image.NEAREST)
        
        # Convertir en PhotoImage
        tex_tk = ImageTk.PhotoImage(resized)
        
        # Stocker dans le cache (avec une limite de taille de cache)
        if len(self.wall_textures_cache) > 1000:  # Limiter la taille du cache
            self.wall_textures_cache.clear()
        self.wall_textures_cache[cache_key] = tex_tk
        
        return tex_tk
    
    def get_sprite_texture(self, sprite, height):
        """Retourne une texture de sprite redimensionnée"""
        # Clé de cache
        cache_key = (id(sprite), height, sprite.animation_frame, sprite.is_hit, sprite.is_dead)
        
        # Vérifier si la texture est dans le cache
        if cache_key in self.sprite_textures_cache:
            return self.sprite_textures_cache[cache_key]
        
        # Calculer la colonne de texture à utiliser en fonction de l'angle relatif
        rel_angle = (math.atan2(sprite.y - self.y, sprite.x - self.x) - sprite.angle + math.pi) % (2 * math.pi)
        tex_x = int((rel_angle / (2 * math.pi)) * 64) % 64
        
        # Variation de la texture selon l'animation
        frame_offset = sprite.animation_frame * 16  # 4 frames, chacun décalé de 16px
        tex_x = (tex_x + frame_offset) % 64
        
        # Effets spéciaux pour hit et mort
        if sprite.is_dead:
            column = self.enemy_texture_columns[tex_x].point(lambda x: x // 2)  # Assombrir
        elif sprite.is_hit:
            column = self.enemy_texture_columns[tex_x].point(lambda x: min(255, x + 100))  # Éclaircir (flash)
        else:
            column = self.enemy_texture_columns[tex_x]
        
        # Redimensionner la colonne de texture
        if height < 64:
            resized = column.resize((1, height), Image.NEAREST)
        else:
            crop_height = min(64, int(64 * 64 / height))
            start = (64 - crop_height) // 2
            cropped = column.crop((0, start, 1, start + crop_height))
            resized = cropped.resize((1, height), Image.NEAREST)
        
        # Convertir en PhotoImage
        tex_tk = ImageTk.PhotoImage(resized)
        
        # Stocker dans le cache
        if len(self.sprite_textures_cache) > 1000:
            self.sprite_textures_cache.clear()
        self.sprite_textures_cache[cache_key] = tex_tk
        
        return tex_tk
    
    def rendu(self):
        self.canvas.delete("all")
        
        # Dessiner le ciel et le sol
        self.canvas.create_rectangle(0, 0, LARGEUR, HAUTEUR//2, fill="#87CEEB", outline="")
        self.canvas.create_rectangle(0, HAUTEUR//2, LARGEUR, HAUTEUR, fill="#8B4513", outline="")
        
        # Lancer des rayons à travers l'écran
        nb_rayons = LARGEUR
        z_buffer = [float('inf')] * nb_rayons  # Pour stocker les distances des murs
        
        for i in range(nb_rayons):
            # Calculer l'angle du rayon
            ray_angle = self.angle - FOV/2 + FOV * i / nb_rayons
            
            # Lancer le rayon
            dist, tex_x, side, _ = self.raycast(ray_angle)
            z_buffer[i] = dist
            
            # Calculer la hauteur à l'écran
            hauteur = min(HAUTEUR * 2, int(HAUTEUR / (dist + 0.0001)))
            
            # Position y de départ pour dessiner
            start_y = (HAUTEUR - hauteur) // 2
            
            # Assombrir légèrement les murs verticaux pour l'effet 3D
            darken = 0.7 if side == 1 else 1.0
            
            # Obtenir la texture du mur
            wall_tex = self.get_wall_texture(tex_x, hauteur)
            
            # Dessiner la colonne
            self.canvas.create_image(i, start_y, anchor='nw', image=wall_tex)
        
        # Trier les sprites par distance (du plus loin au plus proche)
        sprites_to_render = []
        for sprite in self.sprites:
            dx = sprite.x - self.x
            dy = sprite.y - self.y
            dist = dx*dx + dy*dy  # Distance au carré
            angle = math.atan2(dy, dx)
            
            # Calculer l'angle relatif au joueur
            sprite_angle = (angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            
            # Vérifier si le sprite est dans le champ de vision
            if abs(sprite_angle) < FOV/2 + 0.2:  # Marge pour éviter les pop-ins
                sprites_to_render.append((sprite, dist, sprite_angle))
        
        # Trier par distance (du plus loin au plus proche)
        sprites_to_render.sort(key=lambda x: x[1], reverse=True)
        
        # Dessiner les sprites
        for sprite, dist, sprite_angle in sprites_to_render:
            # Calculer la position sur l'écran
            sprite_screen_x = int(LARGEUR/2 * (1 + sprite_angle / (FOV/2)))
            
            # Calculer la taille à l'écran
			
            sprite_height = min(HAUTEUR * 2, int(HAUTEUR / (math.sqrt(dist) + 0.0001)))
            sprite_width = sprite_height  # Sprites carrés
            
            # Position y de départ pour dessiner
            sprite_start_y = (HAUTEUR - sprite_height) // 2
            sprite_start_x = sprite_screen_x - sprite_width // 2
            
            # Dessiner le sprite colonne par colonne
            for sx in range(max(0, sprite_start_x), min(LARGEUR, sprite_start_x + sprite_width)):
                # Vérifier si cette colonne est visible (pas cachée par un mur)
                if z_buffer[sx] > math.sqrt(dist):
                    # Obtenir la texture du sprite
                    sprite_tex = self.get_sprite_texture(sprite, sprite_height)
                    
                    # Dessiner la colonne du sprite
                    self.canvas.create_image(sx, sprite_start_y, anchor='nw', image=sprite_tex)
            
            sprite.is_visible = True
        
        # Dessiner le gun
        gun_y = HAUTEUR - 100
        gun_x = (LARGEUR - 200) // 2
        self.canvas.create_image(gun_x, gun_y, anchor='nw', image=self.gun.get_current_image())
        
        # Dessiner le viseur
        self.canvas.create_line(LARGEUR//2 - 10, HAUTEUR//2, LARGEUR//2 + 10, HAUTEUR//2, fill="white")
        self.canvas.create_line(LARGEUR//2, HAUTEUR//2 - 10, LARGEUR//2, HAUTEUR//2 + 10, fill="white")
        
        # Afficher les infos HUD (munitions, score)
        ammo_text = f"AMMO: {self.gun.ammo}/{self.gun.max_ammo}"
        if self.gun.is_reloading:
            reload_progress = min(100, int((self.current_time - self.gun.reload_start_time) / self.gun.reload_time * 100))
            ammo_text += f" RELOADING {reload_progress}%"
        self.canvas.create_text(LARGEUR - 100, HAUTEUR - 30, text=ammo_text, fill="white", font=("Arial", 12))
        self.canvas.create_text(100, HAUTEUR - 30, text=f"SCORE: {self.score}", fill="white", font=("Arial", 12))
        
        # Afficher la minimap
                # Afficher la minimap
        self.draw_minimap()

    def draw_minimap(self):
        # Taille de la minimap
        map_size = 100
        tile_size = map_size / len(carte)

        # Position de la minimap (coin supérieur droit)
        map_x, map_y = LARGEUR - map_size - 10, 10

        # Dessiner le fond
        self.canvas.create_rectangle(
            map_x, map_y, map_x + map_size, map_y + map_size,
            fill="black", outline="white"
        )

        # Dessiner les murs
        for y in range(len(carte)):
            for x in range(len(carte[0])):
                if carte[y][x] == 1:
                    self.canvas.create_rectangle(
                        map_x + x * tile_size,
                        map_y + y * tile_size,
                        map_x + (x + 1) * tile_size,
                        map_y + (y + 1) * tile_size,
                        fill="gray", outline=""
                    )

        # Dessiner les ennemis vivants
        for sprite in self.sprites:
            if not sprite.is_dead:
                sx = map_x + sprite.x * tile_size
                sy = map_y + sprite.y * tile_size
                self.canvas.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill="red")

        # Dessiner le joueur
        px = map_x + self.x * tile_size
        py = map_y + self.y * tile_size
        self.canvas.create_oval(px - 2, py - 2, px + 2, py + 2, fill="green")

# Lancement du jeu
if __name__ == "__main__":
    root = tk.Tk()
    game = FPSGame(root)
    root.mainloop()

