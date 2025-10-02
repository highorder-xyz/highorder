

import lvgl as lv
import utime
from usr.boot import bootup

bootup()


def create_style_font(fontfile):
    style_font = lv.style_t()
    style_font.init()
    style_font.set_radius(0)
    style_font.set_bg_color(lv.color_make(0x21, 0x95, 0xf6))
    style_font.set_bg_grad_color(lv.color_make(0x21, 0x95, 0xf6))
    style_font.set_bg_grad_dir(lv.GRAD_DIR.VER)
    style_font.set_bg_opa(0)
    style_font.set_text_color(lv.color_make(0x00, 0x00, 0x00))
    font_t = lv.font_load('U:/%s'%(fontfile))
    style_font.set_text_font(font_t)
    style_font.set_text_letter_space(2)
    style_font.set_pad_left(0)
    style_font.set_pad_right(0)
    style_font.set_pad_top(0)
    style_font.set_pad_bottom(0)
    return style_font

style_font = create_style_font('lv_font_harmony20.bin')
style_font_led = create_style_font('lv_font_7segment20.bin')
style_font_led_big = create_style_font('lv_font_7segment28.bin')
# # # 创建样式
# style_font = lv.style_t()
# style_font.init()
# style_font.set_radius(0)
# style_font.set_bg_color(lv.color_make(0x21, 0x95, 0xf6))
# style_font.set_bg_grad_color(lv.color_make(0x21, 0x95, 0xf6))
# style_font.set_bg_grad_dir(lv.GRAD_DIR.VER)
# style_font.set_bg_opa(0)
# style_font.set_text_color(lv.color_make(0x00, 0x00, 0x00))
# style_font.set_text_font_v2('U:/lv_font_harmony20.bin', 23)
# # style_font.set_text_font(lv.font_default())
# style_font.set_text_letter_space(2)
# style_font.set_pad_left(0)
# style_font.set_pad_right(0)
# style_font.set_pad_top(0)
# style_font.set_pad_bottom(0)

# 创建一个界面
screen = lv.obj()

# 创建一个label
screen_label_welcome = lv.label(screen)
screen_label_welcome.set_pos(10, 120)
# screen_label_welcome.set_size(200, 32)
screen_label_welcome.set_text("汉字测试abc12")
screen_label_welcome.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
# add style for screen_label_welcome
screen_label_welcome.add_style(style_font, lv.PART.MAIN | lv.STATE.DEFAULT)




# 加载界面
class Clock(object):
    def __init__(self):
        self.timer = None

    def render(self, lv_obj):
        def timer_handler(timer):
            lt2 = utime.localtime()
            time_str2 = "%02d:%02d"%(lt2[3], lt2[4])
            date_str2 = "%02d-%02d"%(lt2[1], lt2[2])
            if time_str2 != time_str or date_str2 != date_str:
                time_label.set_text(time_str2)
                date_label.set_text(date_str2)

        lt = utime.localtime()
        clk_obj = lv.obj(lv_obj)
        clk_obj.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        time_label = lv.label(clk_obj)

        time_label.add_style(style_font_led_big, lv.PART.MAIN | lv.STATE.DEFAULT)
        time_str = "%02d:%02d"%(lt[3], lt[4])
        time_label.set_text(time_str)
        date_label = lv.label(clk_obj)
        date_label.add_style(style_font_led, lv.PART.MAIN | lv.STATE.DEFAULT)
        date_str = "%02d-%02d"%(lt[1], lt[2])
        date_label.set_text(date_str)
        self.timer = lv.timer_create(timer_handler, 1000, None)

clock = Clock()
clock.render(screen)
lv.scr_load(screen)
