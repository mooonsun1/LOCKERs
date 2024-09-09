from facenet_pytorch import MTCNN, InceptionResnetV1, fixed_image_standardization, training
import torch , torchvision
from torch.utils.data import DataLoader, SubsetRandomSampler
from torch import optim
from torch.optim.lr_scheduler import CosineAnnealingLR, MultiStepLR
from torch.utils.tensorboard import SummaryWriter
from torchvision import datasets, transforms
import numpy as np
import os
from PIL import Image

# 경로 설정(각자 경로에 맞게 설정)
train_data_dir = r"C:\Users\MUNSUNG\Desktop\만선\modeling\datasets\train"
valid_data_dir = r"C:\Users\MUNSUNG\Desktop\만선\modeling\datasets\valid"
test_data_dir = r"C:\Users\MUNSUNG\Desktop\만선\modeling\datasets\test"

# 학습 설정값
batch_size = 64
epochs = 20
workers = 4 if os.name == 'nt' else 8

# device
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device
)


def process_dataset(dataset_dir, save_dir, batch_size, workers):
    """데이터셋을 처리하여 얼굴을 감지하고 크롭하여 저장하는 함수"""
    # 데이터셋 정의
    dataset = datasets.ImageFolder(dataset_dir, transform=transforms.Resize((512, 512)))
    dataset.samples = [
        (p, p.replace(dataset_dir, save_dir))
        for p, _ in dataset.samples
    ]

    # 데이터로더 정의
    data_loader = DataLoader(
        dataset,
        num_workers=workers,
        batch_size=batch_size,
        collate_fn=training.collate_pil
    )

    for i, (x, y) in enumerate(data_loader):
        try:
            # 얼굴 감지
            for j in range(len(x)):
                img = x[j]
                save_path = y[j]

                # 이미지를 PIL 형태로 변환 (ImageFolder 사용 시 PIL 형태로 불러옴)
                img_pil = Image.fromarray(np.array(img))

                # 얼굴 감지
                boxes, probs = mtcnn.detect(img_pil)

                if boxes is not None:
                    # 얼굴이 감지된 경우 크롭 및 저장
                    mtcnn(img_pil, save_path=save_path)
                else:
                    print(f"Batch [{i+1}/{len(data_loader)}], Image {j + 1}: No faces detected.")
        
        except Exception as e:
            print(f"Batch {i + 1}, Image {j + 1}: Error - {e}")
            continue

        print(f'Batch {i + 1} of {len(data_loader)}')

# 데이터셋 경로 설정
train_save_dir = os.path.join(train_data_dir + '_cropped')
valid_save_dir = os.path.join(valid_data_dir + '_cropped')
test_save_dir = os.path.join(test_data_dir + '_cropped')

# 데이터셋 처리
process_dataset(train_data_dir, train_save_dir, batch_size, workers)
process_dataset(valid_data_dir, valid_save_dir, batch_size, workers)
process_dataset(test_data_dir, test_save_dir, batch_size, workers)

# MTCNN 모델 메모리에서 제거
del mtcnn