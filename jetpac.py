# jetpac
from lcd13 import *
from readbmp import *
import time,random
  
def getsprite (spritesheet, width, height, x, y):     
        # make small sprites by blitting spritesheet over a small framebuf,
        # taking advantage of clipping
        buffer = bytearray(height * width * 2)
        sprite = framebuf.FrameBuffer(buffer, width, height, framebuf.RGB565)
        sprite.blit(spritesheet,-x,-y)
        return (sprite)
    
class spriteobj:
    x = y = 0
    xdir = 3
    ydir = 0.5
    time = 0
    grabbed = 0
def collide (obj,x1,y1,xdistance):
    #xdistance = 10
    ydistance = 10
    if (abs(x - obj.x) < xdistance  and abs(y - obj.y) < ydistance) : return True
    else : return False

def hitplatform (x,y):
    for p in platforms:
            px,py,width = p
            if ( (x > px and (x-px) < width) and (abs(py - y - 8) < 8)) : return True
    return False

if __name__=='__main__':
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
    # takes 1 second..
    start = time.ticks_ms()
    spritesheet = readbmp ("jetpac.bmp")
    print (time.ticks_ms() - start)
    
    jetmansprite = getsprite(spritesheet,17,23,0,24)
    aliensprite = getsprite(spritesheet,16,16,0,50)
    splatsprite = getsprite(spritesheet,25,16,69,0)
    fuelsprite = getsprite(spritesheet,16,16,112,100)
    gemsprite = getsprite(spritesheet,16,16,112,0)
    rocketsprite = getsprite(spritesheet,16,64,39,64)
    
    x = y = 150
    xdir = ydir = 5
    costume = 0
    frames = 0
    
    splat = spriteobj()
    fuel = spriteobj()
    fuel.x = 110
    
    aliens = [spriteobj() for i in range(3)]
    for alien in aliens :
        alien.x = random.randrange(200)
        alien.y = random.randrange(200)
    
    platforms = [(32,90,60), (90,150,60), (172,52,60), (-20,238,250)]
    
    gc.collect()
    #print(gc.mem_free())
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
        if (fuel.ydir > 0) : fuel.ydir += 0.1
        
        if (hitplatform(fuel.x,fuel.y)) :
            fuel.ydir = 0
        if (hitplatform(x,y + 10) and ydir > 0) :
            ydir = 0
        #laser
        if (keyB.value() == 0) : firing  = 1
        else : firing = 0
        
        #aliens
        for alien in aliens :
            alien.x += alien.xdir
            alien.y += alien.ydir
            dead = 0
            if (alien.x > 240) : dead = 1
            if (hitplatform(alien.x,alien.y)) : dead = 1
            if (firing and collide(alien,x,y,50)) : dead = 1
            # player collides with alien
            if (collide(alien,x,y,10)) :
                xdir = ydir = 10
                dead = 1
            if (dead) :
                    splat.x = alien.x
                    splat.y = alien.y
                    splat.time = 5
                    
                    alien.x = -10
                    alien.y = random.randrange(200)
                    alien.xdir = 2 + random.randrange(3)        
            LCD.blit(aliensprite,int(alien.x),int(alien.y),0)
        #explosions stay on screen for 5 frames    
        if (splat.time  > 0) :
            splat.time -= 1
            LCD.blit(splatsprite,int(splat.x),int(splat.y),0)
        
        # fuel grabbing and dropping
        if (not fuel.grabbed and collide(fuel,x,y-30,10)) : fuel.grabbed = 1
        if (fuel.grabbed) :
                fuel.x = x
                fuel.y = y + 20
                fuel.ydir = 1
                dropzone = 180
                if (abs(fuel.x - dropzone) < 20) : fuel.grabbed = 0
        if (fuel.y > 220) :
            fuel.x = 100
            fuel.y = 0
            fuel.ydir = 1
        LCD.blit(fuelsprite,int(fuel.x),int(fuel.y),0)
        
        LCD.blit(gemsprite,185,37,0)
        LCD.blit(rocketsprite,160,190,0)
        LCD.blit(jetmansprite,int(x),int(y),0)
        # platforms
        for p in platforms:
            px,py,width = p
            LCD.line(px, py, px +width ,py ,LCD.green)
            LCD.line(px, py+1, px +width ,py+1 ,LCD.green)
        #laser
        if firing:
            for laser in range(5,50):
                if (xdir > 1) : laser *= -1;
                if (random.random() > 0.5) : LCD.pixel(int(x) - laser,int(y) + 15, LCD.green)
        LCD.show()
