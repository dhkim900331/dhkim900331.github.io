---
date: 2023-05-23 09:09:18 +0900
layout: post
title: "[ETC/Outlook/VBA] How To Automatically Send Mail"
tags: [ETC, Outlook, VBA, Macro]
typora-root-url: ..
---

# 1. 개요

Outlook 에 내장된 VBA 를 이용하여, 자동으로 이메일을 보내는 Macro를 개발해본다.
{{ site.content.br_big }}
# 2. 설명

Win Object를 잘 다루지 못하므로, Googling 을 통해서 많은 도움을 얻고자 했는데.. Chat GPT를 통해서 뚝딱 완성이 되어 버렸다.

질문은 여러개가 있었지만, 주요한 것은 두개정도다.

```
- how to make macro that automatically send email per 1 minutes and that is background like user32
- can you change TimerLoop to other method with user32 library ?
```
{{ site.content.br_small }}
토대로 완성된 코드는,

```vb
Option Explicit

Private Declare PtrSafe Function SetTimer Lib "user32" (ByVal hWnd As LongPtr, ByVal nIDEvent As LongPtr, ByVal uElapse As Long, ByVal lpTimerFunc As LongPtr) As LongPtr
Private Declare PtrSafe Function KillTimer Lib "user32" (ByVal hWnd As LongPtr, ByVal nIDEvent As LongPtr) As LongPtr

Private TimerID As LongPtr

Sub StartEmailSending()
    ' Start the Windows timer
    Dim Minutes As Integer
    Minutes = 10
    TimerID = SetTimer(0, 0, Minutes * 60000, AddressOf TimerCallback)
End Sub

Sub StopEmailSending()
    ' Stop the Windows timer
    KillTimer 0, TimerID
End Sub

Private Sub TimerCallback(ByVal hWnd As LongPtr, ByVal uMsg As Long, ByVal nIDEvent As LongPtr, ByVal dwTime As Long)
    ' Callback function triggered by the timer
    SendEmail
End Sub

Private Sub SendEmail()
    Dim dtToday As Date
    dtToday = Now()

    Dim objMail As Outlook.MailItem
    Set objMail = Application.CreateItem(olMailItem)
    objMail.Subject = "[AutoRemider] " & dtToday
    objMail.Body = "Reminder"
    objMail.To = "abcd@efg.com"
    objMail.Send
    Set objMail = Nothing
End Sub



```
{{ site.content.br_small }}
Outlook Macro run에서 StartEmailSending 를 통해 X분마다 user32 의 SetTimer background 동작으로 mail 을 보낸다.
