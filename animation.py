import pyrr
import pyassimp
import Bone
import AssimpPyrrHelpers
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
    def __init__(self, animationPath: str, model: Model):
        self.m_Duration = 0.0
        self.m_TicksPerSecond = 0.0
        self.m_Bones = []
        self.m_RootNode = AssimpNodeData()
        self.m_BoneInfoMap = {}
        
        importer = pyassimp.AssimpImporter()
        scene = importer.ReadFile(animationPath, pyassimp.aiProcess_Triangulate)
        assert scene and scene.mRootNode
        animation = scene.mAnimations[0]
        self.m_Duration = animation.mDuration
        self.m_TicksPerSecond = animation.mTicksPerSecond
        globalTransformation = scene.mRootNode.mTransformation
        globalTransformation = globalTransformation.Inverse()
        self.ReadHierarchyData(self.m_RootNode, scene.mRootNode)
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
        size = animation.mNumChannels
        boneInfoMap = model.GetBoneInfoMap()
        boneCount = model.GetBoneCount()

        for i in range(size):
            channel = animation.mChannels[i]
            boneName = channel.mNodeName.data.decode('utf-8')

            if boneName not in boneInfoMap:
                boneInfoMap[boneName].id = boneCount
                boneCount += 1
            self.m_Bones.append(Bone(channel.mNodeName.data.decode('utf-8'),
                boneInfoMap[channel.mNodeName.data.decode('utf-8')].id, channel))

        self.m_BoneInfoMap = boneInfoMap

    def ReadHierarchyData(self, dest: AssimpNodeData, src: pyassimp.Node):
        assert src

        dest.name = src.mName.data.decode('utf-8')
        dest.transformation = AssimpPyrrHelpers.ConvertMatrixToPyrrFormat(src.mTransformation)
        dest.childrenCount = src.mNumChildren

        for i in range(src.mNumChildren):
            newData = AssimpNodeData()
            self.ReadHierarchyData(newData, src.mChildren[i])
            dest.children.append(newData)
