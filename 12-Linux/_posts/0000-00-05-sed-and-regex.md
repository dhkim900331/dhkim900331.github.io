---
date: 2023-03-15 08:36:40 +0900
layout: post
title: "[Linux/sed] sed and regex"
tags: [Linux, OS, sed, regex]
typora-root-url: ..
---

# 1. 개요

sed 기본적인 사용 방법과 regex를 활용한 몇몇 유용한 패턴을 정리한다



# 2. 기본 사용법

다음과 같은 Document가 있다고 가정하고,

기본적인 사용방법을 예시로 든다.

변경된 결과만 언급하기로 한다.

```sh
$ cat /tmp/sed/before.txt
Hello world!
My name is ${NAME}

This time is 'How to use sed'
Through practice, You can enhance editing text document!
-
Ref. My blog addr is //dhkim900331.github.com
My email is ks900331@naver.com
My phone is 010-1234-5678
```



## 2.1 간단한 문자 변경

- ```sh
  $ sed "s/\!/\!\!/g" before.txt
  Hello world!!
  Through practice, You can enhance editing text document!!
  ```

  * 느낌표(!) 두개 만들기
  * 느낌표(!, Exclamation Mark)는 Linux에서 특수문자이기 때문에 문자마다 Escape(\, back-slash)를 사용해야 한다. [참고](https://www.baeldung.com/linux/bash-exclamation-mark)
  * 추가로 확인해보니, single quote(')를 사용하여 특수문자를 제거할 수 있다.
    * `sed 's,!,!!,g' before.txt`



* ```sh
  $ sed "s/world\!/world\!\!/g" before.txt
  Hello world!!
  ```

  * 원하는 글자의 느낌표만 두개로 변경하였다.



## 2.2 특수 문자 변경

slash, quote와 같은 특수문자를 변경할 때는 escape가 필요하다고 하였는데, 다음과 같이 복잡하게 구성이 되는 경우가 있다.

```sh
$ sed "s/\/\//https:\/\//g" before.txt
Ref. My blog addr is https://dhkim900331.github.com
```

// &rarr; https:// 변경하기 위해 slash와 escape를 섞다보니 복잡하다.



```sh
$ sed "s|//|https://|g" before.txt
Ref. My blog addr is https://dhkim900331.github.com
```

이렇게 delimiter(구분자) 를 변경하면 가독성이 좋아진다.

또는 `sed "s,//,https://,g" before.txt`, `sed "s@//@https://@g" before.txt`



## 2.3 라인 변경

특정 라인을 편집하려면,

```sh
$ cat -n before.txt
     1  Hello world!
     2  My name is ${NAME}
     3
     4  This time is 'How to use sed'
     5  Through practice, You can enhance editing text document!
     6  -
     7  Ref. My blog addr is //dhkim900331.github.com
     8  My email is ks900331@naver.com
     9  My phone is 010-1234-5678

$ sed "6s,-,------------," before.txt
Through practice, You can enhance editing text document!
------------
Ref. My blog addr is //dhkim900331.github.com
```

6번째 줄의 Dash(`-`)를 여러개 복사했다.



## 2.4 라인 전체 변경

라인 전체를 통째로 변경하려면,

```sh
$ sed "/My/c\privacy" before.txt
privacy
privacy
privacy
```

Blog, Email, Phone 정보가 있던 줄 전체를 변경했다.



```sh
$ sed "/^My/c\privacy" before.txt
Ref. My blog addr is //dhkim900331.github.com
privacy
privacy
```

Regex로 시작(`^`) 문자를 지정하여, 일부만 변경했다.

이 명령어 패턴에서는, delimiter가 slash만 되는 것 같다.



## 2.5 추가 및 삭제

```sh
$ sed "1p" before.txt
Hello world!
Hello world!
My name is ${NAME}

$ sed "1d" before.txt
My name is ${NAME}
```

P(print), D(delete) 으로 첫번째 줄을 복사 또는 첫번째 줄 삭제



```sh
$ sed "1,3d" before.txt
This time is 'How to use sed'
```

1~3줄 삭제



```sh
$ cat -n before.txt
     1  Hello world!
     2  My name is ${NAME}
     3
     4  This time is 'How to use sed'
     5  Through practice, You can enhance editing text document!
     6  -
     7  Ref. My blog addr is //dhkim900331.github.com
     8  My email is ks900331@naver.com
     9  My phone is 010-1234-5678
     
$ sed "1~3d" before.txt
My name is ${NAME}

Through practice, You can enhance editing text document!
-
My email is ks900331@naver.com
My phone is 010-1234-5678
```

Line 1 삭제, Line 3 까지 건너 뛰기를 반복한다.

반복하므로, Line 1, 4(1+3), 7(1+3+3), 10(1+3+3+3) 을 삭제한다.



```sh
$ sed '1,1!d' before.txt
Hello world!
```

1~1 라인을 제외하고 모두 삭제한다.



## 2.6 정규식 변경

개인정보 중에 전화번호만 검출하여 변경한다.

```sh
$ sed 's/[0-9]\{1,3\}-[0-9]\{1,4\}-[0-9]\{1,4\}/privacy/g' before.txt
My phone is privacy
```

[0-9] : 0~9 숫자

\\{1,3\\} : 1~3 자리이며 escape brace 필요

복잡하므로 강조 표시를 해보자면,,,

$ sed 's/**[0-9]\\{1,3\\}**-**[0-9]\\{1,4\\}**-**[0-9]\\{1,4\\}**/privacy/g' before.txt



사실 이 부분은,, 정규식을 알면 되는 내용이다.



## 2.7 Group Capture

Group Catpure라는 것은, 정규식으로 검색된 특정 부분을 Capture(촬영, 변수화)하여 원하는 대로 꺼내어 쓸 수 있게 해주는 것이다.

사실 이 부분은 sed의 범위를 넘어선다.



다음의 예제를 보면,

```sh
$ TEXT="0 a A"

$ echo ${TEXT} | sed "s#\([0-9]\) \([a-z]\) \([A-Z]\)#numeric(\1) lower(\2) upper(\3)#"
numeric(0) lower(a) upper(A)
```

0 a A 문자를 정규식으로 숫자, 소문자, 대문자 구분을 하고 소괄호로 group capture 하여 \1, \2, \3 으로 꺼내어 쓸 수 있다.

숫자,소문자,대문자 인지를 구별하는 것은 정규식의 기능이고, 구분된 문자들을 특정 그룹으로 묶어 (묶을 때 소괄호) group capture를 하였고,

capture를 back-slash 숫자로 갯수만큼 꺼내어 쓸 수 있다는 것.



위 예제를 변형시켜 보면,

```sh
$ TEXT="a 0 A"
$ echo ${TEXT} | sed "s#\([0-9]\) \([a-z]\) \([A-Z]\)#numeric(\1) lower(\2) upper(\3)#"
a 0 A
```

TEXT 변수안의 글자의 순서를 뒤바꿨을 뿐인데, sed 정규식이 실행되지 않아 원본 그대로 출력이 되었다.

내가 지금까지 알기로는, 순서 까지 스마트하게 capture하는 방법은 모르겠다.

위의 정규식은 항상 "숫자 v 소문자 v 대문자"가 위치할 것이라는 가정이 들어있다.

***v 는 뛰어 쓰기를 의미한다.***



# 3. 유용한 패턴

기본 사용법을 가지고, 필드에서 바로 써먹을 수 있는 몇가지 유용한 패턴을 정리해본다.



## 3.1 Group Capture

다음과 같이 이미 정리된 문서가 있다.

```sh
$ cat phone_email_name.txt
010-1234-5678 Jason@Jason.com Jason
010-2555-2323 Daniel@Daniel.com
013-5555-1234 bakeuion@bakeuion.com bakeuion
```



* 1단계, Phone number 정규식 만들기
  *  `[0-9]{1,4}` : 0~9 숫자가 1~4자리 있다는 의미
  * `-` : Phone 중간 번호 마디로써, 그냥 단순 문자.
  * `( ~ )` : 소괄호 단위로 Group이라고 하며, Capture가 된다. 아래에서 설명하지만 Capture를 하면 변수로 꺼내어 쓸 수 있게 된다.

<font size="5pt">( [0-9]{1,4} - [0-9]{1,4} - [0-9]{1,4} )</font>



* 2단계, 불필요한 공백 제거 및 소,중괄호 Escape 처리
  * 불필요한 공백이라는 의미는, 1단계에서 정규식 코드를 가독성있게 하여 설명하기 위하여 공백을 추가하였는데, 그것을 제거한다는 의미
  * 소,중괄호만 Back-slash로 escape 처리해야 하는 것으로 보여진다, 대괄호는 하지 않아도 되는 것으로 확인됨, 구체적은 설명된 문서는 못찾음.
  * 변수로 담아 3단계에서 가독성을 높인다.

<font size="5pt">PHONE_REGEX="\\([0-9]\\{1,4\\}-[0-9]\\{1,4\\}-[0-9]\\{1,4\\}\\)"</font>



* 3단계, 다음의 sed syntax에 삽입한다.
  * `\1` : 1단계에서 말한 Group Capture 순서대로 꺼낼 수 있는 변수다. 소괄호 묶음 마다 숫자를 증가시켜 꺼내 쓸 수 있다.

<font size="5pt">sed "s#${PHONE_REGEX}#Phone(\1)#" phone_email_name.txt</font>



결과는,,,

```sh
$ PHONE_REGEX="\([0-9]\{1,4\}-[0-9]\{1,4\}-[0-9]\{1,4\}\)"
sed "s#${PHONE_REGEX}#Phone(\1)#" phone_email_name.txt
Phone(010-1234-5678) Jason@Jason.com Jason
Phone(010-2555-2323) Daniel@Daniel.com Daniel
Phone(013-5555-1234) bakeuion@bakeuion.com bakeuion
```



최종적으로는 다음처럼 정리할 수 있다.

```sh
$ PHONE_REGEX="\([0-9]\{1,4\}-[0-9]\{1,4\}-[0-9]\{1,4\}\)"
$ EMAIL_REGEX="\([0-9a-zA-Z].*@[0-9a-zA-Z].*[.com|.kr]\)"
$ NAME_REGEX="\([a-zA-Z].*\)"

$ sed "s#${PHONE_REGEX} ${EMAIL_REGEX} ${NAME_REGEX}# Phone(\1) Email(\2) Name(\3) #" phone_email_name.txt
 Phone(010-1234-5678) Email(Jason@Jason.com) Name(Jason)
 Phone(010-2555-2323) Email(Daniel@Daniel.com) Name(Daniel)
 Phone(013-5555-1234) Email(bakeuion@bakeuion.com) Name(bakeuion)
```



어떤 데이터 순서를 가지고 있던 간에, 이메일 데이터만 제대로 뽑을 수 있는 regex를 만들다가 어려워서 포기했다~



# 4. 참고

[Regex Cheat Sheet](https://www.regexlib.com/CheatSheet.aspx)
