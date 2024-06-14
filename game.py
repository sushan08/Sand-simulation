import freetype
from OpenGL.GL import *
import glfw
from enum import Enum
import numpy as np
import threading
import subprocess
from text import Font
from constants import *
import random

class CellKind(Enum):
    EMPTY = 0
    SAND = 1
    SOLID = 2
    TNT = 3

class Game:
    def __init__(self):
        self.cells = np.full((GRID_HEIGHT, GRID_WIDTH), CellKind.EMPTY, dtype=object)
        self.mouse_pressed = False
        self.last_gravity_update = 0
        self.font = Font('8_bit_wonder.ttf', 24)
        self.menu_items = [("Start", (WIDTH // 2 - 100, HEIGHT // 2)), ("EXIT", (WIDTH // 2 - 100, HEIGHT // 2 - 60)),("SAND SIMULATION", (750,650))]
        self.game_items = [("Sand", (50, OPTIONS_Y)), ("Solid", (200, OPTIONS_Y)), ("Erase", (400, OPTIONS_Y)), ("TNT", (600, OPTIONS_Y))]
        self.in_menu = True
        self.current_tool = None
        self.selected_menu_item = None
        self.selected_game_item = CellKind.SAND

    def draw_cell(self, x, y, color):
        glColor3f(*color)
        glVertex2f(x * CELL_SIZE, y * CELL_SIZE)
        glVertex2f((x + 1) * CELL_SIZE, y * CELL_SIZE)
        glVertex2f((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE)
        glVertex2f(x * CELL_SIZE, (y + 1) * CELL_SIZE)

    def render(self):
        glBegin(GL_QUADS)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.get_color(self.cells[y][x])
                self.draw_cell(x, y, color)
        glEnd()

    def get_color(self, cell_kind):
        return {
            CellKind.EMPTY: BG_COLOR,
            CellKind.SAND: SAND_COLOR,
            CellKind.SOLID: SOLID_COLOR,
            CellKind.TNT: TNT_COLOR
        }.get(cell_kind, BG_COLOR)

    def update_cell(self, xpos, ypos, button):
        x = int(xpos // CELL_SIZE)
        y = int((HEIGHT - ypos) // CELL_SIZE)

        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            if button == glfw.MOUSE_BUTTON_RIGHT:
                if self.current_tool == CellKind.SAND and self.cells[y][x] == CellKind.SOLID:
                    return
                if self.current_tool == CellKind.TNT and y <= 1:
                    return
                self.cells[y][x] = self.current_tool

    def apply_gravity(self):
        for y in range(1, GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.cells[y][x] == CellKind.SAND:
                    if self.cells[y - 1][x] == CellKind.EMPTY:
                        self.cells[y][x] = CellKind.EMPTY
                        self.cells[y - 1][x] = CellKind.SAND
                    elif x > 0 and self.cells[y - 1][x + 1] == CellKind.EMPTY:
                        self.cells[y][x] = CellKind.EMPTY
                        self.cells[y - 1][x + 1] = CellKind.SAND
                    elif x < GRID_WIDTH - 1 and self.cells[y - 1][x - 1] == CellKind.EMPTY:
                        self.cells[y][x] = CellKind.EMPTY
                        self.cells[y - 1][x - 1] = CellKind.SAND
                elif self.cells[y][x] == CellKind.TNT:
                    if self.cells[y - 1][x] == CellKind.EMPTY:
                        if y <= 1:
                            self.cells[y][x] = CellKind.EMPTY
                            return
                        self.cells[y][x] = CellKind.EMPTY
                        self.cells[y - 1][x] = CellKind.TNT
                    elif self.cells[y - 1][x] == CellKind.SAND or self.cells[y - 1][x] == CellKind.SOLID:
                        self.cells[y][x] = CellKind.EMPTY
                        self.flood_fill(x, y - 1)
                    elif self.cells[y - 1][x - 1] == CellKind.SAND or self.cells[y][x - 1] == CellKind.SOLID:
                        self.cells[y][x] = CellKind.EMPTY
                        self.flood_fill(x - 1, y - 1)
                    elif self.cells[y - 1][x + 1] == CellKind.SAND or self.cells[y][x + 1] == CellKind.SOLID:
                        self.cells[y][x] = CellKind.EMPTY
                        self.flood_fill(x + 1, y - 1)

    def flood_fill(self, x, y):
        target = self.cells[y][x]
        iterations = random.choice(range(100))
        stack = [(x, y)]
        while stack and iterations:
            cx, cy = stack.pop()
            iterations -= 1
            if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT and self.cells[cy][cx] == target:
                self.cells[cy][cx] = CellKind.EMPTY
                stack.extend([(cx + 1, cy), (cx - 1, cy),
                              (cx, cy + 1), (cx, cy - 1),
                              (cx + 1, cy + 1), (cx - 1, cy - 1),
                              (cx + 1, cy - 1), (cx - 1, cy + 1)])

    def render_menu(self):
        for item, position in self.menu_items:
            self.font.render_text(position[0], position[1], item, gap=2, color=MENU_COLOR)

    def render_game_options(self):
        for item, position in self.game_items:
            color = HIGHLIGHT_COLOR if item == self.selected_game_item else TEXT_COLOR
            self.font.render_text(position[0], position[1], item, gap=5, color=color)

    def check_menu_click(self, xpos, ypos):
        ypos -= 24
        for item, position in self.menu_items:
            text_width = len(item) * 24
            if position[0] - 24 <= xpos <= (position[0] + text_width) and position[1] - 24 <= ypos <= (position[1] + 24):
                if item == "Start":
                    self.in_menu = False
                elif item == "EXIT":
                    glfw.set_window_should_close(window, True)
                self.selected_menu_item = item

    def check_game_option_click(self, xpos, ypos):
        ypos -= 24
        for item, position in self.game_items:
            text_width = len(item) * 24
            if position[0] <= xpos <= (position[0] + text_width) and position[1] - 24 <= ypos <= (position[1] + 24):
                if item == "Sand":
                    self.current_tool = CellKind.SAND
                elif item == "Solid":
                    self.current_tool = CellKind.SOLID
                elif item == "Erase":
                    self.current_tool = CellKind.EMPTY
                elif item == "TNT":
                    self.current_tool = CellKind.TNT
                self.selected_game_item = item

def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT or button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            game.mouse_pressed = True
            xpos, ypos = glfw.get_cursor_pos(window)
            ypos = HEIGHT - ypos
            if game.in_menu:
                game.check_menu_click(xpos, ypos)
            else:
                game.check_game_option_click(xpos, ypos)
        elif action == glfw.RELEASE:
            game.mouse_pressed = False

def cursor_position_callback(window, xpos, ypos):
    if game.mouse_pressed:
        game.update_cell(xpos, ypos, glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT))

def play_music(file):
    return subprocess.Popen(["ffplay", "-nodisp","-loop", "-1", "-autoexit","-af", "volume=0.15,afade=type=in:start_time=0:duration=10", file])


def main():
    global game, window
    game = Game()

    music_process = play_music("jam_jam.mp3")

    if not glfw.init():
        raise Exception("GLFW initialization failed")

    window = glfw.create_window(WIDTH, HEIGHT, "Cellular Automaton", None, None)
    if not window:
        glfw.terminate()
        music_process.terminate()  # Ensure music process is terminated
        raise Exception("Window creation failed")

    glfw.make_context_current(window)

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)

    last_time = glfw.get_time()
    while not glfw.window_should_close(window):
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        glViewport(0, 0, WIDTH, HEIGHT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        current_time = glfw.get_time()
        if (current_time - last_time) * 100 >= GRAVITY_DELAY:
            game.apply_gravity()
            last_time = current_time

        if game.in_menu:
            game.render_menu()
        else:
            game.render()
            game.render_game_options()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()
    music_process.terminate()  # Terminate music process when exiting

if __name__ == "__main__":
    main()
