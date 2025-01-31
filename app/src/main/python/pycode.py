
from collections import deque, Counter
from scipy.spatial.distance import cosine
import math
import numpy as np

def confidence(resultBundle):
    print(resultBundle)
    return 0.1

def coordinates2angle(vector_a, vector_b):

    angle = math.atan2(np.cross(vector_a, vector_b), np.dot(vector_a, vector_b))
    degree = math.degrees(angle)
    return int(np.clip(degree, 0, 180))

def hip_knee_angle(keypoints):
    """
    :param keypoints: left shoulder, left hip, left knee, left ankel, right shoulder, right hip, right knee, right ankel
    :return: left hip angle, left knee angle, right hip angle, right knee angle, unit is (0,180) in integer
    """
    left_body = keypoints[1] - keypoints[0]
    left_thigh = keypoints[2] - keypoints[1]
    left_shin = keypoints[3] - keypoints[2]
    right_body = keypoints[5] - keypoints[4]
    right_thigh = keypoints[6] - keypoints[5]
    right_shin = keypoints[7] - keypoints[6]
    return (coordinates2angle(left_body, left_thigh),
            coordinates2angle(left_thigh, left_shin),
            coordinates2angle(right_body, right_thigh),
            coordinates2angle(right_thigh, right_shin)
            )

class lunge_worker():
    def __init__(self, frequency=24, enable_dtw=True, joint_num=4):
        self.joint_num = joint_num
        self.enable_dtw = enable_dtw
        self.frequency = frequency
        self.history = deque(maxlen=frequency)
        self.leg = deque(maxlen=frequency)
        x = np.linspace(0, np.pi*2, self.frequency)
        self.example = np.repeat(np.sin(x), joint_num).reshape((-1, joint_num))
        if enable_dtw:
            self.dtw_workers = [dtw_calculator(i,
                                               frequency=frequency,
                                               example=self.example[:,i].flatten(),
                                               )
                                for i in range(joint_num)
                                ]



    def update(self, angles):
        self.history.append(angles)
        self.working_leg()
        if self.enable_dtw:
            for i in range(self.joint_num):
                self.dtw_workers[i].update(angles[i])

    def working_leg(self):
        """
        Use the maximum angle to decide the working leg.
        left if 0 and right is 1
        :return:
        """
        self.leg.append(np.unravel_index(np.argmax(self.history, axis=None),
                                         np.array(self.history).shape)[1] // 2)

        return

    def cos_similarity(self):
        """
        This function ignores joint number variable,
        Fix the joint sequence and joint number here
        :return: (0,100) for similarity score
        """
        leg = Counter(self.leg).most_common()[0][0]
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

