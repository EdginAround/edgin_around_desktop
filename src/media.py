import pyglet

from OpenGL import GL

from typing import Any, Iterable

IMAGE_NAMES = ('grass', 'water', 'hero', 'warior')


class Textures:
    def __init__(self, image_names: Iterable[str]) -> None:
        self._images = { image_name: self._load_texture(image_name) for image_name in image_names }

    def _load_texture(self, image_name: str) -> int:
        image = pyglet.image.load(f'res/images/{image_name}.png')
        texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.width, image.height, 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image.get_data()
        )
        return texture

    def __getitem__(self, key) -> int:
        return self._images[key]

    def __getattr__(self, key) -> int:
        return self._images[key]

class Media:
    def __init__(self) -> None:
        self.tex: Any = Textures([])

    def load_textures(self) -> None:
        self.tex = Textures(IMAGE_NAMES)

