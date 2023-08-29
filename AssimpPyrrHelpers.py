import pyrr
import pyassimp


class AssimpPyrrHelpers:
    @staticmethod
    def ConvertMatrixToPyrrFormat(from_mat):
        to_mat = pyrr.Matrix44()
        to_mat[0][0] = from_mat.a1
        to_mat[1][0] = from_mat.a2
        to_mat[2][0] = from_mat.a3
        to_mat[3][0] = from_mat.a4
        to_mat[0][1] = from_mat.b1
        to_mat[1][1] = from_mat.b2
        to_mat[2][1] = from_mat.b3
        to_mat[3][1] = from_mat.b4
        to_mat[0][2] = from_mat.c1
        to_mat[1][2] = from_mat.c2
        to_mat[2][2] = from_mat.c3
        to_mat[3][2] = from_mat.c4
        to_mat[0][3] = from_mat.d1
        to_mat[1][3] = from_mat.d2
        to_mat[2][3] = from_mat.d3
        to_mat[3][3] = from_mat.d4
        return to_mat

    @staticmethod
    def GetPyrrVec(vec):
        return pyrr.Vector3(vec.x, vec.y, vec.z)

    @staticmethod
    def GetPyrrQuat(orientation):
        return pyrr.Quaternion(orientation.w, orientation.x, orientation.y, orientation.z)
