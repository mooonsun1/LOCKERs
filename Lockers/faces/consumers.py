import json
import cv2
import numpy as np
import mediapipe as mp
from channels.generic.websocket import WebsocketConsumer

class ScriptConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.cap = cv2.VideoCapture(0)  # 웹캠 시작
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

        # 실시간 프레임 처리 동기 함수 실행
        self.process_frames()

    def disconnect(self, close_code):
        # 연결 종료 시 자원 해제
        self.cap.release()
        cv2.destroyAllWindows()

    def process_frames(self):
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                print("프레임 읽기 실패")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)

            # 얼굴 랜드마크가 감지되면 처리
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # 각도 계산 및 처리 로직 (여기서 처리된 각도를 전송할 수 있습니다.)
                    self.send_frame_to_client(frame)

            # 속도 조절 (30fps)
            cv2.waitKey(33)

    def send_frame_to_client(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)  # 프레임을 JPEG 형식으로 인코딩
        frame_data = buffer.tobytes()

        # 프레임을 base64로 인코딩 후 전송
        self.send(json.dumps({
            'frame': frame_data.hex()  # 프레임을 hex 형식으로 변환하여 전송
        }))

    def receive(self, text_data):
        data = json.loads(text_data)
        # 클라이언트에서 받은 메시지를 처리 (필요시)
