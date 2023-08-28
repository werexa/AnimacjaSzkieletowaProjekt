import ctypes
import OpenGL.GL as gl
import pyrr  # Make sure to have pyrr installed

MAX_BONE_INFLUENCE = 4

class Vertex:
    def __init__(self):
        self.Position = pyrr.Vector3([0.0, 0.0, 0.0])
        self.Normal = pyrr.Vector3([0.0, 0.0, 0.0])
        self.TexCoords = pyrr.Vector2([0.0, 0.0])
        self.Tangent = pyrr.Vector3([0.0, 0.0, 0.0])
        self.Bitangent = pyrr.Vector3([0.0, 0.0, 0.0])
        self.m_BoneIDs = [0] * MAX_BONE_INFLUENCE
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
        self.VAO = 0
        self.setupMesh()

    def Draw(self, shader):
        diffuseNr = 1
        specularNr = 1
        normalNr = 1
        heightNr = 1

        for i in range(len(self.textures)):
            gl.glActiveTexture(gl.GL_TEXTURE0 + i)
            name = self.textures[i].type
            number = ""

            if name == "texture_diffuse":
                number = str(diffuseNr)
                diffuseNr += 1
            elif name == "texture_specular":
                number = str(specularNr)
                specularNr += 1
            elif name == "texture_normal":
                number = str(normalNr)
                normalNr += 1
            elif name == "texture_height":
                number = str(heightNr)
                heightNr += 1

            shader.setUniform1i((name + number), i)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.textures[i].id)

        gl.glBindVertexArray(self.VAO)
        gl.glDrawElements(gl.GL_TRIANGLES, len(self.indices), gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)
        gl.glActiveTexture(gl.GL_TEXTURE0)

    def setupMesh(self):
        self.VAO = gl.glGenVertexArrays(1)
        VBO = gl.glGenBuffers(1)
        EBO = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.VAO)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(self.vertices) * 128, self.vertices, gl.GL_STATIC_DRAW)  # Assuming each Vertex is 128 bytes
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(self.indices) * 4, self.indices, gl.GL_STATIC_DRAW)

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 128, None)
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 128, ctypes.c_void_p(12))
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 128, ctypes.c_void_p(24))
        gl.glEnableVertexAttribArray(3)
        gl.glVertexAttribPointer(3, 3, gl.GL_FLOAT, gl.GL_FALSE, 128, ctypes.c_void_p(32))
        gl.glEnableVertexAttribArray(4)
        gl.glVertexAttribPointer(4, 3, gl.GL_FLOAT, gl.GL_FALSE, 128, ctypes.c_void_p(44))
        gl.glEnableVertexAttribArray(5)
        gl.glVertexAttribIPointer(5, 4, gl.GL_INT, 128, ctypes.c_void_p(56))
        gl.glEnableVertexAttribArray(6)
        gl.glVertexAttribPointer(6, 4, gl.GL_FLOAT, gl.GL_FALSE, 128, ctypes.c_void_p(72))

        gl.glBindVertexArray(0)
