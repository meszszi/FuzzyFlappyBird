from game import Game
import pygame

from fuzzy import compute

manual = False

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((500, 400))

    game = Game(
        width=500,
        height=400,
        walls_width=15,
        walls_space=200,
        walls_speed=3,
        gravity=0.3,
        max_boost=0.6,
        max_ball_speed=10,
        min_gap=60,
        max_gap=60,
        margin=40,
        ball_radius=15,
        ball_init_x=50
    )

    done = False
    game_over = False

    clock = pygame.time.Clock()

    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        pressed = pygame.key.get_pressed()

        if not game_over:

            if not manual:
                if pressed[pygame.K_UP]:
                    game.ball.v_speed -= 0.2

                if pressed[pygame.K_DOWN]:
                    game.ball.v_speed += 0.2

                speed, gap_y, wall_dist = game.get_fuzzy_inputs()
                boosters = compute(speed, gap_y, wall_dist)

            else:
                if pressed[pygame.K_UP]:
                    boosters = 1

                else:
                    boosters = 0

            game.make_step(boosters)
            screen.fill((0, 0, 0))
            game.draw(screen, booster=boosters)

            if game.game_over():
                game_over = True

            pygame.display.flip()

        else:
            if pressed[pygame.K_SPACE]:
                game.restart()
                game_over = False

            if pressed[pygame.K_ESCAPE]:
                done = True

        clock.tick(60)