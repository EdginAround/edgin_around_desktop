import os
import pyglet

from OpenGL import GL

from typing import Dict, Iterable, List

DIR_SOUNDS: str = "effects"
DIR_INVENTORY: str = "inventory"

IMAGE_NAMES_INVENTORY: List[str] = [
    "axe",
    "empty_slot",
    "gold",
    "hat",
    "left_hand",
    "log",
    "raw_meat",
    "right_hand",
    "rocks",
]


def _load_texture(file_path: str) -> int:
    image = pyglet.image.load(file_path)
    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,
        0,
        GL.GL_RGBA,
        image.width,
        image.height,
        0,
        GL.GL_RGBA,
        GL.GL_UNSIGNED_BYTE,
        image.get_data(),
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
        return _load_texture(os.path.join(dir_name, f"{image_name}.png"))

    def __getitem__(self, key) -> int:
        return self._images[key]

    def __getattr__(self, key) -> int:
        return self._images[key]


class Sounds:
    def __init__(self, resource_dir: str) -> None:
        self._sounds: Dict[str, pyglet.media.Player] = dict()
        self._load(os.path.join(resource_dir, DIR_SOUNDS))

    def _load(self, dir: str) -> None:
        for item in os.listdir(dir):
            path = os.path.join(dir, item)
            if os.path.isfile(path) and item.endswith(".mp3"):
                self._sounds[item[:-4]] = pyglet.media.load(path, streaming=False)

    def play(self, sound_name: str) -> None:
        if sound_name in self._sounds:
            self._sounds[sound_name].play()


def load_inventory_textures(resource_dir: str) -> Textures:
    return Textures(IMAGE_NAMES_INVENTORY, os.path.join(resource_dir, DIR_INVENTORY))
