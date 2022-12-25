from tkinter import Menu
from tkinter.messagebox import showinfo
from tkinter.filedialog import asksaveasfilename, askdirectory
from customtkinter import CTkFrame, CTkButton
from PIL import Image, ImageDraw
import xlsxwriter
import os
import shutil


class CanvasMenu(CTkFrame):
    _BACKGROUND_COLOR = "white"
    _TEXT_COLOR = "#1b469e"

    def __init__(self, root, filename, get_data, images):
        super().__init__(master=root)

        self._filename = filename
        self._get_data = get_data
        self._images = images

        self._menu = Menu(self, tearoff=0)
        self._menu.add_command(label="Save data", command=self._save_data, font=("Roboto", 10))
        self._menu.add_command(label="Save pictures", command=self._save_images, font=("Roboto", 10))

        self._button = CTkButton(self,
                                 text="Files",
                                 command=self._show,
                                 corner_radius=0,
                                 fg_color=self._BACKGROUND_COLOR,
                                 bg_color=self._BACKGROUND_COLOR,
                                 width=50,
                                 height=25,
                                 hover_color=self._BACKGROUND_COLOR,
                                 border_color=self._BACKGROUND_COLOR,
                                 text_font=("Roboto", 10),
                                 highlightbackground=self._BACKGROUND_COLOR,
                                 highlightcolor=self._BACKGROUND_COLOR,
                                 )
        self._button.pack()

    def _show(self):
        self._menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + 25)

    def _save_data(self):
        data: dict = self._get_data()

        if not data:
            return

        browser = asksaveasfilename(initialfile=self._filename, defaultextension=".xlsx", filetypes=[("Files", "*.*")])

        if browser:
            file = xlsxwriter.Workbook(browser)
            bold = file.add_format({'bold': True, 'align': 'center'})
            center = file.add_format({'align': 'center'})

            for walltype, coords in data.items():
                wall = file.add_worksheet(name=walltype)

                wall.write(0, 0, "№", bold)

                wall.write_column(1, 0, [n for n in range(1, len(coords) + 1)], bold)

                columns = []
                for n in range(1, int(len(coords[0]) / 2) + 1):
                    columns.extend([f"x{n}", f"y{n}"])
                wall.write_row(0, 1, columns, bold)

                for i, points in enumerate(coords):
                    wall.write_row(i + 1, 1, points, center)

            file.close()

            showinfo(message="Data successfully saved")

    def _imdraw(self, image, points) -> Image:
        POINT_RADIUS = 7
        LINE_WIDTH = 2
        POINT_COLOR = "red"
        LINE_COLOR = "yellow"
        IMAGE = Image.open(image)
        IMAGE_DRAW = ImageDraw.Draw(IMAGE)
        POINTS = [(points[i], points[i + 1]) for i in range(0, len(points), 2)]

        def create_point(point):
            IMAGE_DRAW.ellipse([point[0] - POINT_RADIUS,
                                point[1] - POINT_RADIUS,
                                point[0] + POINT_RADIUS,
                                point[1] + POINT_RADIUS],
                               fill=POINT_COLOR)

        def create_line(x1, y1, x2, y2):
            IMAGE_DRAW.line([x1, y1, x2, y2], width=LINE_WIDTH, fill=LINE_COLOR)

        for n in range(len(POINTS) - 1):
            create_line(POINTS[n][0], POINTS[n][1], POINTS[n + 1][0], POINTS[n + 1][1])

        for point in POINTS:
            create_point(point)

        return IMAGE

    def _save_images(self):
        data: dict = self._get_data()
        path = askdirectory()

        if path:
            path += "/" + self._filename + "_images"

            if os.path.exists(path):
                shutil.rmtree(path)
            os.mkdir(path)

            for wall, points in data.items():
                wall_path = path + "/" + wall
                os.mkdir(wall_path)

                for i in range(len(points)):
                    img_path = wall_path + f"/{i + 1}.png"
                    self._imdraw(self._images[i], points[i]).save(img_path)

            showinfo(message="Images successfully saved")
