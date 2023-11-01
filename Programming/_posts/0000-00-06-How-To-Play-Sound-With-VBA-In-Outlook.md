---
date: 2023-11-01 10:58:33 +0900
layout: post
title: "[Programming/VBA/Outlook] How to play sound with VBA in Outlook?"
tags: [Programming, VBA, Outlook, Sound, Play]
typora-root-url: ..
---

# 1. Overview

Outlook에서 중요한 이메일을 받으면, 알림이 울리도록 설정할 수 있지만, 반복적으로 사용자가 컴퓨터 앞에 도착할 때까지 울리지 않는다.

꼭 수신받아야 하는 이메일이 왔을 경우를 위하여 반복적으로 사운드 파일을 재생하도록 한다.





# 2. Description

## 2.1 Class Module

VBA 클래스 모듈은 다음과 같다.

```vb
Private WithEvents objInspectors As Outlook.Inspectors
Private WithEvents objMailItem As Outlook.MailItem

Private Sub Application_Startup()
    Set objInspectors = Application.Inspectors
End Sub

Private Sub objInspectors_NewInspector(ByVal Inspector As Inspector)
    If Inspector.CurrentItem.Class = olMail Then
        Set objMailItem = Inspector.CurrentItem
    End If
End Sub
```





## 2.2 ThisOutlookSession

ThisOutlookSession 코드는 다음과 같다.

```vb
Private Declare PtrSafe Function PlaySound Lib "winmm.dll" Alias "PlaySoundA" (ByVal lpszName As String, ByVal hModule As Long, ByVal dwFlags As Long) As Long

Private Const SND_ASYNC = &H1
Private Const SND_LOOP = &H8

Private Sub Application_NewMail()
    Check_NewMail Application.Session.GetDefaultFolder(olFolderInbox)
    Check_NewMail Application.Session.GetDefaultFolder(olFolderInbox).Folders("TAS")
End Sub

Private Sub Check_NewMail(objInBox As Outlook.MAPIFolder)
    Dim objMail As Object
    Dim receivedDate As Date
    Dim daysAgo As Date
    Dim daysFuture As Date
    
    For Each objMail In objInBox.Items ' 최근 메일부터 가져옴
               
        ' 안읽은 이메일만 체크
        If objMail.UnRead = True Then
            
            ' 최근 3일 이내의 날짜 계산
            daysAgo = Format(DateAdd("d", -3, Date), "yyyy-mm-dd")
            daysFuture = Format(DateAdd("d", 0, Date), "yyyy-mm-dd")
            receivedDate = Format(objMail.ReceivedTime, "yyyy-mm-dd")

            ' 최근 3일간의 메일만 확인
            If (daysAgo <= receivedDate) And (daysFuture >= receivedDate) Then
                    ' Body 에서 "status: new" 텍스트를 확인
                    If InStr(1, LCase(objMail.Body), "status: new") > 0 Then
                        PlaySoundLoop
                    End If
            End If
        End If
    Next objMail
End Sub

Private Sub PlaySoundLoop()
    ' 여기에 사운드 파일 경로를 지정
    Dim soundFile As String
    soundFile = "C:\Windows\Media\Windows Ringin.wav"
    
    Do
        PlaySound soundFile, 0, SND_ASYNC Or SND_LOOP
        DoEvents ' 다른 이벤트 처리를 위한 코드
    Loop Until (MsgBox("Press OK to stop the sound.", vbOKOnly, "Stop Sound") = vbOK)
    
    ' 사용자가 확인 버튼을 누르면 사운드 중지
    PlaySound vbNullString, 0, SND_ASYNC ' 사운드 중지
End Sub
```



`Private Declare PtrSafe` VBA 7.1, Windows 11 64bit 환경이므로 필요한 선언부



`GetDefaultFolder(olFolderInbox)` 기본 수신함(Inbox) 외에도

`Folders("TAS")` Inbox 하위에 TAS 폴더 또한 보기 위하여 설정하였다.

메일에 자동 규칙으로 자동 분류가 되면, 기본 수신함에 도착하지 않고 바로 TAS에 가기 때문에 반드시 필요했다.



`For Each objMail In objInBox.Items` 기본적으로 메일의 최근 목록부터 과거로 가져온다고 하지만, 그렇지 않은 것 같다.



`InStr(1, LCase(objMail.Body), "status: new")` 이메일 본문을 소문자로 변환하고, 'status: new' 가 포함되어 있는지 확인한다.





# 3. References

ChatGPT 도움으로 해결함
