import pyrr
from typing import List, Dict
from bone import Bone  # Import Bone class if available

class Animator:
    def __init__(self, animation):
        self.m_CurrentTime = 0.0
        self.m_CurrentAnimation = animation

        self.m_FinalBoneMatrices = [pyrr.Matrix44.identity() for _ in range(100)]

    def update_animation(self, dt):
        self.m_DeltaTime = dt
        if self.m_CurrentAnimation:
            self.m_CurrentTime += self.m_CurrentAnimation.get_ticks_per_second() * dt
            self.m_CurrentTime = self.m_CurrentTime % self.m_CurrentAnimation.get_duration()
            self.calculate_bone_transform(self.m_CurrentAnimation.get_root_node(), pyrr.Matrix44.identity())

    def play_animation(self, animation):
        self.m_CurrentAnimation = animation
        self.m_CurrentTime = 0.0

    def calculate_bone_transform(self, node, parent_transform):
        node_name = node.name
        node_transform = node.transformation

        bone = self.m_CurrentAnimation.find_bone(node_name)

        if bone:
            bone.update(self.m_CurrentTime)
            node_transform = bone.get_local_transform()

        global_transformation = parent_transform @ node_transform

        bone_info_map = self.m_CurrentAnimation.get_bone_id_map()
        if node_name in bone_info_map:
            index = bone_info_map[node_name].id
            offset = bone_info_map[node_name].offset
            self.m_FinalBoneMatrices[index] = global_transformation @ offset

        for child in node.children:
            self.calculate_bone_transform(child, global_transformation)

    def get_final_bone_matrices(self):
        return self.m_FinalBoneMatrices

# Example usage
# if __name__ == "__main__":
#     # Assume you have defined the necessary Animation and AssimpNodeData classes
#     animation = Animation()  # Replace with actual Animation instance
#     animator = Animator(animation)
#     animator.update_animation(0.1)  # Update the animation with a time step of 0.1 seconds
#     final_bone_matrices = animator.get_final_bone_matrices()
#     print(final_bone_matrices)
