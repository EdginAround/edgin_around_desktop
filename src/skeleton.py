import math
import numpy

from typing import Dict, List, Optional, Set, Tuple

from . import geometry


class Area:
    def __init__(self, left: int, right: int, top: int, bottom: int):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom


class Interaction:
    def __init__(self, hover_area: Area):
        self.hover_area = hover_area


class Image:
    def __init__(
            self,
            id: str,
            name: str,
            size: Tuple[float, float],
            pivot: Tuple[float, float],
        ) -> None:
        self.id = id
        self.name = name
        self.size = size
        self.pivot = pivot


class Sources:
    def __init__(self, skin_name: str, images: List[Image]) -> None:
        self._skin_name = skin_name
        self._images = {image.id: image for image in images}

    def get_image(self, id: str) -> Image:
        return self._images[id]

    def get_skin_name(self) -> str:
        return self._skin_name


class Pose:
    def __init__(
            self,
            moment: float,
            source_id: str,
            position: Tuple[float, float],
            scale: Tuple[float, float],
            angle: float,
            alpha: float,
        ) -> None:
        self.moment = moment
        self.source_id = source_id
        self.position = position
        self.scale = scale
        self.angle = angle
        self.alpha = alpha

    def get_transformation(self) -> numpy.array:
        return geometry.Matrices2D.scale(self.scale) \
             @ geometry.Matrices2D.translation(self.position) \
             @ geometry.Matrices2D.rotation(self.angle)


class Bone:
    def __init__(
            self,
            id: str,
            parent: Optional[str],
            poses: List[Pose],
        ) -> None:
        self.id = id
        self.parent = parent
        self.poses = poses

    def get_pose_at(self, moment: float, length: float) -> Pose:
        moment = moment % length

        if len(self.poses) == 1:
            return self.poses[0]

        if moment < self.poses[-1].moment:
            for i in range(len(self.poses) - 1):
                pose1 = self.poses[i + 0]
                pose2 = self.poses[i + 1]
                if pose1.moment <= moment and moment <= pose2.moment:
                    moment1 = pose1.moment
                    moment2 = pose2.moment
                    break

        else:
            pose1 = self.poses[-1]
            pose2 = self.poses[0]
            moment1 = pose1.moment
            moment2 = length

        d = 1.0 / (moment2 - moment1)
        w1 = d * (moment2 - moment)
        w2 = d * (moment - moment1)

        return Pose(
            moment=moment,
            source_id=pose1.source_id,
            position=(
                w1 * pose1.position[0] + w2 * pose2.position[0],
                w1 * pose1.position[1] + w2 * pose2.position[1],
            ),
            scale=(
                w1 * pose1.scale[0] + w2 * pose2.scale[0],
                w1 * pose1.scale[1] + w2 * pose2.scale[1],
            ),
            angle=w1 * pose1.angle + w2 * pose2.angle,
            alpha=w1 * pose1.alpha + w2 * pose2.alpha,
        )


class Animation:
    def __init__(
            self,
            name: str,
            is_looped: bool,
            length: float,
            scale: float,
            bones: List[Bone],
        ) -> None:
        self._name = name
        self._is_looped = is_looped
        self._length = length
        self._scale = scale

        ids = set(bone.id for bone in bones)
        if len(ids) != len(bones):
            raise Exception('Bone IDs are not unique')

        parents = set(bone.parent for bone in bones)
        parents.remove(None)
        if not ids.issuperset(parents):
            raise Exception('Parent node not defined', ids, parents)

        self._index = [bone.id for bone in bones]

        sorted_bones = list()
        selected_ids: Set[Optional[str]] = { None }
        while True:
            new_bones = [bone for bone in bones if bone.parent in selected_ids]
            sorted_bones.extend(new_bones)

            if len(new_bones) == 0:
                break

            selected_ids = {bone.id for bone in new_bones}

        if len(sorted_bones) != len(bones):
            raise Exception('Bones not reachable from root bones')

        self._bones = sorted_bones

    def is_looped(self) -> bool:
        return self._is_looped

    def get_name(self) -> str:
        return self._name

    def get_length(self) -> float:
        return self._length

    def get_num_layers(self) -> int:
        return len(self._bones)

    def tick(
        self,
        moment: float,
        sources: Sources,
        subanimations: Dict[str, Tuple['Animation', Sources]] = dict(),
    ) -> List[geometry.Tile]:
        # Prepare bone poses. Bones are sorted in such a way that parents are always prepared before
        # their children.
        info: Dict[str, Tuple[numpy.array, Pose]] = dict()
        for bone in self._bones:
            current_pose = bone.get_pose_at(moment, self.get_length())
            trans = current_pose.get_transformation()
            if bone.parent is not None:
                parent_trans, parent_pose = info[bone.parent]
                trans = parent_trans @ trans
            info[bone.id] = (trans, current_pose)

        # Prepare tiles.
        tiles: List[geometry.Tile] = list()
        for id in self._index:
            trans, pose = info[id]

            if id in subanimations:
                subanimation, subsources = subanimations[id]
                subtiles = subanimation.tick(moment, subsources)
                transformation = geometry.Matrices2D.scale((self._scale, self._scale)) @ trans @ \
                                 geometry.Matrices2D.scale((1.0 / self._scale, 1.0 / self._scale))
                tiles.extend([tile.transformed(transformation) for tile in subtiles])

            elif pose.source_id is not None:
                skin_name = sources.get_skin_name()
                image = sources.get_image(pose.source_id)
                scale = (self._scale, self._scale)
                tiles.append(self._make_tile(skin_name, image, trans).scaled(scale))

        return tiles

    def _make_tile(self, skin: str, image: Image, transformation: numpy.array) -> geometry.Tile:
        pivot = (-image.pivot[0], image.pivot[1] - image.size[1])
        tile = geometry.Tile((skin, image.name), pivot, image.size)
        tile.transform(transformation)
        return tile


class Skeleton:
    DEFAULT_ANIMATION = 'idle'

    def __init__(
            self,
            skin_name: str,
            interation: Interaction,
            images: List[Image],
            animations: List[Animation],
        ) -> None:
        assert len(animations) > 0

        self._interaction = interation
        self._sources = Sources(skin_name, images)
        self._animations = {animation.get_name(): animation for animation in animations}
        self._selected_animation = animations[0].get_name()
        self._subskeletons: Dict[str, Skeleton] = dict()

    def get_interaction(self) -> Interaction:
        return self._interaction

    def get_animation(self, name: str) -> Optional[Animation]:
        return self._animations.get(name, None)

    def get_selected_animation(self) -> Optional[Animation]:
        return self._animations.get(self._selected_animation, None)

    def has_selected_animation(self) -> bool:
        return self._selected_animation in self._animations

    def is_animation_looped(self) -> bool:
        animation = self.get_selected_animation()
        if animation is not None:
            return animation.is_looped()
        else:
            return True

    def get_animation_length(self) -> float:
        animation = self.get_selected_animation()
        if animation is not None:
            return animation.get_length()
        else:
            return 0.0

    def get_sources(self) -> Sources:
        return self._sources

    def get_max_num_layers(self) -> int:
        return max(animation.get_num_layers() for animation in self._animations.values())

    def select_animation(self, name: str) -> bool:
        if name in self._animations:
            self._selected_animation = name
            return True
        else:
            return False

    def select_default_animation(self) -> bool:
        return self.select_animation(self.DEFAULT_ANIMATION)

    def attach_skeleton(self, bone_id: str, skeleton: Optional['Skeleton']) -> None:
        if skeleton is not None:
            self._subskeletons[bone_id] = skeleton

        elif bone_id in self._subskeletons:
            del self._subskeletons[bone_id]

    def tick(
        self,
        moment: float,
    ) -> List[geometry.Tile]:
        assert self._selected_animation in self._animations

        animation = self._animations[self._selected_animation]
        subanimations = dict()
        for name, skeleton in self._subskeletons.items():
            subanimation = skeleton.get_selected_animation()
            if subanimation is not None:
                subanimations[name] = (subanimation, skeleton.get_sources())

        return animation.tick(moment, self.get_sources(), subanimations)

