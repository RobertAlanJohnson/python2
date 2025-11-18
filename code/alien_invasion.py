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
        # 初始化音效系统
        pygame.mixer.init()
        
        # 加载音效
        self._load_sounds()
        
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()  # 外星人子弹组

        self._create_fleet()

        # Start Alien Invasion in an inactive state.
        self.game_active = False

        # Make the Play button.
        self.play_button = Button(self, "Play")
        
        # 添加激活护盾的按键标志
        self.shield_key_pressed = False
    
    def _load_sounds(self):
        """加载游戏音效"""
        try:
            self.shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
            self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
            self.alien_shoot_sound = pygame.mixer.Sound("sounds/alien_shoot.wav")  # 外星人射击音效
            self.shield_hit_sound = pygame.mixer.Sound("sounds/shield_hit.wav")  # 护盾被击中音效
            
            # 加载并播放背景音乐
            pygame.mixer.music.load("sounds/background.mp3")
            pygame.mixer.music.play(-1)  # -1 表示循环播放
            pygame.mixer.music.set_volume(0.3)  # 设置音量为30%
        except pygame.error as e:
            # 如果无法加载音效文件，设置为None
            self.shoot_sound = None
            self.explosion_sound = None
            self.alien_shoot_sound = None
            self.shield_hit_sound = None
            print(f"Warning: Could not load sound files. Sounds will be disabled. Error: {e}")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()  # 更新外星人子弹

            self._update_screen()
            
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
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
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.alien_bullets.empty()  # 清空外星人子弹
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)
            
            # 重新开始背景音乐
            pygame.mixer.music.play(-1)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_s:  # 按S键激活/隐藏护盾
            if not self.shield_key_pressed:
                self.shield_key_pressed = True
                if not self.ship.shield_active:
                    self.ship.activate_shield()
                else:
                    self.ship.deactivate_shield()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_s:
            self.shield_key_pressed = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            
            # 播放射击音效
            if self.shoot_sound:
                self.shoot_sound.play()

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                
                # 播放爆炸音效
                if self.explosion_sound:
                    self.explosion_sound.play()
                    
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self.alien_bullets.empty()  # 清空外星人子弹
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _update_alien_bullets(self):
        """更新外星人子弹"""
        # 更新子弹位置
        self.alien_bullets.update()
        
        # 清除消失的子弹
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        
        # 检查子弹是否击中飞船（包括护盾）
        for bullet in self.alien_bullets.copy():
            # 如果飞船有激活的护盾，检查是否击中护盾
            if self.ship.shield_active:
                # 计算子弹与飞船中心的距离
                distance = ((bullet.rect.centerx - self.ship.rect.centerx) ** 2 + 
                           (bullet.rect.centery - self.ship.rect.centery) ** 2) ** 0.5
                # 如果子弹在护盾范围内
                if distance <= self.ship.shield_radius:
                    # 护盾吸收攻击 - 减少一次可抵挡的攻击次数
                    self.ship.hit_shield(1)
                    self.alien_bullets.remove(bullet)  # 移除子弹
                    
                    # 播放护盾被击中音效
                    if self.shield_hit_sound:
                        self.shield_hit_sound.play()
                    continue  # 继续检查下一个子弹
            
            # 如果没有护盾或者子弹未击中护盾，检查是否直接击中飞船
            if self.ship.rect.colliderect(bullet.rect):
                self.alien_bullets.remove(bullet)
                self._ship_hit()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien or alien bullet."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # 播放爆炸音效
            if self.explosion_sound:
                self.explosion_sound.play()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.alien_bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # 重置护盾状态
            self.ship.deactivate_shield()

            # Pause.
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)
            
            # 停止背景音乐
            pygame.mixer.music.stop()

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()
        
        # 外星人随机射击
        for alien in self.aliens.sprites():
            if alien.can_shoot():
                alien_bullet = alien.shoot()
                self.alien_bullets.add(alien_bullet)
                
                # 播放外星人射击音效
                if self.alien_shoot_sound:
                    self.alien_shoot_sound.play()

        # Look for alien-ship collisions.
        alien_collisions = pygame.sprite.spritecollide(self.ship, self.aliens, False)
        if alien_collisions:
            # 检查是否有护盾可以保护飞船
            if not self.ship.hit_shield(30):  # 外星人撞击造成30点伤害
                self._ship_hit()
            else:
                # 护盾吸收了撞击，移除撞击的外星人
                for alien in alien_collisions:
                    alien.kill()
                    
                # 播放护盾被击中音效
                if self.shield_hit_sound:
                    self.shield_hit_sound.play()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        
        # 绘制外星人子弹
        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()