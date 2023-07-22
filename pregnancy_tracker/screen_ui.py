import os

from PIL import Image, ImageDraw

from .icons import carriage_icon_path, moon_icon_path
from .fonts import create_font
from .gray_scale import WHITE, DARK_GRAY, BLACK, LIGHT_GRAY


class ScreenUI:
    ICON_SIZE = 20
    ICON_CIRCLE_SIZE = 40
    ICON_X_MARGIN = 8
    PROGRESS_BAR_Y_CENTER = 105
    PROGRESS_BAR_HEIGHT = 10
    TEXT_MARGIN_TOP = 16
    TEXT_MARGIN_BOTTOM = 16

    def __init__(self, width, height, pregnancy):
        self.pregnancy = pregnancy
        self.width = width
        self.height = height
        self._img = Image.new('L', (self.width, self.height), 255)  # 255: clear the frame
        self._img_draw = ImageDraw.Draw(self._img)

    def _calculate_text_size(self, message, font):
        _, _, w, h = self._img_draw.textbbox((0, 0), message, font=font)
        return w, h

    def _draw_percent(self):
        font = create_font(46)
        percent_str = self.pregnancy.get_percent_str()
        w, h = self._calculate_text_size(percent_str, font)
        pos = ((self.width-w)/2, self.TEXT_MARGIN_TOP)
        self._img_draw.text(pos, percent_str, font=font, fill=BLACK)

    def _draw_weekday(self):
        font = create_font(30)
        percent_str = self.pregnancy.get_weekday_str()
        w, h = self._calculate_text_size(percent_str, font)
        pos = ((self.width-w)/2, (self.height-h-self.TEXT_MARGIN_BOTTOM))
        self._img_draw.text(pos, percent_str, font=font, fill=BLACK)

    def _draw_carriage(self):
        carriage = Image.open(carriage_icon_path)
        carriage.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.width - self.ICON_CIRCLE_SIZE - self.ICON_X_MARGIN
        circle_x2 = self.width - self.ICON_X_MARGIN
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=DARK_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - carriage.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - carriage.height)/2)
        self._img.paste(carriage, (icon_x, icon_y), carriage)

    def _draw_moon(self):
        moon = Image.open(moon_icon_path)
        moon.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.ICON_X_MARGIN
        circle_x2 = circle_x1 + self.ICON_CIRCLE_SIZE
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=LIGHT_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - moon.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - moon.height)/2)
        self._img.paste(moon, (icon_x, icon_y), moon)

    def _draw_progress_bar_mid(self):
        self._draw_progress_done()
        self._draw_progress_remaining()
        self._draw_progress_circle()

    def _draw_progress_bar(self):
        self._draw_moon()
        self._draw_progress_bar_mid()
        self._draw_carriage()

    def draw(self):
        self._draw_percent()
        self._draw_weekday()
        self._draw_progress_bar()
        return self._img

    def _draw_progress_done(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        x2 = self._get_progress_bar_mid_x_point()
        self._img_draw.rectangle((x1, y1, x2, y2), fill=LIGHT_GRAY)

    def _draw_progress_remaining(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self._get_progress_bar_mid_x_point()
        x2 = self.width - self.ICON_X_MARGIN - self.ICON_CIRCLE_SIZE
        self._img_draw.rectangle((x1, y1, x2, y2), fill=DARK_GRAY)

    def _draw_progress_circle(self):
        mid_x = self._get_progress_bar_mid_x_point()
        mid_y = self.PROGRESS_BAR_Y_CENTER
        size = self.PROGRESS_BAR_HEIGHT
        pos = (mid_x-size/2, mid_y-size/2, mid_x+size/2, mid_y+size/2)
        self._img_draw.ellipse(pos, fill=LIGHT_GRAY)

    def _get_progress_bar_length(self):
        return self.width - 2*self.ICON_X_MARGIN - 2*self.ICON_CIRCLE_SIZE

    def _get_progress_bar_mid_x_point(self):
        offset = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        return offset + self._get_progress_bar_length()*self.pregnancy.get_progress()