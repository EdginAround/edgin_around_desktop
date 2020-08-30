import ctypes
import numpy
import tinyarray

from PIL import Image, ImageDraw, ImageFont
from OpenGL import GL

from typing import List

from . import formations


class ImageFileContent(formations.Content):
    def __init__(self, filename: str) -> None:
        image = Image.open(filename)
        data = numpy.array(list(image.getdata()), numpy.uint8)
        image.close()

        texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.size[0], image.size[1], 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, data,
        )

        super().__init__(formations.Size(image.size[0], image.size[1]), texture_id)

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)


class ImageFormation(formations.Formation):
    def __init__(self, size: formations.Size, texture_id: int) -> None:
        super().__init__()
        self.set_image(size, texture_id)

    def set_image(self, size: formations.Size, texture_id: int) -> None:
        content = formations.Content(size, texture_id)
        self.set_content(content)


class Label(formations.Formation):
    FONT = "DejaVuSans.ttf"

    def __init__(
            self,
            text='',
            margin=0,
            padding=4,
            fg_color=formations.Color(1.0, 1.0, 1.0, 1.0),
            bg_color=formations.Color(0.0, 0.0, 0.0, 1.0),
            font_size=12,
            gravity=formations.Gravity.START
        ) -> None:
        super().__init__()
        self._text = text
        self._margin = margin
        self._padding = padding
        self._fg_color = fg_color
        self._bg_color = bg_color
        self._font_size = font_size
        self._texture_id = GL.glGenTextures(1)
        self._font = ImageFont.truetype(self.FONT, self._font_size)
        self._gravity = gravity
        self._recreate()

    def set_margin(self, margin: int) -> None:
        self._margin = margin
        self._recreate()

    def set_padding(self, padding: int) -> None:
        self._padding = padding
        self._recreate()

    def set_bg_color(self, color: formations.Color) -> None:
        self._bg_color = color
        self._recreate()

    def set_fg_color(self, color: formations.Color) -> None:
        self._fg_color = color
        self._recreate()

    def set_text(self, text: str) -> None:
        self._text = text
        self._recreate()

    def set_gravity(self, gravity: formations.Gravity) -> None:
        self._gravity = gravity

    def resize(self, size: formations.Size) -> bool:
        resized = super().resize(size)
        if resized:
            self._recreate()
        return resized

    def _recreate(self) -> None:
        size = self.get_size()
        outer_width, outer_height = int(size.width), int(size.height)
        inner_width = int(size.width - 2 * self._margin)
        inner_height = int(size.height - 2 * self._margin)

        if inner_width < 1 or inner_height < 1:
            return

        bg_color = self._bg_color.to_256_tuple()
        fg_color = self._fg_color.to_256_tuple()

        text_width, text_height = self._font.getsize(self._text)
        if self._gravity == formations.Gravity.START:
            position = self._padding
        elif self._gravity == formations.Gravity.CENTER:
            position = 0.5 * (inner_width - text_width)
        elif self._gravity == formations.Gravity.END:
            position = inner_width - text_width

        image = Image.new('RGBA', (inner_width, inner_height), bg_color)
        draw = ImageDraw.Draw(image)
        draw.text((position, self._padding), self._text, fill=fg_color, font=self._font)

        # NOTE: Converting image data to numpy array has bad performance. `tinyarray` used here
        # seems to improve the performance.
        data1 = image.getdata()
        data2 = tinyarray.array(data1)
        data3 = numpy.array(data2)

        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, inner_width, inner_height, 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, data3,
        )

        self.set_content(formations.Content(size, self._texture_id))

    def calc_pref_width(self, height: float) -> float:
        text_width, text_height = self._font.getsize(self._text)
        return text_width + 2 * (self._margin + self._padding)

    def calc_pref_height(self, width: float) -> float:
        asscent, descent = self._font.getmetrics()
        return asscent + descent + 2 * (self._margin + self._padding)

    def prepare_plains(
            self,
            parent_position=formations.Position(0.0, 0.0),
        ) -> List[formations.Plain]:
        self._needs_update = False
        margin_size = 2 * self._margin
        margin_offset = formations.Position(self._margin, self._margin)
        position = parent_position + self._position + margin_offset
        size = formations.Size(self._size.width - margin_size, self._size.height - margin_size)
        return [formations.Plain(self._texture_id, None, position, size)]

