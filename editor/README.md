# DongDong Blog Markdown Editor

Typora처럼 좌측 원문과 우측 실시간 미리보기를 함께 제공하는 개인용 로컬 편집기입니다.

## 실행

`serve.cmd`를 더블 클릭한 뒤 브라우저에서 다음 주소를 엽니다.

```text
http://localhost:4173/editor/
```

처음 한 번 `블로그 저장소 선택`으로 이 저장소의 루트를 선택합니다. 브라우저는 선택한 폴더만 읽고 쓰도록 허용을 요청합니다.

## 동작

- 새 글: 기존 `0000-XX-XX-slug.md` 순번을 계산하고 실제 발행일은 front matter의 `date`에 기록합니다.
- 이미지: 파일을 선택하거나 왼쪽 원문 창에 끌어놓습니다. 파일은 자동으로 `assets/posts/images/<Category>/<slug>/`에 복사되고, `/assets/posts/images/...` 사이트 절대 경로 Markdown URL이 삽입됩니다. 마지막 URL은 버튼으로 클립보드에 복사할 수 있습니다. alt 텍스트는 파일명으로 자동 입력됩니다.
- 줄바꿈: 일반 Enter 한 번은 그대로 둡니다. 연속 Enter가 설정한 횟수에 도달하면 `<br>`을 원문에 자동 삽입합니다. 코드 블록 내부는 변환하지 않습니다.
- 저장: 현재 게시물 파일에 UTF-8로 저장합니다. 게시 전에는 기존 `tools/blog_audit.py`도 실행하세요.

이 앱은 로컬 파일 권한을 위해 Chromium 계열 브라우저(Edge 또는 Chrome)에서 `localhost`로 실행해야 합니다.
