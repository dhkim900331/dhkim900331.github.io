---
date: 2023-04-27 08:41:13 +0900
layout: post
title: "[Scripts/Batch] How to make Bandizip Batch"
tags: [Batch, Windows, Bandizip]
typora-root-url: ..
---

# 1. 개요

Oracle GCS 업무를 수행하면서, 고객이 SR에 업로드한 파일을 내려 받아보면 `<Filename>_SR-Number.<zip>` 과 같은 형식으로 되어 있다.

Bandizip 으로 압축을 일괄 해제하면, 각기 디렉토리에 분리되어 풀리는 등, 하나의 디렉토리에 모아서 보기가 여간 쉬운 일이 아니다.

Bandizip 에서 제공하는 CLI 와 Window batch script를 이용하여 편리하게 만들어 본다.



# 2. 준비물

## 2.1 Batch Script

다음의 Script를 MySR.bat 으로 생성한다.

EXE, OUT variable 은 환경에 맞게 설정한다.

```powershell
@echo off

@rem Bandizip 실행 경로
set EXE=C:\PROGRA~1\Bandizip\Bandizip.exe
@rem Bandizip 이 SR 파일 압축 해제하는 경로
set OUT=C:\Users\Dong-Hyun.KIM\Downloads

@rem File에서 underscope(_) 몇개 인지 카운팅 한다.
@rem count 결과는 하나 더 많은 결과를 보여준다.
set FILE=%1
set count=0
for %%a in (%FILE:_= %) do set /a count+=1

@rem File 명에서 underscope(_) 로 구획을 나누어, 총 몇개의 컬럼이 있는지 확인한다.
@rem count 값의 컬럼을 추출한다. (ex, SR-Number.zip)
@rem 하나 더 많은 갯수를 가리키는 count 변수가 여기서는 제대로 쓰인다.
@rem 코드 참고, https://stackoverflow.com/questions/44502909/batch-file-count-all-occurrences-of-a-character-within-a-string
for /f "delims=_ tokens=%count%" %%n in ('echo %FILE%') do (

  @rem SR-Number.zip 에서 확장자를 제거한다. (ex, SR-Number)
  @rem Bandizip 을 실행하여 압축을 SR-Number에 해제한다.
  for /f "delims=. tokens=1" %%m in ('echo %%~n') do (

	@rem 코드 참고, https://kr.bandisoft.com/bandizip/help/parameter/
	%EXE% x -aos -o:%OUT%\%%m %FILE%
  )

)
```



## 2.2 Registry

다음의 내용을 임의의 이름으로 저장하여 실행하면 Registry가 추가된다.

MySR.bat 을 마우스 우클릭 시에 실행할 수 있게 한다.

아래 경로는 예시이다.

```powershell
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\*\shell\MySRDC\command]
@="\"C:\\Users\\Dong-Hyun.KIM\\Desktop\\GoodMorning\\1. GCS\\9. Auto-Bandizip\\MyDC.bat\" %1"
```



Registry 등록을 하면 마우스 우클릭에 MySRDC 메뉴가 보인다.

<img src="/../assets/posts/images/How-to-make-Bandizip-Batch/image-20230426122458147.png" alt="image-20230426122458147" style="zoom:50%;" />



아래처럼, 서로 다른 SR에서 가져온 압축 파일을 MySRDC로 일괄 해제할 수 있다.

![image-20230426122855928](/../assets/posts/images/How-to-make-Bandizip-Batch/image-20230426122855928.png)



