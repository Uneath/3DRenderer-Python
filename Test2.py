class B1:
    def __init__(self):
        print("b1")

    def val(self):
        print("val 1")
        return 1

class B2 (B1):
    def __init__(self):
        print("b2")
        super(B2,self).__init__("hej")
        print("b2 f")

    def val(self):
        print("val 2")
        return 2

class B3 (B1):
    def __init__(self,h: str):
        print(h)
        print("b3")
        super().__init__()
        print("b3 f")

    def val(self):
        print("val 3")
        return 3

class B4(B2,B3):
    def __init__(self):
        print("b4")
        super().__init__()
        print("b4 f")

    def val(self):
        return super().val()


x = 0
while x <10:
    x+=1
else:
    print("Hello")