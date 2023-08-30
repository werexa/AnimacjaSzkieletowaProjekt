import bpy
import os
from pathlib import Path
import pyrr
# from bpy_extras.image_utils import load_image
from OpenGL.GL import glGenTextures, glBindTexture, glTexImage2D, glGenerateMipmap, GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE

MAX_BONE_INFLUENCE = 4

class KeyPosition:
    def __init__(self):
        self.position = pyrr.Vector3([0.0])
        self.timeStamp = 0.0

class KeyRotation:
    def __init__(self):
        self.orientation = pyrr.Quaternion()
        self.timeStamp = 0.0

class KeyScale:
    def __init__(self):
        self.scale = pyrr.Vector3([1.0])
        self.timeStamp = 0.0

class BoneInfo:
    def __init__(self):
        self.id = -1
        self.offset = pyrr.Matrix44.identity()

class Vertex:
    def __init__(self):
        self.Position = pyrr.Vector3([0.0, 0.0, 0.0])  # Replace [0.0, 0.0, 0.0] with the desired coordinates
        self.Normal = pyrr.Vector3([0.0, 0.0, 0.0])
        self.TexCoords = (0.0,0.0)
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
        # bpy.ops.import_scene.fbx(filepath=str(path))
        bpy.ops.wm.collada_import(filepath=str(path))
        bpy_scene = bpy.context.scene
        self.process_node(bpy_scene.objects[0], bpy_scene)
        bpy.ops.object.select_all(action='DESELECT')
        bpy_scene.objects[0].select_set(True)
        bpy.ops.object.delete()

    def process_node(self, obj, scene):
        if obj.type == 'MESH':
            mesh = obj.data
            self.meshes.append(self.process_mesh(mesh, scene))

        for child in obj.children:
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
        for vertex in mesh.vertices:
            for group in vertex.groups:
                boneIndex = group.group
                weight = group.weight
                boneName = scene.objects[scene.objects.active.data.bones[boneIndex].name].name
                if boneName not in self.m_BoneInfoMap:
                    newBoneInfo = BoneInfo()
                    newBoneInfo.id = self.m_BoneCounter
                    newBoneInfo.offset = pyrr.Matrix44(scene.objects.active.data.bones[boneIndex].matrix_local)
                    self.m_BoneInfoMap[boneName] = newBoneInfo
                    boneID = self.m_BoneCounter
                    self.m_BoneCounter += 1
                else:
                    boneID = self.m_BoneInfoMap[boneName].id

                self.set_vertex_bone_data(vertices[group.index], boneID, weight)

    def process_mesh(self, mesh, scene):
        vertices = []
        indices = []
        textures = []

        for vertex in mesh.vertices:
            new_vertex = Vertex()
            self.set_vertex_bone_data_to_default(new_vertex)
            new_vertex.Position = pyrr.Vector3(vertex.co)
            new_vertex.Normal = pyrr.Vector3(vertex.normal)
            new_vertex.TexCoords = (0.0,0.0)
            vertices.append(new_vertex)

        for polygon in mesh.polygons:
            indices.extend(polygon.vertices)

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

        image = bpy.data.images.load(filename)
        if image:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.size[0], image.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, image.pixels)
            glGenerateMipmap(GL_TEXTURE_2D)
        else:
            print(f"Texture failed to load at path: {filename}")

        return texture_id
