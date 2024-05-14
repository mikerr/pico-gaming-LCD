
from machine import Pin,SPI,PWM
import framebuf
import time,random
import gc

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

class LCD_1inch3(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 240
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,100000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

  
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
        buffer = bytearray(height * width *2)
        sprite1 = framebuf.FrameBuffer(buffer, width, height, framebuf.RGB565)
        for x in range(height):
            for y in range(width):       
                col = lebytes_to_int(list(bytearray(f.read(3))))
                sprite1.pixel(y,height - x,col)
        f.close()
        return (sprite1)
    
def getsprite (spritesheet, width, height, x, y):     
        # make small sprites by blitting spritesheet over a small framebuf,
        # taking advantage of clipping
        gc.collect()
        buffer = bytearray(height * width *2)
        sprite = framebuf.FrameBuffer(buffer, width, height, framebuf.RGB565)
        sprite.blit(spritesheet,-x,-y)
        return (sprite)
    
class spriteobj:
    x = y = 0
    xdir = 3
    ydir = 0.5
    
def collide (obj,x1,y1):
    if (abs(x - obj.x) + abs(y - obj.y) < 20) : return True
    else : return False

def hitplatform (x,y):
    for p in platforms:
            px,py,width = p
            if ( (x > px and (x-px) < width) and (abs(py - y - 8) < 8)) : return True
    return False

if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)

    LCD = LCD_1inch3()
    
    keyA = Pin(15,Pin.IN,Pin.PULL_UP)
    keyB = Pin(17,Pin.IN,Pin.PULL_UP)
    keyX = Pin(19 ,Pin.IN,Pin.PULL_UP)
    keyY= Pin(21 ,Pin.IN,Pin.PULL_UP)
    
    up = Pin(2,Pin.IN,Pin.PULL_UP)
    down = Pin(18,Pin.IN,Pin.PULL_UP)
    left = Pin(16,Pin.IN,Pin.PULL_UP)
    right = Pin(20,Pin.IN,Pin.PULL_UP)
 
    LCD.fill(LCD.blue)
    LCD.text("Loading...",20,100,LCD.white)
    LCD.show()
    # takes 5 seconds..
    spritesheet = readbmp ("jetpac.bmp")

    jetmansprite = getsprite(spritesheet,17,23,0,24)
    aliensprite = getsprite(spritesheet,16,16,0,50)
    fuelsprite = getsprite(spritesheet,16,16,112,100)
    gemsprite = getsprite(spritesheet,16,16,112,0)
    rocketsprite = getsprite(spritesheet,16,64,39,64)
    
    x = y = 150
    xdir = ydir = 5
    costume = 0
    frames = 0
    
    fuel = spriteobj()
    fuel.x = 110
    
    aliens = [spriteobj() for i in range(3)]
    for alien in aliens :
        alien.x = random.randrange(200)
        alien.y = random.randrange(200)
    
    platforms = [(32,90,60), (90,150,60), (172,52,60), (-20,238,250)]
    while True:
        LCD.fill(LCD.blue)    
        time.sleep(0.02)
        frames += 1  
        #walking animation on ground
        if (frames % 2 and abs(ydir) < 1 and abs(xdir) > 1 ) :
            costume = 24 - costume
            jetmansprite = getsprite(spritesheet,17,23,0,costume)
        
        #move directions
        xdir += left.value() - right.value()
        if (keyA.value() == 0): ydir -= 1        
        # not too fast
        if (abs(xdir) > 15): xdir *= 0.5
        xdir *= 0.9
        # keep on screen
        if (x < -15 ): x = 230
        if (x > 230) : x = -15
        if (y > 220): y = 210
        if (y < 0) : ydir = 1
        
        x += xdir 
        y += ydir 
        # gravity
        ydir += 0.5
        fuel.y += fuel.ydir
        if (fuel.ydir > 0) : fuel.ydir += 0.5
        
        if (hitplatform(fuel.x,fuel.y)) :
            fuel.ydir = 0
        if (hitplatform(x,y + 10) and ydir > 0) :
            ydir = 0
        #laser
        if (keyB.value() == 0) :
            for laser in range(5,50):
                if (xdir > 1) : laser *= -1;
                if (random.random() > 0.5) : LCD.pixel(int(x) - laser,int(y) + 15, LCD.green)
        #aliens
        for alien in aliens :
            alien.x += alien.xdir
            alien.y += alien.ydir
            splat = False
            if (alien.x > 220 or hitplatform(alien.x,alien.y)):
                splat = True
            # player collides with alien
            if (collide(alien,x,y)) :
                xdir = ydir = 10
                splat = True
            if (splat) :
                alien.x = -10
                alien.y = random.randrange(200)
                alien.xdir = 2 + random.randrange(3)
            LCD.blit(aliensprite,int(alien.x),int(alien.y),0)
        
        LCD.blit(gemsprite,185,37,0)
        LCD.blit(fuelsprite,int(fuel.x),int(fuel.y),0)
        LCD.blit(rocketsprite,160,190,0)
        LCD.blit(jetmansprite,int(x),int(y),0)
        # platforms
        for p in platforms:
            px,py,width = p
            LCD.line(px, py, px +width ,py ,LCD.green)
            LCD.line(px, py+1, px +width ,py+1 ,LCD.green)
        LCD.show()
