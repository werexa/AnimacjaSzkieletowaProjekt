import pyrr
from pyrr import Matrix44, Vector3

class Camera:
    def __init__(self, position=Vector3([0.0, 0.0, 0.0]), up=Vector3([0.0, 1.0, 0.0]), yaw=-90.0, pitch=0.0):
        self.position = position
        self.front = Vector3([0.0, 0.0, -1.0])
        self.up = up
        self.right = Vector3([0.0])
        self.world_up = up
        self.yaw = yaw
        self.pitch = pitch
        self.movement_speed = 2.5
        self.mouse_sensitivity = 0.1
        self.zoom = 45.0
        self.update_camera_vectors()

    def get_view_matrix(self):
        return Matrix44.look_at(self.position, self.position + self.front, self.up)

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
        front = Vector3()
        front.x = pyrr.cos(pyrr.radians(self.yaw)) * pyrr.cos(pyrr.radians(self.pitch))
        front.y = pyrr.sin(pyrr.radians(self.pitch))
        front.z = pyrr.sin(pyrr.radians(self.yaw)) * pyrr.cos(pyrr.radians(self.pitch))
        self.front = pyrr.normalize(front)
        self.right = pyrr.normalize(pyrr.cross(self.front, self.world_up))
        self.up = pyrr.normalize(pyrr.cross(self.right, self.front))

# Example usage
if __name__ == "__main__":
    camera = Camera(Vector3([0.0, 0.0, 3.0]))
    view_matrix = camera.get_view_matrix()
    print(view_matrix)
    # Process input and camera updates go here
