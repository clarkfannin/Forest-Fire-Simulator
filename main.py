# /// script
# dependencies = [
#     "asyncio",
#     "pygame-ce",
# ]
# ///
import asyncio
import pygame
import random
import math

BLACK = (0, 0, 0)
GREY = (128, 128, 128)
WHITE = (200, 200, 200)
GREEN = (35, 101, 51)
ORANGE = (220, 108, 39)
RED = (240, 0, 0)
YELLOW = (186, 142, 43)
FIRE = [ORANGE, RED, YELLOW]
BLUE = (0, 150, 255)
(WIDTH, HEIGHT) = (640, 640)
BLOCK_SIZE = 4
CELL_COUNT = (WIDTH // BLOCK_SIZE) * (HEIGHT // BLOCK_SIZE)
SPEED = 50
BASE_SPREAD_CHANCE = 0.07
HYDRATION_RESISTANCE = 1.5
grid = []
water_positions = []
text_options = [
    ("Someone has dropped a cigarette...", "有人掉了一根香菸..."),
    ("A cigarette has been dropped...", "一支香菸掉了..."),
    ("Someone has forgotten their campfire...", "有人忘了他們的營火..."),
]
ending_text = ["The forest rests...", "森林休息..."]
text_timer = 0
game_started = False

my_font = None
chinese_font = None
small_font = None

eng_text = ""
chi_text = ""
english_surface = None
chinese_surface = None
eng_rect = None
chi_rect = None

# Simple UI class for buttons
class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = WHITE
        self.visible = True
        
    def draw(self, surface):
        if not self.visible:
            return
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, pos):
        return self.visible and self.rect.collidepoint(pos)

# Simple slider class
class Slider:
    def __init__(self, x, y, width, label, min_val, max_val, start_val, font):
        self.rect = pygame.Rect(x, y, width, 10)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.font = font
        self.dragging = False
        self.visible = True
        self.handle_radius = 8
        
    def get_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        x = self.rect.x + int(ratio * self.rect.width)
        y = self.rect.centery
        return (x, y)
    
    def draw(self, surface):
        if not self.visible:
            return
        # Draw label
        label_surf = self.font.render(self.label, True, WHITE)
        surface.blit(label_surf, (self.rect.x - 100, self.rect.y - 5))
        
        # Draw track
        pygame.draw.rect(surface, GREY, self.rect)
        
        # Draw handle
        handle_pos = self.get_handle_pos()
        pygame.draw.circle(surface, WHITE, handle_pos, self.handle_radius)
        pygame.draw.circle(surface, (100, 100, 100), handle_pos, self.handle_radius, 2)
    
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_pos = self.get_handle_pos()
            dist = math.sqrt((event.pos[0] - handle_pos[0])**2 + (event.pos[1] - handle_pos[1])**2)
            if dist <= self.handle_radius:
                self.dragging = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                x = max(self.rect.x, min(event.pos[0], self.rect.right))
                ratio = (x - self.rect.x) / self.rect.width
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
                return True
        return False


async def main():
    pygame.init()
    pygame.display.set_caption('Forest Fire Simulator')
    global SCREEN, CLOCK, SPEED, BASE_SPREAD_CHANCE, HYDRATION_RESISTANCE, game_started, text_timer, eng_text, chi_text, english_surface, chinese_surface, eng_rect, chi_rect, my_font, chinese_font, small_font
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    CLOCK = pygame.time.Clock()
    
    try:
        my_font = pygame.font.Font('Arial.ttf', 30)
        chinese_font = pygame.font.Font('NotoSansTC.ttf', 30)
        small_font = pygame.font.Font('Arial.ttf', 14)
    except Exception as e:
        print(f"Error loading fonts: {e}")
        print("Make sure Arial.ttf and NotoSansTC.ttf are in the project directory")
        pygame.quit()
        exit(1)
    
    start_button = Button(270, 290, 100, 50, 'Start Fire', small_font)
    
    slider_width = 150
    slider_x = WIDTH - slider_width - 30
    slider_start_y = 20
    slider_spacing = 40
    
    speed_slider = Slider(slider_x, slider_start_y, slider_width, "Speed:", 1, 100, 50, small_font)
    spread_slider = Slider(slider_x, slider_start_y + slider_spacing, slider_width, "Spread:", 0.01, 0.1, BASE_SPREAD_CHANCE, small_font)
    hydr_slider = Slider(slider_x, slider_start_y + 2 * slider_spacing, slider_width, "Hydration:", 1, 100, 50, small_font)
    
    speed_slider.visible = False
    spread_slider.visible = False
    hydr_slider.visible = False

    eng_text, chi_text = random.choice(text_options)

    SCREEN.fill(BLACK)
    pygame.display.flip()

    running = True
    time_since_last_call = 0
    text_fade_start = 5000
    text_fade_duration = 1000
    showing_ending = False

    def update():
        nonlocal text_fade_duration, showing_ending
        checkCells()

    while running:
        dt = CLOCK.tick(20)
        time_since_last_call += dt
        if time_since_last_call > SPEED:
            if game_started:
                text_timer += dt
                update()
            time_since_last_call = 0
            drawGrid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(event.pos):
                    start_button.visible = False
                    speed_slider.visible = True
                    spread_slider.visible = True
                    hydr_slider.visible = True
                    game_started = True
                    fillGridList()
                    initFont()
                elif game_started:
                    if eng_text == ending_text[0]:
                        eng_text = ""
                        chi_text = ""
                        english_surface = my_font.render(eng_text, True, WHITE)
                        chinese_surface = chinese_font.render(chi_text, True, WHITE)
                        SCREEN.fill(BLACK)
                        drawGrid()
                        pygame.display.flip()
                    else:
                        cols = WIDTH // BLOCK_SIZE
                        mouse_x, mouse_y = event.pos
                        grid_x = mouse_x // BLOCK_SIZE
                        grid_y = mouse_y // BLOCK_SIZE
                        index = grid_y * cols + grid_x
                        if 0 <= index < len(grid):
                            grid[index] = {"color": random.choice(FIRE), "age": 0}
            
            if speed_slider.handle_event(event):
                slider_value = speed_slider.value
                SPEED = int(501 - (slider_value * 5))
                
            if spread_slider.handle_event(event):
                BASE_SPREAD_CHANCE = spread_slider.value
                
            if hydr_slider.handle_event(event):
                slider_value = hydr_slider.value
                if slider_value == 1:
                    HYDRATION_RESISTANCE = 0.001
                else:
                    log_min = -3
                    log_max = 0.7
                    log_value = log_min + (slider_value / 100) * (log_max - log_min)
                    HYDRATION_RESISTANCE = 10 ** log_value

        current_time = text_timer

        start_button.draw(SCREEN)
        speed_slider.draw(SCREEN)
        spread_slider.draw(SCREEN)
        hydr_slider.draw(SCREEN)

        if showing_ending:
            alpha = 255
        else:
            if current_time < text_fade_start:
                alpha = 255
            elif current_time < text_fade_start + text_fade_duration:
                t = (current_time - text_fade_start) / text_fade_duration
                alpha = max(0, 255 - int(t * 255))
            else:
                alpha = 0
                if not any(cell["color"] in FIRE for cell in grid):
                    showing_ending = True
                    eng_text = ending_text[0]
                    chi_text = ending_text[1]
                    initFont()

        if (english_surface and chinese_surface) and (alpha > 0 or showing_ending):
            temp_eng = english_surface.copy()
            temp_chi = chinese_surface.copy()

            temp_eng.set_alpha(alpha if not showing_ending else 255)
            temp_chi.set_alpha(alpha if not showing_ending else 255)

            SCREEN.blit(temp_eng, eng_rect)
            SCREEN.blit(temp_chi, chi_rect)

        await asyncio.sleep(0)
        pygame.display.update()


def initFont():
    global english_surface, chinese_surface, eng_rect, chi_rect
    english_surface = my_font.render(eng_text, True, WHITE)
    chinese_surface = chinese_font.render(chi_text, True, WHITE)
    margin = 20
    eng_rect = english_surface.get_rect()
    chi_rect = chinese_surface.get_rect()
    chi_rect.centerx = WIDTH // 2
    chi_rect.bottom = HEIGHT - margin
    eng_rect.centerx = WIDTH // 2
    eng_rect.bottom = chi_rect.top - 5


def fillGridList():
    global grid
    grid = [{"color": BLACK, "age": 0} for _ in range(CELL_COUNT)]
    cols = WIDTH // BLOCK_SIZE

    water_positions.clear()

    for i in range(CELL_COUNT):
        grid[i] = {"color": GREEN, "age": 0, "hydration": 0}

    num_water_clusters = random.randint(5, 10)
    for _ in range(num_water_clusters):
        center_i = random.randint(0, CELL_COUNT - 1)
        center_x = center_i % cols
        center_y = center_i // cols

        pool_size = random.randint(30, 2000)
        water_cells = set()

        water_cells.add((center_x, center_y))

        for _ in range(pool_size):
            if not water_cells:
                break

            grow_from = random.choice(list(water_cells))
            grow_x, grow_y = grow_from

            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (1, 1), (-1, 1), (1, -1)]
            random.shuffle(directions)

            for dx, dy in directions:
                new_x = grow_x + dx
                new_y = grow_y + dy

                if (0 <= new_x < cols and 0 <= new_y < (CELL_COUNT // cols)
                        and (new_x, new_y) not in water_cells):

                    if random.random() > 0.7:
                        water_cells.add((new_x, new_y))
                        break

        for water_x, water_y in water_cells:
            new_i = water_y * cols + water_x
            grid[new_i] = {"color": BLUE, "age": 0}
            water_positions.append((water_x, water_y))

    for i, cell in enumerate(grid):
        if cell["color"] == GREEN:
            cell_x = i % cols
            cell_y = i // cols

            random.seed(i)
            random_factor = random.uniform(0.7, 1.3)
            random.seed()

            min_distance = float('inf')
            for (water_x, water_y) in water_positions:
                distance = abs(cell_x - water_x) + abs(cell_y - water_y)
                if distance < min_distance:
                    min_distance = distance

            max_hydration = 0.8
            base_hydration = 0.1
            decay_factor = 0.08
            cell["hydration"] = base_hydration + \
                (max_hydration - base_hydration) * \
                math.exp(-min_distance * decay_factor)

            base_max_distance = 60
            max_distance = base_max_distance * random_factor
            distance_ratio = min_distance / (min_distance + max_distance)
            cell["alpha"] = int(105 + (distance_ratio * 150))
            cell["alpha"] = min(255, max(105, cell["alpha"]))

    fire_cell = random.randint(0, len(grid) - 1)
    if grid[fire_cell]["color"] == GREEN:
        grid[fire_cell] = {"color": random.choice(FIRE), "age": 0}


def drawGrid():
    SCREEN.fill(BLACK)
    cols = WIDTH // BLOCK_SIZE
    for i, cell in enumerate(grid):
        color = cell["color"]
        x = (i % cols) * BLOCK_SIZE
        y = (i // cols) * BLOCK_SIZE

        if color == GREEN:
            surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            surface.fill(GREEN)
            alpha_value = cell.get("alpha", 255)
            surface.set_alpha(alpha_value)
            SCREEN.blit(surface, (x, y))
        elif color == BLUE:
            surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            surface.fill(BLUE)
            surface.set_alpha(random.randrange(100, 255))
            SCREEN.blit(surface, (x, y))
        elif color in FIRE:
            surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            surface.fill(random.choice(FIRE))
            surface.set_alpha(random.randrange(200, 255))
            SCREEN.blit(surface, (x, y))
        elif color == BLACK:
            surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            random.seed(i)
            shade = random.randint(30, 120)
            random.seed()
            surface.fill((shade, shade, shade))
            surface.set_alpha(255)
            SCREEN.blit(surface, (x, y))


def checkCells():
    global eng_text, chi_text, english_surface, chinese_surface, eng_rect, chi_rect, text_timer, grid
    cols = WIDTH // BLOCK_SIZE
    rows = HEIGHT // BLOCK_SIZE

    changes = []

    for i in range(len(grid)):
        current_row = i // cols
        current_col = i % cols

        neighbors = []

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row = current_row + dr
                new_col = current_col + dc

                if 0 <= new_row < rows and 0 <= new_col < cols:
                    neighbor_idx = new_row * cols + new_col
                    neighbors.append(neighbor_idx)

        if grid[i]["color"] == GREEN:
            for neighbor_idx in neighbors:
                hydration = grid[i].get("hydration", 0)
                if grid[neighbor_idx]["color"] in FIRE:
                    spread_probability = BASE_SPREAD_CHANCE * \
                        (1 - hydration * HYDRATION_RESISTANCE)

                    if random.random() < spread_probability:
                        changes.append(
                            (i, {"color": random.choice(FIRE), "age": 0}))
                        break

        elif grid[i]["color"] in FIRE:
            current_age = grid[i]["age"] + 1
            if current_age > 12:
                changes.append((i, {"color": BLACK, "age": 0}))
            else:
                water_nearby = False
                for neighbor_idx in neighbors:
                    if grid[neighbor_idx]["color"] == BLUE:
                        if random.random() < 0.99:
                            changes.append((i, {"color": BLACK, "age": 0}))
                            water_nearby = True
                            break
                if not water_nearby:
                    changes.append(
                        (i, {"color": random.choice(FIRE), "age": current_age}))

    for i, new_data in changes:
        grid[i].update(new_data)


asyncio.run(main())