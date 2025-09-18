#from WindowRenderer import *
import sys
import time

import threading
#from tkinter import *
import tkinter
from typing import cast

from PIL import Image as PILImage
from PIL import ImageTk
#import Image,

def fn1(root,canvas:tkinter.Canvas,pi,img):
    for i in range(0, 800):
        for j in range(0, 600):
            pass
            pi[i, j] = (255, 0, 0, 255)
    myImg = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, image=myImg, anchor=tkinter.NW)
    canvas.update()
    root.after(100,fn2,root,canvas,pi,img)
    print("here1")

def fn2(root,canvas,pi,img):
    print("here2")
    for i in range(0, 800):
        for j in range(0, 600):
            pi[i, j] = (255, 0, 255, 255)
    img.show()
    myImg = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, image=myImg, anchor=tkinter.NW)
    canvas.update()
    root.after(100, fn1,root,canvas,pi,img)

def Main():
    root = tkinter.Tk()
    root.geometry("800x600")


    canvas: tkinter.Canvas = tkinter.Canvas(root, width = 800, height = 600)
    canvas.pack()

    img = PILImage.new("RGBA", (800, 600), (0, 0, 0, 0))
    pi = img.load()

    for i in range(0, 800):
        for j in range(0, 600):
            pi[i, j] = (255, 0, 255, 255)

    myImg = ImageTk.PhotoImage(image=img)

    canvas.create_image (400,300,image =myImg)
    canvas.update()

    root.mainloop()

    pass

if __name__ == "__main__":
    Main()
