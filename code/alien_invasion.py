import sys
from time import sleep
import random
import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien, AlienBullet


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        pygame.mixer.init()
        self._load_sounds()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()

        self._create_fleet()
        self.game_active = False
        self.play_button = Button(self, "Play")

    def _load_sounds(self):
        """Load sound effects."""
        try:
            self.shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
            self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
            self.alien_shoot_sound = pygame.mixer.Sound("sounds/alien_shoot.wav")
            self.shield_hit_sound = pygame.mixer.Sound("sounds/shield_hit.wav")
            pygame.mixer.music.load("sounds/background.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
        except pygame.error as e:
            self.shoot_sound = None
            self.explosion_sound = None
            self.alien_shoot_sound = None
            self.shield_hit_sound = None
            print(f"Warning: Sound files missing. Error: {e}")

    def run_game(self):
        """Start the main loop."""
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stats.save_high_score()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True
            self.bullets.empty()
            self.alien_bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            self.ship.activate_shield()  # ✅ 关键：每局重置护盾
            pygame.mouse.set_visible(False)
            pygame.mixer.music.play(-1)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            if self.shoot_sound:
                self.shoot_sound.play()

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                if self.explosion_sound:
                    self.explosion_sound.play()
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            self.bullets.empty()
            self.alien_bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _update_alien_bullets(self):
        self.alien_bullets.update()
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        # 检查是否击中飞船/护盾
        for bullet in self.alien_bullets.copy():
            # 简化护盾检测：使用 inflate 扩大飞船碰撞区
            if self.ship.shield_active:
                # 扩大飞船矩形 60x60 范围作为护盾区域
                shield_rect = self.ship.rect.inflate(60, 60)
                if shield_rect.colliderect(bullet.rect):
                    self.ship.hit_shield()  # ✅ 无参数
                    self.alien_bullets.remove(bullet)
                    if self.shield_hit_sound:
                        self.shield_hit_sound.play()
                    continue
            # 无护盾或未击中护盾 → 检查是否击中飞船
            if self.ship.rect.colliderect(bullet.rect):
                self.alien_bullets.remove(bullet)
                self._ship_hit()

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            if self.explosion_sound:
                self.explosion_sound.play()
            self.bullets.empty()
            self.alien_bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            self.ship.activate_shield()  # ✅ 残机重置护盾
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)
            pygame.mixer.music.stop()

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        # 外星人随机射击
        for alien in self.aliens.sprites():
            if alien.can_shoot():
                alien_bullet = alien.shoot()
                self.alien_bullets.add(alien_bullet)
                if self.alien_shoot_sound:
                    self.alien_shoot_sound.play()
        # 检查外星人撞飞船
        alien_collisions = pygame.sprite.spritecollide(self.ship, self.aliens, False)
        if alien_collisions:
            if not self.ship.hit_shield():  # ✅ 无参数
                self._ship_hit()
            else:
                for alien in alien_collisions:
                    alien.kill()
                if self.shield_hit_sound:
                    self.shield_hit_sound.play()
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()