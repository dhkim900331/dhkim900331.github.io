---
date: 2025-01-31 09:38:00 +0900
layout: post
title: "[Jekyll] Redirect from old url to new url"
tags: [Jekyll, redirect]
typora-root-url: ..
---

# 1. Overview

MD 포스트 파일 이름을 변경하는 등으로 인해 기존 포스트 URL 이 변경되는 경우, Google search console에 등록되어 있는 기존 URL을 변경되었다고 알리기 위해 유용하게 사용 된다.

<br>

# 2. Descriptions

`_layouts\redirected.html` 을 생성
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={{ page.redirect_to }}">
    <title>Redirecting...</title>
    <script>
        window.location.href = "{{ page.redirect_to }}";
    </script>
</head>
<body>
    <p>Redirecting to <a href="{{ page.redirect_to }}">{{ page.redirect_to }}</a>...</p>
</body>
</html>

```

<br>

redirects 아래에 다음과 같은 MD 파일은, 기존 URL `/servlet/FileUpload` 을 새로운 URL `/weblogic/Uploading-File-With-Servlet` 으로 Redirecting 된다.
```
# redirects\servlet-FileUpload.md 파일 내용 (파일명은 중요하지 않다.)
---
layout: redirected
sitemap: false
permalink: /servlet/FileUpload
redirect_to: /weblogic/Uploading-File-With-Servlet
---
```

<br>

# 3. References
