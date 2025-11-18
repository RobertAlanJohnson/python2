import pygame
from pygame.sprite import Sprite
import random


class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and set its rect attribute.
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)
        
        # 添加射击时间跟踪
        self.last_shot = pygame.time.get_ticks()
        # 增加射击间隔，降低射击频率 (原来是2000-10000毫秒，现在增加到5000-15000毫秒)
        self.shoot_delay = random.randint(5000, 15000)  # 随机5-15秒射击一次

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        """Move the alien right or left."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x
        
    def can_shoot(self):
        """检查外星人是否可以射击"""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            # 重新设置下次射击时间，继续保持较低频率
            self.shoot_delay = random.randint(5000, 15000)  # 随机5-15秒射击一次
            return True
        return False
        
    def shoot(self):
        """创建一个子弹"""
        alien_bullet = AlienBullet(self.screen, self.rect.centerx, self.rect.bottom)
        return alien_bullet


class AlienBullet(Sprite):
    """外星人子弹类"""
    
    def __init__(self, screen, x, y):
        """初始化子弹"""
        super().__init__()
        self.screen = screen
        
        # 创建子弹矩形
        self.rect = pygame.Rect(0, 0, 3, 15)
        self.rect.centerx = x
        self.rect.top = y
        
        # 存储子弹位置
        self.y = float(self.rect.y)
        
        # 子弹颜色和速度
        self.color = (255, 0, 0)  # 红色子弹
        self.speed = 0.5
        
    def update(self):
        """向下移动子弹"""
        self.y += self.speed
        self.rect.y = self.y
        
    def draw_bullet(self):
        """绘制子弹"""
        pygame.draw.rect(self.screen, self.color, self.rect)