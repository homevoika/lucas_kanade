from tkinter import *
from customtkinter import *
from tkinter.filedialog import askopenfilename as upload_files
from tkinter.messagebox import showerror, showinfo
from PIL import Image, ImageTk
from threading import Thread, ThreadError
from pathlib import PurePath

from progress_bar import ProgessBar
from lucas_kanade.optical_flow import LucasKanade
from gallery import WindowGallery
from menu import CanvasMenu
from screen_load import ScreenLoad
from settings import SettingsWindow


class App(CTk):
    _BACKGROUND_COLOR = "white"
    _TEXT_COLOR = "#1b469e"

    def __init__(self):
        super().__init__()

        self.geometry("640x500")
        self.title("Lucas Kanade")
        self.iconbitmap("images/heart.ico")
        self.configure(background=self._BACKGROUND_COLOR)
        self.resizable(False, False)
        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        # Починить

        self._title_programm = CTkLabel(self,
                                        text="Lucas Kanade",
                                        text_font=("Helvetica", 48),
                                        text_color=self._TEXT_COLOR)
        self._title_programm.pack(pady=45)

        self._entry_name = CTkLabel(self,
                                    text="Amount of points",
                                    text_font=("Helvetica", 12),
                                    text_color=self._TEXT_COLOR)
        self._entry_name.pack()

        self._entry_points = CTkEntry(self,
                                      width=250,
                                      height=55,
                                      border_width=1,
                                      corner_radius=8,
                                      border_color=self._TEXT_COLOR,
                                      text_color=self._TEXT_COLOR,
                                      text_font=("Helvetica", 18),
                                      validate='key',
                                      validatecommand=(self.register(lambda inp: inp.isdigit()), '%S'))
        self._entry_points.insert(0, 9)
        self._entry_points.pack(pady=3)

        self._upload_button = CTkButton(self,
                                        text="Select files  ",
                                        image=self._load_image("images/add-folder.png", 26),
                                        compound="right",
                                        cursor="hand2",
                                        width=250,
                                        height=60,
                                        text_color=self._BACKGROUND_COLOR,
                                        fg_color=self._TEXT_COLOR,
                                        corner_radius=8,
                                        text_font=("Helvetica", 18),
                                        command=self._upload_files)
        self._upload_button.pack(pady=(35, 20))
        self._settings_button = CTkButton(self,
                                          text="Settings ",
                                          cursor="hand2",
                                          width=250,
                                          height=50,
                                          text_color=self._BACKGROUND_COLOR,
                                          fg_color=self._TEXT_COLOR,
                                          corner_radius=8,
                                          text_font=("Helvetica", 18),
                                          command=self._open_settings)
        self._settings_button.pack(pady=10)

        # Gallery Window

        self._files = ()
        self._name_dir = None
        self._gallery_win = None
        self._update_topwin()
        self._frame_wait = None
        self._gallery = None
        self._menu = None

        # Settings Window

        self._settings_win = None
        self._settings_frame = None

        # Lucas
        self._lk = None
        self._lk_result = {}

        self.mainloop()

    def _load_image(self, path, image_size):
        return ImageTk.PhotoImage(Image.open(path).resize((image_size, image_size)))

    def _update_topwin(self):
        if self._gallery_win is not None and not Toplevel.winfo_exists(self._gallery_win):
            self._files = ()
            self._name_dir = None
            self._gallery_win = None
            self._frame_wait = None
            self._gallery = None
            self._menu = None
            self._lk = None
            self._lk_result = {}
        self.after(1000, self._update_topwin)

    def _upload_files(self):
        if self._gallery_win is not None:
            self._gallery_win.destroy()

        amount_points = int(self._entry_points.get())
        if amount_points < 2:
            showinfo(message="Need to enter more points")
            return

        filetypes = [('Image files', '*.jpg'), ('Image files', '*.jpeg'), ('Image files', '*.png')]
        self._files = upload_files(multiple=True, filetypes=filetypes)

        if not LucasKanade.contour_exist(self._files) and self._files:
            showerror(message="Contour not found")
            return

        if self._files:
            self._name_dir = PurePath(self._files[0]).parent.name
            self._start()

    def _open_settings(self):
        self._settings_win = Toplevel(self)
        self._settings_win.geometry("830x464")
        self._settings_win.title("Settings")
        self._settings_win.resizable(False, False)
        self._settings_win.configure(background=self._BACKGROUND_COLOR)
        self._settings_win.iconbitmap("images/heart.ico")
        self._settings_frame = SettingsWindow(self._settings_win, self._settings_win.destroy)
        self._settings_frame.place(x=0)

    def _start(self):
        frame = Image.open(self._files[0])
        w, h = frame.width, frame.height
        screenwidth = self.winfo_screenwidth()

        if w > screenwidth:
            scale = screenwidth / w
            w *= scale
            h *= scale

        h += 140

        self._gallery_win = CTkToplevel(self)
        self._gallery_win.title(self._name_dir)
        self._gallery_win.geometry(f"{w}x{h}")
        self._gallery_win.configure(background=self._BACKGROUND_COLOR)
        self._gallery_win.iconbitmap("images/heart.ico")
        self._gallery_win.minsize(width=w, height=h)

        self._frame_wait = ScreenLoad(self._gallery_win)
        self._frame_wait.pack(expand=True)

        al = Thread(target=self._lucas_canade)
        al.start()

    def _lucas_canade(self):
        try:
            amount_points = int(self._entry_points.get())
            self._lk = LucasKanade(num_points=amount_points)
            imgs, imgs_read, img_contours = self._lk.get_imgs_and_contours(self._files)

            for wall_type in img_contours:
                self._lk.set_contour(img_contours[wall_type])
                for i in range(len(imgs_read) - 1):
                    self._lk.predict(imgs_read[i], imgs_read[i + 1])
                self._lk_result[wall_type] = self._lk.get_result_predict()

            self._gallery = WindowGallery(self._gallery_win, self._lk_result, imgs)
            self._frame_wait.pack_forget()
            self._menu = CanvasMenu(self._gallery_win, self._name_dir, self._gallery.get_all_points_walls, imgs)
            self._menu.pack(anchor=NW)
            self._gallery.pack(expand=True)
            self._frame_wait.delete()
        except:
            showerror("Thread error")
