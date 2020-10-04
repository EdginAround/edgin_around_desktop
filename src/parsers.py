import math, yaml

from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import skeleton


class SamlSource:
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
            source_id: str,
        ) -> None:
        self.key = key
        self.position_x = position_x
        self.position_y = position_y
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.angle = angle
        self.alpha = alpha
        self.source_id = source_id

    def updated(self, other: 'SamlPose') -> 'SamlPose':
        return SamlPose(
            key=other.key,
            source_id=other.source_id if other.source_id is not None else self.source_id,
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
            parent: Optional[str],
            pose: SamlPose,
        ) -> None:
        self.id = id
        self.parent = parent
        self.pose = pose


class SamlMuscle:
    def __init__(
            self,
            bone_id: str,
            timeline: List[SamlPose],
        ) -> None:
        self.bone_id = bone_id
        self.timeline = timeline


class SamlSkeleton:
    def __init__(
            self,
            id: str,
            scale: float,
            bones: List[SamlBone],
        ) -> None:
        self._id = id
        self._scale = scale
        self._bones = bones


class SamlAnimation:
    def __init__(
            self,
            id: str,
            skeleton_id: str,
            is_looped: bool,
            length: float,
            keys: Dict[str, float],
            muscles = List[SamlMuscle],
        ) -> None:
        self._id = id
        self._skeleton_id = skeleton_id
        self._is_looped = is_looped
        self._length = length
        self._keys = keys
        self._muscles = muscles


class SamlParser:
    def __init__(self) -> None:
        self._interaction = skeleton.Interaction(skeleton.Area(0, 0, 0, 0))
        self._sources: List[SamlSource] = list()
        self._skeletons: Dict[str, SamlSkeleton] = dict()
        self._animations: List[SamlAnimation] = list()

    def parse(self, filepath: str):
        data = yaml.load(open(filepath), Loader=yaml.FullLoader)

        self._interaction = self._parse_interaction(data['interaction'])
        self._sources = [self._parse_source(source) for source in data['sources']]
        self._animations = [self._parse_animation(animation) for animation in data['animations']]

        self._skeletons = dict()
        for skeleton_data in data['skeletons']:
            parsed_skeleton = self._parse_skeleton(skeleton_data)
            self._skeletons[parsed_skeleton._id] = parsed_skeleton

    def _parse_interaction(self, data: Dict[str, Any]) -> skeleton.Interaction:
        area = data['hover_area']
        hover_area=skeleton.Area(
            left=area['left'],
            right=area['right'],
            top=area['top'],
            bottom=area['bottom'],
        )
        return skeleton.Interaction(hover_area)

    def _parse_skeleton(self, data: Dict[str, Any]) -> SamlSkeleton:
        id = data['id']
        scale = data['scale']
        bones = [self._parse_bone(bone_data) for bone_data in data['bones']]
        return SamlSkeleton(id, scale, bones)

    def _parse_animation(self, data: Dict[str, Any]) -> SamlAnimation:
        id = data['id']
        skeleton_id = data['skeleton_id']
        is_looped = data.get('is_looped', True)
        length = data['length']
        keys = data['keys']
        muscles = [self._parse_muscle(muscle_data) for muscle_data in data['muscles']]
        return SamlAnimation(id, skeleton_id, is_looped, length, keys, muscles)

    def _parse_bone(self, data: Dict[str, Any]) -> SamlBone:
        id = data['id']
        parent = data.get('parent', None)
        pose = self._parse_pose_defaults(data['pose'])
        return SamlBone(id, parent, pose)

    def _parse_muscle(self, data: Dict[str, Any]) -> SamlMuscle:
        bone_id = data['bone_id']
        timeline = [self._parse_pose_empty(pose_data) for pose_data in data.get('timeline', list())]
        return SamlMuscle(bone_id, timeline)

    def _parse_source(self, data: Dict[str, Any]) -> SamlSource:
        return SamlSource(
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
            source_id=data.get('source_id', None),
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
            source_id=data.get('source_id', None),
        )

    def to_skeleton(self, name: str) -> skeleton.Skeleton:
        interaction = self._prepare_interaction()

        images = list()
        for source in self._sources:
            images.append(self._prepare_image(source))

        animations: List[skeleton.Animation] = list()
        for animation in self._animations:
            bones = list()
            skelet = self._skeletons[animation._skeleton_id]
            for bone in skelet._bones:
                muscle = next((m for m in animation._muscles if m.bone_id == bone.id), None)
                bones.append(self._prepare_bone(bone, muscle, animation._keys))

            animations.append(skeleton.Animation(
                animation._id,
                animation._is_looped,
                animation._length,
                skelet._scale,
                bones,
            ))

        return skeleton.Skeleton(name, interaction, images, animations)

    def _prepare_interaction(self) -> skeleton.Interaction:
        return self._interaction

    def _prepare_image(self, source: SamlSource) -> skeleton.Image:
        return skeleton.Image(
            id=source.id,
            name=source.name,
            size=(source.size_x, source.size_y),
            pivot=(source.pivot_x, source.pivot_y),
        )

    def _prepare_bone(
            self,
            bone: SamlBone,
            muscle: Optional[SamlMuscle],
            keys: Dict[str, float],
        ) -> skeleton.Bone:
        poses = list()

        if muscle is not None:
            for timeline_pose in muscle.timeline:
                poses.append(self._prepare_pose(bone.pose.updated(timeline_pose), keys))

        if len(poses) == 0:
            poses.append(self._prepare_pose(bone.pose, keys))

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
            source_id=pose.source_id,
            position=(pose.position_x, pose.position_y),
            scale=(pose.scale_x, pose.scale_y),
            angle=(2 * math.pi * pose.angle),
            alpha=pose.alpha,
        )

    def _find_source(self, source_id: str) -> Optional[SamlSource]:
        for source in self._sources:
            if source.id == source_id:
                return source
        return None

    def get_images(self) -> List[str]:
        return [source.name for source in self._sources]

