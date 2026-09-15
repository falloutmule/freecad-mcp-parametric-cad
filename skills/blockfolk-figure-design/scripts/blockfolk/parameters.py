"""Independent character, mechanism and manufacturing parameter groups (mm)."""
from dataclasses import dataclass, asdict, replace
import json
import math


def positive(value):
    if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError("Expected a finite positive dimension")
    return value


@dataclass(frozen=True)
class Process:
    clearance: float = 0.45
    release_gap: float = 0.35
    nozzle: float = 0.4
    layer: float = 0.2

    def __post_init__(self):
        for value in asdict(self).values():
            positive(value)


@dataclass(frozen=True)
class Proportions:
    height: float = 100.0
    head_width_ratio: float = 0.34
    head_height_ratio: float = 0.34
    head_depth_ratio: float = 0.25
    torso_width_ratio: float = 0.26
    torso_depth_ratio: float = 0.14
    upper_arm_ratio: float = 0.145
    thigh_ratio: float = 0.16
    shin_ratio: float = 0.175

    def __post_init__(self):
        for key, value in asdict(self).items():
            positive(value)
            if key.endswith("ratio") and value >= 1:
                raise ValueError("A component ratio must be below one")

    def dimensions(self):
        return {key.removesuffix("_ratio"): value * self.height
                for key, value in asdict(self).items() if key.endswith("_ratio")}


@dataclass(frozen=True)
class Hinge:
    journal_radius: float = 2.55
    cap_radius: float = 4.6
    cap_thickness: float = 1.3
    cap_inner_half_span: float = 3.2
    shell_radius: float = 5.8
    chamber_radius: float = 3.7
    chamber_width: float = 3.9
    cam_radius: float = 2.35
    cam_width: float = 3.2
    leaf_inner_radius: float = 2.5
    leaf_thickness: float = 0.8
    tooth_radius: float = 2.0
    leaf_width: float = 2.2

    def __post_init__(self):
        for value in asdict(self).values():
            positive(value)

    def derived(self, process, holding=True):
        bore = self.journal_radius + process.clearance
        width = 2 * (self.cap_inner_half_span - process.clearance)
        land = (width - self.chamber_width) / 2 if holding else min(0.8, width / 3)
        if land <= 0 or self.cap_radius <= bore or self.shell_radius <= bore * math.sqrt(2):
            raise ValueError("Insufficient bearing, cap or roof space")
        if holding:
            if not (self.leaf_width < self.cam_width < self.chamber_width < width):
                raise ValueError("Require leaf < cam < chamber < bearing width")
            if not self.tooth_radius < self.cam_radius < self.leaf_inner_radius:
                raise ValueError("Follower must engage cam within leaf's inner radius")
            travel = self.chamber_radius - self.leaf_inner_radius - self.leaf_thickness
            if self.cam_radius - self.tooth_radius >= travel:
                raise ValueError("Insufficient radial follower travel")
        return dict(bore=bore, bearing_width=width, guide_land=land,
                    axis_height=self.cap_radius)


@dataclass(frozen=True)
class Design:
    proportions: Proportions = Proportions()
    mechanism: Hinge = Hinge()
    process: Process = Process()

    def resize_character(self, height):
        return replace(self, proportions=replace(self.proportions, height=height))

    def dumps(self):
        return json.dumps(dict(schema_version=1, **asdict(self)), indent=2, allow_nan=False)

    @classmethod
    def loads(cls, text):
        data = json.loads(text)
        if set(data) != {"schema_version", "proportions", "mechanism", "process"} or data.pop("schema_version") != 1:
            raise ValueError("Unsupported parameter schema")
        return cls(Proportions(**data["proportions"]), Hinge(**data["mechanism"]), Process(**data["process"]))


def envelope_fits(available, radius_a, radius_b, connecting_web):
    for value in (available, radius_a, radius_b, connecting_web):
        positive(value)
    return available >= radius_a + radius_b + connecting_web
