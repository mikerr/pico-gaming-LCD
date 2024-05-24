# load bmp direct to screen
# 24bit BMP, uncompressed

from lcd13 import *
import os

def readbmp(fb,filename):
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
                             
        #gc.collect()
        #buffer = bytearray(height * width *2)
        #sprite1 = framebuf.FrameBuffer(buffer, width, height, framebuf.RGB565)
        for x in range(height):
            colrow = list(bytearray(f.read(3 * width)))
            #if ( x % 30 == 0) : LCD.show()
            for y in range(width):
                b,g,r = colrow[y*3:y*3+3]
                # RGB565
                rgb = ((r >> 3)  << 11) | ((g >>2) << 5) | (b >> 3 )
                
                # swap needed for ILI9341 screen
                swapL = rgb >> 8
                swapH = (rgb & 0x00FF) << 8
                col = swapL | swapH
                
                fb.pixel(y,height - x,col)
                
        f.close()
        return 
    
if __name__=='__main__':

    LCD = LCD_1inch3()
     
    LCD.fill(0)
    #LCD.show()
    if 'pic' in globals() :
        readbmp(LCD,pic)
        LCD.show()
    else :
      while True:
        path = "img/"
        files = os.listdir(path)
        for file in files:
            readbmp(LCD,path + file)
            LCD.show()
