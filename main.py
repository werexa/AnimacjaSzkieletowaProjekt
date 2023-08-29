import glfw
import pyrr
import Shader
import Animator
import Animation
import model_animation as ma
import numpy as np
import pathlib
import OpenGL as gl
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

SCR_WIDTH = 800
SCR_HEIGHT = 600

camera_pos = np.array([0.0, 0.0, 3.0])
lastX = SCR_WIDTH / 2.0
lastY = SCR_HEIGHT / 2.0
firstMouse = True

deltaTime = 0.0
lastFrame = 0.0

def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

def mouse_callback(window, xpos, ypos):
    global firstMouse, lastX, lastY, camera
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    camera.process_mouse_movement(xoffset, yoffset)

def scroll_callback(window, xoffset, yoffset):
    camera.process_mouse_scroll(yoffset)

def process_input(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard("FORWARD", deltaTime)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard("BACKWARD", deltaTime)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard("LEFT", deltaTime)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard("RIGHT", deltaTime)

class Camera:
    def __init__(self, pos):
        self.camera_pos = pos
        self.camera_front = np.array([0.0, 0.0, -1.0])
        self.camera_up = np.array([0.0, 1.0, 0.0])
        self.yaw = -90.0
        self.pitch = 0.0
        self.fov = 45.0

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

    def process_keyboard(self, direction, delta_time):
        camera_speed = 2.5 * delta_time
        if direction == "FORWARD":
            self.camera_pos += camera_speed * self.camera_front
        if direction == "BACKWARD":
            self.camera_pos -= camera_speed * self.camera_front
        if direction == "LEFT":
            right = pyrr.vector3.cross(self.camera_front, self.camera_up)
            self.camera_pos -= pyrr.vector3.normalize(right) * camera_speed
        if direction == "RIGHT":
            right = pyrr.vector3.cross(self.camera_front, self.camera_up)
            self.camera_pos += pyrr.vector3.normalize(right) * camera_speed

    def process_mouse_movement(self, xoffset, yoffset):
        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        front = pyrr.vector3.create(
            np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch)),
            np.sin(np.radians(self.pitch)),
            np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        )
        self.camera_front = pyrr.vector3.normalize(front)

    def process_mouse_scroll(self, yoffset):
        if self.fov >= 1.0 and self.fov <= 45.0:
            self.fov -= yoffset
        if self.fov <= 1.0:
            self.fov = 1.0
        if self.fov >= 45.0:
            self.fov = 45.0

def main():
    global deltaTime, lastFrame, camera

    # Initialize the library
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(SCR_WIDTH, SCR_HEIGHT, "LearnOpenGL", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glEnable(GL_DEPTH_TEST)

    # Shader setup (you'll need to replace this with loading shaders)

    outShader = Shader("anim_model.vs", "anim_model.fs")

    ourModel = ma.Model(pathlib.Path("resources/objects/vampire/dancing_vampire.dae"))
    danceAnimation = Animation(pathlib.Path("resources/objects/vampire/dancing_vampire.dae"),ourModel)
    animator = Animator(danceAnimation)
    # shader_program = compileProgram(
    #     compileShader(vertex_shader, GL_VERTEX_SHADER),
    #     compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    # )
    # glUseProgram(shader_program)

    # camera = Camera(camera_pos)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        deltaTime = current_frame - lastFrame
        lastFrame = current_frame

        process_input(window)
        animator.update_animation(deltaTime)

        glClearColor(0.05, 0.05, 0.05, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #enable shader
        outShader.use()
        projection = pyrr.matrix44.create_perspective_projection_matrix(
            45.0,                   # FOV (field of view)
            SCR_WIDTH / SCR_HEIGHT, # Aspect ratio
            0.1,                    # Near clipping plane
            100.0                   # Far clipping plane
        )

        # projection = glm.perspective(glm.radians(camera.fov), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
        view = camera.get_view_matrix()
        outShader.set_mat4("projection", projection)
        outShader.set_mat4("view", view)
        # glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, projection)
        # glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, view)

        transforms = animator.get_final_bone_matrices()
        for i in range(len(transforms)):
            outShader.set_mat4("finalBonesMatrices[" + str(i) + "]", transforms[i])
        # glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, model)

        # Render model
        model = pyrr.Matrix44.from_translation(pyrr.Vector3([0.0, 0.0, 0.0]))  # Przykładowa macierz modelu
        model = pyrr.translate(model, (0.0, -0.4, 0.0))  # translate it down so it's at the center of the scene
        model = pyrr.scale(model, (0.5, 0.5, 0.5))
        outShader.set_mat4("model", model)
        ourModel.Draw(outShader)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
