import ctypes
import numpy

from OpenGL import GL


class Fbo:
    def __init__(self) -> None:
        self._fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)

        self._texture_color = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_color)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

        self._texture_depth = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_depth)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

        if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer not complete")

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def get_color_texture_id(self) -> int:
        return self._texture_color

    def attach(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER,
            GL.GL_COLOR_ATTACHMENT0,
            GL.GL_TEXTURE_2D,
            self._texture_color,
            0,
        )
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER,
            GL.GL_DEPTH_ATTACHMENT,
            GL.GL_TEXTURE_2D,
            self._texture_depth,
            0,
        )

    def detach(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def resize(self, width: float, height: float) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_color)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            width,
            height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            ctypes.c_void_p(0),
        )

        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_depth)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_DEPTH_COMPONENT,
            width,
            height,
            0,
            GL.GL_DEPTH_COMPONENT,
            GL.GL_UNSIGNED_BYTE,
            ctypes.c_void_p(0),
        )

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def __enter__(self) -> "Fbo":
        self.attach()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.detach()
