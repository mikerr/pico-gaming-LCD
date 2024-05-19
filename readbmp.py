import framebuf

# Read a BMP image direct into a framebuffer
# 24bit uncompressed
# Allocate the framebufffer to the same size as image, and returns framebuffer
# designed for low memory e.g. pi pico

def readbmp(filename):
        def lebytes_to_int(bytes):
            n = 0x00
            while len(bytes) > 0:
                n <<= 8
                n |= bytes.pop()
            return int(n)

        f = open(filename, 'rb') 
        img_bytes = list(bytearray(f.read(26))) # just read header
        start_pos = lebytes_to_int(img_bytes[10:14])

        width = lebytes_to_int(img_bytes[18:22])
        height = lebytes_to_int(img_bytes[22:26])
        
        seektostart = f.read(start_pos - 26)
                             
        gc.collect()
        buffer = bytearray(height * width * 2)
        spritesheet = framebuf.FrameBuffer(buffer, width, height, framebuf.RGB565)
        for x in range(height):
            colrow= list(bytearray(f.read(3 * width)))
            for y in range(width):       
                b,g,r = colrow[y*3:y*3+3]
                # RGB565
                rgb = ((r >> 3)  << 11) | ((g >>2) << 5) | (b >> 3 )
                
                # swap needed for ILI9341 screen
                swapL = rgb >> 8
                swapH = (rgb & 0x00FF) << 8
                col = swapL | swapH
                
                fb.pixel(y,height - x,col)
                spritesheet.pixel(y,height - x,col)
        f.close()
        return (spritesheet)
