import lvgl as lv
from machine import I2C, Pin, I2C_simulation

class FT6x36:
    def __init__(self, sda, scl, freq=100000, addr=0x38, width=-1, height=-1,
                 inv_x=False, inv_y=False, swap_xy=False):

        # if not lv.is_initialized():
        #     lv.init()

        self.width, self.height = width, height
        self.inv_x, self.inv_y, self.swap_xy = inv_x, inv_y, swap_xy
        self.i2c = I2C_simulation(scl, sda, freq)
        self.addr = addr
        try:
            focaltech = int.from_bytes(self.readfrom_mem(0xA8, 1), "big")
            cipher_mid = int.from_bytes(self.readfrom_mem(0x9F, 1), "big")
            cipher_high = int.from_bytes(self.readfrom_mem(0xA3, 1), "big")
            if(focaltech != 0x11 or cipher_mid != 0x26 or cipher_high != 0x64):
                print(focaltech, cipher_mid, cipher_high)
                print('FT6X36 touch IC not found.')
                return
            hw_id = int.from_bytes(self.readfrom_mem(0xA6, 1), "big")
            rel = int.from_bytes(self.readfrom_mem(0xAF, 1), "big")
            lib = int.from_bytes(self.readfrom_mem(0xA1, 2), "big")
            print("FT6X36 touch IC ready (fw id 0x{0:X} rel {1:d}, lib {2:X})".format(hw_id, rel, lib))
        except:
            print("FT6X36 touch IC not responding")
            raise
            return
        self.point = lv.point_t( {'x': 0, 'y': 0} )
        self.points = [lv.point_t( {'x': 0, 'y': 0} ), lv.point_t( {'x': 0, 'y': 0} )]
        self.state = lv.INDEV_STATE.RELEASED

        # self.indev_drv = lv.indev_create()
        # self.indev_drv.set_type(lv.INDEV_TYPE.POINTER)
        # self.indev_drv.set_read_cb(self.callback)
        indev_drv = lv.indev_drv_t()
        indev_drv.init()
        indev_drv.type = lv.INDEV_TYPE.POINTER
        indev_drv.read_cb = self.callback
        indev_drv.register()
        self.indev_drv = indev_drv

    def readfrom_mem(self, addr, data_len):
        r_data = bytearray(data_len)
        self.i2c.read(self.addr, bytearray([addr, 0]), 1, r_data, data_len, 2)
        return r_data

    def callback(self, driver, data):

        def get_point(offset):
            x = (sensorbytes[offset    ] << 8 | sensorbytes[offset + 1]) & 0x0fff
            y = (sensorbytes[offset + 2] << 8 | sensorbytes[offset + 3]) & 0x0fff
            if (self.width != -1 and x >= self.width) or (self.height != -1 and y >= self.height):
                raise ValueError
            x = self.width - x - 1 if self.inv_x else x
            y = self.height - y - 1 if self.inv_y else y
            (x, y) = (y, x) if self.swap_xy else (x, y)
            return { 'x': x, 'y': y }

        data.point = self.points[0]
        data.state = self.state
        sensorbytes = self.readfrom_mem(0x02, 11)
        self.presses = sensorbytes[0]
        if self.presses > 2:
            return
        try:
            if self.presses:
                self.points[0] = get_point(1)
            if self.presses == 2:
                self.points[1] = get_point(7)
        except ValueError:
            return
        if sensorbytes[3] >> 4:
            self.points[0], self.points[1] = self.points[1], self.points[0]
        data.point = self.points[0]
        data.state = self.state = lv.INDEV_STATE.PRESSED if self.presses else lv.INDEV_STATE.RELEASED