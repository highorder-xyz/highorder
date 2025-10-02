

import lvgl as lv
import utime
from usr.lcd import Ili9341
from machine import I2C, I2C_simulation
from machine import ExtInt, Pin
import log
from usr.touch import FT6x36
import ustruct as struct

# 设置日志输出级别
log.basicConfig(level=log.INFO)
ho_log = log.getLogger("highorder")

def fs_open_cb(drv, path, mode):

    if mode == lv.FS_MODE.WR:
        p_mode = 'wb'
    elif mode == lv.FS_MODE.RD:
        p_mode = 'rb'
    elif mode == lv.FS_MODE.WR | lv.FS_MODE.RD:
        p_mode = 'rb+'
    else:
        raise RuntimeError("fs_open_callback() - open mode error, %s is invalid mode" % mode)

    try:
        f = open(path, p_mode)

    except OSError as e:
        raise RuntimeError("fs_open_callback(%s) exception: %s" % (path, e))

    return {'file' : f, 'path': path}


def fs_close_cb(drv, fs_file):
    try:
        fs_file.__cast__()['file'].close()
    except OSError as e:
        raise RuntimeError("fs_close_callback(%s) exception: %s" % (fs_file.__cast__()['path'], e))

    return lv.FS_RES.OK


def fs_read_cb(drv, fs_file, buf, btr, br):
    try:
        tmp_data = fs_file.__cast__()['file'].read(btr)
        buf.__dereference__(btr)[0:len(tmp_data)] = tmp_data
        br.__dereference__(4)[0:4] = struct.pack("<L", len(tmp_data))
    except OSError as e:
        raise RuntimeError("fs_read_callback(%s) exception %s" % (fs_file.__cast__()['path'], e))

    return lv.FS_RES.OK


def fs_seek_cb(drv, fs_file, pos, whence):
    try:
        fs_file.__cast__()['file'].seek(pos, whence)
    except OSError as e:
        raise RuntimeError("fs_seek_callback(%s) exception %s" % (fs_file.__cast__()['path'], e))

    return lv.FS_RES.OK


def fs_tell_cb(drv, fs_file, pos):
    try:
        tpos = fs_file.__cast__()['file'].tell()
        pos.__dereference__(4)[0:4] = struct.pack("<L", tpos)
    except OSError as e:
        raise RuntimeError("fs_tell_callback(%s) exception %s" % (fs_file.__cast__()['path'], e))

    return lv.FS_RES.OK


def fs_write_cb(drv, fs_file, buf, btw, bw):
    try:
        wr = fs_file.__cast__()['file'].write(buf.__dereference__(btw)[0:btw])
        bw.__dereference__(4)[0:4] = struct.pack("<L", wr)
    except OSError as e:
        raise RuntimeError("fs_write_callback(%s) exception %s" % (fs_file.__cast__()['path'], e))

    return lv.FS_RES.OK


def fs_register(fs_drv, letter, cache_size=500):

    fs_drv.init()
    fs_drv.letter = ord(letter)
    fs_drv.open_cb = fs_open_cb
    fs_drv.read_cb = fs_read_cb
    fs_drv.write_cb = fs_write_cb
    fs_drv.seek_cb = fs_seek_cb
    fs_drv.tell_cb = fs_tell_cb
    fs_drv.close_cb = fs_close_cb
    fs_drv.register()


def bootup():
    # 创建lcd对象
    print("waiting device init...")
    lcd = Ili9341(clk=26000)
    LCD_SIZE_W = lcd._lcd_w
    LCD_SIZE_H = lcd._lcd_h
    lcd.Clear(0x0000)
    lcd.lcd.lcd_display_off()
    utime.sleep_ms(500)
    lcd.lcd.lcd_display_on()
    lcd.Clear(0x00)
    print("lcd init complete")

    lv.init() #Initialize LVGL resource
    # Register SDL display driver.
    disp_buf1 = lv.disp_draw_buf_t()
    buf1_1 = bytearray(LCD_SIZE_W * LCD_SIZE_H * 2)
    disp_buf1.init(buf1_1, None, len(buf1_1))
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf1
    disp_drv.flush_cb = lcd.lcd.lcd_write
    disp_drv.hor_res = LCD_SIZE_W
    disp_drv.ver_res = LCD_SIZE_H
    disp_drv.register()

    lv.tick_inc(10)
    lv.task_handler()
    version = '%s.%s'%(lv.version_major(), lv.version_minor())
    print("lvgl(%s) init complete"%(version))


    gpio_rst = Pin(Pin.GPIO13, Pin.OUT, Pin.PULL_PU,  1)
    gpio_rst.write(1)
    utime.sleep_ms(20)
    gpio_rst.write(0)
    utime.sleep_ms(20)
    gpio_rst.write(1)
    utime.sleep_ms(500)
    touch = FT6x36(Pin.GPIO8, Pin.GPIO9, width=LCD_SIZE_W, height=LCD_SIZE_H)
    print("touch init complete")

    # fs_drv = lv.fs_drv_t()
    # fs_register(fs_drv, 'U')

    # def touched(args):
    #     print('### touched interrupt  {} ###'.format(args))

    # gpio_int = Pin(Pin.GPIO11, Pin.IN, Pin.PULL_DISABLE, 1)
    # extint = ExtInt(ExtInt.GPIO11, ExtInt.IRQ_FALLING, ExtInt.PULL_DISABLE, touched)
    # extint.enable()

    return (LCD_SIZE_W, LCD_SIZE_H)
