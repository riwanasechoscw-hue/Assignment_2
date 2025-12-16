"""High-level pygame loop coordinating the maze, player, and ghosts."""

from __future__ import annotations


import pygame

from .constants import FPS, LEVEL_LAYOUT, POWER_DURATION
from .entities.ghost import Ghost
from .entities.player import Player
from .maze import Maze
from .sprites import get_ghost_sprite
from .vector import Vec2, vec_distance


class Game:
    """Owns the pygame lifecycle plus high-level game-state transitions."""

    def __init__(self):
        """Create the pygame window, maze, and player.

        Returns:
            None: Initializes pygame state and core actors in place.
        """
        pygame.init()
        pygame.display.set_caption("MinoPac")
        self.maze = Maze.from_strings(LEVEL_LAYOUT)
        self.screen = pygame.display.set_mode((self.maze.pixel_width, self.maze.pixel_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        self.player = Player(self.maze)
        
        # TODO: Add the Ghosts here

        self.score = 0
        self.power_time_remaining = 0.0
        self.game_over = False
        self.win = False
        self.moves_taken = 0

    def run(self) -> None:
        """Execute the main game loop until the window is closed.

        Returns:
            None: Blocks until pygame quits.
        """
        self.reset()
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()

    def reset(self) -> None:
        """Reset level state, score, and actors to their initial configuration.

        Returns:
            None
        """
        self.maze = Maze.from_strings(LEVEL_LAYOUT)
        self.player = Player(self.maze)
        
        # TODO: Reset the Ghosts here

        self.score = 0
        self.power_time_remaining = 0.0
        self.game_over = False
        self.win = False
        self.moves_taken = 0

    def handle_events(self) -> None:
        """Pump the pygame event queue and translate input into movement intents.

        Returns:
            None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                    continue
                if self.game_over:
                    continue
                direction = self.key_to_direction(event.key)
                if direction is not None:
                    self.player.set_next_direction(direction)

    def update(self, dt: float) -> None:
        """Advance the simulation by ``dt`` seconds, handling movement and collisions.

        Args:
            dt (float): Delta time since the previous frame in seconds.

        Returns:
            None
        """
        if self.game_over:
            return

        self.player.update(dt)

        # TODO: Update the Ghosts here

        self.resolve_player_tile()

        # TODO: Handle Ghost decision-making here

        self.check_collisions()
        self.update_power_timer(dt)

    def key_to_direction(self, key: int) -> tuple[int, int] | None:
        """Convert an arrow/WASD keycode to a normalized direction vector.

        Args:
            key (int): Pygame key constant.

        Returns:
            tuple[int, int] | None: Direction vector if supported, otherwise ``None``.
        """
        mapping = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
        }
        return mapping.get(key)

    def resolve_player_tile(self) -> None:
        """Handle pellet collection, scoring, and frightened timers for the player.

        Returns:
            None
        """
        pellet = self.maze.eat_pellet(self.player.grid_pos)
        if pellet == ".":
            self.score += 10
        elif pellet == "o":
            self.score += 50
            self.power_time_remaining = POWER_DURATION
            # TODO: Frighten the Ghosts here

        if self.maze.remaining_pellets() == 0:
            self.game_over = True
            self.win = True

        # Power timer now handled continuously in ``update``.

    def check_collisions(self) -> None:
        """Check for overlaps between the player and any active ghosts.

        Returns:
            None
        """
        pass
        # TODO: Check for collisions with the Ghosts here

    def update_power_timer(self, dt: float) -> None:
        """Tick down the active power duration and end fright mode when it expires."""
        if self.power_time_remaining <= 0.0:
            return
        self.power_time_remaining -= dt
        if self.power_time_remaining <= 0.0:
            self.power_time_remaining = 0.0
            # TODO: End the fright of the Ghosts here
            pass

    def handle_player_hit(self) -> None:
        """Handle life loss, game-over logic, and resetting actors.

        Returns:
            None
        """
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.game_over = True
            self.win = False
            return
        self.player.reset()
        # TODO: Reset the Ghosts here
        self.power_time_remaining = 0.0
        self.repeat_timer = self.player.movement_speed

    def draw(self) -> None:
        """Render the maze, actors, and HUD, then flip the display buffer.

        Returns:
            None
        """
        self.maze.draw(self.screen)
        self.player.draw(self.screen)
        # Draw a placeholder ghost at (13, 11)
        ghost_surface = get_ghost_sprite((255, 0, 0))
        ghost_pos = self.maze.grid_to_pixel((13, 11))
        ghost_rect = ghost_surface.get_rect(center=ghost_pos)
        self.screen.blit(ghost_surface, ghost_pos)



        #
        # TODO: Draw the Ghosts here
        #

        info = f"Score: {self.score}   Lives: {self.player.lives}"
        if self.power_time_remaining > 0:
            info += f"   Power: {self.power_time_remaining:0.1f}s"
        label = self.font.render(info, True, (255, 255, 255))
        self.screen.blit(label, (10, self.maze.pixel_height - 20))

        if self.game_over:
            message = "You Win! Press R to restart." if self.win else "Game Over! Press R to restart."
            text = self.font.render(message, True, (255, 255, 255))
            rect = text.get_rect(center=(self.maze.pixel_width / 2, self.maze.pixel_height / 2))
            self.screen.blit(text, rect)

        pygame.display.flip()

