# puzzle_manager.py
import pygame
import random
from settings import *


class PuzzleManager:
    """
    PuzzleManager artık dinamik grid_size desteği içerir.
    __init__(image, grid_size=None)
      - image: pygame Surface
      - grid_size: 2,3,4 vb. (None -> settings.GRID_SIZE kullanılır)
    """
    def __init__(self, image, grid_size=None):
        print("PuzzleManager başlatıldı.")
        if grid_size is None:
            self.grid_size = GRID_SIZE
        else:
            self.grid_size = grid_size

        # Tahtayı PUZZLE_BOARD_SIZE olarak scale et
        self.original_image = pygame.transform.scale(image, (PUZZLE_BOARD_SIZE, PUZZLE_BOARD_SIZE))
        self.tiles = []         # id -> Surface (list)
        self.grid = []          # 2D list of tile ids
        self.solved_grid = []   # hedef grid (2D)
        self.blank_pos = (0, 0)
        self.blank_tile_id = None
        self.tile_size = PUZZLE_BOARD_SIZE // self.grid_size
        self.create_puzzle()

    def create_puzzle(self):
        print("Puzzle oluşturuluyor...")
        self.tiles.clear()
        self.grid.clear()
        self.solved_grid.clear()

        tile_id = 0
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                # copy ile parent'a bağlı kalmaz
                tile_image = self.original_image.subsurface(rect).copy()
                self.tiles.append(tile_image)
                tile_id += 1

        ids = list(range(self.grid_size * self.grid_size))
        self.solved_grid = [ids[i * self.grid_size:(i + 1) * self.grid_size] for i in range(self.grid_size)]
        self.grid = [row[:] for row in self.solved_grid]

        self.blank_tile_id = (self.grid_size * self.grid_size) - 1
        self.blank_pos = (self.grid_size - 1, self.grid_size - 1)

        print("Puzzle başarıyla oluşturuldu. Karıştırılıyor...")
        self.shuffle_puzzle()

    def get_valid_moves(self):
        """Boş karenin etrafındaki geçerli hamleleri (komşu kareleri) bulur."""
        moves = []
        row, col = self.blank_pos
        if row > 0: moves.append((row - 1, col))
        if row < self.grid_size - 1: moves.append((row + 1, col))
        if col > 0: moves.append((row, col - 1))
        if col < self.grid_size - 1: moves.append((row, col + 1))
        return moves

    def shuffle_puzzle(self):
        """Çözülebilir şekilde karıştır: çözülmüş halden rastgele geçerli hamleler."""
        num_shuffles = self.grid_size * self.grid_size * 20
        for _ in range(num_shuffles):
            valid_moves = self.get_valid_moves()
            move_pos = random.choice(valid_moves)
            self.move_tile(move_pos, is_shuffling=True)

    def get_tile_pos_from_screen(self, screen_pos, puzzle_area_pos):
        """Ekran koordinatını grid koordinatına çevirir."""
        if not screen_pos:
            return None
        px, py = puzzle_area_pos
        sx, sy = screen_pos
        if px <= sx < px + PUZZLE_BOARD_SIZE and py <= sy < py + PUZZLE_BOARD_SIZE:
            col = (sx - px) // self.tile_size
            row = (sy - py) // self.tile_size
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                return (row, col)
        return None

    def can_move_tile(self, tile_grid_pos):
        if tile_grid_pos is None:
            return False
        dist = abs(tile_grid_pos[0] - self.blank_pos[0]) + abs(tile_grid_pos[1] - self.blank_pos[1])
        return dist == 1

    def move_tile(self, tile_grid_pos, is_shuffling=False):
        if not is_shuffling and not self.can_move_tile(tile_grid_pos):
            return
        blank_r, blank_c = self.blank_pos
        tile_r, tile_c = tile_grid_pos

        self.grid[blank_r][blank_c], self.grid[tile_r][tile_c] = self.grid[tile_r][tile_c], self.grid[blank_r][blank_c]
        self.blank_pos = tile_grid_pos

    def is_solved(self):
        return self.grid == self.solved_grid

    def draw(self, surface, puzzle_area_pos, show_blank=False):
        """Puzzle parçalarını surface'a çizer. show_blank: True -> boş parçayı da göster."""
        px, py = puzzle_area_pos
        for r, row in enumerate(self.grid):
            for c, tile_id in enumerate(row):
                if tile_id == self.blank_tile_id and not show_blank:
                    continue
                tile_surf = self.tiles[tile_id]
                dest_rect = pygame.Rect(px + c * self.tile_size, py + r * self.tile_size, self.tile_size, self.tile_size)
                surface.blit(tile_surf, dest_rect)
                pygame.draw.rect(surface, (60, 60, 60), dest_rect, 2, border_radius=6)
