import pygame
import random
import sys
import math

# 初始化
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("弹幕躲避游戏")
clock = pygame.time.Clock()

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
GREEN = (50, 255, 100)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (180, 70, 255)

# 玩家类
class Player:
    def __init__(self):
        self.radius = 20
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.color = BLUE
        self.invincible = False
        self.invincible_time = 0
    
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # 边界限制
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
    
    def draw(self, surface):
        # 绘制玩家
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # 绘制方向指示器
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        distance = max(0.1, math.sqrt(dx*dx + dy*dy))
        
        # 绘制无敌闪烁效果
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius, 3)
    
    def get_hitbox(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

# 弹幕基类
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 3
        self.color = RED
        self.active = True
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT + 20:
            self.active = False
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 1)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

# 跟踪弹幕
class HomingBullet(Bullet):
    def __init__(self, x, y, target_x, target_y):
        super().__init__(x, y)
        self.speed = 2
        self.color = PURPLE
        self.target_x = target_x
        self.target_y = target_y
        self.angle = 0
    
    def update(self, player_x=None, player_y=None):
        if player_x and player_y:
            # 向玩家位置移动
            dx = player_x - self.x
            dy = player_y - self.y
            dist = max(0.1, math.sqrt(dx*dx + dy*dy))
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
        
        self.angle += 0.1
        if (self.x < -20 or self.x > WIDTH + 20 or 
            self.y < -20 or self.y > HEIGHT + 20):
            self.active = False

# 散射弹幕
class SpreadBullet(Bullet):
    def __init__(self, x, y, angle):
        super().__init__(x, y)
        self.speed = 4
        self.color = GREEN
        self.angle = angle
        self.radius = 6
    
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        if (self.x < -20 or self.x > WIDTH + 20 or 
            self.y < -20 or self.y > HEIGHT + 20):
            self.active = False

# 游戏主类
class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.bullet_timer = 0
        self.wave = 1
        self.spawn_interval = 30  # 弹幕生成间隔（帧数）
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def spawn_bullets(self):
        self.bullet_timer += 1
        
        # 普通弹幕
        if self.bullet_timer % self.spawn_interval == 0:
            for _ in range(min(3 + self.wave // 3, 8)):
                x = random.randint(30, WIDTH - 30)
                self.bullets.append(Bullet(x, -20))
        
        # 每100帧生成跟踪弹幕
        if self.bullet_timer % 100 == 0 and self.wave >= 2:
            for _ in range(min(2, 1 + self.wave // 4)):
                x = random.randint(50, WIDTH - 50)
                self.bullets.append(HomingBullet(x, -20, self.player.x, self.player.y))
        
        # 每150帧生成散射弹幕
        if self.bullet_timer % 150 == 0 and self.wave >= 3:
            center_x = random.randint(100, WIDTH - 100)
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                self.bullets.append(SpreadBullet(center_x, -20, angle))
    
    def update(self):
        if self.game_over:
            return
        
        # 生成弹幕
        self.spawn_bullets()
        
        # 更新弹幕
        for bullet in self.bullets[:]:
            if isinstance(bullet, HomingBullet):
                bullet.update(self.player.x, self.player.y)
            else:
                bullet.update()
            
            # 碰撞检测
            if (bullet.active and 
                self.player.get_hitbox().colliderect(bullet.get_rect())):
                if not self.player.invincible:
                    self.game_over = True
                    return
                else:
                    bullet.active = False
        
        # 清理不活跃的弹幕
        self.bullets = [b for b in self.bullets if b.active]
        
        # 每存活1秒得10分
        if pygame.time.get_ticks() % 1000 < 16:  # 大约每秒一次
            self.score += 10
        
        # 每5000分增加难度
        self.wave = 1 + self.score // 5000
        self.spawn_interval = max(10, 30 - self.wave * 2)
    
    def draw(self, surface):
        # 绘制背景
        surface.fill(BLACK)
        
        # 绘制网格背景
        for i in range(0, WIDTH, 40):
            pygame.draw.line(surface, (20, 20, 20), (i, 0), (i, HEIGHT))
        for i in range(0, HEIGHT, 40):
            pygame.draw.line(surface, (20, 20, 20), (0, i), (WIDTH, i))
        
        # 绘制所有弹幕
        for bullet in self.bullets:
            bullet.draw(surface)
        
        # 绘制玩家
        self.player.draw(surface)
        
        # 绘制UI
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        wave_text = self.font.render(f"波次: {self.wave}", True, WHITE)
        surface.blit(score_text, (10, 10))
        surface.blit(wave_text, (10, 50))
        
        # 绘制提示
        tips = [
            "方向键或WASD移动",
            "坚持越久分数越高",
            f"弹幕数量: {len(self.bullets)}"
        ]
        
        for i, tip in enumerate(tips):
            tip_text = self.small_font.render(tip, True, (150, 150, 150))
            surface.blit(tip_text, (WIDTH - 200, 10 + i * 25))
        
        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("游戏结束!", True, RED)
            final_score = self.font.render(f"最终分数: {self.score}", True, WHITE)
            restart_text = self.small_font.render("按R键重新开始，按ESC退出", True, (200, 200, 200))
            
            surface.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 60))
            surface.blit(final_score, (WIDTH//2 - 100, HEIGHT//2 - 20))
            surface.blit(restart_text, (WIDTH//2 - 150, HEIGHT//2 + 20))

# 主游戏循环
def main():
    game = Game()
    running = True
    
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_over:
                    game = Game()  # 重新开始游戏
                elif event.key == pygame.K_SPACE and not game.player.invincible:
                    # 无敌技能（冷却时间）
                    game.player.invincible = True
                    game.player.invincible_time = pygame.time.get_ticks()
        
        # 更新无敌状态
        if game.player.invincible:
            if pygame.time.get_ticks() - game.player.invincible_time > 2000:  # 2秒无敌
                game.player.invincible = False
        
        # 获取按键状态
        keys = pygame.key.get_pressed()
        game.player.move(keys)
        
        # 更新游戏状态
        game.update()
        
        # 绘制
        game.draw(screen)
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()




