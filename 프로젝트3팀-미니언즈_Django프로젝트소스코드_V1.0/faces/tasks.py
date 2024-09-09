from celery import shared_task
import subprocess

@shared_task
def execute_script_task():
    script_path = r'C:\Users\USER\OneDrive\classes\LOCKERs\DA35-Final-Minions-LOCKERs\Lockers\faces\facepos.py'
    
    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True, check=True)
        # 결과를 로그에 남기거나 다른 처리를 수행할 수 있음
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"스크립트 실행 중 오류 발생: {e.output}")
