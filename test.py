!pip install plotly smplx torch numpy trimesh

# =========================================

import numpy as np
import torch
import smplx
import plotly.graph_objects as go

# =========================================

# SMPL-X 모델 로드
model_path = '/content/drive/MyDrive/SMPL-X_Model/smplx/SMPLX_MALE.pkl'
smplx_model = smplx.create(model_path, model_type='smplx', gender='male', ext='pkl')

# =========================================

# 측정값 예시 (단위: mm)
measurements = {
    "height": 1657,
    "neck_height": 1389,
    "shoulder_height": 1332,
    "armpit_height": 1231,
    "waist_height": 1057,
    "hip_height": 889,
    "crotch_height": 739,
    "ankle_height": 61,
    "fist_height": 759,
    "elbow_height": 1005,
    "chest_width": 294
}

# =========================================

# 최적화
from scipy.optimize import minimize
import numpy as np

# Residual 계산 함수 정의
def residuals(betas, measurements):
    # SMPL 모델로부터 추정된 치수 계산
    body_pose = np.zeros((1, 63)) # 자세 파라미터
    global_orient = np.zeros((1, 3)) # 빈 행렬 생성
    transl = np.zeros((1, 3)) # 빈 행렬 생성
    
    output = smplx_model(betas=torch.tensor(betas, dtype=torch.float32).unsqueeze(0), # 인체의 형태 정의하는 파라미터
                         body_pose=torch.tensor(body_pose, dtype=torch.float32), # 몸의 자세를 정의하는 파라미터
                         global_orient=torch.tensor(global_orient, dtype=torch.float32), # 모델의 전반적인 방향을 정의하는 파라미터
                         transl=torch.tensor(transl, dtype=torch.float32)) # 모델의 위치를 정의하는 파라미터
    
    vertices = output.vertices.detach().cpu().numpy().squeeze() # 추출된 vertics의 데이터를 numpy 배열로 변환 -> 3D 공간에서 각 점의 좌표가 됨
    
    # 필요한 측정값을 추출
    estimated_measurements = {
        "height": vertices[:, 1].max() - vertices[:, 1].min(),
        "neck_height": np.mean(vertices[[3087, 3088, 3091], 1]),  # Example vertices for neck height
        "shoulder_height": np.mean(vertices[[2901, 2902, 2903], 1]),  # Example vertices for shoulder height
        "armpit_height": np.mean(vertices[[3153, 3154, 3155], 1]),  # Example vertices for armpit height
        "waist_height": np.mean(vertices[[3265, 3266, 3267], 1]),  # Example vertices for waist height
        # 더 많은 측정값들을 추출하여 계산
    }
    
    # Residual 계산
    residual = 0
    for key in measurements:
        if key in estimated_measurements:
            residual += (measurements[key] - estimated_measurements[key]) ** 2
    return residual

# 초기 파라미터 설정
initial_betas = np.random.rand(10)  # 다양한 초기값 설정

# 최적화 실행
result = minimize(residuals, initial_betas, args=(measurements,), method='L-BFGS-B', options={'maxiter': 500})
optimized_betas = result.x
print("최적화된 베타 파라미터:", optimized_betas)

# 최적화 결과 평가
if result.success:
    print("최적화가 성공적으로 완료되었습니다.")
else:
    print("최적화가 실패했습니다. 최적화 상태:", result.message)

# =========================================


# 최적화된 파라미터를 사용하여 SMPL 모델 생성
body_pose = np.zeros((1, 63))
global_orient = np.zeros((1, 3))
transl = np.zeros((1, 3))

output = smplx_model(betas=torch.tensor(optimized_betas, dtype=torch.float32).unsqueeze(0),
                     body_pose=torch.tensor(body_pose, dtype=torch.float32),
                     global_orient=torch.tensor(global_orient, dtype=torch.float32),
                     transl=torch.tensor(transl, dtype=torch.float32))

vertices = output.vertices.detach().cpu().numpy().squeeze()
faces = smplx_model.faces

# Plotly를 사용하여 3D 모델 시각화
I = faces[:, 0]
J = faces[:, 1]
K = faces[:, 2]

x = vertices[:, 0]
y = vertices[:, 1]
z = vertices[:, 2]

fig = go.Figure(data=[go.Mesh3d(
    x=x, y=y, z=z,
    i=I, j=J, k=K,
    color='lightblue', opacity=0.50
)])

fig.update_layout(scene=dict(
    xaxis=dict(title='X'),
    yaxis=dict(title='Y'),
    zaxis=dict(title='Z')
))

fig.show()