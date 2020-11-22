import cv2
import mediapipe as mp
import ipdb
import numpy as np

from model.sign_detector import SignDetector
from dataframe_landmark import DataframeLandmark

def dumps_data(dd):
    pass
    # import json
    # with open("data.json", "w+") as output:
    #
    #     output.writelines(json.dumps(dd))
    # output.close()


def display_from_stream(stream, mp_pose, mp_hands):
    stream.open()
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        min_detection_confidence=0.5, min_tracking_confidence=0.4)
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.2)
    for img in stream.get_images():
        try:
            results_hands = hands.process(img)
            results_pose = pose.process(img)
            img.flags.writeable = True
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            if results_pose.pose_landmarks:
                mp_drawing.draw_landmarks(
                    img, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            cv2.imshow('MediaPipe Hands', img)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
        except Exception as err:
            print(err)
            break
    stream.close()
    hands.close()
    pose.close()


def display_evaluate_from_stream(stream, mp_pose, mp_hands):
    model = SignDetector()
    dfl = DataframeLandmark()
    stream.open()
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        min_detection_confidence=0.5, min_tracking_confidence=0.4)
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.2)
    for img in stream.get_images():
        try:
            results_hands = hands.process(img)
            results_pose = pose.process(img)
            img.flags.writeable = True
            if results_hands.multi_hand_landmarks and results_pose.pose_landmarks:
                dfl.append_landmarks(results_hands, results_pose)
                display_image_landmark(img, results_hands.multi_hand_landmarks, results_pose.pose_landmarks)
        except Exception as err:
            print(err)
            break
    dataframe = dfl.get_random_dataframe_with_target_value()
    predicted_word_idx = model.evaluate(np.array(dataframe))
    print('#'*100)
    print('#'*25, "Prediction du mot:", predicted_word_idx, '#'*25)
    print('#'*100)
    stream.close()
    hands.close()
    pose.close()


def display_image_landmark(image, hand_multi_landmarks, pose_landmarks):
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    mp_pose = mp.solutions.pose
    image.flags.writeable = True
    for hand_landmark in hand_multi_landmarks:
        mp_drawing.draw_landmarks(
            image, hand_landmark, mp_hands.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(
        image, pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        pass
