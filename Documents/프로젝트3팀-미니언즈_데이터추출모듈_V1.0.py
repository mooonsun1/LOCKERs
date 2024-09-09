import os
import shutil
import random
import splitfolders
from zipfile import ZipFile
from glob import glob

import os
import random
import shutil

# 경로 설정 (각자 경로에 맞게 수정)
base_path = "D:/project_Lockers/Data"  # 원본 데이터 경로
target_path = "D:/project_Lockers/Data/datasets2"  # 새로운 데이터셋 경로

# 각 화질별 데이터 경로 설정
high_path = os.path.join(base_path, "high_data")
middle_path = os.path.join(base_path, "middle_data")
low_path = os.path.join(base_path, "low_data")

# 각 데이터셋 구성 개수
train_count = {'High': 650, 'Middle': 650, 'Low': 700}
valid_count = {'High': 400, 'Middle': 400, 'Low': 400}
test_count = {'High': 400, 'Middle': 400, 'Low': 400}

# 악세사리 착용여부 | 광원 | 표정 | 촬영 각도
acc = ['S001', 'S002', 'S003', 'S004', 'S005', 'S006']
lux = ['L1', 'L2', 'L3', 'L4', 'L8', 'L9', 'L12', 'L13', 'L16', 'L17', 'L19', 'L22', 'L25', 'L28']
emotion = ['E01', 'E02']
angle = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C16', 'C19', 'C20']

def random_sample_files(image_quality_path, person_class, sample_count):
    """화질별로 특정 사람 클래스에서 무작위로 파일을 추출하는 함수"""
    all_files = []
    person_path = os.path.join(image_quality_path, person_class)
    
    # 사람 클래스 내에서 모든 파일을 찾아 리스트에 추가
    for a in acc:
        for l in lux:
            for e in emotion:
                for ang in angle:
                    file_name = f"{ang}.jpg"
                    file_path = os.path.join(person_path, a, l, e, file_name)
                    if os.path.exists(file_path):
                        all_files.append(file_path)
    
    # 파일을 섞고 필요한 개수만큼 선택
    return random.sample(all_files, min(sample_count, len(all_files)))

def copy_files(file_list, destination_folder, person_id, start_counter=1):
    """파일을 새로운 폴더로 복사"""
    os.makedirs(destination_folder, exist_ok=True)
    counter = start_counter
    for file in file_list:
        file_name = os.path.basename(file)
        new_file_name = f"{person_id}_C{counter}_{file_name}"
        target_file = os.path.join(destination_folder, new_file_name)
        shutil.copy2(file, target_file)
        print(f"Copied {file} to {target_file}")
        counter += 1
    return counter

def extract_dataset():
    datasets = ['Train', 'Valid', 'Test']
    
    # 사람 클래스를 모든 화질 경로에서 랜덤하게 400명 선택
    person_classes = sorted(os.listdir(low_path))  # low_path에 있는 사람 클래스 (1200명)

    # 각 데이터셋을 처리
    for dataset in datasets:
        if dataset == 'Train':
            counts = train_count
        elif dataset == 'Valid':
            counts = valid_count
        elif dataset == 'Test':
            counts = test_count
        
        dataset_path = os.path.join(target_path, dataset)
        
        # 각 화질별로 처리
        for person_id in person_classes:
            print(f"Processing person: {person_id} for {dataset}...")

            start_counter = 1  # 파일 번호를 클래스마다 시작

            # 고화질
            sampled_high = random_sample_files(high_path, person_id, counts['High'])
            # 중화질
            sampled_middle = random_sample_files(middle_path, person_id, counts['Middle'])
            # 저화질
            sampled_low = random_sample_files(low_path, person_id, counts['Low'])

            # 모든 화질을 섞어서 하나의 폴더에 넣음
            all_samples = sampled_high + sampled_middle + sampled_low
            random.shuffle(all_samples)  # 파일을 섞음

            # 새로운 폴더에 복사
            destination_folder = os.path.join(dataset_path, person_id)
            copy_files(all_samples, destination_folder, person_id, start_counter)

# 랜덤 추출
extract_dataset()
