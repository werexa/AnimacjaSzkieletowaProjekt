import glm

class Camera:
    def __init__(self, position=glm.vec3(0.0, 0.0, 0.0), up=glm.vec3(0.0, 1.0, 0.0), yaw=-90.0, pitch=0.0):
        self.position = position
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = up
        self.right = glm.vec3(0.0)
        self.world_up = up
        self.yaw = yaw
        self.pitch = pitch
        self.movement_speed = 2.5
        self.mouse_sensitivity = 0.1
        self.zoom = 45.0
        self.update_camera_vectors()

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def process_keyboard(self, direction, delta_time):
        velocity = self.movement_speed * delta_time
        if direction == "FORWARD":
            self.position += self.front * velocity
        if direction == "BACKWARD":
            self.position -= self.front * velocity
        if direction == "LEFT":
            self.position -= self.right * velocity
        if direction == "RIGHT":
            self.position += self.right * velocity

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_camera_vectors()

    def process_mouse_scroll(self, yoffset):
        self.zoom -= yoffset
        if self.zoom < 1.0:
            self.zoom = 1.0
        if self.zoom > 45.0:
            self.zoom = 45.0

    def update_camera_vectors(self):
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

# Example usage
if __name__ == "__main__":
    camera = Camera(glm.vec3(0.0, 0.0, 3.0))
    view_matrix = camera.get_view_matrix()
    print(view_matrix)
    # Process input and camera updates go here
