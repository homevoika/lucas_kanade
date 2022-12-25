from customtkinter import *
from PIL import Image, ImageTk
from canvas import ContourCanvas

BACKGROUND_COLOR = "white"
BUTTON_COLOR = "#C0C0C0"
BUTTON_HOVER_COLOR = "#929292"
TEXT_COLOR = "#323232"


class BottomBar(CTkFrame):
    """Создание бара для управлениями изображениями"""

    def __init__(self, root, elemenets, **kwargs):
        super().__init__(master=root, fg_color=BACKGROUND_COLOR, **kwargs)

        self._current_value = 1
        self._amount_imgs = elemenets

        self._butt_left = CTkButton(self, text="<", width=72, height=30, text_color=TEXT_COLOR,
                                    text_font=("Roboto", 18), corner_radius=9, fg_color=BUTTON_COLOR,
                                    hover_color=BUTTON_HOVER_COLOR, command=self._left_click)
        self._butt_left.grid(row=0, column=0)

        self._entry = CTkEntry(self, fg_color=BACKGROUND_COLOR, width=70, text_color=TEXT_COLOR,
                               text_font=("Roboto", 22), justify=RIGHT, border_color=BACKGROUND_COLOR, validate='key',
                               validatecommand=(self.register(lambda inp: inp.isdigit()), '%S'))
        self._entry.insert(0, self._current_value)
        self._entry.grid(row=0, column=1, padx=(25, 0))
        self._entry.bind("<Return>", self._set_value)

        self._label = CTkLabel(self, fg_color=BACKGROUND_COLOR, width=70, text=f"/  {self._amount_imgs}",
                               text_color=TEXT_COLOR, text_font=("Roboto", 22))
        self._label.grid(row=0, column=2, padx=(0, 60))

        self._butt_right = CTkButton(self, text=">", width=72, height=30, text_color=TEXT_COLOR,
                                     text_font=("Roboto", 18), corner_radius=9, fg_color=BUTTON_COLOR,
                                     hover_color=BUTTON_HOVER_COLOR, command=self._right_click)
        self._butt_right.grid(row=0, column=3)

    def _right_click(self):
        if self._current_value == self._amount_imgs:
            return
        self._current_value += 1
        self._entry.delete(0, END)
        self._entry.insert(0, self._current_value)

    def _left_click(self):
        if self._current_value == 1:
            return
        self._current_value -= 1
        self._entry.delete(0, END)
        self._entry.insert(0, self._current_value)

    def _set_value(self, event=None):
        entry_value = int(self._entry.get())
        if entry_value > self._amount_imgs or entry_value < 1:
            self._entry.delete(0, END)
            self._entry.insert(0, self._current_value)
            self.focus()
            return
        self._current_value = int(self._entry.get())
        self.focus()

    def get_current_value(self):
        return self._current_value


class ImageFrame(CTkFrame):
    """Создание фрейма с интерактивными изображениями"""

    def __init__(self, *args, bar, images, points, **kwargs):
        super().__init__(*args, **kwargs)

        self._bar = bar
        self._number_page = self._bar.get_current_value()
        self._prev_number_page = self._bar.get_current_value()

        self._points = points
        self._canvases = [ContourCanvas(self, img, self._points[i]) for i, img in enumerate(images)]

        self._canvases[self._number_page - 1].pack(expand=True)
        self._update_page()

    def _update_page(self):
        if self._number_page != self._prev_number_page:
            self._canvases[self._prev_number_page - 1].pack_forget()
            self._canvases[self._number_page - 1].pack(expand=True)
            self._prev_number_page = self._number_page
        self._canvases[self._number_page - 1].update()
        self._number_page = self._bar.get_current_value()
        self.after(10, self._update_page)

    def get_points_all_frames(self):
        return [canvas.get_points() for canvas in self._canvases]


class Button(CTkButton):
    def __init__(self, *args, index, **kwargs):
        super().__init__(*args,
                         width=100,
                         height=20,
                         text_color=TEXT_COLOR,
                         text_font=("Roboto", 14),
                         cursor="hand2",
                         corner_radius=20,
                         fg_color=BACKGROUND_COLOR,
                         hover_color=BUTTON_COLOR,
                         command=self.on,
                         **kwargs)

        self._index = index
        self._active = False

    def on(self):
        self._active = True

    def off(self):
        self._active = False

    @property
    def index(self):
        return self._index

    @property
    def active(self):
        return self._active


class WallTypes(CTkFrame):
    """Создание кнопок с типами контуров"""

    def __init__(self, *args, walls, **kwargs):
        super().__init__(*args, fg_color=BACKGROUND_COLOR, **kwargs)

        self._buttons_walls = tuple((Button(self, index=i, text=wall) for i, wall in enumerate(walls)))

        if len(self._buttons_walls) == 3:
            self._buttons_walls[0].grid(row=0, column=0)
            self._buttons_walls[1].grid(row=0, column=1, padx=25)
            self._buttons_walls[2].grid(row=0, column=2)
        elif len(self._buttons_walls) == 2:
            self._buttons_walls[0].grid(row=0, column=0)
            self._buttons_walls[1].grid(row=0, column=1, padx=(25, 0))
        else:
            self._buttons_walls[0].grid()

        self._current_index = 0
        self._current_wall_type = self._buttons_walls[self._current_index].text
        self._buttons_walls[self._current_index].on()
        self._buttons_walls[self._current_index].configure(fg_color=BUTTON_COLOR)
        self._update()

    def _update(self):
        for bt in self._buttons_walls:
            if bt.index != self._current_index and bt.active:
                bt.configure(fg_color=BUTTON_COLOR)
                self._buttons_walls[self._current_index].off()
                self._buttons_walls[self._current_index].configure(fg_color=BACKGROUND_COLOR)
                self._current_index = bt.index
                self._current_wall_type = bt.text
        self.after(10, self._update)

    @property
    def current_type(self):
        return self._current_wall_type


class WindowGallery(CTkFrame):
    def __init__(self, root, walls: dict, images, **kwargs):
        super().__init__(master=root, fg_color=BACKGROUND_COLOR, **kwargs)

        # 1 - str wall, 2 - list points, 3 - bar for wall

        self._data = [(wall, points, BottomBar(self, len(points))) for wall, points in walls.items()]

        self._walls = WallTypes(self, walls=[wall[0] for wall in self._data])

        self._frames_images = {data[0]: (ImageFrame(self, points=data[1], bar=data[2], images=images), data[2]) for data
                               in self._data}

        self._walls.pack(pady=10)

        self._prev_wall = self._walls.current_type
        self._curr_wall = None

        self._frames_images[self._prev_wall][0].pack()
        self._frames_images[self._prev_wall][1].pack(pady=10)

        self._update()

    def _update(self):
        self._current_wall = self._walls.current_type
        if self._current_wall != self._prev_wall:
            self._frames_images[self._current_wall][0].pack()
            self._frames_images[self._current_wall][1].pack(pady=10)
            self._frames_images[self._prev_wall][0].pack_forget()
            self._frames_images[self._prev_wall][1].pack_forget()
            self._prev_wall = self._current_wall
        self.after(10, self._update)

    def get_all_points_walls(self) -> dict:
        return {wall: frames[0].get_points_all_frames() for wall, frames in self._frames_images.items()}



