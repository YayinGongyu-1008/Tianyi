import pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
x, y = 180, 180
dx = dy = 3

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 20)
    x += dx
    y += dy
    if x <= 20 or x >= 380: dx = -dx
    if y <= 20 or y >= 380: dy = -dy
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
