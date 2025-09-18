#Requirements:
#   keyboard
#   numpy

import sys
import time
from tkinter import *
from SceneObject import *
import keyboard
from typing import cast


class Side:
    def __init__(self, absolute: Union[int|type(Ellipsis)] = ..., blocks: Union[int|type(Ellipsis)] = ..., block: Union[int|type(Ellipsis)] = ...):
        self.absolute: int = absolute
        self.blocks: int = blocks
        self.block: int = block
        self.Resize()
    
    def Resize(self, absolute: int|None = ..., blocks: int|None = ..., block: int|None = ...):
        if (absolute == ...) + (blocks == ...) + (block == ...) <= 1:
            self.absolute = absolute if absolute is not None else self.absolute
            self.blocks = blocks if blocks is not None else self.blocks
            self.block = block if block is not None else self.block

        try:
            if self.absolute is ...:
                self.absolute = int(self.blocks * self.block)
            if self.blocks is ...:
                self.blocks = int(self.absolute / self.block)
            if self.block is ...:
                self.block = int(self.absolute / self.blocks)
    
            if self.blocks * self.block != self.absolute:
                raise TypeError(f"At least two parameters must be provided.\n" +
                                f"Values: {self.__str__()}")

        except ValueError:
            raise ValueError("Parameters do not match up to create a field, the product of two is not the third.\n" +
                             "(If you're specifying the absolute value, make sure it's a multiple of the other.")
    def __str__(self):
        return f"absolute: {self.absolute}\tblocks: {self.blocks}\tblock: {self.block}"

class WindowRenderer:
    """Window renderer class

            A class to store and render a scene of physicalObject(s) rendering with Camera(s).

            You may pass a subclass of CustomMainloopClass to the parameter mainloopClassReference to be called as part of
            the mainloop of the program. To function the class must override the Mainloop function which only accepts self as a parameter.
            The class CustomMainloopClass also has a member master which becomes a reference to the renderer when the instance of the
            CustomMainloopClass is passed to the WindowRenderer constructor. By default, the CustomMainloopClass calls
            self.master.HandleInput() which handles user input for movement. Call super().Mainloop() to reference call the base function.
            HandleInput allows you to move around the scene using 'WASD' as well as 'space' and 'shift' and rotate using the arrow keys.
            Use 'TAB' to swap between the cameras in the scene.

            Use the AddSceneObject function to add objects to be rendered,
            alternatively create the sceneObject after creating the WindowRenderer
            by passing a reference to the WindowRenderer when creating the sceneObject using the renderer parameter.
            Note that once mainloop() has been called for the master you won't
            be able to add sceneObject(s) outside of events called by the mainloop,
            set autoStart to False if you want to add more objects before manually starting the mainloop.

            There are three variables pertaining to the length of the sides for the render canvas. Absolute is the length in pixels,
            blocks is the amount of blocks and block is the amount of pixels in a block. Two of these three must be assigned for both
            Height and Width, the third will be calculated if not assigned. Note that assigning all three, yet incorrectly will not result
            in the program fixing the mistake.
            These values can be reassigned using the ReassignSize function, where once again only two for each side must be specified.

            !-May change this-!
            You can create subclasses to the physicalObject class to pass them to WindowRenderer and have it render them however you like.
            The CastRayToObject member function belonging to physicalObject is called for every ray and expects a list of
            tuples list[tuple[Vector3D, float, float]] where the first element is a color in RGB [0,1].
            The second is the distance between the camera and the collision point, this is used to order different collisions as well as
            filter out negative distances which are behind the camera. The final element communicates how opaque whatever was collided with is,
            0 is completely transparent whereas 1 is completely opaque [0,1].
            !-May change this-!


            Parameters:
                master (Tk): The window that the canvas will be displayed on. If none is specified a new window will be created.

            Functions:
                ReassignSize(absoluteWidth: int = ..., absoluteHeight: int = ..., blocksWidth: int = ..., blocksHeight: int = ...,
                blockWidth: int = ..., blockHeight: int = ...):

                The ReassignSize function allows you to resize the canvas.
                For each side specify an int for a value you wish to change and None for one you wish to lock, the third unspecified value will be changed,
                Note that you can break the renderer if you specify incorrect values. If no values are parsed for any of the three values
                of one of the sides the side will not be changed.

            Examples:
                ReassignSize


        """

    class KeyChecker:
        def __init__(self):
            self.pressed = set()
            self.down = set()
            self.released = set()
            self._updated = set()

        def Clear(self):
            self.pressed.clear()
            self.released.clear()
            self._updated.clear()

        def _UpdateKey(self, key:str) -> None:
            if key in self._updated:
                return
            self._updated.add(key)
            KeyDown: bool = keyboard.is_pressed(key)

            if KeyDown != (key in self.down):
                if KeyDown:
                    self.pressed.add(key)
                    self.down.add(key)
                else:
                    self.down.discard(key)
                    self.released.add(key)

        def IsPressed(self, key:str) -> bool:
            self._UpdateKey(key)
            return key in self.pressed

        def IsReleased(self, key:str) -> bool:
            self._UpdateKey(key)
            return key in self.released

        @staticmethod
        def IsDown(key:str) -> bool:
            return keyboard.is_pressed(key)

        @staticmethod
        def IsUp(key:str) -> bool:
            return not keyboard.is_pressed(key)

        def __str__(self) -> str:
            return f"down: {self.down}, pressed: {self.pressed}, released: {self.released}, _updated: {self._updated}"

    instance:'WindowRenderer'
    def __init__(self, width:Side, height:Side,
                 mainloopClassReference: 'CustomMainloopClass' = ...,
                 master: Tk = ...,
                 delay: int = 25,
                 sceneObjects: list[SceneObject] = (),
                 autoStart: bool = True,
                 antiAliasing: bool = False):

        #Setting up the main loop function class
        self.mainloopClassReference: 'CustomMainloopClass' = mainloopClassReference
        if mainloopClassReference is not ...:
            self.mainloopClassReference.SetMaster(self)

        # Handle setting up Tk if none was provided
        ownMaster: bool = False
        if master is ...:
            ownMaster = True
            master = Tk()
            master.title("MyWindowTitle")

        #Miscelaneous metadata
        self.keyChecker: WindowRenderer.KeyChecker = WindowRenderer.KeyChecker()
        self.downKeys:set[str] = set()
        self.startTime: float = time.time()
        self.master: Tk = master
        self.delay: int = delay
        self.colorMatrix: list[list[Vector3D]] = []
        self.antiAliasing: bool = antiAliasing

        #SceneObjects
        self.sceneObjects: list[SceneObject] = []
        self.cameraObjects: list[Camera] =  []
        self.physicalObjects: list[PhysicalObject] = []
        self.nonViablePhysicalObjects: list[PhysicalObject] = []
        self.pointLights: list[PointLight] = []
        self.physicalLightObjects: list[LightObject] = []
        self.AddSceneObject(*sceneObjects)

        self.currentCamera: Camera|ellipsis = ...
        self.currentPlayer: PhysicalObject|ellipsis = ...

        #Size
        self.canvas: Canvas = Canvas()
        self.width: Side|None = None
        self.height: Side|None = None
        self.ReassignSize(width,height)

        if len(self.cameraObjects) != 0:
            self.currentCamera = self.cameraObjects[0]
        if len(self.nonViablePhysicalObjects) != 0:
            self.currentPlayer = self.nonViablePhysicalObjects[0]

        #Start loop
        self.master.after(self.delay, WindowRenderer.Mainloop, self)
        if ownMaster and autoStart:
            self.master.mainloop()

    def AddSceneObject(self, *addedSceneObjects: SceneObject):
        for sceneObject in addedSceneObjects:
            if sceneObject not in self.sceneObjects:
                #For example players which don't have a physical body
                if type(sceneObject) is PhysicalObject:
                    self.nonViablePhysicalObjects.append(cast(PhysicalObject,sceneObject))
                    if self.currentPlayer is ...:
                        self.currentPlayer = sceneObject

                #For example a sphere which is going to be rendered
                elif isinstance(sceneObject,PhysicalObject):
                    self.physicalObjects.append(sceneObject)

                #Cameras to view from
                elif isinstance(sceneObject,Camera):
                    self.cameraObjects.append(sceneObject)
                    if self.currentCamera is ...:
                        self.currentCamera = sceneObject
                elif isinstance(sceneObject,PointLight):
                    self.pointLights.append(sceneObject)
                elif isinstance(sceneObject,PhysicalLightObject):
                    self.physicalLightObjects.append(sceneObject)

                else:
                    print(type(sceneObject))
                    time.sleep(1)
                    raise TypeError
                sceneObject.renderer = self
                self.sceneObjects.append(sceneObject)

    def __str__(self)->str:
        return "0x"+"{hex:X}".format(hex = int(self.__repr__()[-19:-1],16)).zfill(18)

    def PrintObjects(self):
        print("SceneObjects:")
        for obj in self.sceneObjects:
            print(obj)
        print("PhysicalObjects:")
        for obj in self.physicalObjects:
            print(obj)
        print("CameraObjects:")
        for obj in self.cameraObjects:
            print(obj)
        print("NonViablePhysicalObjects:")
        for obj in self.nonViablePhysicalObjects:
            print(obj)

    def ReassignSize(self, width: Union[Side|type(Ellipsis)] = ..., height:Union[Side|type(Ellipsis)] = ...):
        if width is not ...:
            self.width = width
        if height is not ...:
            self.height = height

        # Canvas
        self.canvas.destroy()
        self.canvas = Canvas(self.master, width=self.width.absolute, height=self.height.absolute)
        self.canvas.width = self.width.absolute
        self.canvas.height = self.height.absolute
        self.canvas.pack()

        # Window size
        self.master.geometry(str(self.width.absolute) + "x" + str(self.height.absolute))


        # colorMatrix
        self.colorMatrix = []
        for i in range(self.width.blocks + 1):
            self.colorMatrix.append([])
            for j in range(self.height.blocks + 1):
                self.colorMatrix[i].append(Vector3D)

    def HandleInputs(self):
        if self.currentPlayer is not ...:
            if keyboard.is_pressed("w"):
                self.currentPlayer.MoveRelativePosition(self.currentCamera.PerfRot(Vector3D(0,0,1)))
            if keyboard.is_pressed("s"):
                self.currentPlayer.MoveRelativePosition(self.currentCamera.PerfRot(Vector3D(0,0,-1)))
            if keyboard.is_pressed("a"):
                self.currentPlayer.MoveRelativePosition(self.currentCamera.PerfRot(Vector3D(-1,0,0)))
            if keyboard.is_pressed("d"):
                self.currentPlayer.MoveRelativePosition(self.currentCamera.PerfRot(Vector3D(1,0,0)))
            if keyboard.is_pressed("space"):
                self.currentPlayer.MoveRelativePosition(self.currentCamera.PerfRot(Vector3D(0,1,0)))
            if keyboard.is_pressed("left_shift"):
                self.currentPlayer.MoveRelativePosition(self.currentCamera.PerfRot(Vector3D(0,-1,0)))
                
        if self.currentCamera is not ...:
            if keyboard.is_pressed("left_arrow"):
                self.currentPlayer.RotY(-math.pi/(2*10))
                self.cameraObjects[1].RotY(-math.pi/(2*10))
                self.cameraObjects[0].RotY(-math.pi/(2*10))
                if self.currentCamera is self.cameraObjects[1]:
                    self.currentCamera.RotY(-math.pi / (2 * 10))

            if keyboard.is_pressed("right_arrow"):
                self.currentPlayer.RotY(math.pi / (2 * 10))
                self.cameraObjects[1].RotY(math.pi / (2 * 10))
                self.cameraObjects[0].RotY(math.pi / (2 * 10))
                if self.currentCamera is self.cameraObjects[1]:
                    self.currentCamera.RotY(math.pi / (2 * 10))

            if keyboard.is_pressed("up_arrow"):
                self.currentCamera.RotX(math.pi/(2*10))
            if keyboard.is_pressed("down_arrow"):
                self.currentCamera.RotX(-math.pi / (2 * 10))

        if self.keyChecker.IsPressed("tab"):
            if self.currentCamera is ... or len(self.cameraObjects) == 0:
                print("There is no camera, add one to swap between them")
            elif len(self.cameraObjects) == 1 and self.cameraObjects[0] == self.currentCamera:
                print("There is only one camera, add one to swap between them")
            else:
                for index in range(len(self.cameraObjects)):
                    if self.cameraObjects[index] is self.currentCamera:
                        self.currentCamera = self.cameraObjects[(index+1)%len(self.cameraObjects)]
                        break
                else:
                    print("Current camera not found, setting to first camera.")
                    self.currentCamera = self.cameraObjects[0]

        if keyboard.is_pressed("escape"):
            sys.exit(0)

    @staticmethod
    def Mainloop(this: 'WindowRenderer'):
        start: float = time.time()
        if this.mainloopClassReference is not ...:
            this.mainloopClassReference.Mainloop()

        #for i in range(this.width.blocks):
        #    for j in range(this.height.blocks):
        #        this.renderBoxA(i,j)


        print("rendering")

        if this.antiAliasing:
            this.renderAntiAliasing()
        else:
            this.renderNoAntiAliasing()

        print("Finished rendering")

        # Clear just before going into render since this is when we're going to
        this.keyChecker.Clear()

        this.master.after(int(numpy.clip(this.delay+start-time.time(),0, this.delay)), WindowRenderer.Mainloop, this)

    def renderBoxA(self, x: int, y: int):
        color: int = (int(10 * (time.time() - self.startTime)) + x + 100 * y) % 255
        color: str = "#FF" + "0x{:02X}".format(color)[2:] + "FF"
        self.canvas.create_rectangle(x * self.width.block, y * self.height.block,
                                     (1 + x) * self.width.block, (1 + y) * self.height.block,
                                     fill=color, outline=color)

    def renderNoAntiAliasing(self):
        self.canvas.delete("all")
        if self.currentCamera is ...:
            return

        for i in range(self.width.blocks):
            for j in range(self.height.blocks):
                self.renderRaysNoAntiAliasing(i, j, self.currentCamera)


        self.canvas.update()

        self.canvas.postscript(file =r"Pictures/Render.img", colormode ="color")

    def renderRaysNoAntiAliasing(self, x: int, y: int, camera: Camera):
        vector = camera.PerfRot(Vector3D(  x=camera.fov.fovWidth*(((2 * x + 1)/self.width.blocks)-1),
                            y=-camera.fov.fovHeight*(((2 * y + 1)/self.height.blocks)-1),
                            z=1))
        color: Vector3D = WindowRenderer.CastRay(camera,vector,self.physicalObjects)
        self.canvas.create_rectangle(x * self.width.block, y * self.height.block,
                                     (x+1) * self.width.block-1,(y+1) * self.height.block-1,
                                     fill = color.ToColor(), outline= color.ToColor())

    def renderAntiAliasing(self):
        self.canvas.delete("all")
        if self.currentCamera is ...:
            return

        for i in range(self.width.blocks+1):
            for j in range(self.height.blocks+1):
                self.colorMatrix[i][j] =  self.renderRaysAntiAliasing(i, j, self.currentCamera)


        for i in range(self.width.blocks):
            for j in range(self.height.blocks):
                color: str = ((self.colorMatrix[i][j] + self.colorMatrix[i+1][j]+self.colorMatrix[i][j+1]+self.colorMatrix[i+1][j+1]) * 0.25).ToColor()
                self.canvas.create_rectangle(i * self.width.block, j * self.height.block,
                                         (1 + i) * self.width.block-1, (1 + j) * self.height.block-1,
                                         fill=color, outline=color)
        self.canvas.update()

    def renderRaysAntiAliasing(self, x: int, y: int, camera: Camera)->Vector3D:
        vector = camera.PerfRot(Vector3D(x=camera.fov.fovWidth * (((2 * x) / self.width.blocks) - 1),
                                         y=-camera.fov.fovHeight * (((2 * y) / self.height.blocks) - 1),
                                         z=1))
        return WindowRenderer.CastRay(camera,
                               vector,
                               self.physicalObjects)

    @staticmethod
    def CastRay(camera:Camera, vector: Vector3D, physicalObjects: list[PhysicalObject]) -> Vector3D:
        start:Vector3D = camera.GetAbsolutePosition()
        u:Vector3D = vector * (1/vector.abs())
        hitMarks: list[HitMark] = []
        for physicalObject in physicalObjects:
            if physicalObject in camera.filteredObjects:
                continue
            hitMarks.extend(physicalObject.CastRayToObject(start,u))

        hitMarks.sort(key=lambda x:x.distance)

        color: Vector3D = Vector3D()
        opacity: float = 0.0
        for hitMark in hitMarks:
            if hitMark.distance <= 0:
                continue
            vec:float=  (1 - cast(float, opacity))
            color += hitMark.color * (vec * hitMark.opacity)
            opacity += (hitMark.opacity * (1-opacity))
            if hitMark.opacity >=1:
                break
        return color


    #For debugging
    @staticmethod
    def HitInformation(physicalObject: PhysicalObject,u:Vector3D,hitMark: tuple[Vector3D,float,float])->None:
        print(physicalObject)
        if hitMark is not None:
            print("Hit location", hitMark[0])
            print("Radius", abs(hitMark[0]))
            print("T", hitMark[1])
            print("Origin vector", u * hitMark[1])
            print("Distance", abs(u * hitMark[1]))
            print()
        else:
            print("No hit")

class CustomMainloopClass:
    def __init__(self):
        self.master: WindowRenderer|None = None

    def SetMaster(self, master: WindowRenderer) -> None:
        self.master = master

    def Mainloop(self) -> None:
        self.master.HandleInputs()

class CustomClass(CustomMainloopClass):
    def Mainloop(self) -> None:
        super().Mainloop()
        master:WindowRenderer = self.master
        keyChecker: WindowRenderer.KeyChecker = master.keyChecker

        if keyChecker.IsPressed("r"):
            self.master.physicalObjects[1].tilt.Rot(tiltY=math.pi/6)

        if keyChecker.IsPressed("t"):
            self.master.physicalObjects[1].tilt.Rot(tiltX=math.pi/6)
                
        if keyChecker.IsPressed("y"):
            self.master.physicalObjects[1].tilt.Rot(tiltZ=math.pi/6)

        #master.PrintObjects()

        if keyboard.is_pressed("enter"):
            master.ReassignSize(Side(absolute= 500, block=5),Side( absolute= 425,block = 5))
        print(master.width)

def Main():
    width: int = 800
    height: int = 800
    blocksWidth = 50
    blocksHeight = 50
    blockSize: Union[int|type(Ellipsis)] = ...

    #Create renderer
    functionClass : CustomClass = CustomClass()
    WindowRenderer.instance = WindowRenderer(width = Side(absolute=width,blocks=blocksWidth, block=blockSize),
                                                    height = Side(absolute=height,blocks=blocksHeight, block=blockSize),
                                                    mainloopClassReference=functionClass,
                                                    delay=10,autoStart = False)

    windowRenderer = WindowRenderer.instance

    #Add scene objects
    player:PhysicalObject = PhysicalObject(Vector3D(0,0,0))
    player.name = "Player"
    cam: Camera = Camera(fov=Fov(1.5, 1.5), parent = player,filteredObjects= [player],name = "MainCamera")
    sphere:DiffuseSphere = DiffuseSphere(Vector3D(z=4), 1.5, tilt=PhysicalTilt())
    #cam.filteredObjects.append(sphere)
    #sphere2: DiffuseSphere = DiffuseSphere(Vector3D(z=5), 1.5, tilt=PhysicalTilt())
    sceneObjects: list[SceneObject] = [
        player,
        cam,
        sphere,
        #sphere2,
        PointLight(Vector3D(-5,0,0), parent = player),
        DiffuseSphere(Vector3D(-5,0,0),0.5),
        DiffuseSphere(Vector3D(), 10, tilt= PhysicalTilt()),
        DiffuseSphere(Vector3D(y=12, z=12), 3,tilt= PhysicalTilt()),
        #Quadrilateral(Face,(Vector3D(),Vector3D(10),Vector3D(y=10),Vector3D(10,10,-10)),Vector3D(z=10)),
        #Parallelogram(Face,(Vector3D(-10),Vector3D(y=10)),Vector3D(x = -5,z=10)),
        #Hexahedron(Face,sides=(Vector3D(x=10),Vector3D(y=10),Vector3D(z=10))),
        Camera(tilt = CameraTilt(-math.pi/4,-math.pi*(3/4)),position=Vector3D(2,2,0),parent = sphere),
    ]


    windowRenderer.AddSceneObject(*sceneObjects)
    windowRenderer.currentPlayer=player



    del sceneObjects


    windowRenderer.PrintObjects()



    windowRenderer.master.mainloop()

    time.sleep(0.5)


if __name__ == "__main__":
    Main()