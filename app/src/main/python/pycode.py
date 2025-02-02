
from collections import deque, Counter
from scipy.spatial.distance import cosine
import math
import numpy as np
import json
import os

class MagicDriver():
    def __init__(self, freq:int):
        self.body = deque(maxlen=freq)
        self.human = False
        self.lunge_worker = lunge_worker(frequency=24, enable_dtw=False, joint_num=4)
        return

    def update(self, jsonStr:str):
        data = json.loads(jsonStr)
        landmarks = data['results'][0].get('landmarks', [])
        self.body.append(bool(landmarks))
        self._update_human_status()
        if self.human:
            joints = np.array([
                [landmarks[0][joint]['x'], landmarks[0][joint]['y'], landmarks[0][joint]['z']]
                for joint in [11, 23, 25, 27, 12, 24, 26, 28]
            ])
            angles = hip_knee_angle(joints)
            self.lunge_worker.update(angles)

            return self.lunge_worker.live_progress
        return 0

    def _update_human_status(self):
        self.human = all(self.body) if not self.human else not all(self.body)

def coordinates2angle(A, B):
    R = rotation_matrix(A, B)
    angles = Decompose_R_XYZ(R)
    return [int(angle) for angle in angles] + [int(np.linalg.norm(angles))]


def Decompose_R_XYZ(R):
    """
    Convert a 3x3 rotation matrix to Euler angles (roll, pitch, yaw).
    Uses the XYZ rotation order.
    """
    beta = -np.arcsin(R[2, 0])  # Pitch (Y-axis)

    if np.abs(R[2, 0]) < 1:  # Normal case
        alpha = np.arctan2(R[1, 0], R[0, 0])  # Yaw (Z-axis)
        gamma = np.arctan2(R[2, 1], R[2, 2])  # Roll (X-axis)
    else:  # Gimbal lock case
        alpha = np.arctan2(-R[0, 1], R[1, 1])
        gamma = 0

    return np.degrees([gamma, beta, alpha])  # Convert to degrees

def rotation_matrix(A, B):
    # get unit vectors
    uA = A / np.linalg.norm(A)
    uB = B / np.linalg.norm(B)

    v = np.cross(uA, uB)
    s = np.linalg.norm(v)
    c = np.sum(uA * uB)

    vx = np.array([[0, -v[2], v[1]],
                   [v[2], 0, -v[0]],
                   [-v[1], v[0], 0]])

    R = np.eye(3) + vx + vx @ vx * ((1 - c) / s ** 2)

    return R


def hip_knee_angle(kpts):
    """
    Compute angles for hips and knees based on keypoints.
    :param kpts: np.array shape (8,3), ordered as follows:
        left shoulder, left hip, left knee, left ankle,
        right shoulder, right hip, right knee, right ankle
    :return: List of four joint angles (0-180 degrees, integers)
    """
    segments = [
        (kpts[1] - kpts[0], kpts[2] - kpts[1]),
        (kpts[2] - kpts[1], kpts[3] - kpts[2]),
        (kpts[5] - kpts[4], kpts[6] - kpts[5]),
        (kpts[6] - kpts[5], kpts[7] - kpts[6])
    ]

    return [coordinates2angle(*seg) for seg in segments]


class lunge_worker():
    def __init__(self, frequency=24, enable_dtw=False, joint_num=4):
        self.joint_num = joint_num
        self.enable_dtw = enable_dtw
        self.frequency = frequency
        self.history = deque(maxlen=frequency)
        self.leg = deque(maxlen=frequency//2)
        self.progress = self.count = self.live_progress = 0
        self.progress_bar = False
        self.min = np.array([360,360])

    def update(self, angles):
        """
        Updates the joint angle history and progress tracking.

        :param angles: list shape of (joint_num, xyz)
        :return: The last angle values.
        """
        angles = self.max_angle(np.array(angles))
        self.history.append(angles)
        self.update_progress()
        return angles[:, -1]

    def working_leg(self):
        """
        Use the maximum angle to decide the working leg.
        left if 0 and right is 1
        This is a stable working leg, not streaming one
        :return:
        """
        return Counter(self.leg).most_common()[0][0]

    def max_angle(self, angles):
        """
        Selects the side with the maximum joint angle.
        :param angles: NumPy array of joint angles.
        :return: Reordered angles for processing.
        """
        leg = np.argmax(angles[:, -1]) // 2  # Determine dominant leg
        return angles[[leg * 2, leg * 2 + 1, 2 - leg * 2, 3 - leg * 2]]

    def _hip_knee(self):
        """
        Computes the mean hip and knee angles over a short window.
        :return: (hip angle, knee angle)
        """
        window_size = self.frequency // 4
        hip, knee, _, _ = np.mean(np.array(self.history)[-window_size:], axis=0)
        return hip[-1], knee[-1]

    def _progress(self, hip, knee):
        """
        Computes the lunge progress based on hip and knee angles.

        :param hip: Current hip angle.
        :param knee: Current knee angle.
        :return: Normalized progress value (0 to 1).
        """
        self.min = np.minimum(self.min, [hip, knee])
        hip_progress = np.clip((hip - self.min[0]) / 55, 0, 1)
        knee_progress = np.clip((knee - self.min[1]) / 90, 0, 1)
        return round(np.mean([hip_progress, knee_progress]), 2)

    def update_progress(self):
        """
        Updates the progress state based on the hip and knee angles.
        """
        if abs(self.progress - 1) < 0.009:
            self.count += 1
            self.progress = 0
            self.min.fill(360)
            self.progress_bar = False
        hip, knee = self._hip_knee()
        self.live_progress = self._progress(hip, knee)
        if abs(self.progress - 0) < 0.01 and self.live_progress >= 0.35:
            self.progress_bar = True
        if self.progress_bar and self.live_progress > self.progress:
            self.progress = self.live_progress


if __name__ == '__main__':
    driver = MagicDriver(24)