
from collections import deque, Counter
from scipy.spatial.distance import cosine
import math
import numpy as np
import json
import os

class magic_driver():
    def __init__(self, freq):
        self.body = deque(maxlen=freq)
        self.human = False
        self.lunge_worker = lunge_worker(frequency=24, enable_dtw=False, joint_num=4)
        return

    def update(self, jsonStr):
        data = json.loads(jsonStr)
        self.body.append(False if len(data['results'][0]['landmarks']) == 0 else True)
        self.human_exist()
        if self.human:
            joints = []
            for joint in [11, 23, 25, 27, 12, 24, 26, 28]:
                joints.append(
                                [
                                data['results'][0]['landmarks'][0][joint]['x'],
                                data['results'][0]['landmarks'][0][joint]['y'],
                                data['results'][0]['landmarks'][0][joint]['z'],
                                ]
                              )
            angles = hip_knee_angle(np.array(joints))
            self.lunge_worker.update(angles)
            print(self.lunge_worker.progress)
            return self.lunge_worker.progress

        return 0

    def human_exist(self):
        if all(self.body) and not self.human:
            self.human = True
        elif not all(self.body) and self.human:
            self.human = False
        return

def coordinates2angle(A,B):
    _R = rotation_matrix(A, B)
    tx, ty, tz = Decompose_R_XYZ(_R)
    joint_rs = [tx.astype(int),
                ty.astype(int),
                tz.astype(int),
                np.linalg.norm([tx, ty, tz]).astype(int)]
    return joint_rs

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
    :param kpts: np.array shape of (8,3), left shoulder, left hip, left knee, left ankel, right shoulder, right hip, right knee, right ankel
    :return: left hip angle, left knee angle, right hip angle, right knee angle, unit is (0,180) in integer
    """
    left_body = kpts[1] - kpts[0]
    left_thigh = kpts[2] - kpts[1]
    left_shin = kpts[3] - kpts[2]
    right_body = kpts[5] - kpts[4]
    right_thigh = kpts[6] - kpts[5]
    right_shin = kpts[7] - kpts[6]
    return [coordinates2angle(left_body, left_thigh),
            coordinates2angle(left_thigh, left_shin),
            coordinates2angle(right_body, right_thigh),
            coordinates2angle(right_thigh, right_shin)
            ]

class lunge_worker():
    def __init__(self, frequency=24, enable_dtw=False, joint_num=4):
        self.joint_num = joint_num
        self.enable_dtw = enable_dtw
        self.frequency = frequency
        self.history = deque(maxlen=frequency*5)
        self.leg = deque(maxlen=frequency//2)
        x = np.linspace(0, np.pi*2, self.frequency)
        self.example = np.repeat(np.sin(x), joint_num).reshape((-1, joint_num))
        if enable_dtw:
            self.dtw_workers = [dtw_calculator(i,
                                               frequency=frequency,
                                               example=self.example[:,i].flatten(),
                                               )
                                for i in range(joint_num)
                                ]
        self.progress = 0
        self.count = 0
        self.live_progress = 0



    def update(self, angles):
        """

        :param angles: list shape of (joint num, xyz)
        :return:
        """
        self.history.append(angles)
        self.leg.append(np.unravel_index(np.argmax(self.history, axis=None),
                                                 np.array(self.history).shape)[1] // 2)
        self.update_progress(angles)
        if self.enable_dtw:
            for i in range(self.joint_num):
                self.dtw_workers[i].update(angles[i])

    def working_leg(self):
        """
        Use the maximum angle to decide the working leg.
        left if 0 and right is 1
        :return:
        """
        return Counter(self.leg).most_common()[0][0]

    def max_angle(self, angles):
        angles = np.array(angles)
        leg = np.argmax(np.array(angles)[:,-1]) // 2
        return angles[leg:leg+2]


    def _progress(self, angles):
        hip, knee = self.max_angle(angles)
        hip_progress = np.clip(hip[-1] / 95, 0, 1)
        knee_progress = np.clip(knee[-1] / 95, 0, 1)
        return round(np.mean([hip_progress, knee_progress]), 2)

    def update_progress(self, angles):
        self.live_progress = self._progress(angles)

        if self.progress == 1:
            self.count += 1
            self.progress = 0
        elif 0 < self.live_progress - self.progress <= 0.4:
            self.progress = self.live_progress




    def cos_similarity(self):
        """
        This function ignores joint number variable,
        Fix the joint sequence and joint number here
        :return: (0,100) for similarity score
        """
        leg = self.working_leg()
        idx = [leg * 2, leg * 2 + 1, 2 - leg * 2,  3 - leg * 2] # lunge leg first
        score = cosine(
                        np.array(self.history)[:, idx].T.flatten(),
                        self.example.T.flatten()
                    )
        return int(round((1-score) * 100,0))

    def dtw_similarity(self):
        return np.mean([worker.dtw_similarity() for worker in self.dtw_workers])



class dtw_calculator():
    def __init__(self, name, frequency=20, example=None):
        """
        Cache DTW cost matrix and update with new frame
        :param name:
        """
        self.name = name
        self.frequency = frequency
        self.example=example
        self.dtw_cost_matrix = deque(maxlen=self.frequency)
        for i in range(self.frequency):
            self.dtw_cost_matrix.append([255] * self.frequency)
        self.min_idx = deque(maxlen=self.frequency * self.frequency)
        return

    def update(self, angle):
        distance = np.abs(self.example - angle)

        self.dtw_cost_matrix.appendleft(distance)
        # find min among neighbours
        min_idx = [1,0]
        min_val = self.dtw_cost_matrix[min_idx[0]][min_idx[1]]
        self.min_idx.appendleft(min_idx)
        self.dtw_cost_matrix[0][0] += min_val


        for i in range(1, self.frequency):
            lst = [[1,-1], [0,-1], [1,0]]
            neighbours = [self.dtw_cost_matrix[row][i+col] for row, col in lst]
            min_idx = lst[neighbours.index(min(neighbours))]
            min_val = self.dtw_cost_matrix[min_idx[0]][min_idx[1]]
            self.min_idx.appendleft(min_idx)
            self.dtw_cost_matrix[0][i] += min_val


    def dtw_similarity(self):
        i, j = 0, self.frequency-1
        distance = 0
        path_num = 0
        while i < self.frequency and j >= 0:
            distance += self.dtw_cost_matrix[i][j]
            path_num += 1
            new_i, new_j = self.min_idx[i * self.frequency + j]
            i, j = i + new_i, j + new_j
        return distance/path_num

