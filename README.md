# qgis_plugin_template
QGIS 플러그인 개발을 위한 탬플릿

# 사용 방법
- 해당 레포지토리를 탬플릿으로 하여 새 레포지토리를 생성한다.
- 생성된 레포지토리를 로컬에 클론한다.
- create_venv.bat의 내용을 확인하고 o4w_env.bat의 경로를 자신의 환경에 맞게 수정한다.
- create_venv.bat을 실행하여 가상환경을 생성한다.
- 가상환경을 활성화 한 후 pip install -r requirements.txt를 실행하여 필요한 패키지를 설치한다.
- to_venv 폴더 내의 qgis.pth와 site_customized.py 내의 경로를 자신의 환경에 맞게 수정한다.
- to_venv 폴더내 파일 및 폴더를 복사하여 자신의 가상환경 폴더(.venv)에 붙여넣는다.

# 기타 오류사항 해결
- SSL module in Python is not available 오류는 [해당 링크](https://stackoverflow.com/questions/60290795/ssl-module-in-python-is-not-available-qgis/71226425#71226425) 참고
