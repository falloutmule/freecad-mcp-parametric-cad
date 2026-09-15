"""Joint graph kinematics and semantic cues; not a FreeCAD occurrence resolver."""
from dataclasses import dataclass
import math

IDENTITY = tuple(tuple(float(i == j) for j in range(4)) for i in range(4))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)) for i in range(4))


def point(matrix, xyz):
    return tuple(sum(matrix[i][j] * xyz[j] for j in range(3)) + matrix[i][3] for i in range(3))


def turn(center, axis, degrees):
    if len(center) != 3 or len(axis) != 3 or not all(math.isfinite(v) for v in (*center, *axis, degrees)):
        raise ValueError("Finite 3D axis and center required")
    length = math.sqrt(sum(v*v for v in axis))
    if length <= 1e-12:
        raise ValueError("Zero axis")
    u = [v / length for v in axis]
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    skew = ((0, -u[2], u[1]), (u[2], 0, -u[0]), (-u[1], u[0], 0))
    r = [[c * (i == j) + (1-c) * u[i]*u[j] + s*skew[i][j] for j in range(3)] for i in range(3)]
    return tuple(tuple(r[i]) + (center[i] - sum(r[i][j]*center[j] for j in range(3)),) for i in range(3)) + ((0., 0., 0., 1.),)


@dataclass(frozen=True)
class Joint:
    name: str
    parent: str
    child: str
    center: tuple
    axis: tuple
    limits: tuple


def transforms(joints, angles, root="Torso"):
    names = [j.name for j in joints]
    children = [j.child for j in joints]
    if len(set(names)) != len(names) or len(set(children)) != len(children) or root in children or set(angles)-set(names):
        raise ValueError("Duplicate/unknown joint, repeated child or reused root")
    result, remaining = {root: IDENTITY}, list(joints)
    while remaining:
        ready = [j for j in remaining if j.parent in result]
        if not ready:
            raise ValueError("Disconnected or cyclic joint graph")
        for j in ready:
            angle = angles.get(j.name, 0)
            if not j.limits[0] <= angle <= j.limits[1]:
                raise ValueError("Angle outside declared useful range")
            result[j.child] = multiply(result[j.parent], turn(j.center, j.axis, angle))
            remaining.remove(j)
    return result


def semantic_checks(name, landmarks, height):
    if not math.isfinite(height) or height <= 0:
        raise ValueError("Positive height required")
    checks = {}
    if name == "sitting":
        for side in ("L", "R"):
            hip, knee, ankle = (landmarks[k+side] for k in ("hip", "knee", "ankle"))
            checks[side+"_thigh_forward"] = knee[1]-hip[1] > .07*height
            checks[side+"_thigh_level"] = abs(knee[2]-hip[2]) < .06*height
            checks[side+"_shin_down"] = knee[2]-ankle[2] > .07*height
    elif name == "raised_arm":
        checks["hand_above_shoulder"] = landmarks["handR"][2]-landmarks["shoulderR"][2] > .03*height
    elif name == "standing":
        checks["feet_level"] = abs(landmarks["ankleL"][2]-landmarks["ankleR"][2]) < .02*height
        for side in ("L", "R"):
            checks[side+"_leg_descends"] = landmarks["hip"+side][2] > landmarks["knee"+side][2] > landmarks["ankle"+side][2]
        checks["head_above_hips"] = landmarks["headTop"][2] > landmarks["hipR"][2]+.3*height
    else:
        raise ValueError("Unknown semantic pose")
    return dict(landmark_checks_pass=all(checks.values()), checks=checks,
                visual_review_required=True, collision_status="UNVERIFIED")
