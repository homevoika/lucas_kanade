from os.path import basename

import cv2
import numpy as np
from skimage.transform import pyramid_gaussian, resize
from skimage.color import rgb2hsv
from skimage.io import imread
from PIL import Image, ImageTk

from lucas_kanade.lv import get_contour_points, area2cont, cont2area, interpolate_contour


class LucasKanade:
    def __init__(self, gauss_layers=1, window=61, num_points=9):
        self._files = ()

        self._gauss_layers = gauss_layers
        self._window = window
        self._num_points = num_points

        self._contour = None
        self._result = None

    def _window_image(self, img, cent_point):
        y0 = int(np.round(cent_point[0]) - self._window // 2)
        y1 = int(np.round(cent_point[0]) + self._window // 2 + 1)
        x0 = int(np.round(cent_point[1]) - self._window // 2)
        x1 = int(np.round(cent_point[1]) + self._window // 2 + 1)
        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0
        if y1 > img.shape[0]:
            y1 = img.shape[0]
        if x1 > img.shape[1]:
            x1 = img.shape[1]
        img = img[y0:y1, x0:x1]
        if img.shape[0] != self._window:
            if y0 == 0:
                img = np.concatenate((np.zeros((self._window - img.shape[0], img.shape[1])), img), axis=0)
            elif y1 == img.shape[0]:
                img = np.concatenate((img, np.zeros((self._window - img.shape[0], img.shape[1]))), axis=0)
        if img.shape[1] != self._window:
            if x0 == 0:
                img = np.concatenate((np.zeros((img.shape[0], self._window - img.shape[1])), img), axis=1)
            elif x1 == img.shape[1]:
                img = np.concatenate((img, np.zeros((img.shape[0], self._window - img.shape[1]))), axis=1)
        return img

    def _get_points(self, img, img_next):
        """ Принимает на вход два последовательных изображения и возвращает координаты точек второго"""
        r_1_imgs = list(pyramid_gaussian(img, max_layer=self._gauss_layers))
        r_2_imgs = list(pyramid_gaussian(img_next, max_layer=self._gauss_layers))
        new_points = []

        for point in self._contour:
            flow = np.array([[0], [0]])
            for l, (img_1, img_2) in enumerate(zip(r_1_imgs[::-1], r_2_imgs[::-1])):
                img1 = self._window_image(img_1,
                                          (point[0] / 2 ** (self._gauss_layers - l),
                                           point[1] / 2 ** (self._gauss_layers - l)))

                img2 = self._window_image(img_2,
                                          ((point[0] + flow[1]) / 2 ** (self._gauss_layers - l),
                                           (point[1] + flow[0]) / 2 ** (self._gauss_layers - l)))

                f_y, f_x = np.gradient(img1)
                f_t = img1 - img2
                A = np.array([[np.sum(f_x ** 2), np.sum(f_x * f_y)],
                              [np.sum(f_x * f_y), np.sum(f_y ** 2)]])
                B = np.array([[np.sum(f_x * f_t)],
                              [np.sum(f_y * f_t)]
                              ])
                solv_flow = np.linalg.lstsq(A, B, rcond=None)[0]  # np.matmul(np.linalg.inv(A), B)
                flow = 2 * (flow + solv_flow)

            new_points.append((point[0] + int(flow[1]), point[1] + int(flow[0])))

        self._contour = new_points

        return self._contour

    def set_contour(self, file):
        """Устанавливает контур"""

        rang = (0.06, 0.07)
        hsvcont = rgb2hsv(imread(file)[:, :, :3])
        img_cont = (hsvcont[:, :, 0] > rang[0]) & (hsvcont[:, :, 0] < rang[1])

        cont_x, cont_y, *_ = get_contour_points(area2cont(img_cont), kind='contour', num=self._num_points)
        self._contour = [(y, x) for x, y in zip(cont_x, cont_y)]
        self._result = [self._contour]

    def predict(self, img, img_next):
        self._result.append(self._get_points(img, img_next))

    def get_result_predict(self):
        """Возвращает список точек каждого фрейма"""
        result = []
        for points in self._result:
            frame = []
            for point in points:
                frame.append(point[1])
                frame.append(point[0])
            result.append(frame)

        return result

    @staticmethod
    def get_imgs_and_contours(files):
        """Возвращает imread фреймы и словарь контуров"""

        date = list(files)
        date.sort(key=lambda n: basename(n))

        imgs = []
        imgs_read = []
        img_cont = {}

        for file in date:
            if "endo_epi" in file or "epi_endo" in file:
                img_cont["endo_epi"] = file
            elif "endo" in file:
                img_cont["endo"] = file
            elif "epi" in file:
                img_cont["epi"] = file
            else:
                imgs.append(file)
                imgs_read.append(imread(file, as_gray=True))

        return imgs, imgs_read, img_cont

    @staticmethod
    def contour_exist(files):
        for f in files:
            if "endo" in basename(f) or "epi" in basename(f):
                return True
        return False

