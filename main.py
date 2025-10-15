import pygame
import sys
import os
import random
from settings import *
from hand_tracker import HandTracker
from ui_manager import UIManager
from puzzle_manager import PuzzleManager


def get_random_image_path_for_difficulty(difficulty):
    if difficulty == "kolay":
        folder = IMAGES_FOLDER_KOLAY
    elif difficulty == "zor":
        folder = IMAGES_FOLDER_ZOR
    else:
        folder = IMAGES_FOLDER_ORTA

    if not os.path.isdir(folder):
        return None
    supported = ['.png', '.jpg', '.jpeg']
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in supported]
    if not files:
        return None
    return os.path.join(folder, random.choice(files))


def load_image_safe(path):
    try:
        img = pygame.image.load(path)
        try:
            return img.convert_alpha()
        except Exception:
            return img.convert()
    except Exception as e:
        print("Resim yüklenemedi:", e)
        return None


def select_difficulty_screen(ui, tracker):
    """
    El kontrollü menu: kullanıcı sağ el ile hover ve pinch ile seçer.
    Döner: "kolay"/"orta"/"zor" veya None (çıkış).
    """
    last_pinch_time = 0
    pinch_cooldown = PINCH_COOLDOWN_MS
    running = True
    hovered = None

    while running:
        frame, hand_data = tracker.process_frame()
        cursor = hand_data.get("cursor_pos") if hand_data else None
        pinch_event = hand_data.get("pinch_event") if hand_data else 'NONE'
        pinch_active = hand_data.get("pinch_active") if hand_data else False

        buttons = ui.draw_menu(hand_data, hovered_key=hovered)

        hovered = None
        for key, rect in buttons:
            if cursor and rect.collidepoint(cursor):
                hovered = key
                break

        # If pinch_down and hovered -> select (cooldown apply)
        if pinch_event == 'PINCH_DOWN' and hovered:
            now = pygame.time.get_ticks()
            if now - last_pinch_time > pinch_cooldown:
                last_pinch_time = now
                return hovered

        # Sadece çıkış ve ESC tuşu için olay döngüsü
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

        ui.tick()

    return None


def pause_menu(ui, tracker):
    """
    Pause menu: göster, pinch ile butonlardan seçim yapılır.
    Döner: 'devam', 'yeniden', 'menu' veya 'quit'
    """
    last_pinch_time = 0
    pinch_cooldown = PINCH_COOLDOWN_MS

    while True:
        frame, hand_data = tracker.process_frame()
        cursor = hand_data.get("cursor_pos") if hand_data else None
        pinch_event = hand_data.get("pinch_event") if hand_data else 'NONE'
        buttons = ui.draw_pause(hand_data)

        hovered = None
        for key, rect in buttons.items():
            if cursor and rect.collidepoint(cursor):
                hovered = key
                break

        if pinch_event == 'PINCH_DOWN' and hovered:
            now = pygame.time.get_ticks()
            if now - last_pinch_time > pinch_cooldown:
                last_pinch_time = now
                return hovered

        # Sadece çıkış ve ESC tuşu için olay döngüsü
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        ui.tick()


def main():
    pygame.init()
    ui = UIManager()
    tracker = HandTracker()

    try:
        while True:
            difficulty = select_difficulty_screen(ui, tracker)
            if difficulty is None:
                break

            grid_map = {"kolay": 2, "orta": 3, "zor": 4}
            grid_size = grid_map.get(difficulty, 3)

            img_path = get_random_image_path_for_difficulty(difficulty)
            if img_path is None:
                print(
                    f"'{difficulty}' klasöründe resim bulunamadı. Lütfen '{IMAGES_FOLDER_ORTA}', '{IMAGES_FOLDER_KOLAY}', '{IMAGES_FOLDER_ZOR}' klasörlerini kontrol edin.")
                break

            image = load_image_safe(img_path)
            if image is None:
                print("Resim yüklenemedi, çıkılıyor.")
                break

            puzzle = PuzzleManager(image, grid_size=grid_size)

            game_state = "PLAYING"
            start_ticks = pygame.time.get_ticks()
            paused_time_accum = 0
            pause_started_at = None

            running = True
            while running:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        running = False
                        break

                frame, hand_data = tracker.process_frame()
                if frame is None:
                    print("Kamera hatası.")
                    running = False
                    break

                cursor = hand_data.get("cursor_pos")
                pinch_event = hand_data.get("pinch_event")
                pinch_active = hand_data.get("pinch_active")
                left_fist = hand_data.get("left_fist")

                if left_fist and game_state == "PLAYING":
                    game_state = "PAUSED"
                    pause_started_at = pygame.time.get_ticks()

                if game_state == "PAUSED":
                    choice = pause_menu(ui, tracker)
                    if choice == "devam":
                        game_state = "PLAYING"
                        if pause_started_at:
                            paused_time_accum += (pygame.time.get_ticks() - pause_started_at)
                            pause_started_at = None
                    elif choice == "yeniden":
                        puzzle = PuzzleManager(image, grid_size=grid_size)
                        game_state = "PLAYING"
                        start_ticks = pygame.time.get_ticks()
                        paused_time_accum = 0
                        pause_started_at = None
                    elif choice == "menu":
                        running = False
                        break
                    elif choice == "quit":
                        tracker.close()
                        pygame.quit()
                        sys.exit(0)
                    continue

                if game_state == "PLAYING":
                    elapsed_time = (pygame.time.get_ticks() - start_ticks - paused_time_accum) / 1000.0

                    if pinch_event == 'PINCH_DOWN' and cursor:
                        tile_pos = puzzle.get_tile_pos_from_screen(cursor, ui.puzzle_area_pos)
                        if tile_pos:
                            puzzle.move_tile(tile_pos)
                            if puzzle.is_solved():
                                game_state = "WON"
                                final_time = elapsed_time
                    ui.draw_game(hand_data, puzzle, game_state, elapsed_time)

                elif game_state == "WON":
                    ui.draw_game(hand_data, puzzle, game_state, final_time)
                    pygame.time.delay(1500)
                    running = False
                    break

                ui.tick()
    finally:
        tracker.close()
        pygame.quit()


if __name__ == "__main__":
    main()