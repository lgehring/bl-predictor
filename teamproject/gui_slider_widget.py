"""
This module was taken from https://github.com/MenxLi/tkSliderWidget
and was modified to fit the project

BSD 2-Clause License

Copyright (c) 2020, Mengxun Li
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from tkinter import Canvas
from tkinter import Frame


class Slider(Frame):
    LINE_COLOR = "#476b6b"
    LINE_WIDTH = 3
    BAR_COLOR_INNER = "#5c8a8a"
    BAR_COLOR_OUTTER = "#c2d6d6"
    BAR_RADIUS = 10
    BAR_RADIUS_INNER = BAR_RADIUS - 5
    DIGIT_PRECISION = '.0f'  # for showing in the canvas

    def __init__(self, master, width=400, height=80, min_val=0, max_val=1,
                 init_lis=None, show_value=True, **kw):
        Frame.__init__(self, master, height=height, width=width)
        super().__init__(master, **kw)
        self.master = master
        if init_lis is None:
            init_lis = [min_val]
        self.init_lis = init_lis
        self.max_val = max_val
        self.min_val = min_val
        self.show_value = show_value
        self.H = height
        self.W = width
        self.canv_H = self.H
        self.canv_W = self.W
        if not show_value:
            self.slider_y = self.canv_H / 2  # y pos of the slider
        else:
            self.slider_y = self.canv_H * 2 / 5
        self.slider_x = Slider.BAR_RADIUS  # x pos of the slider (left side)

        self.bars = []
        self.selected_idx = None  # current selection bar index
        for value in self.init_lis:
            pos = (value - min_val) / (max_val - min_val)
            ids = []
            bar = {"Pos": pos, "Ids": ids, "Value": value}
            self.bars.append(bar)

        self.canv = Canvas(self, height=self.canv_H, width=self.canv_W)
        self.canv.pack()
        self.canv.bind("<Motion>", self._mouseMotion)
        self.canv.bind("<B1-Motion>", self._moveBar)

        self.__addTrack(self.slider_x, self.slider_y,
                        self.canv_W - self.slider_x, self.slider_y)
        for bar in self.bars:
            bar["Ids"] = self.__addBar(bar["Pos"])

    def getValues(self):
        values = [bar["Value"] for bar in self.bars]
        return sorted(values)

    def _mouseMotion(self, event):
        x = event.x
        y = event.y
        selection = self.__checkSelection(x, y)
        if selection[0]:
            self.canv.config(cursor="hand2")
            self.selected_idx = selection[1]
        else:
            self.canv.config(cursor="")
            self.selected_idx = None

    def _moveBar(self, event):
        x = event.x
        if self.selected_idx is None:
            return False
        pos = self.__calcPos(x)
        idx = self.selected_idx
        self.__moveBar(idx, pos)

    def __addTrack(self, startx, starty, endx, endy):
        ident = self.canv.create_line(startx, starty, endx, endy,
                                      fill=Slider.LINE_COLOR,
                                      width=Slider.LINE_WIDTH)
        return ident

    def __addBar(self, pos):
        """@ pos: position of the bar, ranged from (0,1)"""
        if pos < 0 or pos > 1:
            raise Exception("Pos error - Pos: " + str(pos))
        _r = Slider.BAR_RADIUS
        r = Slider.BAR_RADIUS_INNER
        _l = self.canv_W - 2 * self.slider_x
        y = self.slider_y
        x = self.slider_x + pos * _l
        id_outer = self.canv.create_oval(x - _r, y - _r, x + _r, y + _r,
                                         fill=Slider.BAR_COLOR_OUTTER, width=2,
                                         outline="")
        id_inner = self.canv.create_oval(x - r, y - r, x + r, y + r,
                                         fill=Slider.BAR_COLOR_INNER,
                                         outline="")
        if self.show_value:
            y_value = y + Slider.BAR_RADIUS + 8
            value = pos * (self.max_val - self.min_val) + self.min_val
            id_value = self.canv.create_text(x,
                                             y_value,
                                             text=format(
                                                 value,
                                                 Slider.DIGIT_PRECISION))
            return [id_outer, id_inner, id_value]
        else:
            return [id_outer, id_inner]

    def __moveBar(self, idx, pos):
        ids = self.bars[idx]["Ids"]
        for idents in ids:
            self.canv.delete(idents)
        self.bars[idx]["Ids"] = self.__addBar(pos)
        self.bars[idx]["Pos"] = pos
        self.bars[idx]["Value"] = (pos * (self.max_val - self.min_val) +
                                   self.min_val)

    def __calcPos(self, x):
        """calculate position from x coordinate"""
        pos = (x - self.slider_x) / (self.canv_W - 2 * self.slider_x)
        if pos < 0:
            return 0
        elif pos > 1:
            return 1
        else:
            return pos

    def __getValue(self, idx):
        """#######Not used function#####"""
        bar = self.bars[idx]
        ids = bar["Ids"]
        x = self.canv.coords(ids[0])[0] + Slider.BAR_RADIUS
        pos = self.__calcPos(x)
        return pos * (self.max_val - self.min_val) + self.min_val

    def __checkSelection(self, x, y):
        """
        To check if the position is inside the bounding rectangle of a Bar
        Return [True, bar_index] or [False, None]
        """
        for idx in range(len(self.bars)):
            ident = self.bars[idx]["Ids"][0]
            bbox = self.canv.bbox(ident)
            if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
                return [True, idx]
        return [False, None]
