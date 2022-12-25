from tkinter import Tk, Frame, Canvas, NW, Label
from PIL import Image, ImageTk
from config import SettingsFile


class ControlPoint(Frame):
    _RADIUS = None
    _COLOR = None
    _TAG = "point"

    def __init__(self, canvas, x, y):
        super().__init__()

        pc, _, pr, _ = SettingsFile.get_fields()
        self._RADIUS = float(pr)
        self._COLOR = pc

        self._canvas = canvas
        self._point = self._canvas.create_oval(
            x - self._RADIUS,
            y - self._RADIUS,
            x + self._RADIUS,
            y + self._RADIUS,
            fill=self._COLOR,
            outline=self._COLOR,
            tags=self._TAG
        )

        self._drag_data = {"x": 0, "y": 0, "item": None}

        self._canvas.tag_bind("point", "<ButtonPress-1>", self._drag_start)
        self._canvas.tag_bind("point", "<ButtonRelease-1>", self._drag_stop)
        self._canvas.tag_bind("point", "<B1-Motion>", self._drag)

    def _drag_start(self, event):
        self._drag_data["item"] = self._canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _drag_stop(self, event):
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def _drag(self, event):
        if self._drag_data["item"] == self._canvas.find_all()[0]:
            return
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        self._canvas.move(self._drag_data["item"], delta_x, delta_y)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def position(self):
        radius = self._RADIUS
        position = self._canvas.coords(self._point)
        return [int(position[0] + radius), int(position[1] + radius)]


class DrawContour(Frame):
    _WIDTH = None
    _COLOR = None

    def __init__(self, canvas, points):
        super().__init__()

        self._canvas = canvas
        self._points = []
        self._lines = []

        _, lc, _, lw = SettingsFile.get_fields()
        self._WIDTH = float(lw)
        self._COLOR = lc

        for i in range(0, len(points), 2):
            self._points.append(ControlPoint(self._canvas, points[i], points[i + 1]))

        for i in range(len(self._points) - 1):
            line = self._canvas.create_line(
                self._points[i].position()[0],
                self._points[i].position()[1],
                self._points[i + 1].position()[0],
                self._points[i + 1].position()[1],
                fill=self._COLOR,
                width=self._WIDTH
            )
            self._canvas.tag_lower(line)
            self._lines.append(line)

    def get_points(self):
        res = []
        for p in self._points:
            res.extend(p.position())
        return res

    def update(self):
        for i in range(len(self._points) - 1):
            x, y = self._points[i].position()[0], self._points[i].position()[1]
            x2, y2 = self._points[i + 1].position()[0], self._points[i + 1].position()[1]
            self._canvas.coords(self._lines[i], x, y, x2, y2)


class ContourCanvas(Canvas):
    def __init__(self, root, img, points):
        super().__init__(master=root)

        self._points = points
        self._scale = 1
        self._screenwidth = root.winfo_screenwidth()

        self._image = Image.open(img)

        if self._image.width > self._screenwidth:
            self._scale = self._screenwidth / self._image.width

        self._image = self._image.resize((int(self._image.width * self._scale), int(self._image.height * self._scale)))
        self._image = ImageTk.PhotoImage(self._image)

        self.configure(width=self._image.width(), height=self._image.height(), highlightthickness=0)

        self._contour = DrawContour(self, self._points)
        self.tag_lower(self.create_image(0, 0, anchor=NW, image=self._image))
        self.scale("all", 0, 0, self._scale, self._scale)

    def get_points(self):
        self.scale("all", 0, 0, 1 / self._scale, 1 / self._scale)
        points = self._contour.get_points()
        self.scale("all", 0, 0, self._scale, self._scale)
        return points

    def update(self):
        self._contour.update()
