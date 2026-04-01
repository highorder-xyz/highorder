
import lvgl as lv
import utime

class Assets:
    _font_paths = {
        'font_harmony20': 'U:/lv_font_harmony20.bin',
        'font_7segment20': 'U:/lv_font_7segment20.bin',
        'font_7segment28': 'U:/lv_font_7segment28.bin'
    }
    _fonts = {}

    @classmethod
    def font(cls, name):
        if name not in cls._font_paths:
            raise Exception('font name %s not found'%(name))
        if name not in cls._fonts:
            font_t = lv.font_load(cls._font_paths[name])
            cls._fonts[name] = font_t
        return cls._fonts[name]


class Clock(object):
    def __init__(self):
        self.timer = None
        self.font_7segment20 = Assets.font('font_7segment20')
        self.font_7segment28 = Assets.font('font_7segment28')

    def render(self, lv_obj):
        def timer_handler(timer):
            lt2 = utime.localtime()
            time_str2 = "%02d:%02d:%02d"%(lt2[3], lt2[4], lt2[5])
            date_str2 = "%02d-%02d"%(lt2[1], lt2[2])
            if time_str2 != time_str or date_str2 != date_str:
                time_label.set_text(time_str2)
                date_label.set_text(date_str2)

        lt = utime.localtime()
        clk_obj = lv.obj(lv_obj)
        clk_obj.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        clk_obj.set_flex_align(lv.FLEX_ALIGN.START,
                lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        clk_obj.set_width(160)
        clk_obj.set_height(78)
        time_label = lv.label(clk_obj)
        time_label.set_style_text_font(self.font_7segment28, 0)
        time_str = "%02d:%02d:%02d"%(lt[3], lt[4], lt[5])
        time_label.set_text(time_str)
        date_label = lv.label(clk_obj)
        date_label.set_style_text_font(self.font_7segment20, 0)
        date_str = "%02d-%02d"%(lt[1], lt[2])
        date_label.set_text(date_str)
        self.timer = lv.timer_create(timer_handler, 1000, None)

class PageRender(object):
    def __init__(self, core):
        self.win = None
        self.font_harmony20 = Assets.font('font_harmony20')
        self.core = core
        self.watch_timer = None
        self.refresh_timer = None
        self.route = None
        self.page = None
        self.init_styles()
        self.scr = None

    def init_styles(self):
        flex_style = lv.style_t()
        flex_style.init()
        flex_style.set_bg_opa(0)
        flex_style.set_pad_left(0)
        flex_style.set_pad_right(0)
        flex_style.set_pad_top(0)
        flex_style.set_pad_bottom(0)
        flex_style.set_border_width(0)
        self.flex_style = flex_style

    def watch_page_cb(self, timer):
        while 1:
            try:
                page_data = self.core.pages.popleft()
            except:
                break
            self.render(page_data)

    def refresh_cb(self, timer):
        if len(self.core.pages) > 0:
            return
        if not self.route:
            return
        route = self.route
        self.core.navigate_to(route)


    def register(self):
        self.watch_timer = lv.timer_create(self.watch_page_cb, 300, None)


    def clear_screen(self):
        if self.scr:
            del self.scr
            self.scr = None

    def close_refresh_timer(self):
        if self.refresh_timer:
            del self.refresh_timer
            self.refresh_timer = None

    def render(self, page):
        if page == self.page:
            print('same page, ignore...')
            return

        self.close_refresh_timer()

        route = page.get('route', '/')
        self.route = route
        self.page = page

        elements = page.get('elements', [])
        if len(elements) < 1:
            return

        scr = lv.obj()
        scr.set_width(240)
        scr.set_height(320)

        content = scr
        content.set_width(240)
        content.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        content.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        content.set_flex_align(lv.FLEX_ALIGN.START,
                lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        for el in elements:
            self.render_element(el, content)

        self.clear_screen()
        self.scr = scr
        lv.scr_load(self.scr)

        refresh_interval = int(page.get('refresh', {}).get('interval', 0))
        if refresh_interval and refresh_interval > 0:
            self.refresh_timer = lv.timer_create(self.refresh_cb, refresh_interval*1000, None)

    def event_handler(self, evt):
        code = evt.get_code()
        obj  = evt.get_target()

    def handle_route_to(self, route):
        print('handle route to %s'%(route))

    def render_element(self, el, lv_obj):
        # print('render_element', el.get('type'))
        el_type = el.get('type')
        if el_type == 'nav_bar':
            self.render_nav_bar(el, lv_obj)
        elif el_type == 'clock':
            self.render_clock(el, lv_obj)
        elif el_type == 'tab_bar':
            self.render_tab_bar(el, lv_obj)
        elif el_type == 'row':
            self.render_row(el, lv_obj)
        elif el_type == 'column':
            self.render_column(el, lv_obj)
        elif el_type == 'plain-text':
            self.render_plain_text(el, lv_obj)
        elif el_type == 'button':
            self.render_button(el, lv_obj)
        elif el_type == 'qrcode':
            self.render_qrcode(el, lv_obj)
        elif el_type == 'divider':
            self.render_divider(el, lv_obj)
        elif el_type == 'progressbar':
            self.render_progressbar(el, lv_obj)
        elif el_type == 'checkbox':
            self.render_checkbox(el, lv_obj)

    def render_nav_bar(self, opt, lv_obj):
        self.win.add_title(opt.get('title', ''))

    def render_clock(self, opt, lv_obj):
        clock = Clock()
        clock.render(lv_obj)

    def render_tab_bar(self, opt, lv_obj):
        def tab_bar_event_handler(evt):
            obj  = evt.get_target()
            selected = obj.get_selected_btn()

            if selected < len(hrefs):
                href = hrefs[selected]
                self.handle_route_to(href)

        tabs = lv.btnmatrix(lv_obj)
        hrefs = []
        btnm_map = []
        for tab in opt.get('tabs', []):
            btnm_map.append(tab.get('name', ''))
            hrefs.append(tab.get('href', ''))
        btnm_map.append("")

        tabs.set_map(btnm_map)
        tabs.set_one_checked(True)
        tabs.set_btn_ctrl(1, lv.btnmatrix.CTRL.CHECKED )
        # tabs.align(lv.ALIGN.CENTER, 0, 0)
        tabs.align(lv.ALIGN.TOP_MID, 0, 0)

        style_bg = lv.style_t()
        style_bg.init()
        style_bg.set_pad_all(0)
        style_bg.set_pad_gap(0)
        style_bg.set_clip_corner(True)
        style_bg.set_border_width(0)
        tabs.add_style(style_bg, 0)

        tabs.set_size(220, 40)
        tabs.add_event_cb(tab_bar_event_handler, lv.EVENT.PRESSED, None)

    def render_row(self, opt, lv_obj):
        row_obj = lv.obj(lv_obj)
        row_obj.set_flex_flow(lv.FLEX_FLOW.ROW)
        row_obj.set_flex_align(lv.FLEX_ALIGN.SPACE_AROUND,
                lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row_obj.set_width(lv.pct(100))
        row_obj.set_height(lv.SIZE.CONTENT)
        row_obj.add_style(self.flex_style, 0)
        for element in opt.get('elements', []):
            self.render_element(element, row_obj)

    def render_column(self, opt, lv_obj):
        column_obj = lv.obj(lv_obj)
        column_obj.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        column_obj.set_flex_align(lv.FLEX_ALIGN.START,
                lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        column_obj.set_width(lv.SIZE.CONTENT)
        column_obj.set_height(lv.pct(100))
        column_obj.add_style(self.flex_style, 0)
        for element in opt.get('elements', []):
            self.render_element(element, column_obj)

    def render_plain_text(self, opt, lv_obj):
        style = opt.get('style', {})
        tags = style.get('tags', [])
        label=lv.label(lv_obj)
        label.set_width(220)
        label.set_style_text_font(self.font_harmony20, 0)
        for tag in tags:
            if tag == 'underline':
                label.set_style_text_decor(lv.TEXT_DECOR.UNDERLINE, lv.PART.MAIN)
            elif tag == 'strike':
                label.set_style_text_decor(lv.TEXT_DECOR.STRIKETHROUGH, lv.PART.MAIN)
        text = opt.get("text", "")
        label.set_text(text)


    def render_button(self, opt, lv_obj):
        btn = lv.btn(lv_obj)
        # btn.add_event_cb(event_handler,lv.EVENT.ALL, None)

        btn.align(lv.ALIGN.CENTER,0,40)

        label=lv.label(btn)
        label.set_style_text_font(self.font_harmony20, 0)
        text = opt.get("text", "")
        label.set_text(text)
        label.center()


    def render_qrcode(self, opt, lv_obj):
        bg_color = lv.palette_lighten(lv.PALETTE.LIGHT_BLUE, 5)
        fg_color = lv.palette_darken(lv.PALETTE.BLUE, 4)

        qr = lv.qrcode(lv_obj, 120, fg_color, bg_color)
        data = opt.get('code', '')
        if data:
            qr.update(data,len(data))

    def render_divider(self, opt, lv_obj):
        style_bg = lv.style_t()

        style_bg.init()
        style_bg.set_border_color(lv.palette_main(lv.PALETTE.GREY))
        style_bg.set_border_width(2)

        bar = lv.bar(lv_obj)
        bar.remove_style_all()   # To have a clean start
        bar.add_style(style_bg, 0)

        bar.set_size(232, 2)
        bar.center()

    def render_progressbar(self, opt, lv_obj):
        value = int(opt.get('percent', 0))
        style_bg = lv.style_t()
        style_indic = lv.style_t()

        style_bg.init()
        style_bg.set_border_color(lv.palette_main(lv.PALETTE.BLUE))
        style_bg.set_border_width(2)
        style_bg.set_pad_all(6)            # To make the indicator smaller
        style_bg.set_radius(6)
        style_bg.set_anim_time(1000)

        style_indic.init()
        style_indic.set_bg_opa(lv.OPA.COVER)
        style_indic.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))
        style_indic.set_radius(3)

        bar = lv.bar(lv_obj)
        bar.remove_style_all()   # To have a clean start
        bar.add_style(style_bg, 0)
        bar.add_style(style_indic, lv.PART.INDICATOR)

        bar.set_size(160, 20)
        bar.center()
        bar.set_value(value, lv.ANIM.ON)

    def render_checkbox(self, opt, lv_obj):
        text = opt.get('text', '')
        value = opt.get('value', False)
        if value:
            value = True
        cb = lv.checkbox(lv_obj)
        cb.set_text(text)
        if value == True:
            cb.add_state(lv.STATE.CHECKED)