import freetype
from OpenGL.GL import *
import glfw
from constants import *

class Font:
    def __init__(self, font_path, size):
        self.face = freetype.Face(font_path)
        self.face.set_char_size(size * 64)
        self.cache = {}

    def get_char(self, char):
        if char in self.cache:
            return self.cache[char]
        self.face.load_char(char)
        bitmap = self.face.glyph.bitmap
        width, height = bitmap.width, bitmap.rows
        top, left = self.face.glyph.bitmap_top, self.face.glyph.bitmap_left
        data = bitmap.buffer
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, width, height, 0, GL_RED, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        char_info = (tex_id, width, height, top, left)
        self.cache[char] = char_info
        return char_info

    def render_text(self, x, y, text, scale=1, gap=1.5, color=TEXT_COLOR):
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glColor3f(*color)
        for char in text:
            tex_id, w, h, top, left = self.get_char(char)
            xpos = x + left * scale
            ypos = y - (h - top) * scale
            w *= scale
            h *= scale
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(xpos, ypos)
            glTexCoord2f(1, 1); glVertex2f(xpos + w, ypos)
            glTexCoord2f(1, 0); glVertex2f(xpos + w, ypos + h)
            glTexCoord2f(0, 0); glVertex2f(xpos, ypos + h)
            glEnd()
            x += (self.face.glyph.advance.x >> 6) * scale + gap
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        glPopAttrib()
