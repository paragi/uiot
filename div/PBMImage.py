
# configuration
display_width = 128
display_height = 64


class Display_stub:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y

    def text(self, str, x, y, c = 1):
        print(str)

    def pixel(self, x, y, c):
        pass

    def show(self):
        pass
    def invert(self, state):
        pass

class DisplayStub:
    def __init__(self, display_width, display_height, bus = None):
        self.width = display_width
        self.height = display_height
        self.size = int(self.width * self.height / 8)
        self.buffer = bytearray(self.size)

    def show(self):
        print()  # New line"
        for y in range(0, self.height):
            print("-", end ="")
            for x in range(0, self.width//6):
                byte_index = int((y * self.width + x) / 8)
                for bit in range(7, -1, -1):
                    print(int((self.buffer[byte_index] & (1 << bit)) != 0), end ="")
            print()

    def pixel(self,x, y, c):
            c = int(c != 0)
            byte_index, bit = divmod(y * self.width + x, 8)
            self.buffer[byte_index] = self.buffer[byte_index] & ~(c << bit)

    def text(self, str, x, y, c = 1):
        print(str)

    def invert(self, state):
        pass

class PBMImage:
    def __init__(self, file_name):
        self.width = 0
        self.height = 0
        self.image = bytearray()
        self.loaded = False
        self.error_message = ""

        try:
            with open(file_name, 'rb') as f:
                # identifying pbm file type. "P1" = ascii "P4"= binary
                magic_number = str(f.readline(), 'utf-8').strip()
                if magic_number != "P4":
                    self.error_message = "Wrong file format ( %d ) (expecting binary/raw pbm format)" % magic_number
                    return
                comment = str(f.readline())
                self.width, self.height = [int(x) for x in f.readline().split()]
                if not self.width or not self.height:
                    self.error_message = "Size error"
                    return
                self.image = f.read(-1)
                self.len = len(self.image)
                if self.width * self.height / 8 != self.len:
                    self.error_message = "Size mismatch: x%d y%d l%d" % (self.width, self.height, self.len)
                    return
        except IOError:
            self.error_message = "Error While Opening the file ( %s )" % file_name
            return
        self.loaded = True


def display_splash():
    image = PBMImage('init_logo.pbm')
    if not image.loaded:
        print("No init image:", image.error_message)
        return

    for y in range(0, image.height):
        for x in range(0, image.width):
            byte_index = int((y * image.width + x) /8)
            for bit in range(0,8):
                display.pixel(x, y, int(image.image[byte_index] & 1<<bit != 0))

    display.show()

if __name__ == '__main__':
    display = DisplayStub(display_width, display_height)
    display_splash()
