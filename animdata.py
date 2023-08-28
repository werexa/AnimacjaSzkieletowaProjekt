import pyrr

class BoneInfo:
    def __init__(self, id: int, offset: pyrr.Matrix44):
        self.id = id
        self.offset = offset
