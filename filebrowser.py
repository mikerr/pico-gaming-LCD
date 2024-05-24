
# filebrowser

from lcd13 import *
import os,time

LCD = LCD_1inch3()

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
 
def isdir (file): return( os.stat(file)[0] == 16384)

def view_text(LCD,pathfile):
    
    offset = 0
    try:
        while True:
            with open(pathfile,'tr') as f:
                LCD.fill(0)
                LCD.text(pathfile,100,0,LCD.red)
                y = 12
                l = 0
                for line in f:
                    if (l >= offset) :
                        LCD.text(line.strip(),0,y,LCD.white)
                        y += 12
                        if (y > 240) : break
                    l += 1
            LCD.show()
            offset +=  up.value() - down.value()
            if (keyB.value() == 0) : break
    except:
        LCD.text("binary file",10,100,LCD.white)
        LCD.show()
        time.sleep(1)
def wait_for_key(key) :
    while (key.value() != 0) : time.sleep (0.1)
    
def run_script(pathfile):
    exec (open(pathfile).read())
path = "/"
files = os.listdir(path)        
cursor = 0
while True:
    time.sleep(0.1)
    cursor += up.value() - down.value()
    cursor = max(0, min(cursor,len(files)-1)) # clamp
        
    LCD.fill(0)
    y = 0
    selected = ""
    for file in files:
            if (y == cursor) :
                selected = file
                LCD.rect(0, y *12, 240, 12, LCD.blue,1)
            if (isdir(path + file)) : color = LCD.green
            else : color = LCD.white
            LCD.text(file,10,y *12, color)
            y += 1
    if (keyA.value() == 0) :
        if (isdir(path + selected)) :
            # change directory
            path = selected + "/"
            files = os.listdir(path)
        else :
            # open file
            pathfile = path + selected
            if (pathfile.endswith(".txt")):
                view_text(LCD,path + selected)
            
            if (pathfile.endswith(".bmp")):
                LCD = ""
                pic = pathfile
                run_script("bmp2screen.py")
                wait_for_key(keyB)
            
            if (pathfile.endswith(".py")) :
                LCD =""
                run_script(path + selected)
                
    if (keyB.value() == 0) :
        # go back up a level
        path = "/"
        files = os.listdir(path)
    LCD.show()
