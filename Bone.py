import pyrr
from pyrr import Matrix44, Quaternion, Vector3
from pyrr.quaternion import slerp as quat_slerp, normalize as quat_normalize

class KeyPosition:
    def __init__(self):
        self.position = Vector3([0.0, 0.0, 0.0])
        self.timeStamp = 0.0

class KeyRotation:
    def __init__(self):
        self.orientation = Quaternion()
        self.timeStamp = 0.0

class KeyScale:
    def __init__(self):
        self.scale = Vector3([1.0, 1.0, 1.0])
        self.timeStamp = 0.0

class Bone:
    def __init__(self, name, ID, channel):
        self.m_Name = name
        self.m_ID = ID
        self.m_LocalTransform = Matrix44.identity()
        self.m_NumPositions = channel.mNumPositionKeys

        self.m_Positions = []
        for positionIndex in range(self.m_NumPositions):
            aiPosition = channel.mPositionKeys[positionIndex].mValue
            timeStamp = channel.mPositionKeys[positionIndex].mTime
            data = KeyPosition()
            data.position = Vector3([aiPosition.x, aiPosition.y, aiPosition.z])
            data.timeStamp = timeStamp
            self.m_Positions.append(data)

        self.m_NumRotations = channel.mNumRotationKeys
        self.m_Rotations = []
        for rotationIndex in range(self.m_NumRotations):
            aiOrientation = channel.mRotationKeys[rotationIndex].mValue
            timeStamp = channel.mRotationKeys[rotationIndex].mTime
            data = KeyRotation()
            data.orientation = Quaternion([aiOrientation.w, aiOrientation.x, aiOrientation.y, aiOrientation.z])
            data.timeStamp = timeStamp
            self.m_Rotations.append(data)

        self.m_NumScalings = channel.mNumScalingKeys
        self.m_Scales = []
        for keyIndex in range(self.m_NumScalings):
            scale = channel.mScalingKeys[keyIndex].mValue
            timeStamp = channel.mScalingKeys[keyIndex].mTime
            data = KeyScale()
            data.scale = Vector3([scale.x, scale.y, scale.z])
            data.timeStamp = timeStamp
            self.m_Scales.append(data)

    def Update(self, animationTime):
        translation = self.InterpolatePosition(animationTime)
        rotation = self.InterpolateRotation(animationTime)
        scale = self.InterpolateScaling(animationTime)
        self.m_LocalTransform = translation * rotation * scale

    def GetLocalTransform(self):
        return self.m_LocalTransform

    def GetBoneName(self):
        return self.m_Name

    def GetBoneID(self):
        return self.m_ID

    def GetPositionIndex(self, animationTime):
        for index in range(self.m_NumPositions - 1):
            if animationTime < self.m_Positions[index + 1].timeStamp:
                return index
        return 0

    def GetRotationIndex(self, animationTime):
        for index in range(self.m_NumRotations - 1):
            if animationTime < self.m_Rotations[index + 1].timeStamp:
                return index
        return 0

    def GetScaleIndex(self, animationTime):
        for index in range(self.m_NumScalings - 1):
            if animationTime < self.m_Scales[index + 1].timeStamp:
                return index
        return 0

    def GetScaleFactor(self, lastTimeStamp, nextTimeStamp, animationTime):
        scaleFactor = 0.0
        midWayLength = animationTime - lastTimeStamp
        framesDiff = nextTimeStamp - lastTimeStamp
        if framesDiff > 0.0:
            scaleFactor = midWayLength / framesDiff
        return scaleFactor

    def InterpolatePosition(self, animationTime):
        if self.m_NumPositions == 1:
            return Matrix44.from_translation(self.m_Positions[0].position)
        
        p0Index = self.GetPositionIndex(animationTime)
        p1Index = p0Index + 1
        scaleFactor = self.GetScaleFactor(self.m_Positions[p0Index].timeStamp,
            self.m_Positions[p1Index].timeStamp, animationTime)
        finalPosition = self.m_Positions[p0Index].position * (1.0 - scaleFactor) + self.m_Positions[p1Index].position * scaleFactor
        return Matrix44.from_translation(finalPosition)

    def InterpolateRotation(self, animationTime):
        if self.m_NumRotations == 1:
            rotation = quat_normalize(self.m_Rotations[0].orientation)
            return Matrix44.from_quaternion(rotation)
        
        p0Index = self.GetRotationIndex(animationTime)
        p1Index = p0Index + 1
        scaleFactor = self.GetScaleFactor(self.m_Rotations[p0Index].timeStamp,
            self.m_Rotations[p1Index].timeStamp, animationTime)
        finalRotation = quat_slerp(self.m_Rotations[p0Index].orientation, self.m_Rotations[p1Index].orientation, scaleFactor)
        finalRotation = quat_normalize(finalRotation)
        return Matrix44.from_quaternion(finalRotation)

    def InterpolateScaling(self, animationTime):
        if self.m_NumScalings == 1:
            return Matrix44.from_scale(self.m_Scales[0].scale)
        
        p0Index = self.GetScaleIndex(animationTime)
        p1Index = p0Index + 1
        scaleFactor = self.GetScaleFactor(self.m_Scales[p0Index].timeStamp,
            self.m_Scales[p1Index].timeStamp, animationTime)
        finalScale = self.m_Scales[p0Index].scale * (1.0 - scaleFactor) + self.m_Scales[p1Index].scale * scaleFactor
        return Matrix44.from_scale(finalScale)