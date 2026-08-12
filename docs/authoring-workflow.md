# 작성 및 이미지 워크플로

## 새 게시물

파일명 접두사는 URL 날짜를 없애기 위한 규칙이므로 유지한다. 실제 날짜는 front matter의 `date`다.

```powershell
python tools/new_post.py WebLogic jdbc-store-recovery `
  --title "[WebLogic/JMS] JDBC Store recovery after database restart" `
  --tags "Middleware, WebLogic, JMS, JDBCStore"
```

생성기는 다음 순번으로 `WebLogic/_posts/0000-XX-XX-jdbc-store-recovery.md`를 만들며, 이미 있는 파일을 덮어쓰지 않는다.

## 줄바꿈

일반 Markdown은 빈 줄 하나로 문단을 나눈다. `<br>`는 제목과 본문 사이의 시각적 여백처럼 문단 규칙으로 표현할 수 없는 경우만 사용한다.

기존의 “연속 개행 수를 `<br>` 수로 변환” 규칙은 코드 블록, 목록, 표, 인용문에는 적용하면 안 된다. 향후 편집기는 다음처럼 사용자가 정한 임계값을 설정으로 저장하고, 변환 전 diff를 보여줘야 한다.

```yaml
blank_line_conversion:
  3: 1 # 빈 줄 3개 이상이면 br 1개
  5: 2 # 빈 줄 5개 이상이면 br 2개
```

숫자는 아직 확정하지 않았으므로 현재 자동 변환하지 않는다.

## 이미지: 로컬 미리보기와 공개 URL을 하나로 맞추기

각 이미지 파일은 아래 위치에 둔다.

```text
assets/posts/images/<Category>/<slug>/
```

Markdown에는 항상 사이트 기준 절대 경로만 쓴다.

```markdown
![JMS JDBC Store 상태](/assets/posts/images/WebLogic/jdbc-store-recovery/jdbc-store-state.png)
```

Typora에서 이 경로를 로컬에서도 보이게 하려면 `typora-root-url: ../..`을 사용한다. 이 값은 `<Category>/_posts`에서 저장소 루트로 가는 경로다. 향후 전용 편집기는 이 매핑을 내장하므로 사용자가 URL을 고칠 일이 없게 한다.

## 게시 전

```powershell
python tools/blog_audit.py
```

검사기는 내용을 변경하지 않고 중복 URL, 로컬 이미지 경로, 이중 `.md` 확장자, 가능한 비밀값을 보고한다. 기존 글의 기술 내용 변경은 작성자 승인 후에만 한다.
