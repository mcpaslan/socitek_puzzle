import pygame
import os
from settings import *


class UIManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Socitek PUZZLE")

        font_name = "Consolas"
        try:
            self.font = pygame.font.SysFont(font_name, 40, bold=True)
            self.big_font = pygame.font.SysFont(font_name, 90, bold=True)
        except:
            print(f"'{font_name}' fontu bulunamadı. Varsayılan font kullanılıyor.")
            self.font = pygame.font.SysFont(None, 40, bold=True)
            self.big_font = pygame.font.SysFont(None, 90, bold=True)
        # =======================================

        self.clock = pygame.time.Clock()
        self.puzzle_area_pos = (WINDOW_WIDTH - PUZZLE_BOARD_SIZE - Y_MARGIN, Y_MARGIN)

        self.background_image = None
        if os.path.exists(BACKGROUND_IMAGE_PATH):
            try:
                temp_img = pygame.image.load(BACKGROUND_IMAGE_PATH).convert_alpha()
                self.background_image = pygame.transform.scale(temp_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                print(f"Arka plan resmi yüklendi: {BACKGROUND_IMAGE_PATH}")
            except pygame.error as e:
                print(f"Arka plan resmi yüklenirken hata oluştu: {e}")
        else:
            print(f"Arka plan resmi bulunamadı: {BACKGROUND_IMAGE_PATH}")

        self.puzzle_display_area_rect = pygame.Rect(
            Y_MARGIN, Y_MARGIN,
            WINDOW_WIDTH - Y_MARGIN * 2, WINDOW_HEIGHT - Y_MARGIN * 2
        )
        self.puzzle_overlay_surface = pygame.Surface(self.puzzle_display_area_rect.size, pygame.SRCALPHA)
        self.puzzle_overlay_surface.fill((0, 0, 0, 150))

    def _draw_background(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(DARK_BLUE_BG)

    def draw_menu(self, hand_data, hovered_key=None):
        self._draw_background()

        title = self.big_font.render("DÜZEY SEÇİN", True, NEON_ORANGE)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        buttons = []
        labels = [("kolay", "KOLAY"), ("orta", "ORTA"), ("zor", "ZOR")]
        start_y = 240
        gap = 120
        for i, (key, label) in enumerate(labels):
            rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, start_y + i * gap, 400, 90)
            is_hover = (hovered_key == key)
            base_color = NEON_ORANGE if is_hover else NEON_BLUE

            pygame.draw.rect(self.screen, base_color, rect, border_radius=14)
            txt = self.font.render(label, True, WHITE)
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
            pygame.draw.rect(self.screen, NEON_GREEN if is_hover else NEON_BLUE, rect, 3 if is_hover else 2,
                             border_radius=14)
            buttons.append((key, rect))

        self._draw_cursor(hand_data)
        pygame.display.flip()
        return buttons

    def draw_game(self, hand_data, puzzle, game_state, elapsed_time):
        self._draw_background()
        self.screen.blit(self.puzzle_overlay_surface, self.puzzle_display_area_rect.topleft)

        ref_w = int(PUZZLE_BOARD_SIZE * 0.5)
        ref_image = pygame.transform.scale(puzzle.original_image, (ref_w, ref_w))
        self.screen.blit(ref_image, (Y_MARGIN, Y_MARGIN))
        pygame.draw.rect(self.screen, NEON_BLUE, (Y_MARGIN, Y_MARGIN, ref_w, ref_w), 2, border_radius=8)

        puzzle.draw(self.screen, self.puzzle_area_pos, show_blank=(game_state == 'WON'))
        self._draw_timer(elapsed_time)
        self._draw_cursor(hand_data)

        if game_state == 'WON':
            self._draw_win_screen(elapsed_time)

        pygame.display.flip()

    def draw_pause(self, hand_data, hovered_key=None):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render("DURDURULDU", True, NEON_ORANGE)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 120))

        buttons = {}
        labels = [("devam", "Devam Et"), ("yeniden", "Baştan Başlat"), ("menu", "Ana Menüye Dön")]
        btn_w, btn_h = 380, 80
        start_y = 300
        gap = 110

        for i, (key, label) in enumerate(labels):
            rect = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, start_y + i * gap, btn_w, btn_h)
            is_hover = (hovered_key == key)
            color = NEON_GREEN if is_hover else NEON_BLUE

            pygame.draw.rect(self.screen, color, rect, border_radius=14)
            txt = self.font.render(label, True, WHITE)
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
            buttons[key] = rect

        self._draw_cursor(hand_data)
        pygame.display.flip()
        return buttons

    def _draw_timer(self, time_seconds):
        minutes = int(time_seconds) // 60
        seconds = int(time_seconds) % 60
        time_text = f"{minutes:02}:{seconds:02}"
        text_surf = self.font.render(time_text, True, NEON_GREEN)
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, 40))
        self.screen.blit(text_surf, text_rect)

    def _draw_win_screen(self, final_time):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        win_text = self.big_font.render("TEBRİKLER!", True, NEON_ORANGE)
        win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(win_text, win_rect)

        minutes = int(final_time) // 60
        seconds = int(final_time) % 60
        time_str = f"Süre: {minutes:02}:{seconds:02}"
        time_text = self.font.render(time_str, True, NEON_GREEN)
        time_rect = time_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(time_text, time_rect)

    def _draw_cursor(self, hand_data):
        cursor_pos = hand_data.get("cursor_pos")
        if cursor_pos:
            if hand_data.get("pinch_active"):
                pygame.draw.circle(self.screen, NEON_ORANGE, cursor_pos, 18)
                pygame.draw.circle(self.screen, WHITE, cursor_pos, 22, 3)
            else:
                pygame.draw.circle(self.screen, NEON_GREEN, cursor_pos, 12, 3)

    def tick(self):
        self.clock.tick(FPS)