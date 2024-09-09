from django.shortcuts import render, redirect
from django.http import JsonResponse
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import base64
import io
import numpy as np
from faces.models import Faces
from scipy.spatial.distance import cosine
import json
import dlib
from torchvision.models import resnet34, ResNet34_Weights
import torch.nn as nn
import torchvision.transforms as transforms
from django.shortcuts import render, redirect, get_object_or_404
from common.models import Reservations, Locations
import random

# 디바이스 설정 (GPU가 있으면 사용, 없으면 CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 얼굴 인식 모델 설정
mtcnn = MTCNN(
    image_size=160,
    margin=0,
    min_face_size=20,
    thresholds=[0.6, 0.7, 0.7],
    factor=0.709,
    device=device
)
model = InceptionResnetV1(pretrained='vggface2', classify=False).eval().to(device)

# Face classification 모델 설정
weights = ResNet34_Weights.DEFAULT
class_model = resnet34(weights=weights)
class_model.fc = nn.Linear(class_model.fc.in_features, 18)  # 18개의 출력 노드로 설정
class_model.load_state_dict(torch.load(r'C:\Users\USER\OneDrive\classes\LOCKERs\FairFace\res34_fair_align_multi_7_20190809.pt', map_location=device, weights_only=True))
class_model = class_model.to(device)
class_model.eval()

# 얼굴 탐지기를 위한 dlib 설정
detector = dlib.get_frontal_face_detector()

# 이미지 전처리 설정
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def get_embedding_from_image(image_data):
    try:
        # base64 문자열로부터 이미지를 디코딩
        image_pil = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1])))

        img_cropped = mtcnn(image_pil)
        if img_cropped is None:
            raise ValueError("얼굴을 감지할 수 없습니다.")

        img_cropped = img_cropped.unsqueeze(0).to(device)
        with torch.no_grad():
            embedding = model(img_cropped)

        return embedding.cpu().numpy().flatten()

    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {str(e)}")
        return None
    
def classify_face(image_array):
    try:
        if not isinstance(image_array, np.ndarray):
            raise ValueError('이미지가 numpy 배열이 아닙니다.')

        # 변환 적용
        input_tensor = transform(image_array).unsqueeze(0).to(device)
        outputs = class_model(input_tensor)

        gender_scores = torch.softmax(outputs[0][7:9], dim=0)
        age_scores = torch.softmax(outputs[0][9:18], dim=0)

        gender_pred = torch.argmax(gender_scores).item()
        age_pred = torch.argmax(age_scores).item()

        gender = 'Male' if gender_pred == 0 else 'Female'
        age = ["0-2", "3-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"][age_pred]

        # 터미널에 얼굴 분류 결과 출력
        print(f"Face Classification Result - Gender: {gender}, Age: {age}")

        return gender, age
    except Exception as e:
        print(f"얼굴 분류 중 오류 발생: {str(e)}")
        raise

def determine_keyword(gender, age):
    # 10~49 세를 "10-49"로 묶고, 50세 이상을 "50+"로 묉습니다.
    age_group = "10-49" if age in ["10-19", "20-29", "30-39", "40-49"] else "50+"

    # 성별과 나이대에 따라 키워드를 결정합니다.
    if gender == "Male" and age_group == "10-49":
        keywords = ["편의점", "커피", "쉼터"]
    elif gender == "Male" and age_group == "50+":
        keywords = ["술집", "호텔", "호프"]
    elif gender == "Female" and age_group == "10-49":
        keywords = ["맛집", "카페", "빵집"]
    elif gender == "Female" and age_group == "50+":
        keywords = ["찜질방", "백반", "마트"]
    else:
        keywords = ["용산 맛집"]  # 기본 키워드
    return random.choice(keywords)

def recognize_face(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            image_data = body_data.get('image')

            test_embedding = get_embedding_from_image(image_data)
            if test_embedding is None:
                return JsonResponse({'success': False, 'message': '얼굴 임베딩 생성 실패'})

            face_instances = Faces.objects.all()
            best_similarity = -1
            matched_user_id = None
            


            for face_instance in face_instances:
                for i in range(1, 18):
                    face_data_array = np.frombuffer(getattr(face_instance, f'face_data_{i}'), dtype=np.float32)
                    similarity = 1 - cosine(test_embedding, face_data_array)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        matched_user_id = face_instance.user_id
                        

            threshold = 0.7
            if best_similarity > threshold:
                matched_user = Faces.objects.get(user_id=matched_user_id)
                print(f"Matched user_id: {matched_user_id}")
                image_pil = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1])))
                gender, age = classify_face(np.array(image_pil))

                # Debugging 로그 추가
                print(f"DEBUG - Sending Data: Gender: {gender}, Age: {age}, User ID: {matched_user.user.username}")

                return JsonResponse({
                    'success': True, 
                    'message': f'{matched_user.user.username}님 인증되었습니다.', 
                    'gender': gender, 
                    'age': age, 
                    'user_id': matched_user.user.username,
                    'keyword': determine_keyword(gender, age)
                })
            else:
                return JsonResponse({'success': False, 'message': '얼굴 인증 실패', 'similarity': f'{best_similarity:.2f}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"오류 발생: {str(e)}"}, status=500)
        

    return render(request, 'field/face_recognize.html')


def classify_face_view(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            image_data = body_data.get('image')

            # 이미지를 base64로부터 디코딩하고 PIL 이미지로 변환
            image_pil = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1])))
            
            # PIL 이미지를 numpy 배열로 변환
            image_array = np.array(image_pil)
            
            # classify_face 함수를 호출하여 성별과 나이를 예측
            gender, age = classify_face(image_array)

            return JsonResponse({'gender': gender, 'age': age, 'keyword': determine_keyword(gender, age)})
        except Exception as e:
            print(f"얼굴 분류 중 오류 발생: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'})

def map_view(request):
    keyword = request.GET.get('keyword', '용산 맛집')
    gender = request.GET.get('gender')
    age = request.GET.get('age')
    user_id = request.GET.get('user_id')
    location_prefix = request.GET.get('location_prefix', '')

    # 나이 그룹을 한국어로 매핑
    age_mapping = {
        "10-19": "10대",
        "20-29": "20대",
        "30-39": "30대",
        "40-49": "40대",
        "50-59": "50대",
        "60-69": "60대",
        "70+": "70대 이상",
    }
    age = age_mapping.get(age, "나이 없음")

    # 성별을 한국어로 매핑
    gender_mapping = {
        "Male": "남성",
        "Female": "여성",
    }
    gender = gender_mapping.get(gender, "성별 없음")

    # location_prefix가 keyword에 포함되도록 함
    full_keyword = f"{location_prefix} {keyword}".strip()

    # 디버깅 정보 출력
    print(f"Received location_prefix: {location_prefix}")

    return render(request, 'field/map.html', {
        'keyword': full_keyword,
        'gender': gender,
        'age': age,
        'user_id': user_id
    })

def get_location_prefix(request):
    user_id = request.GET.get('user_id')
    
    print(f"API - Received user_id: {user_id}")  # 여기가 제대로 작동하는지 확인하세요

    if not user_id:
        print("API - Received user_id: None")
        return JsonResponse({'location_prefix': ''})

    reservation = Reservations.objects.filter(user__username=user_id).last()
    
    if not reservation:
        print("API - No reservations found for user")
        return JsonResponse({'location_prefix': ''})

    end_location_id = reservation.end_location_id
    if not end_location_id:
        print("API - No end_location_id found in reservation")
        return JsonResponse({'location_prefix': ''})

    location = get_object_or_404(Locations, pk=end_location_id)
    location_prefix = f"{location.city} {location.district}"
    print(f"API - location_prefix: {location_prefix}")
    return JsonResponse({'location_prefix': location_prefix})
