from PIL import Image
from PIL.ImageTk import PhotoImage
from moviepy.editor import *
from customtkinter import CTkFrame, CTkLabel


class ScreenLoad(CTkFrame):
    _BACKGROUND_COLOR = "white"
    _TEXT_COLOR = "#32a7a9"

    def __init__(self, root):
        super().__init__(master=root, fg_color=self._BACKGROUND_COLOR)

        self._gif = VideoFileClip("images/heartbeat.gif")
        self._gif = self._gif.resize(height=256)
        self._n_frame = 0.00
        self._frame = None

        self._end = False

        self._gif_label = CTkLabel(self)
        self._gif_label.pack()
        self._text = CTkLabel(self,
                              text="Please wait",
                              text_font=("Helvetica", 16),
                              text_color=self._TEXT_COLOR,
                              fg_color=self._BACKGROUND_COLOR)
        self._text.pack()

        self._update()

    def _update(self):
        if self._end:
            return
        self._frame = Image.fromarray(self._gif.get_frame(self._n_frame))
        self._frame = PhotoImage(image=self._frame)
        self._gif_label.configure(image=self._frame)
        self._n_frame = 0.00 if self._n_frame > self._gif.end else self._n_frame + 0.03
        self.after(15, self._update)

    def delete(self):
        self._gif.close()
        self._n_frame = 0.00
        self._frame = None
        self._end = True
        self.destroy()