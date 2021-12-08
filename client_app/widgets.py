import pygame as pg
from utils import *
from render import Vector2

BASE_BG_COLOR = (255, 255, 255)
BASE_HOVERED_COLOR = (173, 173, 173)
BASE_DISABLED_COLOR = (128, 128, 128)
BASE_CLICKED_COLOR = (36, 36, 36)
BASE_FOCUSED_COLOR = (44, 146, 230)
ALPHA_COLOR = pg.SRCALPHA


class ImageSprite(pg.sprite.Sprite):
    def __init__(self, pos: tuple, scale: float, image=None, group=None):
        super().__init__(group if group else [])
        self.pos, self.scale = pos, scale
        self.image = pg.transform.scale(image,
                                        (image.get_width() * scale, image.get_height() * scale))
        self.rect = pg.rect.Rect(*pos, *self.image.get_size())

    def resize(self, k):
        self.pos[0] *= k
        self.pos[1] *= k
        self.scale *= k


class SurfaceSprite(pg.sprite.Sprite):
    def __init__(self, pos: tuple, size: tuple, color, border_color=None, width=0,
                 border_radius: bool or int = False, group=None):
        """border radius: if false - 0; if true - min(*size) // 4; if int - value"""
        super().__init__(group if group is not None else [])
        self.pos, self.size = pos, size
        if type(border_radius) in (int, float):
            self.border_radius = int(border_radius)
        elif type(border_radius) == bool:
            self.border_radius = min(*size) // 4 if border_radius else 0
        self.width = width
        self.color = color
        self.border_color = border_color if border_color else ALPHA_COLOR
        self.rect = pg.rect.Rect(*pos, *size)

    def draw(self, color: tuple = None, border_color: tuple = None):  # means render
        image = pg.surface.Surface(self.size, masks=self.color)
        border_color = border_color if border_color else self.border_color
        pg.draw.rect(image, border_color, pg.rect.Rect(0, 0, *self.size), width=self.width,
                     border_radius=self.border_radius)
        self.image = image

    def resize(self, k):
        self.pos[0] *= k
        self.pos[1] *= k
        self.size[0] *= k
        self.size[1] *= k
        self.width, self.border_radius = self.width * k, self.border_radius * k


class BaseGroup:
    def __init__(self, *sprites):
        self.sprites = sprites

    def add(self, *sprites):
        self.sprites += [sprites]

    def clear(self):
        self.sprites = []

    def resize(self, k):
        for s in self.sprites:
            try:
                s.resize(k)
            except AttributeError:
                ...


class Text:
    def __init__(self, text: str, font_family: str = 'standard', font_size=90, antialias=True,
                 border_color: tuple or pg.color.Color = BASE_BG_COLOR, full_font=None, italic=False,
                 bold=False):  # TODO -> color
        self.text, self.antialias, self.border_color = text, antialias, border_color
        self.bold, self.italic = bold, italic
        if not full_font:
            if font_family == 'standard':
                full_font = pg.font.Font(None, font_size)
            else:
                full_font = pg.font.Font(font_family, font_size)
        full_font.bold = bold
        full_font.italic = italic
        self.font = full_font

    def render(self, text: str = None, border_color: tuple = None):  # TODO : -> color
        return self.font.render(self.text if not text else text, self.antialias,
                                self.border_color if not border_color else border_color)

    def set_color(self, border_color: tuple):
        self.border_color = border_color

    def set_text(self, text: str):
        self.text = text

    def set_italic(self, val: bool = True):
        self.font.set_italic(val)


class Label(SurfaceSprite):
    def __init__(self, pos: tuple, size: tuple, text: Text, color, border_color=None, width=0,
                 border_radius: bool or int = False, group=None):
        super().__init__(pos, size, color, border_color=border_color,
                         width=width, border_radius=border_radius,
                         group=group if group is not None else [])
        self.text = text
        self.draw()

    def draw(self, color: tuple = None, border_color: tuple = None):
        super(Label, self).draw(color, border_color)
        rendered = self.text.render()
        self.image.blit(rendered,
                        rendered.get_rect(center=(self.size[0] // 2, self.size[1] // 2)))

    def update(self):
        self.draw()


class InteractiveMixin:
    def __init__(self, disabled=False, disabled_color: tuple = BASE_DISABLED_COLOR,
                 hovered_color=BASE_HOVERED_COLOR, clicked_color=BASE_CLICKED_COLOR):
        self.disabled, self.disabled_color = disabled, disabled_color
        self.hovered_color, self.clicked_color = hovered_color, clicked_color
        self.hovered = False

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
    def __init__(self, pos: tuple, size: tuple, color: tuple or pg.color.Color,
                 label: Text or pg.Surface, func=None, args=(),
                 border_color: tuple or pg.color.Color = None,
                 group=None, scale_text=True, disabled=False, disabled_color=BASE_DISABLED_COLOR,
                 width=0, border_radius=False, hovered_color=BASE_HOVERED_COLOR,
                 paddings_factor: tuple = (1.2, 1.2)):
        """size: if true - fit content | paddings: (horizontal, vertical)"""
        InteractiveMixin.__init__(self, disabled, disabled_color, hovered_color)
        self.func, self.args = func, args
        if scale_text:
            ...
        if isinstance(label, Text):
            self.text_label = label
            self.label = self.text_label.render()
            self.mode = 't'
        elif isinstance(label, pg.Surface):
            self.label = label
            self.mode = 'i'
        else:
            raise TypeError
        if size[0] is True:
            size = (int(self.label.get_width() * paddings_factor[0]), size[1])
        if size[1] is True:
            size = (size[0], int(self.label.get_height() * paddings_factor[1]))
        if type(size) == tuple and self.mode == 'i':
            self.label = pg.transform.smoothscale(self.label, (min(size), min(size)))
        SurfaceSprite.__init__(self, pos, size, color, width=width, border_radius=border_radius,
                               # important 2 place here
                               border_color=border_color,
                               group=group if group is not None else [])
        self.size = size
        self.draw()
        self.base_label = self.label.copy()
        self.hovered_label = changeColor(self.image, self.hovered_color)
        self.disabled_label = changeColor(self.image, self.disabled_color)

    def draw(self, color: tuple = None, border_color: tuple = None):
        SurfaceSprite.draw(self, color, border_color)  # super.draw
        if self.mode == 't':
            self.image.blit(self.label,
                            self.label.get_rect(center=(self.size[0] // 2, self.size[1] // 2)))
        elif self.mode == 'i':
            self.image.blit(self.label,
                            self.label.get_rect())

    def update(self, *args, **kwargs) -> None:
        super(Button, self).update(*args, **kwargs)
        self.handle_hover()
        if self.disabled:
            self.label = self.disabled_label
            return
        # if self.mode == 't':
        #     if self.hovered:
        #         self.current_color = self.hovered_color
        #         self.label = self.text_label.render(border_color=self.hovered_color)
        #     elif self.current_color != self.border_color:
        #         self.current_color = self.border_color
        #         self.label = self.text_label.render()
        # elif self.mode == 'i':
        elif self.hovered:
            self.label = self.hovered_label
        elif self.label != self.base_label:
            self.label = self.base_label

        self.handle_click()
        self.draw()

    # def set_disabled(self, val: bool = True) -> None:
    #     super(Button, self).set_disabled(val)
    #     self.current_color = self.disabled_color
    #     self.label = self.text_label.render(border_color=self.disabled_color)

    def handle_click(self):
        if self.hovered and self.func:
            for _ in pg.event.get(pg.MOUSEBUTTONUP):
                self.func(*self.args)


class LineEdit(SurfaceSprite, InteractiveMixin):  # TODO: make placeholder non editable
    def __init__(self, pos: tuple, size: tuple, color, border_color, group=None,
                 width=0, border_radius=False, disabled=False,
                 disabled_color=BASE_DISABLED_COLOR,
                 placeholder=None, focused=False, focused_color=BASE_FOCUSED_COLOR,
                 hovered_color=BASE_HOVERED_COLOR,
                 full_font: pg.font.Font or pg.font.SysFont = None):
        SurfaceSprite.__init__(self, pos, size, color, width=width, border_radius=border_radius,
                               border_color=border_color, group=group if group else [])
        InteractiveMixin.__init__(self, disabled, disabled_color, hovered_color)
        self.focused, self.focused_color = focused, focused_color
        self.placeholder = placeholder if placeholder else ''
        self.textlabel = Text(self.placeholder,
                              border_color=BASE_HOVERED_COLOR, italic=True, full_font=full_font)
        self.rendered_text = self.textlabel.render()
        self.text: str = self.textlabel.text
        self.draw()

    def draw(self, color: tuple = None, border_color: tuple = None):
        SurfaceSprite.draw(self, color, border_color)
        self.image.blit(self.rendered_text,
                        self.rendered_text.get_rect(
                            center=(self.size[0] // 2, self.size[1] // 2)))

    def update(self, *args, **kwargs) -> None:
        super(LineEdit, self).update(*args, **kwargs)
        self.handle_hover()
        self.handle_click()
        if not self.focused and not self.text:
            self.textlabel.text = self.placeholder
            self.text = self.placeholder
            self.textlabel.set_italic()
            self.rendered_text = self.textlabel.render()
        if self.disabled:
            return
        if self.focused:
            cur_bg_color = self.focused_color
            self.handle_keys()
        elif self.hovered:
            cur_bg_color = self.hovered_color
        else:
            cur_bg_color = self.border_color
        self.draw(border_color=cur_bg_color)

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
        if prev_text == self.placeholder and text:  # if before writing was placeholder and u wrote smth
            self.text = text
            self.textlabel.set_italic(False)
        else:
            self.text += text
        self.text = self.text[:-backspaces] if backspaces else self.text
        if self.text != self.textlabel.text:
            self.textlabel.set_text(self.text)
            self.rendered_text = self.textlabel.render()

    def set_text(self, text):
        self.textlabel.set_text(text)
