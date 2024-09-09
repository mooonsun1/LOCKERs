from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Faces(models.Model):
    face_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    face_data_1 = models.BinaryField(blank=True, null=True)
    face_data_2 = models.BinaryField(blank=True, null=True)
    face_data_3 = models.BinaryField(blank=True, null=True)
    face_data_4 = models.BinaryField(blank=True, null=True)
    face_data_5 = models.BinaryField(blank=True, null=True)
    face_data_6 = models.BinaryField(blank=True, null=True)
    face_data_7 = models.BinaryField(blank=True, null=True)
    face_data_8 = models.BinaryField(blank=True, null=True)
    face_data_9 = models.BinaryField(blank=True, null=True)
    face_data_10 = models.BinaryField(blank=True, null=True)
    face_data_11 = models.BinaryField(blank=True, null=True)
    face_data_12 = models.BinaryField(blank=True, null=True)
    face_data_13 = models.BinaryField(blank=True, null=True)
    face_data_14 = models.BinaryField(blank=True, null=True)
    face_data_15 = models.BinaryField(blank=True, null=True)
    face_data_16 = models.BinaryField(blank=True, null=True)
    face_data_17 = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)      # 업데이트 시 자동으로 현재 시간 저장

    class Meta:
        managed = True  # 이 옵션은 Django가 이 테이블을 직접 관리하지 않도록 설정 (이미 존재하는 테이블에 대해 사용)
        db_table = 'faces'  # 데이터베이스에서 테이블 이름이 'Faces'임을 명시

    def __str__(self):
        return f"{self.user.username}'s face data"
    
    def get_face_data(self):
        # face_data를 반환하는 메서드 추가
        return self.face_data

