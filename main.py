import copy
import pygame
import pygame.freetype
import random

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
blockSize = 4
CELL_COUNT = (WIDTH // blockSize) * (HEIGHT // blockSize)
grid = []
water_positions = []



def main():
    pygame.init()
    pygame.display.set_caption('Forest Fire Simulator')
    global SCREEN, CLOCK
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    CLOCK = pygame.time.Clock()
    my_font = pygame.freetype.SysFont('Comic Sans MS', 30)
    chinese_font = pygame.freetype.Font("NotoSansTC.ttf", 30)
    english_surface, _ = my_font.render('Someone has dropped a cigarette...', WHITE)
    chinese_surface, _ = chinese_font.render('有人掉了一根香菸…', WHITE)
    SCREEN.fill(BLACK)
    pygame.display.flip()
    
    margin = 20
    eng_rect = english_surface.get_rect()
    chi_rect = chinese_surface.get_rect()
    chi_rect.centerx = WIDTH // 2
    chi_rect.bottom = HEIGHT - margin
    eng_rect.centerx = WIDTH // 2
    eng_rect.bottom = chi_rect.top - 5
    
    fillGridList()
    
    running = True
    time_since_last_call = 0
    text_timer = 0
    text_fade_start = 8000
    text_fade_duration = 1000
    while running:
        dt = CLOCK.tick(60)
        time_since_last_call += dt
        text_timer += dt
        if time_since_last_call > 500:
            checkCells()
            time_since_last_call = 0
            drawGrid()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        if text_timer < text_fade_start:
            alpha = 255
        elif text_timer < text_fade_start + text_fade_duration:
            t = (text_timer - text_fade_start) / text_fade_duration
            alpha = max(0, 255 - int(t * 255))
        else:
            alpha = 0

        if alpha > 0:
            english_surface.set_alpha(alpha)
            chinese_surface.set_alpha(alpha)
            SCREEN.blit(english_surface, eng_rect)
            SCREEN.blit(chinese_surface, chi_rect)
        pygame.display.update()
            
def fillGridList():
    global grid
    grid = [{"color": BLACK, "age": 0} for _ in range(CELL_COUNT)]
    cols = WIDTH // blockSize

    water_positions.clear()
    
    for i in range(CELL_COUNT):
        grid[i] = {"color": GREEN, "age": 0, "hydration": 0}
            
    num_water_clusters = random.randint(5, 10)
    for _ in range (num_water_clusters):
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
            
            directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x = grow_x + dx
                new_y = grow_y + dy
                
                if (0 <= new_x < cols and 0 <= new_y < (CELL_COUNT // cols) 
                    and (new_x, new_y) not in water_cells):
                    
                    if random.random() > 0.3:
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

            max_hydration = 1.0 * random_factor
            cell["hydration"] = max_hydration / (min_distance + 1)

            base_max_distance = 60
            max_distance = base_max_distance * random_factor
            distance_ratio = min_distance / (min_distance + max_distance)  # in (0,1)
            cell["alpha"] = int(105 + (distance_ratio * 150))
            cell["alpha"] = min(255, max(105, cell["alpha"]))
        
    grid[random.randint(0, len(grid) - 1)] = {"color": random.choice(FIRE), "age": 0}
    
def drawGrid():
    SCREEN.fill(BLACK)
    cols = WIDTH // blockSize
    for i, cell in enumerate(grid):
        color = cell["color"]
        x = (i % cols) * blockSize
        y = (i // cols) * blockSize
        
        if color == GREEN:
            surface = pygame.Surface((blockSize, blockSize))
            surface.fill(GREEN)
            alpha_value = cell.get("alpha", 255)
            surface.set_alpha(alpha_value)
            SCREEN.blit(surface, (x, y))
        elif color == BLUE:
            surface = pygame.Surface((blockSize, blockSize))
            surface.fill(BLUE)
            surface.set_alpha(random.randrange(100, 255))
            SCREEN.blit(surface, (x, y))
        elif color in FIRE:
            surface = pygame.Surface((blockSize, blockSize))
            surface.fill(random.choice(FIRE))
            surface.set_alpha(random.randrange(200, 255))
            SCREEN.blit(surface, (x, y))
        elif color == BLACK:
            surface = pygame.Surface((blockSize, blockSize))
            random.seed(i)
            shade = random.randint(30, 120)
            random.seed()
            surface.fill((shade, shade, shade))
            surface.set_alpha(255)
            SCREEN.blit(surface, (x, y))
    
def checkCells():
    global grid
    cols = WIDTH // blockSize
    rows = HEIGHT // blockSize
    new_grid = copy.deepcopy(grid)
    
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
                if grid[neighbor_idx]["color"] in FIRE and random.random() > 0.93:
                    new_grid[i] = {"color": random.choice(FIRE), "age": 0}
                    break
                
        elif grid[i]["color"] in FIRE:
            current_age = grid[i]["age"] + 1
            if current_age > 5:
                new_grid[i] = {"color": BLACK, "age": 0}
            else:
                water_nearby = False
                for neighbor_idx in neighbors:
                    if grid[neighbor_idx]["color"] == BLUE:
                        new_grid[i] = {"color": BLACK, "age": 0}
                        water_nearby = True
                        break
                if not water_nearby:
                    new_grid[i] = {"color": random.choice(FIRE), "age": current_age}
    
    grid = new_grid
    
if __name__ == "__main__":
    main()