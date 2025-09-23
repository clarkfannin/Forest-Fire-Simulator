import copy
import pygame
import random

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GREEN = (35, 101, 51)
ORANGE = (220, 108, 39)
RED = (240, 0, 0)
YELLOW = (186, 142, 43)
FIRE = [ORANGE, RED, YELLOW]
BLUE = (0, 150, 255)
(WIDTH, HEIGHT) = (640, 640)
CELL_COUNT = 16384
blockSize = 5
grid = []
water_positions = []



def main():
    pygame.init()
    pygame.display.set_caption('Forest Fire Simulator')
    global SCREEN, CLOCK
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(BLACK)
    pygame.display.flip()
    
    fillGridList()
    
    running = True
    time_since_last_call = 0
    while running:
        dt = CLOCK.tick(10)
        time_since_last_call += dt
        if time_since_last_call > 500:
            checkCells()
            time_since_last_call = 0
        drawGrid()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.update()
            
def fillGridList():
    global grid
    grid = [{"color": BLACK, "age": 0} for _ in range(CELL_COUNT)]
    cols = WIDTH // blockSize
    
    for i in range(CELL_COUNT):
        if random.random() < 0.9:
            grid[i] = {"color": GREEN, "age": 0, "hydration": 0}
            
    num_water_clusters = random.randint(30, 40)
    for _ in range (num_water_clusters):
        center_i = random.randint(0, CELL_COUNT - 1)
        cluster_size = random.randint(10, 30)
        
        for _ in range(cluster_size):
            center_x = center_i % cols
            center_y = center_i // cols
            
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            
            new_x = max(0, min(cols - 1, center_x + offset_x))
            new_y = max(0, min((CELL_COUNT // cols) - 1, center_y + offset_y))
            new_i = new_y * cols + new_x
            
            grid[new_i] = {"color": BLUE, "age": 0}
            water_positions.append((new_x, new_y))
        
    for i, cell in enumerate(grid):
        if cell["color"] == GREEN:
            cell_x = i % cols
            cell_y = i // cols
            max_hydration = 1
            min_distance = float('inf')
            for (water_x, water_y) in water_positions:
                distance = abs(cell_x - water_x) + abs(cell_y - water_y)
                if distance < min_distance:
                    min_distance = distance
            cell["hydration"] = max_hydration / (min_distance + 1)
        
    grid[random.randint(1, len(grid))] = {"color": random.choice(FIRE), "age": 0}
    
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
            alpha_value = int(cell["hydration"] * 200 + 100)
            alpha_value = min(255, max(0, alpha_value))
            surface.set_alpha(alpha_value)
            SCREEN.blit(surface, (x, y))
        else:
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(SCREEN, color, rect)
    
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
                if grid[neighbor_idx]["color"] in FIRE and random.random() > 0.5:
                    new_grid[i]["color"] = random.choice(FIRE)
                    new_grid[i]["age"] = 0
                    break
                
        elif grid[i]["color"] in FIRE:
            current_age = grid[i]["age"] + 1
            if current_age > 5:
                new_grid[i]["color"] = BLACK
                new_grid[i]["age"] = 0
            else:
                water_nearby = False
                for neighbor_idx in neighbors:
                    if grid[neighbor_idx]["color"] == BLUE:
                        new_grid[i]["color"] = BLACK
                        new_grid[i]["age"] = 0
                        water_nearby = True
                        break
                if not water_nearby:
                    new_grid[i]["color"] = random.choice(FIRE)
                    new_grid[i]["age"] = current_age
    
    grid = new_grid
    
if __name__ == "__main__":
    main()