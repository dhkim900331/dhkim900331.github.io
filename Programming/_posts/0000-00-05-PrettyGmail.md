---
date: 2022-05-10 16:26:50 +0900
layout: post
title: "[Programming/Javascript] Gmail 을 이쁘게 복사하자"
tags: [Programming, Javascript, Gmail, Clipboard, Chrome, Extension]
typora-root-url: ..
---

# 1. 개요

고객과 주고받은 이메일을, 사내 Confluence(wiki)에 자주 삽입하곤 하는데

gmail 을 Ctrl+C/V 로 옮기면 매우 안이쁘게 복사가 된다.
{{ site.content.br_small }}
크롬 확장 기능을 이용해 좀 더 깔끔하게 복사 하도록 하는 애드온(확장 프로그램)을 만들어 보았다.

아직 완성도가 매우 떨어진다.
{{ site.content.br_small }}
# 2. 확장 프로그램 설치

* 지원되는 기능
  * 복사 -> 붙여넣기를 할 때, html code를 파싱하여 보낸사람/받는사람/시각/제목/본문을 얻는다.
  * 얻는 결과를 자동으로 클립보드에 넣고 싶지만 모르겠다.
{{ site.content.br_small }}
* 다운로드

[PrettyGmail.zip](/assets/upload/PrettyGmail.zip)
{{ site.content.br_small }}
* 위 파일을 압축해제하고, 다음과 같이 크롬 확장 프로그램으로 추가한다.

[PrettyGmail_1](/../assets_copy_1/posts/images/Programming/PrettyGmail/PrettyGmail_1.png)# 3. 사용법

* 확장 프로그램을 활성화 하고, 다음과 같이 이메일을 복사한다.
  * 현재는, 다양한 대화 형식에서 테스트하지 않았다.
{{ site.content.br_small }}
* 다음의 이메일을 보고 있다고 가정하에..

[PrettyGmail_2](/../assets_copy_1/posts/images/Programming/PrettyGmail/PrettyGmail_2.png)* 다음처럼 Ctrl + A를 눌러 전체 선택하거나, 제목~본문 바닥까지만 드래그한다.
  * 그러고, Ctrl + C 를 눌러 복사하고, 바로 Ctrl + V 를 누르면...

[PrettyGmail_3](/../assets_copy_1/posts/images/Programming/PrettyGmail/PrettyGmail_3.png)* 개발자도구모음의 Console log로 내용이 출력된다.

[PrettyGmail_4](/../assets_copy_1/posts/images/Programming/PrettyGmail/PrettyGmail_4.png)* 위 Console log의 제목 부터 끝까지 복사하여, html 형식으로 집어넣으면 투박하지만 불필요한 css가 제거되고 필요한 내용들만 들어갔다. (맨 아래 명함 이미지도 잘 가져온다^^)
  * 아래 예는, 우리 회사 confluence 문서

[PrettyGmail_5](/../assets_copy_1/posts/images/Programming/PrettyGmail/PrettyGmail_5.png)