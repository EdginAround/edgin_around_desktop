import math, yaml

from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import skeleton


class SamlFile:
    def __init__(
            self,
            id: str,
            name: str,
            size_x: int,
            size_y: int,
            pivot_x: float,
            pivot_y: float,
        ) -> None:
        self.id = id
        self.name = name
        self.size_x = size_x
        self.size_y = size_y
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y


class SamlPose:
    def __init__(
            self,
            key: str,
            position_x: Optional[float],
            position_y: Optional[float],
            scale_x: Optional[float],
            scale_y: Optional[float],
            angle: Optional[float],
            alpha: Optional[float],
            file_id: str,
        ) -> None:
        self.key = key
        self.position_x = position_x
        self.position_y = position_y
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.angle = angle
        self.alpha = alpha
        self.file_id = file_id

    def update(self, other: 'SamlPose') -> 'SamlPose':
        return SamlPose(
            key=other.key,
            file_id=other.file_id if other.file_id is not None else self.file_id,
            position_x=other.position_x if other.position_x is not None else self.position_x,
            position_y=other.position_y if other.position_y is not None else self.position_y,
            scale_x=other.scale_x if other.scale_x is not None else self.scale_x,
            scale_y=other.scale_y if other.scale_y is not None else self.scale_y,
            angle=other.angle if other.angle is not None else self.angle,
            alpha=other.alpha if other.alpha is not None else self.alpha,
        )


class SamlBone:
    def __init__(
            self,
            id: str,
            name: str,
            parent: Optional[str],
            base_pose: SamlPose,
            timeline: List[SamlPose],
        ) -> None:
        self.id = id
        self.name = name
        self.parent = parent
        self.base_pose = base_pose
        self.timeline = timeline


class SamlAnimation:
    def __init__(
            self,
            name: str,
            is_looped: bool,
            length: float,
            keys: Dict[str, float],
            bones = List[SamlBone],
            objects = List[SamlBone],
        ) -> None:
        self._name = name
        self._is_looped = is_looped
        self._length = length
        self._keys = keys
        self._bones = bones
        self._objects = objects


class SamlParser:
    def __init__(self) -> None:
        self._interaction = skeleton.Interaction(skeleton.Area(0, 0, 0, 0))
        self._sources: List[SamlFile] = list()
        self._animations: List[SamlAnimation] = list()

    def parse(self, filepath: str):
        data = yaml.load(open(filepath), Loader=yaml.FullLoader)

        self._interaction = self._parse_interaction(data['interaction'])
        self._sources = [self._parse_file(file) for file in data['sources']]
        self._animations = [self._parse_animation(animation) for animation in data['animations']]

    def _parse_interaction(self, data: Dict[str, Any]) -> skeleton.Interaction:
        area = data['hover_area']
        hover_area=skeleton.Area(
            left=area['left'],
            right=area['right'],
            top=area['top'],
            bottom=area['bottom'],
        )
        return skeleton.Interaction(hover_area)

    def _parse_animation(self, data: Dict[str, Any]) -> SamlAnimation:
        name = data['name']
        is_looped = data.get('is_looped', True)
        length = data['length']
        keys = data['keys']
        bones = [self._parse_bone(bone_data) for bone_data in data['bones']]
        return SamlAnimation(name, is_looped, length, keys, bones)

    def _parse_bone(self, data: Dict[str, Any]) -> SamlBone:
        id = data['id']
        name = data.get('name', '')
        parent = data.get('parent', None)
        pose = self._parse_pose_defaults(data['pose'])
        timeline = [self._parse_pose_empty(pose_data) for pose_data in data.get('timeline', list())]
        return SamlBone(id, name, parent, pose, timeline)

    def _parse_file(self, data: Dict[str, Any]) -> SamlFile:
        return SamlFile(
            id=data['id'],
            name=data['name'],
            size_x=data['size_x'],
            size_y=data['size_y'],
            pivot_x=data['pivot_x'],
            pivot_y=data['pivot_y'],
        )

    def _parse_pose_defaults(self, data: Dict[str, Any]) -> SamlPose:
        return SamlPose(
            key=data.get('key', None),
            position_x=data.get('position_x', 0.0),
            position_y=data.get('position_y', 0.0),
            scale_x=data.get('scale_x', 1.0),
            scale_y=data.get('scale_y', 1.0),
            angle=data.get('angle', 0.0),
            alpha=data.get('alpha', 1.0),
            file_id=data.get('file_id', None),
        )

    def _parse_pose_empty(self, data: Dict[str, Any]) -> SamlPose:
        return SamlPose(
            key=data.get('key', None),
            position_x=data.get('position_x', None),
            position_y=data.get('position_y', None),
            scale_x=data.get('scale_x', None),
            scale_y=data.get('scale_y', None),
            angle=data.get('angle', None),
            alpha=data.get('alpha', None),
            file_id=data.get('file_id', None),
        )

    def to_skeleton(self) -> skeleton.Skeleton:
        interaction = self._prepare_interaction()

        images = list()
        for file in self._sources:
            images.append(self._prepare_image(file))

        animations: List[skeleton.Animation] = list()
        for animation in self._animations:
            bones = [self._prepare_bone(bone, animation._keys) for bone in animation._bones]
            animations.append(skeleton.Animation(
                animation._name,
                animation._is_looped,
                animation._length,
                bones,
            ))

        return skeleton.Skeleton(interaction, images, animations)

    def _prepare_interaction(self) -> skeleton.Interaction:
        return self._interaction

    def _prepare_image(self, file: SamlFile) -> skeleton.Image:
        return skeleton.Image(
            id=file.id,
            name=file.name,
            size=(file.size_x, file.size_y),
            pivot=(file.pivot_x, file.pivot_y),
        )

    def _prepare_bone(self, bone: SamlBone, keys: Dict[str, float]) -> skeleton.Bone:
        base_pose = bone.base_pose
        poses = list()

        for timeline_pose in bone.timeline:
            poses.append(self._prepare_pose(base_pose.update(timeline_pose), keys))

        if len(poses) == 0:
            poses.append(self._prepare_pose(base_pose, keys))

        return skeleton.Bone(bone.id, bone.parent, poses)

    def _prepare_pose(self, pose: SamlPose, keys: Dict[str, float]) -> skeleton.Pose:
        assert pose.position_x is not None
        assert pose.position_y is not None
        assert pose.scale_x is not None
        assert pose.scale_y is not None
        assert pose.angle is not None
        assert pose.alpha is not None

        return skeleton.Pose(
            moment=keys[pose.key] if pose.key is not None else 0.0,
            file_id=pose.file_id,
            position=(pose.position_x, pose.position_y),
            scale=(pose.scale_x, pose.scale_y),
            angle=(2 * math.pi * pose.angle),
            alpha=pose.alpha,
        )

    def _find_file(self, file_id: str) -> Optional[SamlFile]:
        for file in self._sources:
            if file.id == file_id:
                return file
        return None

    def get_images(self) -> List[str]:
        return [file.name for file in self._sources]

