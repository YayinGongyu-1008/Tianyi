import pygame
import sys

# 初始化
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("角色")
clock = pygame.time.Clock()

# 颜色
SKY_BLUE = (135, 206, 235)
RED = (220, 20, 60)

# 角色属性
player = {
    'x': WIDTH // 5,
    'y': HEIGHT // 5,
    'speed': 5,
    'size': 30
}

# 主循环
running = True
while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 按键检测
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player['y'] -= player['speed']
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player['y'] += player['speed']
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player['x'] -= player['speed']
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player['x'] += player['speed']

    # 边界限制
    player['x'] = max(player['size'], min(WIDTH - player['size'], player['x']))
    player['y'] = max(player['size'], min(HEIGHT - player['size'], player['y']))
    
    # 绘制
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, RED, 
                     (player['x'] - player['size']//2, 
                      player['y'] - player['size']//2,
                      player['size'], player['size']))
    
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
sys.exit()