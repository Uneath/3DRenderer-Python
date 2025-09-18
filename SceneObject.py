from typing import Generic, TypeVar, Type

from numpy.ma.core import minimum, maximum

from Helper import *
import copy

#Scene Objects
class SceneObject:
    def __init__(self, position: Vector3D, parent: 'PhysicalObject', renderer, name:str = ""):
        self._position = position
        self.parent = parent
        self.name = name
        if renderer is not ...:
            self.renderer = renderer
            renderer.AddSceneObject(self)

    #If no parent it's just your position
    #If you have a parent, it's their absolute position summed with your relative position turned by their transform,

    def GetAbsolutePosition(self) -> Vector3D:
        if self.parent is None:
            return self._position
        return self.parent.PerfInverseRot(self._position) + self.parent.GetAbsolutePosition()

    def GetRelativePosition(self) -> Vector3D:
        return self._position

    #Don't think I'm done with this
    def SetAbsolutePosition(self, position: Vector3D) -> None:
        if self.parent is None:
            self._position = position
            return
        self._position = self.parent.PerfRot(position - self.parent.GetAbsolutePosition())
        return



    def SetRelativePosition(self, position: Vector3D) -> None:
        self._position = position

    def MoveRelativePosition(self,position: Vector3D) -> None:
        self._position += position

    def PerfRot(self, vector: Vector3D) -> Vector3D: return vector

    def PerfInverseRot(self,vector: Vector3D) -> Vector3D: return vector

    def __str__(self) -> str:
        return super().__str__()+f"\tname: '{self.name}' \trend: {self.renderer}\tpos: {self.GetRelativePosition()}"

#Physical objects
class PhysicalObject(SceneObject):
    def __init__(self, position: Vector3D = Vector3D(), tilt:PhysicalTilt = PhysicalTilt(), parent: 'PhysicalObject' = None, renderer = ..., name:str = "") -> None:
        super().__init__(position, parent, renderer,name)
        self.tilt = tilt

    def __str__(self)->str:
        return super().__str__() + f"\ttilt: {self.tilt}"

    def Rot(self,angleX: float = 0, angleY: float = 0,angleZ:float = 0) -> None:
        self.tilt.Rot(angleX,angleY,angleZ)

    def RotX(self, angle: float, minimum:float = None, maximum:float = None):
        if minimum is not None and maximum is not None:
            self.tilt.tiltX = numpy.clip(self.tilt.tiltX+angle,minimum,maximum)
            return
        self.tilt.Rot(tiltX = angle)

    def RotY(self, angle: float, minimum:float = None, maximum:float = None):
        if minimum is not None and maximum is not None:
            self.tilt.tiltY = numpy.clip(self.tilt.tiltY+angle,minimum,maximum)
            return
        self.tilt.Rot(tiltY=angle)

    def RotZ(self, angle: float, minimum:float = None, maximum:float = None):
        if minimum is not None and maximum is not None:
            self.tilt.tiltZ = numpy.clip(self.tilt.tiltZ+angle,minimum,maximum)
            return
        self.tilt.Rot(tiltZ = angle)

    def PerfRot(self,vector: Vector3D) -> Vector3D:
        if self.parent is None:
            return self.tilt.RotateVector(vector)
        #return self.tilt.RotateVector(self.parent.PerfInverseRot(vector))
        return self.tilt.RotateVector(self.parent.PerfRot(vector))

    def PerfInverseRot(self,vector: Vector3D) -> Vector3D:
        if self.parent is None:
            return self.tilt.InverseRotateVector(vector)
        return self.tilt.InverseRotateVector(self.parent.PerfInverseRot(vector))

    #Virtual functions
    def CastRayToObject(self, start:Vector3D, u:Vector3D)-> list[HitMark]: return []

    def CheckForHitLocation(self, start:Vector3D, u:Vector3D)-> list[tuple[Vector3D,float]]: return []

    def Normal(self, position: Vector3D) -> Vector3D: return Vector3D(1.0)

#Masks for physical Objects
class DiffuseRef (PhysicalObject):
    def CastRayToObject(self, start:Vector3D, u:Vector3D) -> list[HitMark]:
        hits: list[HitMark] = super().CastRayToObject(start, u)
        for hit in hits:
            for lightPoint in self.renderer.pointLights:
                CollisionPoint: Vector3D = start + u * hit.distance
                unitRay = (CollisionPoint - lightPoint.GetAbsolutePosition()).Unit()
                distance: float = abs(CollisionPoint - lightPoint.GetAbsolutePosition())

                for physicalObject in self.renderer.physicalObjects:
                    #Here I need to separate the functions for checking for ray collision and casting a colloration ray
                    #if physicalObject == self:
                    #    continue

                    hitMarks: list[tuple[Vector3D,float]]|None = physicalObject.CheckForHitLocation(CollisionPoint, -unitRay)
                    if hitMarks is None:
                        continue
                    #if len(hitMarks) == 0:
                    #    continue
                    if len(tuple(hitMark for hitMark in hitMarks if 0.01<hitMark[1]<distance)) == 0:
                        continue
                    break
                else:
                    cos: float = -(self.PerfInverseRot(hit.normal).Dot(unitRay))
                    hit.color *= max(cos, 0)
                    continue
                hit.color *= 0

        return hits

#Renderable Physical objects
class CompositeObject(PhysicalObject):
    """Meant to be used as a collection of PhysicalObjects, can NOT take a Camera object, this is asserted when the
    object is added with AddComponent or through the constructor.
    It attempts to render all objects, so they don't have to be added to the renderer, in fact they shouldn't
    as they will be rendered twice. Will automatically be made the parent of the object, this does not have to be done manually.
    """
    def __init__(self, position: Vector3D = Vector3D(), tilt:PhysicalTilt = PhysicalTilt(),
                 parent: 'PhysicalObject' = None, renderer = ..., name:str = "",
                 components: list[PhysicalObject] = ()):
        super().__init__(position,tilt,parent,renderer,name)
        self.components: list[PhysicalObject] = list(components)
        for component in self.components:
            assert isinstance(component,PhysicalObject)
            component.parent = self

    def AddComponent(self, *components: PhysicalObject) -> None:
        for component in components:
            assert isinstance(component,PhysicalObject)
            self.components.append(component)
            component.parent = self

    def CastRayToObject(self,start:Vector3D, u:Vector3D)-> list[HitMark]:
        hitMarks: list[HitMark] = []
        for component in self.components:
            hitMarks.extend(component.CastRayToObject(start,u))
        return hitMarks

class Sphere(PhysicalObject):
    def __init__(self, position:Vector3D, radius: float, tilt: PhysicalTilt = PhysicalTilt(), parent: PhysicalObject = None, renderer = ...,name:str = "") -> None:
        super().__init__(position, tilt,parent, renderer,name)
        self.radius = radius

    def __str__(self)->str:
        return super().__str__()+f"\tradius: {self.radius}"

    def CastRayToObject(self, start:Vector3D,u: Vector3D) -> list[HitMark]:
        returnedHitLocations: tuple[tuple[Vector3D,float],tuple[Vector3D,float]]|None = self.CheckForHitLocation(start,u)
        if returnedHitLocations is None:
            return []

        returnHitMarks: list[HitMark] = []

        for hitLocation in returnedHitLocations:
            vector, distance = hitLocation
            vectorCopy = copy.copy(vector)
            vector.z = 0
            if hitLocation is returnedHitLocations[0]:
                returnHitMarks.append(HitMark(Vector3D(min(abs(vector.x),1),1,1), distance,1,self.Normal(vectorCopy)))
                continue

            returnHitMarks.append(HitMark(Vector3D(0,0,1), distance,1-abs(vector.y)/self.radius,self.Normal(-vectorCopy)))
            continue

        return returnHitMarks

    def CheckForHitLocation(self, start:Vector3D,u: Vector3D)-> tuple[tuple[Vector3D,float],tuple[Vector3D,float]]|None:
        # Check if it hits by calculating k squared
        SO: Vector3D = self.GetAbsolutePosition() - start
        uSO: float = u.Dot(SO)
        a: float = self.radius ** 2 - SO ** 2 + uSO ** 2

        if a < 0:
            return None

        # Calculate hit location in comparison to center of sphere and amount of u
        k: float =(a ** 0.5)
        closeVector: Vector3D = self.PerfRot( u * uSO- SO - u*k)
        farVector: Vector3D = self.PerfRot(u * uSO - SO + u*k)

        return (closeVector, uSO-k),(farVector, uSO+k)

    def Normal(self, position: Vector3D) -> Vector3D: return position.Unit()

class Face(PhysicalObject):
    def __init__(self,position: Vector3D, vertices: tuple[Vector3D,Vector3D,Vector3D], tilt: PhysicalTilt = PhysicalTilt(), parent: PhysicalObject = None, renderer = ...,name:str = "") -> None:
        super().__init__(position,tilt,parent,renderer,name)
        self.vertices: list[Vector3D] = list(vertices)
        self.vectors: list[Vector3D] = [vertices[1]-vertices[0],vertices[2]-vertices[0]]
        self.normal: Vector3D = Face.GetNormal(self.vectors)

        self._gaussMatrix: GaussMatrix = GaussMatrix(Vector3D(0,0,0), Vector3D(0,0,0),Vector3D(0,0,0), Vector3D(0,0,0))

    def SetVertices(self,vertices: tuple[Vector3D,Vector3D,Vector3D]):
        self.vertices = list(vertices)
        self.vectors = [vertices[1]-vertices[0],vertices[2]-vertices[0]]
        self.normal = Face.GetNormal(self.vectors)

    def CastRayToObject(self, start:Vector3D, u:Vector3D) -> list[HitMark]:
        val = self.CheckForHitLocation(start, u)
        if val is None:
            return []

        result, distance = val[0]

        #Some code for color based off of x,y

        #####
        return [HitMark(Vector3D(1,1,1),distance,1,self.Normal(result))]

    def CheckForHitLocation(self, start:Vector3D, u:Vector3D) -> tuple[tuple[Vector3D,float]]|None:
        P: Vector3D = start - self.GetAbsolutePosition() - self.PerfInverseRot(self.vertices[0])
        self._gaussMatrix.LoadProblem(self.PerfInverseRot(self.vectors[0]), self.PerfInverseRot(self.vectors[1]), -u, P)
        result: Vector3D = self._gaussMatrix.SolveGaussMatrix()
        if result is None:
            return None
        x: float = result.x
        y: float = result.y
        distance: float = result.z
        if x<0 or y<0 or x+y>1:
            return None
        return ((Vector3D(x,y,0),distance),)


    def Normal(self,position:Vector3D) -> Vector3D: return self.normal

    def __str__(self)->str:
        return super().__str__() + f"vertices: {self.vertices}, vectors: {self.vectors}, normal: {self.normal}"

    @staticmethod
    def GetNormal(vectors: list[Vector3D]) -> Vector3D:
        vec:Vector3D = vectors[0].Cross(vectors[1])
        return vec.Unit()

_FaceType = TypeVar('_FaceType', bound=Face)

class STLObject(CompositeObject,Generic[_FaceType]):
    def __init__(self,position: Vector3D = Vector3D(),tilt: PhysicalTilt = PhysicalTilt(),parent:PhysicalObject = None,render = ...,name:str = "",faces: list[_FaceType] = ()):
        super().__init__(position,tilt,parent,render,name,faces)

    def AddComponent(self,faces:_FaceType):
        super().__init__(faces)

class Quadrilateral(STLObject):
    def __init__(self,faceType: Type[_FaceType], vertices: tuple[Vector3D,Vector3D,Vector3D, Vector3D],position: Vector3D = Vector3D(),tilt: PhysicalTilt = PhysicalTilt(),parent:PhysicalObject = None,render = ...,name:str = ""):
        self.faceType = faceType
        faces: tuple[_FaceType,_FaceType] = (faceType(Vector3D(),(vertices[0],vertices[1],vertices[2]),tilt,self,render,""),
                                             faceType(Vector3D(),(vertices[1],vertices[2],vertices[3]),tilt,self,render,""))
        super().__init__(position, tilt, parent, render, name, list(faces))

class Parallelogram(Quadrilateral):
    def __init__(self,faceType: Type[_FaceType], sides: tuple[Vector3D,Vector3D],position: Vector3D = Vector3D(),tilt: PhysicalTilt = PhysicalTilt(),parent:PhysicalObject = None,render = ...,name:str = ""):
        super().__init__(faceType,(Vector3D(),sides[0],sides[1],sides[0]+sides[1]),position,tilt,parent,render,name)

class Hexahedron(CompositeObject):
    def __init__(self, faceType: Type[_FaceType],sides: tuple[Vector3D,Vector3D,Vector3D],position: Vector3D = Vector3D(),origin: Vector3D = Vector3D(), tilt: PhysicalTilt = PhysicalTilt(),parent:PhysicalObject = None,renderer = ...,name:str = ""):
        self.faceType = faceType
        faces: tuple[Parallelogram,Parallelogram,Parallelogram,Parallelogram,Parallelogram,Parallelogram]=(
            Parallelogram(faceType,(sides[0],sides[1]),-origin,tilt,self,renderer,""),
            Parallelogram(faceType,(sides[0],sides[2]),-origin,tilt,self,renderer,""),
            Parallelogram(faceType,(sides[2],sides[1]),-origin,tilt,self,renderer,""),
            Parallelogram(faceType,(-sides[0],-sides[1]),sides[0]+sides[1]+sides[2]-origin,tilt,self,renderer,""),
            Parallelogram(faceType,(-sides[0],-sides[2]),sides[0]+sides[1]+sides[2]-origin,tilt,self,renderer,""),
            Parallelogram(faceType,(-sides[2],-sides[1]),sides[0]+sides[1]+sides[2]-origin,tilt,self,renderer,""),
        )

        super().__init__(position,tilt,parent,renderer,name,list(faces))

#Renderable Physical Objects combined with masks
class DiffuseSphere(DiffuseRef, Sphere):
    pass

#Camera
class Camera(SceneObject):
    def __init__(self, position:Vector3D = Vector3D(), fov: Fov = Fov(), tilt:CameraTilt = CameraTilt(),parent:PhysicalObject = None, renderer = ..., filteredObjects: list[PhysicalObject] = ...,name: str = ""):
        super().__init__(position, parent, renderer,name)
        self.filteredObjects: list[PhysicalObject]
        if filteredObjects is ...:
            self.filteredObjects = []
        else:
            self.filteredObjects = filteredObjects
        self.fov = fov
        self.tilt = tilt

    def SetAbsolutePosition(self, position: Vector3D) -> None:...
    def SetRelativePosition(self, position: Vector3D) -> None:...

    def AddFilteredObject(self, physicalObject: PhysicalObject) -> None:
        self.filteredObjects.append(physicalObject)

    def RemoveFilteredObject(self, physicalObject: PhysicalObject) -> bool:
        if physicalObject in self.filteredObjects:
            self.filteredObjects.remove(physicalObject)
            return True
        else:
            return False

    def ClearFilteredObject(self) -> None:
        self.filteredObjects = []

    #Rotate a vector to be relative to the camera, rotates with the camera
    def PerfRot(self, vector: Vector3D) -> Vector3D:
        return self.tilt.rotMat.VecMult(vector)

    #Rotate a vector to be relative to the camera, rotates against the camera
    def PerfInverseRot(self,vector: Vector3D) -> Vector3D:
        return self.tilt.inverseRotMat.VecMult(vector)

    def PerfDependentRot(self, vector: Vector3D) -> Vector3D:
        if self.parent is None:
            return self.tilt.rotMat.VecMult(vector)
        return self.tilt.rotMat.VecMult(self.parent.PerfInverseRot(vector))

    def PerfDependentInverseRot(self,vector: Vector3D) -> Vector3D:
        if self.parent is None:
            return self.tilt.inverseRotMat.VecMult(vector)
        return self.tilt.inverseRotMat.VecMult(self.parent.PerfInverseRot(vector))

    def MoveAbsolute(self, vector: Vector3D) -> None:
        super().SetRelativePosition(self.GetAbsolutePosition()+vector)

    def MoveRelative(self, vector: Vector3D) -> None:
        self.MoveAbsolute(self.PerfRot(vector))

    def SetAbsolute(self, vector: Vector3D) -> None:
        super().SetRelativePosition(vector)

    def SetRelative(self, vector: Vector3D) -> None:
        self.SetAbsolute(self.PerfRot(vector))

    def RotX(self, angle: float):
        self.tilt.RotX(angle)

    def RotY(self, angle: float):
        self.tilt.RotY(angle)

    def __str__(self)->str:
        return super().__str__()+ f"\tfov: {self.fov}\ttilt: {self.tilt}"

#Lights
class LightObject (SceneObject):
    def __init__(self,position: Vector3D = Vector3D(), parent: PhysicalObject = None,renderer = ..., name : str = ""):
        super().__init__(position,parent,renderer,name)

class PointLight (LightObject):
    def __init__(self, position: Vector3D = Vector3D(), parent: PhysicalObject = None, renderer=..., name: str = ""):
        super().__init__(position, parent, renderer, name)

class PhysicalLightObject(LightObject):
    pass

def Main():
    pass

if __name__ == "__main__":
    Main()