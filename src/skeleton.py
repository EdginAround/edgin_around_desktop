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
    def __init__(self, images: List[Image]) -> None:
        self._images = {image.id: image for image in images}

    def get_image(self, id: str) -> Image:
        return self._images[id]



class Pose:
    def __init__(
            self,
            moment: float,
            file_id: str,
            position: Tuple[float, float],
            scale: Tuple[float, float],
            angle: float,
            alpha: float,
        ) -> None:
        self.moment = moment
        self.file_id = file_id
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
        w1 = d * (moment - moment1)
        w2 = d * (moment2 - moment)

        return Pose(
            moment=moment,
            file_id=pose1.file_id,
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
    def __init__(self, name: str, length: float, bones: List[Bone]) -> None:
        self.name = name
        self.length = length

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

    def get_num_layers(self) -> int:
        return len(self._bones)

    def tick(self, moment: float, sources: Sources) -> List[geometry.Tile]:
        info: Dict[str, Tuple[numpy.array, Pose]] = dict()
        for bone in self._bones:
            current_pose = bone.get_pose_at(moment, self.length)
            trans = current_pose.get_transformation()
            if bone.parent is not None:
                parent_trans, parent_pose = info[bone.parent]
                trans = parent_trans @ trans
            info[bone.id] = (trans, current_pose)

        tiles: List[geometry.Tile] = list()
        for id in self._index:
            trans, pose = info[id]
            if pose.file_id is not None:
                image = sources.get_image(pose.file_id)
                tiles.append(self._make_tile(image, trans))

        return tiles

    def _make_tile(self, image: Image, transformation: numpy.array) -> geometry.Tile:
        tile = geometry.Tile(image.name, (-image.pivot[0], -image.pivot[1]), image.size)
        tile.transform(transformation)
        return tile


class Skeleton:
    def __init__(
            self,
            interation: Interaction,
            images: List[Image],
            animations: List[Animation],
        ) -> None:
        self._interaction = interation
        self._sources = Sources(images)
        self._animations = {animation.name: animation for animation in animations}

    def get_interaction(self) -> Interaction:
        return self._interaction

    def get_animation(self, name: str) -> Optional[Animation]:
        return self._animations.get(name, None)

    def get_sources(self) -> Sources:
        return self._sources

    def get_max_num_layers(self) -> int:
        return max(animation.get_num_layers() for animation in self._animations.values())

