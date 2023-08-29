import OpenGL.GL as gl
import pyrr
import os


class Shader:
    def __init__(self, vertex_path, fragment_path):
        vertex_code = ""
        fragment_code = ""

        with open(vertex_path, 'r') as vertex_file:
            vertex_code = vertex_file.read()

        with open(fragment_path, 'r') as fragment_file:
            fragment_code = fragment_file.read()

        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, vertex_code)
        gl.glCompileShader(vertex_shader)
        self.check_compile_errors(vertex_shader, "VERTEX")

        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, fragment_code)
        gl.glCompileShader(fragment_shader)
        self.check_compile_errors(fragment_shader, "FRAGMENT")

        self.ID = gl.glCreateProgram()
        gl.glAttachShader(self.ID, vertex_shader)
        gl.glAttachShader(self.ID, fragment_shader)
        gl.glLinkProgram(self.ID)
        self.check_compile_errors(self.ID, "PROGRAM")

        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

    def use(self):
        gl.glUseProgram(self.ID)

    def set_bool(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniform1i(location, int(value))

    def set_int(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniform1i(location, value)

    def set_float(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniform1f(location, value)

    def set_vec2(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniform2fv(location, 1, value)

    def set_vec3(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniform3fv(location, 1, value)

    def set_vec4(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniform4fv(location, 1, value)

    def set_mat2(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniformMatrix2fv(location, 1, gl.GL_FALSE, value)

    def set_mat3(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniformMatrix3fv(location, 1, gl.GL_FALSE, value)

    def set_mat4(self, name, value):
        location = gl.glGetUniformLocation(self.ID, name)
        gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value)

    def check_compile_errors(self, shader, type_):
        if type_ != "PROGRAM":
            success = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
            if not success:
                info_log = gl.glGetShaderInfoLog(shader).decode()
                print(
                    f"ERROR::SHADER_COMPILATION_ERROR of type: {type_}\n{info_log}")
        else:
            success = gl.glGetProgramiv(shader, gl.GL_LINK_STATUS)
            if not success:
                info_log = gl.glGetProgramInfoLog(shader).decode()
                print(
                    f"ERROR::PROGRAM_LINKING_ERROR of type: {type_}\n{info_log}")


# # Example usage
# if __name__ == "__main__":
#     shader = Shader("vertex_shader.glsl", "fragment_shader.glsl")
#     shader.use()
#     # Set shader uniforms and rendering code goes here
