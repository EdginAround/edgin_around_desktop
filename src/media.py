import pyglet

from OpenGL import GL

from typing import Any, Iterable, List

IMAGE_NAMES_TILE: List[str] = ['grass', 'water']

DIR_INVENTORY: str = './res/inventory'
DIR_SPRITES: str = './res/sprites'
DIR_TILES: str = './res/tiles'


def format_image_name(dir_name: str, image_name: str) -> str:
    return f'{dir_name}/{image_name}.png'


class Textures:
    def __init__(self, image_names: Iterable[str], dir: str) -> None:
        self._images = {
                image_name: self._load_texture(dir, image_name) for image_name in image_names
            }

    def _load_texture(self, dir_name: str, image_name: str) -> int:
        image = pyglet.image.load(format_image_name(dir_name, image_name))
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
        self.tex: Any = Textures([], '')

    def load_tiles(self) -> None:
        self.tex = Textures(IMAGE_NAMES_TILE, DIR_TILES)

