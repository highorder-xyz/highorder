
from machine import LCD
import sys

# 常用颜色定义
red = 0xF800            # 红色
green = 0x07E0          # 绿色
blue = 0x001F           # 蓝色
white = 0xFFFF          # 白色
black = 0x0000          # 黑色
purple = 0xF81F         # 紫色
color = white          # 默认背景色

XSTART_H    = 0xf0         # Start point X coordinate high byte register
XSTART_L    = 0xf1         # Start point X coordinate low byte register
XEND_H      = 0xE0         # End point X coordinate high byte register
XEND_L      = 0xE1         # End point X coordinate low byte register
YSTART_H    = 0xf2         # Start point y coordinate high byte register
YSTART_L    = 0xf3         # Start point y coordinate low byte register
YEND_H      = 0xE2         # End point y coordinate high byte register
YEND_L      = 0xE3         # End point y coordinate low byte register

XSTART      = 0xD0         # Start point X coordinate register (2byte)
XEND        = 0xD1         # End point X coordinate register (2byte)
YSTART      = 0xD2         # Start point Y coordinate register (2byte)
YEND        = 0xD3         # End point Y coordinate register (2byte)

fc=black
bc=white

class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


class Peripheral_LCD(object):
    '''
    LCD通用类,定义LCD屏的通用行为

    '''
    def __init__(self, child_self=None):

        if child_self is None:
            raise CustomError("child LCD should be init first. ")
        else:
            self._child_self = child_self


    def Clear(self, color):
        '''
        清屏
        :param color: color
        '''
        self._child_self.lcd.lcd_clear(color)

    def Fill(self, x_s, y_s, x_e, y_e, color):
        '''
        填充以起始坐标和结束坐标为对角线的矩形
        :param x_s: 起始x坐标
        :param y_s: 起始y坐标
        :param x_e: 结束x坐标
        :param y_e: 结束y坐标
        :param color: color
        '''
        tmp = color.to_bytes(2, 'little')
        count = (x_e - x_s + 1)*(y_e - y_s + 1)

        color_buf = bytearray(0)

        for i in range(count):
            color_buf += tmp

        self._child_self.lcd.lcd_write(color_buf, x_s, y_s, x_e, y_e)

    def ColorFill(self, x_s, y_s, x_e, y_e, color_buff):
        self._child_self.lcd.lcd_write(color_buff, x_s, y_s, x_e, y_e)

    def lcd_show_image(self, image_data, x, y, width, heigth):
        '''
        bytearray图片显示，如果图片宽高小于80x80，可直接该函数一次性写入并显示
        :param image_data:存放待显示图片的RGB数据
        :param x:起点x
        :param y:起点y
        :param width:图片宽度
        :param heigth:图片高度
        '''
        self._child_self.lcd.lcd_write(bytearray(image_data), x, y, x + width - 1, y + heigth - 1)


    @staticmethod
    def get_rgb565_color(r, g, b):
        '''
        将24位色转换位16位色
        如红色的24位色为0xFF0000，则r=0xFF,g=0x00,b=0x00,
        将r、g、b的值传入下面函数即可得到16位相同颜色数据
        '''
        return ((r << 8) & 0xF800) | ((g << 3) & 0x07E0) | ((b >> 3) & 0x001F)


class LCD_ST7789S(Peripheral_LCD):
    def __init__(self, InitData=None, width=320, height=240, clk=4, dir=0):
        self._LcdInit(InitData, width, height, dir, clk)
        super().__init__(self)

    def _LcdInit(self, InitData, width, height, dir, clk):
        L2R_U2D = 0
        L2R_D2U = 1
        R2L_U2D = 2
        R2L_D2U = 3

        U2D_L2R = 4
        U2D_R2L = 5
        D2U_L2R = 6
        D2U_R2L = 7

        regval = 0
        if(dir == L2R_U2D):
            regval |= (0 << 7) | (0 << 6) | (0 << 5)
        elif dir == L2R_D2U:
            regval |= (1 << 7) | (0 << 6) | (0 << 5)
        elif dir == R2L_U2D:
            regval |= (0 << 7) | (1 << 6) | (0 << 5)
        elif dir == R2L_D2U:
            regval |= (1 << 7) | (1 << 6) | (0 << 5)
        elif dir == U2D_L2R:
            regval |= (0 << 7) | (0 << 6) | (1 << 5)
        elif dir == U2D_R2L:
            regval |= (0 << 7) | (1 << 6) | (1 << 5)
        elif dir == D2U_L2R:
            regval |= (1 << 7) | (0 << 6) | (1 << 5)
        elif dir == D2U_R2L:
            regval |= (1 << 7) | (1 << 6) | (1 << 5)
        else:
            regval |= (0 << 7) | (0 << 6) | (0 << 5)

        self._lcd_w = width
        self._lcd_h = height

        if(regval & 0X20):
            if(width < height):
                self._lcd_w = height
                self._lcd_h = width
        else:
            if(width > height):
                self._lcd_w = height
                self._lcd_h = width

        print(self._lcd_w, self._lcd_h)

        init_data = (
            2, 0, 120,

            0, 1, 0x36,
            1, 1, 0x00,
            0, 1, 0x3A,
            1, 1, 0x55,

            0, 5, 0xB2,
            1, 1, 0x0c,
            1, 1, 0x0c,
            1, 1, 0x00,
            1, 1, 0x33,
            1, 1, 0x33,

            0, 1, 0xB7,
            1, 1, 0x35,

            0, 1, 0xBB,
            1, 1, 0x28,
            0, 1, 0xC0,
            1, 1, 0x2C,
            0, 1, 0xC2,
            1, 1, 0x01,
            0, 1, 0xC3,
            1, 1, 0x0b,
            0, 1, 0xC4,
            1, 1, 0x20,
            0, 1, 0xC6,
            1, 1, 0x0F,
            0, 2, 0xD0,
            1, 1, 0xA4,
            1, 1, 0xA1,

            0, 14, 0xE0,
            1, 1, 0xD0,
            1, 1, 0x01,
            1, 1, 0x08,
            1, 1, 0x0F,
            1, 1, 0x11,
            1, 1, 0x2A,
            1, 1, 0x36,
            1, 1, 0x55,
            1, 1, 0x44,
            1, 1, 0x3A,
            1, 1, 0x0B,
            1, 1, 0x06,
            1, 1, 0x11,
            1, 1, 0x20,

            0, 14, 0xE1,
            1, 1, 0xD0,
            1, 1, 0x02,
            1, 1, 0x07,
            1, 1, 0x0A,
            1, 1, 0x0B,
            1, 1, 0x18,
            1, 1, 0x34,
            1, 1, 0x43,
            1, 1, 0x4A,
            1, 1, 0x2B,
            1, 1, 0x1B,
            1, 1, 0x1C,
            1, 1, 0x22,
            1, 1, 0x1F,

            0, 0, 0x21,
            0, 0, 0x11,

            2, 0, 120,
            0, 0, 0x29,

            0, 1, 0x36,
            1, 1, regval
        )
        lcd_set_display_area = (
            0, 4, 0x2a,
            1, 1, 0x00,
            1, 1, 0x00,
            1, 1, 0x01,
            1, 1, 0x40,
            0, 4, 0x2b,
            1, 1, 0x00,
            1, 1, 0x00,
            1, 1, 0x00,
            1, 1, 0xf0,
            0, 0, 0x2c,
        )
        lcd_display_on = (
            0, 0, 0x11,
            2, 0, 20,
            0, 0, 0x29,
        )
        lcd_display_off = (
            0, 0, 0x28,
            2, 0, 120,
            0, 0, 0x10,
        )
        if InitData is None:
            self._initData = bytearray(init_data)
        else:
            self._initData = InitData

        self._invalidData = bytearray(lcd_set_display_area)
        self._displayOn = bytearray(lcd_display_on)
        self._displayOff = bytearray(lcd_display_off)

        self.lcd = LCD()

        self.lcd.lcd_init(
            self._initData,
            self._lcd_w,
            self._lcd_h,
            clk,
            1,
            4,
            0,
            self._invalidData,
            None,
            None,
            None,
            1,
            0,
            0,
            4,
            0,
            0)


class Ili9341(Peripheral_LCD):
    def __init__(self, InitData=None, width=320, height=240, clk=26000,dir=0):
        self._LcdInit(InitData, width, height, dir,clk)
        super().__init__(self)

    def _LcdInit(self, InitData,width,height,dir,clk):
        L2R_U2D = 0
        L2R_D2U = 1
        R2L_U2D = 2
        R2L_D2U = 3

        U2D_L2R = 4
        U2D_R2L = 5
        D2U_L2R = 6
        D2U_R2L = 7

        regval = 1 << 3
        if(dir == L2R_U2D):
            regval |= (0<<7)|(0<<6)|(0<<5)
        elif dir == L2R_D2U:
            regval |= (1<<7)|(0<<6)|(0<<5)
        elif dir == R2L_U2D:
            regval |= (0<<7)|(1<<6)|(0<<5)
        elif dir == R2L_D2U:
            regval |= (1<<7)|(1<<6)|(0<<5)
        elif dir == U2D_L2R:
            regval |= (0<<7)|(0<<6)|(1<<5)
        elif dir == U2D_R2L:
            regval |= (0<<7)|(1<<6)|(1<<5)
        elif dir == D2U_L2R:
            regval |= (1<<7)|(0<<6)|(1<<5)
        elif dir == D2U_R2L:
            regval |= (1<<7)|(1<<6)|(1<<5)
        else:
            regval |= (0<<7)|(0<<6)|(0<<5)


        self._lcd_w = width
        self._lcd_h = height
        if(regval&0X20):
            if(width < height):
                self._lcd_w = height
                self._lcd_h = width
        else:
            if(width > height):
                self._lcd_w = height
                self._lcd_h = width

        print(self._lcd_w, self._lcd_h)

        init_data = (
            2, 0, 120,
            0,3,0xCF,
            1,1,0x00,
            1,1,0xD9,
            1,1,0X30,
            0,4,0xED,
            1,1,0x64,
            1,1,0x03,
            1,1,0X12,
            1,1,0X81,
            0,3,0xE8,
            1,1,0x85,
            1,1,0x10,
            1,1,0x7A,
            0,5,0xCB,
            1,1,0x39,
            1,1,0x2C,
            1,1,0x00,
            1,1,0x34,
            1,1,0x02,
            0,1,0xF7,
            1,1,0x20,
            0,2,0xEA,
            1,1,0x00,
            1,1,0x00,
            0,1,0xC0,
            1,1,0x1B,
            0,1,0xC1,
            1,1,0x12,
            0,2,0xC5,
            1,1,0x08,
            1,1,0x26,
            0,1,0xC7,
            1,1,0XB7,
            0,1,0x36,
            1,1,regval,
            0,1,0x3A,
            1,1,0x55,
            0,2,0xB1,
            1,1,0x00,
            1,1,0x1A,
            0,2,0xB6,
            1,1,0x0A,
            1,1,0xA2,
            0,1,0xF2,
            1,1,0x00,
            0,1,0x26,
            1,1,0x01,
            0,15,0xE0,
            1,1,0x0F,
            1,1,0x1D,
            1,1,0x1A,
            1,1,0x0A,
            1,1,0x0D,
            1,1,0x07,
            1,1,0x49,
            1,1,0X66,
            1,1,0x3B,
            1,1,0x07,
            1,1,0x11,
            1,1,0x01,
            1,1,0x09,
            1,1,0x05,
            1,1,0x04,
            0,15,0XE1,
            1,1,0x00,
            1,1,0x18,
            1,1,0x1D,
            1,1,0x02,
            1,1,0x0F,
            1,1,0x04,
            1,1,0x36,
            1,1,regval,
            1,1,0x4C,
            1,1,0x07,
            1,1,0x13,
            1,1,0x0F,
            1,1,0x2E,
            1,1,0x2F,
            1,1,0x05,
            0,4,0x2B,
            1,1,0x00,
            1,1,0x00,
            1,1,0x01,
            1,1,0x3f,
            0,4,0x2A,
            1,1,0x00,
            1,1,0x00,
            1,1,0x00,
            1,1,0xef,
            0,0,0x11,
            2, 0, 120,
            0,0,0x29,
        )
        lcd_set_display_area = (
            0,4,0x2a,
            1,1,XSTART_H,
            1,1,XSTART_L,
            1,1,XEND_H,
            1,1,XEND_L,
            0,4,0x2b,
            1,1,YSTART_H,
            1,1,YSTART_L,
            1,1,YEND_H,
            1,1,YEND_L,
            0,0,0x2c,
        )
        lcd_display_on = (
            0, 0, 0x11,
            2, 0, 20,
            0, 0, 0x29,
        )
        lcd_display_off = (
            0,0,0x28,
            2,0,120,
            0,0,0x10,
        )
        if InitData is None:
            self._initData = bytearray(init_data)
        else:
            self._initData = InitData

        self._invalidData = bytearray(lcd_set_display_area)
        self._displayOn = bytearray(lcd_display_on)
        self._displayOff = bytearray(lcd_display_off)

        self.lcd = LCD()
        r = self.lcd.lcd_init(
            self._initData,
            self._lcd_w,
            self._lcd_h,
            clk,
            1,
            4,
            0,
            self._invalidData,
            self._displayOn,
            self._displayOff,
            None)
        print('lcd init result: ' + str(r))