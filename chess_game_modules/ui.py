import pygame as pg
import sys

class Button:
    def __init__(self, rect, text, font, callback):
        self.rect = pg.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.hover = False

    def draw(self, surface, selected=False, special_style=False):
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        LIGHT_GRAY = (180, 180, 180)
        MEDIUM_GRAY = (80, 80, 80)
        OFF_WHITE = (240, 240, 240)
        if special_style:
            if self.hover:
                pg.draw.rect(surface, BLACK, self.rect)
                pg.draw.rect(surface, WHITE, self.rect, 4)
                text_color = WHITE
            else:
                pg.draw.rect(surface, MEDIUM_GRAY, self.rect)
                pg.draw.rect(surface, BLACK, self.rect, 4)
                text_color = WHITE
        elif selected:
            pg.draw.rect(surface, BLACK, self.rect)
            pg.draw.rect(surface, WHITE, self.rect, 3)
            text_color = WHITE
        else:
            if self.hover:
                pg.draw.rect(surface, LIGHT_GRAY, self.rect)
                pg.draw.rect(surface, BLACK, self.rect, 3)
            else:
                pg.draw.rect(surface, OFF_WHITE, self.rect)
                pg.draw.rect(surface, MEDIUM_GRAY, self.rect, 2)
            text_color = BLACK
        txt_surf = self.font.render(self.text, True, text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False

def settings_screen():
    pg.init()
    W, H = 1000, 750
    screen = pg.display.set_mode((W, H))
    pg.display.set_caption("Chess Settings")
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DARK_GRAY = (40, 40, 40)
    MEDIUM_GRAY = (80, 80, 80)
    LIGHT_GRAY = (180, 180, 180)
    OFF_WHITE = (240, 240, 240)
    title_font = pg.font.SysFont("Arial", 48, bold=True)
    section_font = pg.font.SysFont("Arial", 28, bold=True)
    button_font = pg.font.SysFont("Arial", 22, bold=True)
    board_sizes = [600, 800, 1000]
    difficulties = ["Easy", "Medium", "Hard"]
    colors = ["White", "Black"]
    selected_board_size = board_sizes[1]
    selected_diff = difficulties[1]
    selected_color = colors[0]
    buttons = []
    def make_select_handler(var_name, value):
        def handler():
            nonlocal selected_board_size, selected_diff, selected_color
            if var_name == "board":
                selected_board_size = value
            elif var_name == "diff":
                selected_diff = value
            elif var_name == "color":
                selected_color = value
        return handler
    panel_width = 850
    panel_height = 550
    panel_x = (W - panel_width) // 2
    panel_y = (H - panel_height) // 2
    btn_width = 200
    btn_height = 65
    btn_spacing = 45
    section_spacing = 125
    start_x = panel_x + (panel_width - (3 * btn_width + 2 * btn_spacing)) // 2
    board_y = panel_y + 140
    diff_y = board_y + section_spacing
    color_y = diff_y + section_spacing
    for i, size in enumerate(board_sizes):
        x = start_x + i * (btn_width + btn_spacing)
        rect = (x, board_y, btn_width, btn_height)
        buttons.append(Button(rect, f"{size}×{size}", button_font, make_select_handler("board", size)))
    for i, diff in enumerate(difficulties):
        x = start_x + i * (btn_width + btn_spacing)
        rect = (x, diff_y, btn_width, btn_height)
        buttons.append(Button(rect, diff, button_font, make_select_handler("diff", diff)))
    for i, color in enumerate(colors):
        x = start_x + i * (btn_width + btn_spacing)
        rect = (x, color_y, btn_width, btn_height)
        color_text = f"Play as {color}"
        buttons.append(Button(rect, color_text, button_font, make_select_handler("color", color)))
    play_rect = (W//2 - 130, color_y + 140, 260, 85)
    play_button = Button(play_rect, "START GAME", section_font, lambda: None)
    buttons.append(play_button)
    running = True
    clock = pg.time.Clock()
    while running:
        clock.tick(60)
        screen.fill(BLACK)
        panel_rect = (panel_x, panel_y, panel_width, panel_height)
        pg.draw.rect(screen, WHITE, panel_rect)
        pg.draw.rect(screen, BLACK, panel_rect, 4)
        square_size = 20
        for corner_x, corner_y in [(50, 50), (W-150, 50), (50, H-150), (W-150, H-150)]:
            for i in range(5):
                for j in range(5):
                    x = corner_x + i * square_size
                    y = corner_y + j * square_size
                    color = WHITE if (i + j) % 2 == 0 else DARK_GRAY
                    pg.draw.rect(screen, color, (x, y, square_size, square_size))
            pattern_rect = (corner_x, corner_y, 5 * square_size, 5 * square_size)
            pg.draw.rect(screen, BLACK, pattern_rect, 2)
        title_text = "CHESS SETTINGS"
        title_surf = title_font.render(title_text, True, BLACK)
        title_x = W // 2 - title_surf.get_width() // 2
        title_y = panel_y + 40
        screen.blit(title_surf, (title_x, title_y))
        sections = [
            ("BOARD SIZE", board_y - 50),
            ("DIFFICULTY", diff_y - 50),
            ("PLAYER COLOR", color_y - 50)
        ]
        for section_text, y in sections:
            section_surf = section_font.render(section_text, True, BLACK)
            section_x = W // 2 - section_surf.get_width() // 2
            screen.blit(section_surf, (section_x, y))
        mouse_pos = pg.mouse.get_pos()
        for btn in buttons:
            btn.check_hover(mouse_pos)
            selected = False
            if "×" in btn.text and f"{selected_board_size}" in btn.text:
                selected = True
            elif btn.text in difficulties and selected_diff == btn.text:
                selected = True
            elif "Play as" in btn.text and selected_color in btn.text:
                selected = True
            elif btn == play_button:
                if btn.hover:
                    pg.draw.rect(screen, BLACK, btn.rect)
                    pg.draw.rect(screen, WHITE, btn.rect, 4)
                    text_color = WHITE
                else:
                    pg.draw.rect(screen, DARK_GRAY, btn.rect)
                    pg.draw.rect(screen, BLACK, btn.rect, 4)
                    text_color = WHITE
                text_surf = btn.font.render(btn.text, True, text_color)
                text_rect = text_surf.get_rect(center=btn.rect.center)
                screen.blit(text_surf, text_rect)
                continue
            if selected:
                pg.draw.rect(screen, BLACK, btn.rect)
                pg.draw.rect(screen, WHITE, btn.rect, 3)
                text_surf = btn.font.render(btn.text, True, WHITE)
            else:
                if btn.hover:
                    pg.draw.rect(screen, LIGHT_GRAY, btn.rect)
                    pg.draw.rect(screen, BLACK, btn.rect, 3)
                else:
                    pg.draw.rect(screen, OFF_WHITE, btn.rect)
                    pg.draw.rect(screen, MEDIUM_GRAY, btn.rect, 2)
                text_surf = btn.font.render(btn.text, True, BLACK)
            text_rect = text_surf.get_rect(center=btn.rect.center)
            screen.blit(text_surf, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(0)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn.check_click(event.pos):
                        if btn is play_button:
                            running = False
                        break
        pg.display.flip()
    return selected_board_size, selected_diff, selected_color
