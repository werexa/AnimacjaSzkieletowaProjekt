import bpy
import pyrr
from model_animation import Model
from typing import Dict
from animdata import BoneInfo

class AssimpNodeData:
    def __init__(self):
        self.transformation = pyrr.Matrix44.identity()
        self.name = ""
        self.childrenCount = 0
        self.children = []

class Animation:
    def __init__(self, animationPath, model: Model):
        self.m_Duration = 0.0
        self.m_TicksPerSecond = 0.0
        self.m_Bones = []
        self.m_RootNode = AssimpNodeData()
        self.m_BoneInfoMap = {}
        
        bpy.ops.wm.open_mainfile(filepath=str(animationPath))
        bpy_scene = bpy.context.scene
        animation = bpy_scene.animation_data.action
        self.m_Duration = animation.frame_range[1] - animation.frame_range[0] + 1
        self.m_TicksPerSecond = bpy_scene.render.fps
        globalTransformation = pyrr.Matrix44.from_matrix3(bpy_scene.world, dtype='f4')
        globalTransformation = globalTransformation.inverse
        self.ReadHierarchyData(self.m_RootNode, bpy_scene.objects[0])
        self.ReadMissingBones(animation, model)
    
    def FindBone(self, name: str):
        bone = next((bone for bone in self.m_Bones if bone.GetBoneName() == name), None)
        return bone
    
    def GetTicksPerSecond(self):
        return self.m_TicksPerSecond
    
    def GetDuration(self):
        return self.m_Duration
    
    def GetRootNode(self):
        return self.m_RootNode
    
    def GetBoneIDMap(self) -> Dict[str, BoneInfo]:
        return self.m_BoneInfoMap

    def ReadMissingBones(self, animation, model):
        size = len(animation.fcurves)
        boneInfoMap = model.GetBoneInfoMap()
        boneCount = model.GetBoneCount()

        for i in range(size):
            channel = animation.fcurves[i]
            boneName = channel.data_path.split('"')[1]

            if boneName not in boneInfoMap:
                boneInfoMap[boneName].id = boneCount
                boneCount += 1
            self.m_Bones.append(Bone(boneName,
                boneInfoMap[boneName].id, channel))

        self.m_BoneInfoMap = boneInfoMap

    def ReadHierarchyData(self, dest: AssimpNodeData, src: bpy.types.Object):
        assert src

        dest.name = src.name
        dest.transformation = pyrr.Matrix44.from_matrix3(src.matrix_world, dtype='f4')
        dest.childrenCount = len(src.children)

        for child in src.children:
            newData = AssimpNodeData()
            self.ReadHierarchyData(newData, child)
            dest.children.append(newData)
