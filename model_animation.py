import os
from pathlib import Path
import glm
import pyassimp
from pyassimp.postprocess import (
    aiProcess_Triangulate,
    aiProcess_GenSmoothNormals,
    aiProcess_CalcTangentSpace,
)

MAX_BONE_INFLUENCE = 4

class KeyPosition:
    def __init__(self):
        self.position = glm.vec3(0.0)
        self.timeStamp = 0.0

class KeyRotation:
    def __init__(self):
        self.orientation = glm.quat()
        self.timeStamp = 0.0

class KeyScale:
    def __init__(self):
        self.scale = glm.vec3(1.0)
        self.timeStamp = 0.0

class BoneInfo:
    def __init__(self):
        self.id = -1
        self.offset = glm.mat4(1.0)

class Vertex:
    def __init__(self):
        self.Position = glm.vec3(0.0)
        self.Normal = glm.vec3(0.0)
        self.TexCoords = glm.vec2(0.0)
        self.m_BoneIDs = [-1] * MAX_BONE_INFLUENCE
        self.m_Weights = [0.0] * MAX_BONE_INFLUENCE

class Texture:
    def __init__(self):
        self.id = 0
        self.type = ""
        self.path = ""

class Mesh:
    def __init__(self, vertices, indices, textures):
        self.vertices = vertices
        self.indices = indices
        self.textures = textures

class Model:
    def __init__(self, path, gamma=False):
        self.directory = Path(path).parent
        self.meshes = []
        self.textures_loaded = []
        self.gamma_correction = gamma
        self.m_BoneInfoMap = {}
        self.m_BoneCounter = 0

        self.load_model(path)

    def load_model(self, path):
        scene = pyassimp.load(path, processing=(aiProcess_Triangulate | aiProcess_GenSmoothNormals | aiProcess_CalcTangentSpace))
        self.process_node(scene.rootnode, scene)
        pyassimp.release(scene)

    def process_node(self, node, scene):
        for mesh_index in node.meshes:
            mesh = scene.meshes[mesh_index]
            self.meshes.append(self.process_mesh(mesh, scene))

        for child in node.children:
            self.process_node(child, scene)

    def set_vertex_bone_data_to_default(self, vertex):
        for i in range(MAX_BONE_INFLUENCE):
            vertex.m_BoneIDs[i] = -1
            vertex.m_Weights[i] = 0.0

    def set_vertex_bone_data(self, vertex, boneID, weight):
        for i in range(MAX_BONE_INFLUENCE):
            if vertex.m_BoneIDs[i] < 0:
                vertex.m_Weights[i] = weight
                vertex.m_BoneIDs[i] = boneID
                break

    def extract_bone_weight_for_vertices(self, vertices, mesh, scene):
        for boneIndex in range(mesh.num_bones):
            bone = mesh.bones[boneIndex]
            boneName = bone.name
            if boneName not in self.m_BoneInfoMap:
                newBoneInfo = BoneInfo()
                newBoneInfo.id = self.m_BoneCounter
                newBoneInfo.offset = glm.mat4(*bone.offset_matrix)
                self.m_BoneInfoMap[boneName] = newBoneInfo
                boneID = self.m_BoneCounter
                self.m_BoneCounter += 1
            else:
                boneID = self.m_BoneInfoMap[boneName].id

            for weight in bone.weights:
                vertexId = weight.vertex_id
                vertex = vertices[vertexId]
                self.set_vertex_bone_data(vertex, boneID, weight.weight)

    def process_mesh(self, mesh, scene):
        vertices = []
        indices = []
        textures = []

        for i in range(mesh.num_vertices):
            vertex = Vertex()
            self.set_vertex_bone_data_to_default(vertex)
            vertex.Position = glm.vec3(*mesh.vertices[i])
            vertex.Normal = glm.vec3(*mesh.normals[i])

            if mesh.texturecoords:
                vertex.TexCoords = glm.vec2(*mesh.texturecoords[0][i][:2])
            else:
                vertex.TexCoords = glm.vec2(0.0, 0.0)

            vertices.append(vertex)

        for face in mesh.faces:
            indices.extend(face.indices)

        material = scene.materials[mesh.materialindex]
        diffuse_maps = self.load_material_textures(material, 'texture_diffuse', 'aiTextureType_DIFFUSE')
        textures.extend(diffuse_maps)
        specular_maps = self.load_material_textures(material, 'texture_specular', 'aiTextureType_SPECULAR')
        textures.extend(specular_maps)
        normal_maps = self.load_material_textures(material, 'texture_normal', 'aiTextureType_HEIGHT')
        textures.extend(normal_maps)
        height_maps = self.load_material_textures(material, 'texture_height', 'aiTextureType_AMBIENT')
        textures.extend(height_maps)

        self.extract_bone_weight_for_vertices(vertices, mesh, scene)

        return Mesh(vertices, indices, textures)

    def load_material_textures(self, mat, texture_type_name, ai_texture_type):
        textures = []

        for i in range(mat.properties[ai_texture_type]):
            tex_path = mat.properties[ai_texture_type][i]
            if tex_path:
                texture = Texture()
                texture.id = self.texture_from_file(tex_path)
                texture.type = texture_type_name
                texture.path = tex_path
                textures.append(texture)
                self.textures_loaded.append(texture)

        return textures

    def texture_from_file(self, path):
        filename = os.path.join(self.directory, path)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        image = pyassimp.load_image(filename)
        if image is not None:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.shape[1], image.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
            glGenerateMipmap(GL_TEXTURE_2D)
            pyassimp.release(image)
        else:
            print(f"Texture failed to load at path: {filename}")

        return texture_id
