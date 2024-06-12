import glfw
from OpenGL.GL import *

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 5
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Particle types
EMPTY = 0
SAND = 1
SOLID = 2

mouse_button_held = False
# Colors
colors = {
    EMPTY: (0.0, 0.0, 0.0),
    SAND: (1.0, 0.8, 0.4),
    SOLID: (0.5, 0.5, 0.5)
}

# Initialize grid
grid = [[EMPTY] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

def init_grid():
    # Fill grid with sand particles
    grid[GRID_HEIGHT//2:][:] = [[SAND] * GRID_WIDTH for _ in range(GRID_HEIGHT//2)]


def update_grid():
    global grid
    new_grid = [[EMPTY] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    
    # Apply gravity to sand particles
    for y in range(1, GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == SAND and (y == GRID_HEIGHT-1 or grid[y+1][x] == EMPTY):
                new_grid[y][x] = EMPTY
                new_grid[y-1][x] = SAND
    
    grid = new_grid

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    # Set up viewport
    glViewport(0, 0, WIDTH, HEIGHT)
    
    # Set up orthographic projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            glColor3f(*colors[grid[y][x]])
            glBegin(GL_QUADS)
            glVertex2f(x * CELL_SIZE, y * CELL_SIZE)
            glVertex2f((x + 1) * CELL_SIZE, y * CELL_SIZE)
            glVertex2f((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE)
            glVertex2f(x * CELL_SIZE, (y + 1) * CELL_SIZE)
            glEnd()
    
    glfw.swap_buffers(window)


def mouse_button_callback(window, button, action, mods):
    global mouse_button_held
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_button_held = True
            
        elif action == glfw.RELEASE:
            mouse_button_held = False
        x, y = glfw.get_cursor_pos(window)   
        
        # Convert mouse coordinates to grid coordinates
        grid_x = int(x // CELL_SIZE)
        grid_y = GRID_HEIGHT - 1 - int(y // CELL_SIZE)  # Invert y-axis to match grid orientation
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            grid[grid_y][grid_x] = SAND


def main():
    if not glfw.init():
        return
    
    global window
    window = glfw.create_window(WIDTH, HEIGHT, "Falling Sand Simulation", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    
    init_grid()
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        update_grid()
        render()
        
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)
    
    glfw.terminate()

if __name__ == "__main__":
    main()
