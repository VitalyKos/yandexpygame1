import random
import sqlite3
import sys
import pygame


def main():
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    pygame.init()
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Змейка")
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 175)
    pygame.font.init()
    font = pygame.font.SysFont(None, 84)
    smaller_font = pygame.font.SysFont(None, 54)
    score = font.render(f"Счет: 1", False, "white")
    best = font.render(f"Рекорд: ???", False, "white")
    results = font.render(f"Результаты", False, "white")
    back = font.render(f"Назад", False, "white")
    margin = 40
    scene = 0

    snake = [(5, 6)]
    apples = []
    game_over = False
    dx = dy = 0
    rows, columns = 21, 13
    cell_size = (width - 2 * margin) // rows, (height - 2 * margin - 50) // columns
    apple_postiions = {(i, j) for i in range(rows) for j in range(columns)}

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cursor.close()
                connection.close()
                pygame.quit()
                sys.exit(0)
            if game_over:
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    game_over = False
                    snake = [(5, 6)]
                    apples = []
                    score = font.render(f"Счет: 1", False, "white")
                    dx = dy = 0
                    best = font.render(f"Рекорд: {cursor.execute('SELECT MAX(score) FROM scores').fetchone()[0]}", False, "white")
                continue
            if event.type == pygame.USEREVENT:
                head = (snake[0][0] + dx) % rows, (snake[0][1] + dy) % columns
                snake = [head, *(snake if head in apples else snake[:-1])]
                if head in apples:
                    apples.remove(head)
                    score = font.render(f"Счет: {len(snake)}", False, "white")
                if head in snake[1:]:
                    game_over = True
                    cursor.execute("INSERT INTO scores VALUES(?)", (len(snake),))
                    connection.commit()
                while len(apples) < 3 and (avaible := list(apple_postiions - set(snake) - set(apples))):
                    apples.append(random.choice(avaible))
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_w):
                    dx, dy = 0, -1
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    dx, dy = 0, 1
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    dx, dy = -1, 0
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    dx, dy = 1, 0
            if event.type == pygame.MOUSEBUTTONUP and [results, back][scene].get_rect().move(900, 15).collidepoint(event.pos):
                connection = sqlite3.connect("database.sqlite")
                cursor = connection.cursor()
                if scene == 1:
                    snake = [(5, 6)]
                    apples = []
                    score = font.render(f"Счет: 1", False, "white")
                    dx = dy = 0
                    best = font.render(f"Рекорд: {cursor.execute('SELECT MAX(score) FROM scores').fetchone()[0]}", False, "white")
                if scene == 0:
                    cursor.execute("INSERT INTO scores VALUES(?)", (len(snake),))
                    connection.commit()
                    data = cursor.execute("SELECT * FROM scores ORDER BY -score LIMIT 10").fetchall()
                scene = 1 - scene

        screen.fill((74, 117, 44))
        if scene == 0:
            for i in range(rows):
                for j in range(columns):
                    pygame.draw.rect(screen, [(170, 215, 81), (162, 209, 73)][(i * 9 + j) % 2],
                                     (i * cell_size[0] + margin, j * cell_size[1] + margin + 50, cell_size[0], cell_size[1]))
            for i, j in apples:
                pygame.draw.circle(screen, (231, 71, 29),
                                   (i * cell_size[0] + cell_size[0] // 2 + margin, j * cell_size[1] + cell_size[1] // 2 + margin + 50),
                                   cell_size[1] // 2.4)
            pygame.draw.rect(screen, (160, 64, 255), (
                snake[0][0] * cell_size[0] + margin + 3, snake[0][1] * cell_size[1] + margin + 50 + 3, cell_size[0] - 6, cell_size[1] - 6))
            for i, j in snake[1:]:
                pygame.draw.rect(screen, (78, 122, 240),
                                 (i * cell_size[0] + margin + 3, j * cell_size[1] + margin + 50 + 3, cell_size[0] - 6, cell_size[1] - 6))

            screen.blit(score, (40, 15))
            screen.blit(best, (400, 15))
            pygame.draw.rect(screen, "gray", (897, 12, results.get_width() + 6, results.get_height() + 6), border_radius=5)
            screen.blit(results, (900, 15))
            if game_over:
                pygame.draw.rect(screen, "red", (
                    snake[0][0] * cell_size[0] + margin + 3, snake[0][1] * cell_size[1] + margin + 50 + 3, cell_size[0] - 6,
                    cell_size[1] - 6))
                screen.blit(font.render(f"Вы проиграли", False, "black"), (400, 300))
                screen.blit(smaller_font.render("Нажмите пробел чтобы продолжить", False, "black"), (300, 400))
        else:
            pygame.draw.rect(screen, "gray", (897, 12, back.get_width() + 6, back.get_height() + 6), border_radius=5)
            screen.blit(back, (900, 15))
            for i, (value,) in enumerate(data, start=1):
                screen.blit(font.render(f"{i}. {value}", False, "white"), ([240, 740][i > 5], ((i - 1) % 5 + 1) * 100))

        pygame.display.flip()
        clock.tick(90)


if __name__ == '__main__':
    main()
