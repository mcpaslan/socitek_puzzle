"""
Projedeki tüm sabit ayarları ve konfigürasyonları bu dosyada tutacağız.
"""

# Pencere Ayarları
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Varsayılan GRID
GRID_SIZE = 3

# Puzzle ölçüleri (tahta boyutu pencere yüksekliğine göre)
Y_MARGIN = 60  # üst ve alt marj
PUZZLE_BOARD_SIZE = WINDOW_HEIGHT - (Y_MARGIN * 2)

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0)
NEON_GREEN = (50, 255, 50)     # Menü başlıkları için
NEON_ORANGE = (255, 165, 0)    # Vurgulu butonlar veya imleç için
NEON_BLUE = (0, 200, 255)      # Butonlar için
DARK_BLUE_BG = (10, 12, 25)    # Genel koyu arka plan (eğer resim yüklenemezse veya oyun alanı dışı için)

# Hand tracker ayarları (tuning için buradan değiştir)
PINCH_TRIGGER_LEVEL = 0.18
PINCH_RELEASE_LEVEL = 0.35
PINCH_COOLDOWN_MS = 400

FIST_AVG_DIST_THRESHOLD = 0.15

# Resim klasörleri (kullanıcının oluşturacağı klasörler)
IMAGES_FOLDER_KOLAY = "images/easy"
IMAGES_FOLDER_ORTA = "images/normal"
IMAGES_FOLDER_ZOR = "images/hard"

BACKGROUND_IMAGE_PATH = "bg/neon_bg.png"
