import pygame as pg


BASE_BG_COLOR = (255, 255, 255)
BASE_HOVERED_COLOR = (173, 173, 173)
BASE_DISABLED_COLOR = (128, 128, 128)
BASE_CLICKED_COLOR = (36, 36, 36)
BASE_FOCUSED_COLOR = (44, 146, 230)


class ImageSprite(pg.sprite.Sprite):
    def __init__(self, pos: tuple, scale: float, group, image=None):
        super().__init__(group)
        self.image = pg.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
        self.rect = pg.rect.Rect(*pos, *self.image.get_size())


class SurfaceSprite(pg.sprite.Sprite):
    def __init__(self, pos: tuple, size: tuple, group, color, width=0, border_radius=False):
        super().__init__(group)
        self.pos, self.size = pos, size
        border_radius = min(*size) // 4 if border_radius else 0
        self.width, self.border_radius = width, border_radius
        self.color = color
        self.rect = pg.rect.Rect(*pos, *size)

    def draw(self, color: tuple = None):
        image = pg.surface.Surface(self.size, pg.SRCALPHA)
        color = self.color if not color else color
        pg.draw.rect(image, color, pg.rect.Rect(0, 0, *self.size), width=self.width,
                     border_radius=self.border_radius)
        self.image = image


class TextLabel:
    def __init__(self, text: str, font_family: str = 'standard', font_size=90, antialias=True,
                 color: tuple or pg.color.Color = BASE_BG_COLOR, full_font=None, italic=False, bold=False):
        self.text, self.antialias, self.color = text, antialias, color
        self.bold, self.italic = bold, italic
        if not full_font:
            if font_family == 'standard':
                full_font = pg.font.Font(None, font_size)
            else:
                full_font = pg.font.Font(font_family, font_size)
        full_font.bold = bold
        full_font.italic = italic
        self.font = full_font

    def render(self, text: str = None, color: tuple = None):
        return self.font.render(self.text if not text else text, self.antialias,
                                self.color if not color else color)

    def set_color(self, color: tuple):
        self.color = color

    def set_text(self, text: str):
        self.text = text


class InteractiveMixin:
    def __init__(self, disabled=False, disabled_color: tuple = BASE_DISABLED_COLOR,
                 hovered_color=BASE_HOVERED_COLOR, clicked_color=BASE_CLICKED_COLOR):
        self.disabled, self.disabled_color = disabled, disabled_color
        self.hovered_color, self.clicked_color = hovered_color, clicked_color

    def set_disabled(self, val: bool = True) -> None:
        self.disabled = val

    def handle_hover(self):
        pos = pg.mouse.get_pos()
        (x, y), (w, h) = self.pos, self.size
        if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
            self.hovered = True
        else:
            self.hovered = False


class Button(SurfaceSprite, InteractiveMixin):
    def __init__(self, pos: tuple, size: tuple, group, color: tuple or pg.color.Color, text_label: TextLabel,
                 func=None, args=(), scale_text=True, disabled=False, disabled_color=BASE_DISABLED_COLOR,
                 width=0, border_radius=False):

        SurfaceSprite.__init__(self, pos, size, group, color, width, border_radius)
        InteractiveMixin.__init__(self, disabled, disabled_color)
        self.func, self.args = func, args
        if scale_text:
            ...
        self.label = text_label.render()
        self.disabled_label = text_label.render(color=disabled_color)
        self.draw()

    def draw(self, color: tuple = None):
        SurfaceSprite.draw(self, color)
        self.image.blit(self.label, self.label.get_rect(center=(self.size[0] // 2, self.size[1] // 2)))

    def update(self, *args, **kwargs) -> None:
        super(Button, self).update(*args, **kwargs)
        if self.disabled:
            self.process_disabled()
            return

    def process_disabled(self):
        self.draw(self.disabled_color)
        self.image.blit(self.disabled_label,
                        self.disabled_label.get_rect(center=(self.size[0] // 2, self.size[1] // 2)))

    def handle_click(self):
        pos = pg.mouse.get_pos()
        (x, y), (w, h) = self.pos, self.size
        if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
            print('ok')
            if self.func:
                self.func(*self.args)


class LineEdit(SurfaceSprite, InteractiveMixin):
    def __init__(self, pos: tuple, size: tuple, group, color,
                 width=0, border_radius=False, disabled=False, disabled_color=BASE_DISABLED_COLOR,
                 placeholder=None, focused=False, focused_color=BASE_FOCUSED_COLOR,
                 hovered_color=BASE_HOVERED_COLOR):
        SurfaceSprite.__init__(self, pos, size, group, color, width, border_radius)
        InteractiveMixin.__init__(self, disabled, disabled_color, hovered_color)
        self.focused, self.focused_color = focused, focused_color
        self.placeholder = placeholder if placeholder else ''
        self.textlabel = TextLabel(self.placeholder,
                                   color=BASE_HOVERED_COLOR, italic=True)
        self.rendered_text = self.textlabel.render()
        self.text: str = self.textlabel.text
        self.draw()

    def draw(self, color: tuple = None):
        SurfaceSprite.draw(self, color)
        self.image.blit(self.rendered_text,
                        self.rendered_text.get_rect(center=(self.size[0] // 2, self.size[1] // 2)))

    def update(self, *args, **kwargs) -> None:
        super(LineEdit, self).update(*args, **kwargs)
        self.handle_hover()
        self.handle_click()
        if not self.focused and not self.text:
            self.textlabel.text = self.placeholder
            self.rendered_text = self.textlabel.render()
            self.draw()
        if self.disabled:
            return
        if self.focused:
            self.draw(self.focused_color)
            self.handle_keys()
        elif self.hovered:
            self.draw(self.hovered_color)
        else:
            self.draw(self.color)

    def handle_click(self):
        if self.hovered and pg.mouse.get_pressed()[0]:
            self.focused = True
        elif not self.hovered and pg.mouse.get_pressed()[0]:
            self.focused = False

    def handle_keys(self):
        prev_text = self.text
        text = ''
        backspaces = 0
        for e in pg.event.get(pg.KEYDOWN):
            if e.key == pg.K_BACKSPACE:
                backspaces += 1
            elif 32 <= e.key <= 126:
                text += e.unicode
            print(e.key)
        if prev_text == self.placeholder and text:
            self.text = text
        else:
            self.text += text
        self.text = self.text[:-backspaces] if backspaces else self.text
        if self.text != self.textlabel.text:
            self.textlabel.set_text(self.text)
            self.rendered_text = self.textlabel.render()

