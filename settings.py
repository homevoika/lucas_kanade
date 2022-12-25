from tkinter import *
from customtkinter import *
from tkinter import colorchooser
from typing import Dict
from PIL import Image, ImageTk
from configparser import ConfigParser
from re import search
from config import SettingsFile

_BACKGROUND_COLOR = "white"
_MAIN_COLOR = "#1b469e"


class ExampleCanvas(Canvas):
    _indices: Dict[int, int] = {}

    def create_circle(self, x, y, r, fill):
        circle = self.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=fill)
        self._indices[circle] = r
        return circle

    def get_circle(self, index):
        if index < 1 or index > len(self.find_all()):
            return None
        x1, y1, _, _ = self.coords(index)
        x, y = x1 + self._indices[index], y1 + self._indices[index]
        return x, y, self._indices[index]

    def circle_config(self, index, x=None, y=None, r=None, fill=None):
        if index < 1 or index > len(self.find_all()):
            return None

        if fill:
            self.itemconfigure(index, fill=fill, outline=fill)

        prev_x, prev_y, prev_r = self.get_circle(index)

        if r:
            self._indices[index] = r

        if x and y:
            if r:
                self.coords(index, x - r, y - r, x + r, y + r)
            else:
                self.coords(index, x - prev_r, y - prev_r, x + prev_r, y + prev_r)
        elif x:
            if r:
                self.coords(index, x - r, prev_y - r, x + r, prev_y + r)
            else:
                self.coords(index, x - prev_r, prev_y - prev_r, x + prev_r, prev_y + prev_r)
        elif y:
            if r:
                self.coords(index, prev_x - r, y - r, prev_x + r, y + r)
            else:
                self.coords(index, prev_x - prev_r, y - prev_r, prev_x + prev_r, y + prev_r)
        elif r:
            self.coords(index, prev_x - r, prev_y - r, prev_x + r, prev_y + r)


class ContourFrame(CTkFrame):
    _POINT_COLOR: str = None
    _LINE_COLOR: str = None
    _POINT_RADIUS: int = None
    _LINE_WIDTH: int = None

    def __init__(self, root):
        super().__init__(master=root)

        self._image = Image.open("images/example.png")
        w, h = self._image.width, self._image.height
        self._image = ImageTk.PhotoImage(self._image)

        self._points = ((134, 352), (92, 263), (104, 174), (156, 92), (240, 52),
                        (323, 101), (377, 178), (409, 253), (394, 340))

        self._canvas = ExampleCanvas(self, width=w, height=h, highlightthickness=0)
        self._canvas.create_image(0, 0, anchor=NW, image=self._image)
        self._canvas.pack()

        for i in range(8):
            self._canvas.create_line(self._points[i][0],
                                     self._points[i][1],
                                     self._points[i + 1][0],
                                     self._points[i + 1][1],
                                     fill="yellow",
                                     width=2)

        for i in range(9):
            self._canvas.create_circle(self._points[i][0], self._points[i][1], 7, fill="red")

    def set_point_color(self, color):
        for i in range(10, 19):
            self._POINT_COLOR = color
            self._canvas.circle_config(i, fill=color)

    def set_point_radius(self, r):
        for i in range(10, 19):
            r = float(r)
            self._POINT_RADIUS = r
            self._canvas.circle_config(i, r=r)

    def set_line_width(self, width):
        for i in range(2, 10):
            width = float(width)
            self._LINE_WIDTH = width
            self._canvas.itemconfigure(i, width=width)

    def set_line_color(self, color):
        for i in range(2, 10):
            self._LINE_COLOR = color
            self._canvas.itemconfigure(i, fill=color)

    def get_settings(self):
        return self._POINT_COLOR, self._LINE_COLOR, int(self._POINT_RADIUS), int(self._LINE_WIDTH)


class SettingsFrame(CTkFrame):
    def _point_palette(self):
        color = colorchooser.askcolor(title="Point color")
        if color[1] is not None:
            self._canvas.set_point_color(color[1])
            self._point_color.configure(fg_color=color[1], hover_color=color[1])

    def _line_palette(self):
        color = colorchooser.askcolor(title="Line color")
        if color[1] is not None:
            self._canvas.set_line_color(color[1])
            self._line_color.configure(fg_color=color[1], hover_color=color[1])

    def __init__(self, root, canvas):
        super().__init__(master=root, fg_color=_BACKGROUND_COLOR, width=320, height=200)

        self._canvas: ContourFrame = canvas
        pc, lc, pr, lw = SettingsFile.get_fields()

        self._point = CTkLabel(self,
                               width=1,
                               text="Point color",
                               text_font=("Helvetica", 16))
        self._point_color = CTkButton(self,
                                      text="",
                                      height=30,
                                      width=30,
                                      corner_radius=10,
                                      fg_color=pc,
                                      hover_color=pc,
                                      border_width=1,
                                      command=self._point_palette)
        self._line = CTkLabel(self,
                              width=1,
                              text="Line color",
                              text_font=("Helvetica", 16))
        self._line_color = CTkButton(self,
                                     text="",
                                     height=30,
                                     width=30,
                                     corner_radius=10,
                                     fg_color=lc,
                                     hover_color=lc,
                                     border_width=1,
                                     command=self._line_palette)

        self._label_pr = CTkLabel(self,
                                  width=1,
                                  text="Point radius",
                                  text_font=("Helvetica", 16))
        self._slider_pr = CTkSlider(self,
                                    from_=1,
                                    to=25,
                                    height=20,
                                    width=150,
                                    button_color=_MAIN_COLOR,
                                    button_hover_color=_MAIN_COLOR,
                                    progress_color=_MAIN_COLOR,
                                    command=lambda r: self._canvas.set_point_radius(r))

        self._label_lw = CTkLabel(self,
                                  width=1,
                                  text="Line width",
                                  text_font=("Helvetica", 16))
        self._slider_lw = CTkSlider(self,
                                    from_=1,
                                    to=10,
                                    height=20,
                                    width=150,
                                    button_color=_MAIN_COLOR,
                                    button_hover_color=_MAIN_COLOR,
                                    progress_color=_MAIN_COLOR,
                                    command=lambda w: self._canvas.set_line_width(w))

        self._point.place(x=0, y=0)
        self._point_color.place(x=210, y=0)

        self._label_pr.place(x=0, y=50)
        self._slider_pr.place(x=150, y=55)

        self._line.place(x=0, y=100)
        self._line_color.place(x=210, y=100)

        self._label_lw.place(x=0, y=150)
        self._slider_lw.place(x=150, y=155)

        self._slider_pr.set(float(pr))
        self._slider_lw.set(float(lw))


class SettingsWindow(CTkFrame):
    def __init__(self, root, destroy_func):
        super().__init__(master=root, width=830, height=464, fg_color=_BACKGROUND_COLOR)

        self._destroy_func = destroy_func
        self._contour = ContourFrame(self)
        self._settings = SettingsFrame(self, self._contour)

        pc, lc, pr, lw = SettingsFile.get_fields()
        self._contour.set_point_radius(pr)
        self._contour.set_line_width(lw)
        self._contour.set_point_color(pc)
        self._contour.set_line_color(lc)

        self._save_button = CTkButton(self,
                                      text="Save",
                                      width=75,
                                      height=30,
                                      text_color=_BACKGROUND_COLOR,
                                      fg_color=_MAIN_COLOR,
                                      corner_radius=8,
                                      text_font=("Helvetica", 11),
                                      command=self._save_settings)

        self._close_button = CTkButton(self,
                                       text="Close",
                                       width=75,
                                       height=30,
                                       text_color=_BACKGROUND_COLOR,
                                       fg_color=_MAIN_COLOR,
                                       corner_radius=8,
                                       text_font=("Helvetica", 11),
                                       command=self._destroy_func)

        self._contour.place(x=0)
        self._settings.place(x=500, y=50)
        self._save_button.place(x=630, y=425)
        self._close_button.place(x=722, y=425)

    def _save_settings(self):
        point_color, line_color, point_radius, line_width = self._contour.get_settings()
        SettingsFile.set_fields(point_color=point_color,
                                line_color=line_color,
                                point_radius=point_radius,
                                line_width=line_width)
        self._destroy_func()

