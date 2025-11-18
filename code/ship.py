import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, ai_game):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a float for the ship's exact horizontal position.
        self.x = float(self.rect.x)

        # Movement flags; start with a ship that's not moving.
        self.moving_right = False
        self.moving_left = False
        
        # 护盾属性 - 默认激活
        self.shield_active = True  # 默认激活护盾
        self.shield_hits = 3  # 护盾能抵挡的攻击次数
        self.shield_radius = 30  # 护盾半径

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Update the ship's position based on movement flags."""
        # Update the ship's x value, not the rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
            
        # Update rect object from self.x.
        self.rect.x = self.x

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
        
        # 如果护盾激活，绘制护盾
        if self.shield_active:
            self._draw_shield()
            
    def _draw_shield(self):
        """绘制护盾效果"""
        # 绘制半透明护盾
        shield_surface = pygame.Surface((self.shield_radius * 2, self.shield_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            shield_surface, 
            (0, 200, 255, 100),  # 半透明蓝色
            (self.shield_radius, self.shield_radius), 
            self.shield_radius
        )
        # 将护盾绘制到屏幕上，位置为中心对齐飞船
        shield_x = self.rect.centerx - self.shield_radius
        shield_y = self.rect.centery - self.shield_radius
        self.screen.blit(shield_surface, (shield_x, shield_y))
        
    def activate_shield(self):
        """激活护盾"""
        self.shield_active = True
        self.shield_hits = 3  # 重置护盾能抵挡的攻击次数为3次
        
    def deactivate_shield(self):
        """隐藏护盾"""
        self.shield_active = False
        
    def hit_shield(self, damage):
        """护盾受到攻击"""
        if self.shield_active:
            self.shield_hits -= 1  # 减少一次可抵挡的攻击次数
            if self.shield_hits <= 0:
                self.shield_hits = 0
                self.deactivate_shield()  # 抵挡次数用完后关闭护盾
            return True  # 护盾吸收了攻击
        return False  # 没有护盾吸收攻击