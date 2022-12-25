from customtkinter import *
from math import ceil


class Bar(CTkProgressBar):
    def __init__(self, *args, elements=1, **kwargs):
        super().__init__(*args, **kwargs)

        self._elements = elements
        self.set(0)

        self._constspeed = 0
        self._percent = 0

    def _custom_step(self):
        self.determinate_value += 1 / (self._elements * 50)
        if self.determinate_value == 1:
            self.determinate_value -= 1
        elif self.determinate_value + 1 / (self._elements * 50) >= 1:
            self.determinate_value = 1
        self.draw()

    def next(self):
        self._update()

        if self._percent == 100:
            self._percent = 0
            self.set(0)

        if self._percent + ceil(100 / self._elements) >= 100:
            self._percent = 100
        else:
            self._percent += ceil(100 / self._elements)

    def percent_value(self):
        return f"{self._percent}%"

    def _update(self):
        if self._constspeed == 50:
            self._constspeed = 0
            return
        self._constspeed += 1
        self._custom_step()
        self.after(50, self._update)


class ProgessBar(CTkFrame):
    def __init__(self, *args, width_bar=100, height_bar=10, elements_bar=1, **kwargs):
        super().__init__(*args, **kwargs)

        self._percent = CTkLabel(self, text_font=("Helvetica", 12))
        self._percent.pack()

        self._bar = Bar(self, height=height_bar, width=width_bar, elements=elements_bar)
        self._bar.pack(pady=5)

        # self._text = CTkLabel(self, text="Images processing", text_font=("Roboto", 12))
        # self._text.pack(pady=20)

        self._update()

    def _update(self):
        self._percent.configure(text=self._bar.percent_value())
        self._percent.after(1, self._update)

    def next(self):
        self._bar.next()
