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

        # Load the ship image
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # Start at bottom center
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

        # Movement flags
        self.moving_right = False
        self.moving_left = False

        # ====== SHIELD (SIMPLIFIED) ======
        self.shield_active = True   # 默认开启
        self.shield_hits = 3        # 可挡 3 次攻击
        # =================================

    def center_ship(self):
        """Center the ship."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Update position."""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        self.rect.x = self.x

    def blitme(self):
        """Draw ship (and shield if active)."""
        self.screen.blit(self.image, self.rect)
        if self.shield_active:
            self._draw_shield()

    def _draw_shield(self):
        """Draw a simple blue translucent shield."""
        # 创建一个 80x80 带透明通道的表面
        shield_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        # 绘制半透明蓝圆（更显眼）
        pygame.draw.circle(shield_surf, (100, 240, 255, 120), (40, 40), 40)
        # 居中绘制到飞船中心
        self.screen.blit(shield_surf, (self.rect.centerx - 40, self.rect.centery - 40))

    def activate_shield(self):
        """Reset and activate shield."""
        self.shield_active = True
        self.shield_hits = 3

    def deactivate_shield(self):
        """Turn off shield."""
        self.shield_active = False

    def hit_shield(self):
        """Called when shield is hit — each hit consumes 1 charge."""
        if self.shield_active:
            self.shield_hits -= 1
            if self.shield_hits <= 0:
                self.deactivate_shield()
            return True  # 已被护盾挡下
        return False     # 无护盾，未挡下