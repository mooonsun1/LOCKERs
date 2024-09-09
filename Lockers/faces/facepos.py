import cv2
import mediapipe as mp
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms
from django.conf import settings
from faces.models import Faces  # Faces 모델 임포트
from django.contrib.auth import get_user_model
import django

# Django 설정 초기화
django.setup()

User = get_user_model()

# 얼굴 메쉬 및 얼굴 인식 모델 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)

transform = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = InceptionResnetV1(pretrained=None, classify=False).to(device)
state_dict = torch.load(r"C:\Users\USER\OneDrive\classes\LOCKERs\saved_models\fintune_best_model_2080_2.pth", map_location=device)
model.load_state_dict(state_dict, strict=False)
model.eval()

# 각도별 원하는 각도 정의
desired_angles = {
    'yaw': [-60, -40, -20, 0, 20, 40, 60],
    'pitch': [-20, -30, 20, 30],
    'roll': [-60, -40, -20, 20, 40, 60]
}

total_images = sum(len(angles) for angles in desired_angles.values())
captured_angles = {'yaw': [], 'pitch': [], 'roll': []}
captured_embeddings = []

# 임베딩 값을 추출하는 함수
def get_embedding_from_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    image_tensor = transform(image_pil).unsqueeze(0).to(device)
    
    with torch.no_grad():
        embedding = model(image_tensor)
    
    return embedding.cpu().numpy().flatten()

# 각도를 처리하는 함수
def process_angle(yaw, pitch, roll, angle_type, angle, captured_angles, captured_embeddings):
    if angle in captured_angles[angle_type]:
        return False

    if check_angle_range(eval(angle_type), angle):
        embedding = get_embedding_from_image(image_rgb)
        captured_angles[angle_type].append(angle)
        captured_embeddings.append(embedding)
        return True
    return False

# 화살표 그리기
def draw_arrow(image, start_point, end_point, color, thickness=2):
    cv2.arrowedLine(image, start_point, end_point, color, thickness)

# 텍스트 쓰기
def put_text(image, text, position, font_scale=0.5, color=(0, 255, 0), thickness=2):
    cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)

# 평균 임베딩 계산
def calculate_average_embedding(captured_embeddings):
    return np.mean(captured_embeddings, axis=0)

# 각도 추적
def check_angle_range(angle, target_angle, tolerance=20):
    return abs(angle - target_angle) <= tolerance

def get_remaining_angles(captured_angles):
    remaining_angles = {'yaw': [], 'pitch': [], 'roll': []}
    for angle_type in remaining_angles:
        for angle in desired_angles[angle_type]:
            if angle not in captured_angles[angle_type]:
                remaining_angles[angle_type].append(angle)
    return remaining_angles

# 얼굴 임베딩 저장 함수
def save_face_embedding(user, embedding):
    # Django ORM을 이용하여 Faces 테이블에 임베딩 저장
    face_record = Faces(user=user, face_data=embedding.tobytes())  # 바이트로 저장
    face_record.save()
    print("Average embedding saved to database for user:", user.username)

# 웹캠 활성화
cap = cv2.VideoCapture(0)

# 얼굴 자세 추적
while cap.isOpened():
    success, image = cap.read()
    if not success:
        break
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = face_mesh.process(image_rgb)
    image_rgb.flags.writeable = True

    image_with_features = image_rgb.copy()  # 스트림 이미지 (화살표 표시)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            nose_tip = face_landmarks.landmark[1]
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]
            chin_tip = face_landmarks.landmark[199]

            image_height, image_width, _ = image_rgb.shape
            nose_tip_point = (int(image_width * nose_tip.x), int(image_height * nose_tip.y))

            normal_vector = np.array([nose_tip.x - chin_tip.x, nose_tip.y - chin_tip.y, nose_tip.z - chin_tip.z])
            normal_vector_normalized = normal_vector / np.linalg.norm(normal_vector)

            arrow_length = 100
            end_point = (int(nose_tip_point[0] + normal_vector_normalized[0] * arrow_length),
                         int(nose_tip_point[1] + normal_vector_normalized[1] * arrow_length))
            
            draw_arrow(image_with_features, nose_tip_point, end_point, (255, 0, 0))  # 화살표는 스트림에만

            yaw = np.degrees(np.arctan2(normal_vector[0], normal_vector[2]))
            pitch = np.degrees(np.arctan2(-normal_vector[1], normal_vector[2]))
            roll = np.degrees(np.arctan2(left_eye.y - right_eye.y, left_eye.x - right_eye.x))

            if yaw < 0:
                yaw += 180
            else:
                yaw -= 180

            if pitch < 0:
                pitch = -90 - pitch
            else:
                pitch = 90 - pitch

            if roll < 0:
                roll += 180
            else:
                roll -= 180

            put_text(image_with_features, f"Yaw: {int(yaw)}", (50, 50), color=(255, 0, 0))
            put_text(image_with_features, f"Pitch: {int(pitch)}", (50, 80), color=(0, 255, 0))
            put_text(image_with_features, f"Roll: {int(roll)}", (50, 110), color=(0, 0, 255))

            for angle_type in ['yaw', 'pitch', 'roll']:
                for angle in desired_angles[angle_type]:
                    if process_angle(yaw, pitch, roll, angle_type, angle, captured_angles, captured_embeddings):
                        break

    total_captured = len(captured_angles['yaw']) + len(captured_angles['pitch']) + len(captured_angles['roll'])
    progress_percent = (total_captured / total_images) * 100
    put_text(image_with_features, f'Progress: {progress_percent:.2f}%', (200, 450), color=(0, 0, 0))

    if progress_percent >= 100:
        average_embedding = calculate_average_embedding(captured_embeddings)
        
        # 현재 로그인된 사용자 가져오기 (request.user)
        # 로그인된 사용자의 경우 request.user를 사용
        user = User.objects.get(username='현재_로그인된_사용자')  # 실제로 로그인된 사용자의 id로 교체 필요
        
        save_face_embedding(user, average_embedding)
        
        print("Average embedding saved to database.")
        break

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
