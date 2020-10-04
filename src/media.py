import os
import pyglet

from OpenGL import GL

from typing import Any, Dict, Iterable, List, Set, Tuple

IMAGE_NAMES_TILE: List[str] = ['grass', 'water']
IMAGE_NAMES_INVENTORY: List[str] = [
    'axe', 'empty_slot', 'gold', 'hat', 'left_hand', 'log', 'raw_meat', 'right_hand', 'rocks',
]

DIR_INVENTORY: str = './res/inventory'
DIR_SPRITES: str = './res/sprites'
DIR_TILES: str = './res/tiles'


def _load_texture(file_path: str) -> int:
    image = pyglet.image.load(file_path)
    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.width, image.height, 0,
        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image.get_data()
    )
    return texture


class Textures:
    def __init__(self, image_names: Iterable[str], dir: str) -> None:
        self._images = {
                image_name: self._load_texture(dir, image_name) for image_name in image_names
            }

    def change_texture(self, name: str, texture_id: int) -> None:
        self._images[name] = texture_id

    def _load_texture(self, dir_name: str, image_name: str) -> int:
        return _load_texture(os.path.join(dir_name, f'{image_name}.png'))

    def __getitem__(self, key) -> int:
        return self._images[key]

    def __getattr__(self, key) -> int:
        return self._images[key]


class Skins:
    def __init__(self, dir: str) -> None:
        self._dir = dir
        self._images: Dict[Tuple[str, ...], int] = dict()
        self._loaded_skins: Set[str] = set()

    def load_directory(self, dir_name: str) -> None:
        if dir_name not in self._loaded_skins:
            dir = os.path.join(self._dir, dir_name)
            for item in os.listdir(dir):
                path = os.path.join(dir, item)
                if os.path.isfile(path) and item.endswith('.png'):
                    self._images[(dir_name, item[:-4])] = _load_texture(path)
            self._loaded_skins.add(dir_name)

    def get(self, key: Tuple[str, ...]) -> int:
        return self._images[key]


class Media:
    def __init__(self) -> None:
        self.tex: Any = Textures([], '')
        self.skins = Skins(DIR_SPRITES)

    def load_tiles(self) -> None:
        self.tex = Textures(IMAGE_NAMES_TILE, DIR_TILES)

    def load_inventory(self) -> None:
        self.tex = Textures(IMAGE_NAMES_INVENTORY, DIR_INVENTORY)

    def load_skin(self, skin_name: str) -> None:
        self.skins.load_directory(skin_name)

