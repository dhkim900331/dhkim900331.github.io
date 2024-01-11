---
date: 2023-06-07 11:00:37 +0900
layout: post
title: "[Java/JOL] Java Layout Object"
tags: [Programming, JOL]
typora-root-url: ..
---

# 1. Overview

JOL(Java Layout Object) Library 사용법





# 2. Description

Java 객체의 실제 크기를 Inspect 하기 위해서는 Instrumentation 을 활용할 수 있으나,

이는 Shallow size만 알아낼 수 있다.

실제 Size를 Heap dump보다 정확하게 추적할 수 있다고 소개하는 JOL 을 사용해보자.





# 3. Use

[최신버전을 다운로드](https://builds.shipilev.net/jol/) 하여 WEB-INF/lib 에 위치시킨다.





## 3.1 My App

아래와 같은 Business Java code 가 있다고 가정한다.

```java
   ArrayList<byte[]> list = new ArrayList<byte[]>();
    int addedNum = 500;
    int addedByte = 1;

    byte[] objectInSession = new byte[addedByte];
    for(int i=0; i<addedNum; i++){
      list.add(objectInSession);
    }

    HttpSession session = request.getSession(true);
    ArrayList<byte[]> sList = (ArrayList<byte[]>)session.getAttribute("listSession");

    if (sList == null){
      sList = list;
    }
    else{
      sList.addAll(list);
    }

    session.setAttribute("listSession", sList);
```



App 반복 요청 시, 매회 ArrayList로 이루어진 500 bytes data를 누적하여 Session에 저장한다.





## 3.2 Import JOL

이때, Session 에 저장되는 실제 size를 추적하기 위해,

다음의 JOL library import 한다.

```java
import org.openjdk.jol.info.ClassLayout;
import org.openjdk.jol.info.GraphLayout;
import org.openjdk.jol.vm.VM;
```





### 3.3 Specified Field Size in VM

`System.out.println(VM.current().details());` 호출 시

```
# VM mode: 64 bits
# Compressed references (oops): 3-bit shift
# Compressed class pointers: 3-bit shift
# WARNING | Compressed references base/shifts are guessed by the experiment!
# WARNING | Therefore, computed addresses are just guesses, and ARE NOT RELIABLE.
# WARNING | Make sure to attach Serviceability Agent to get the reliable addresses.
# Object alignment: 8 bytes
#                       ref, bool, byte, char, shrt,  int,  flt,  lng,  dbl
# Field sizes:            4,    1,    1,    2,    2,    4,    4,    8,    8
# Array element sizes:    4,    1,    1,    2,    2,    4,    4,    8,    8
# Array base offsets:    16,   16,   16,   16,   16,   16,   16,   16,   16
```

byte가 memory에서 1 byte를 차지한다고 알 수 있다.





## 3.4 Shallow Size of ArrayList

`System.out.println(ClassLayout.parseInstance(sList).toPrintable());` 호출 시

```
java.util.ArrayList object internals:
OFF  SZ                 TYPE DESCRIPTION               VALUE
  0   8                      (object header: mark)     0x0000000000000005 (biasable; age: 0)
  8   4                      (object header: class)    0x000179d0
 12   4                  int AbstractList.modCount     500
 16   4                  int ArrayList.size            500
 20   4   java.lang.Object[] ArrayList.elementData     [[0], [0], ... more 400+
 
 ...
 
 Instance size: 24 bytes
Space losses: 0 bytes internal + 0 bytes external = 0 bytes total
```

ClassLayout은 Object 또는 Class 자체의 Size(Shallow size)만을 계산한다고 하기 때문에, ArrayList.size=500 임에도 매우 작은 24 bytes 로 보여진다.





## 3.5 Shallow Size of Array in ArrayList

`System.out.println(ClassLayout.parseInstance(sList.toArray()).toPrintable());` 호출 시

```
[Ljava.lang.Object; object internals:
OFF  SZ               TYPE DESCRIPTION               VALUE
  0   8                    (object header: mark)     0x0000000000000001 (non-biasable; age: 0)
  8   4                    (object header: class)    0x00011840
 12   4                    (array length)            500
 16 2000   java.lang.Object Object;.<elements>        N/A
Instance size: 2016 bytes
```

toArray() 를 조사한 결과, Shallow Size 임에도 2016 bytes 라는 전체 실제 Size로 보인는 결과가 나온다.





## 3.6 Shallow Size of Single Object in ArrayList

`System.out.println(ClassLayout.parseInstance(sList.toArray()[0]).toPrintable());` 호출 시

```
[B object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x0000000000000001 (non-biasable; age: 0)
  8   4        (object header: class)    0x000007a8
 12   4        (array length)            1
 16   1   byte [B.<elements>             N/A
 17   7        (object alignment gap)
Instance size: 24 bytes
Space losses: 0 bytes internal + 7 bytes external = 7 bytes total
```

`byte[] objectInSession` Object의 Size는 24 bytes 이며, 내부에 `new byte[addedByte];` 으로 생성한 1 byte 가 확인된다.



여기까지의 내용으로는 모든 Object의 Size를 추적하여, 실제 Session data size를 확인할 수 있을 것 같았지만 난해하였고,

ClassLayout은 조사하는 Object 자체만의 Shallow Size를 보여준다.





## 3.7 Retained Size of ArrayList

GraphLayout을 이용하면, 첫 진입점부터 닿을 수 있는 Deep 한 곳까지의 모든 Size를 조사할 수 있다고 한다.

ClassLayout을 이용하면 Accurate Size를 얻을 수 없다.



`System.out.println(GraphLayout.parseInstance(sList).toPrintable());` 호출 시

```
java.util.ArrayList@4513a2d0d object externals:
          ADDRESS       SIZE TYPE                PATH                           VALUE
        7d56522c0         24 java.util.ArrayList                                (object)
        7d56522d8         24 [B                  .elementData[0]                [0]
        7d56522f0       4520 (something else)    (somewhere else)               (something else)
        7d5653498       2216 [Ljava.lang.Object; .elementData                   [[0], [0], ... more 400+
```

어디까지 닿았는지 모를 something else (4520 size) 외에 ArrayList (2216 size)가 확인된다.

최소한 App에서 생성한 Session data size는 2216 bytes 이상이 아닐까?



우리가 Session에 넣은 Object가 아니라 Session 자체를 조사하면 어떻게 되나?





## 3.8 Retained Size of HttpSession

`System.out.println(GraphLayout.parseInstance(session).toPrintable());` 호출 시

OOME 으로 죽었다.



`System.out.println(GraphLayout.parseInstance(session).totalSize());` 호출 시

92958432 , 즉 88 Mbytes 로 확인된다.



1 User가 생성한 1 Session의 순수 크기를 알고 싶지만, Retained 는 연결된 모든 Object를 추적하여서 그런지, 매우 큰 MB Size가 나왔다.

이 어플리케이션의 ArrayList를 걷어내고, 좀 더 단순한 구조에서 확인해보는 테스트가 필요해보인다.



그리하여, 다음과 같이 My App을 수정하였다.

```java
import javax.servlet.http.*;
import javax.servlet.annotation.WebServlet;

import javax.servlet.ServletException;
import java.io.IOException;

import org.openjdk.jol.info.ClassLayout;
import org.openjdk.jol.info.GraphLayout;
import org.openjdk.jol.vm.VM;

@WebServlet("/SessionServlet")
public class SessionServlet extends HttpServlet {
  protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
  
    HttpSession session = request.getSession(true);
    byte[] byteSession = (byte[]) session.getAttribute("byteSession");
    byte[] _obj = new byte[500];
    byte[] _tmp = null;
  
    if (byteSession == null){
      session.setAttribute("byteSession", _obj);
      byteSession = (byte[]) session.getAttribute("byteSession");
    }
    else{
      _tmp = new byte[_obj.length + byteSession.length];
      System.arraycopy(_obj, 0, _tmp, 0, _obj.length);
      System.arraycopy(byteSession, 0, _tmp, _obj.length, byteSession.length);
      session.setAttribute("byteSession", _tmp);
      byteSession = (byte[]) session.getAttribute("byteSession");
    }

    String log = "";
    String et = "\n\r";
    if(_obj!=null){
      log += "_obj.length = " + _obj.length + et;
      log += "ObjectSizeAgent.getObjectSize(_obj) = " + ObjectSizeAgent.getObjectSize(_obj) + et;
    }
    
    if(_tmp!=null){
      log += "_tmp.length = " + _tmp.length + et;
      log += "ObjectSizeAgent.getObjectSize(_tmp) = " + ObjectSizeAgent.getObjectSize(_tmp) + et;
    }

    if(byteSession!=null){
      log += "byteSession.length = " + ((byteSession!=null) ? byteSession.length + et : "" + et);
      log += "ObjectSizeAgent.getObjectSize(byteSession) = " + ObjectSizeAgent.getObjectSize(byteSession) + et;
    }
    
    log += "ObjectSizeAgent.getObjectSize(session) = " + ObjectSizeAgent.getObjectSize(session) + et;
    System.out.println(log+et);
    
    final long  MEGABYTE = 1024L * 1024L;
    long heapSize = Runtime.getRuntime().totalMemory() / MEGABYTE;
    long heapMaxSize = Runtime.getRuntime().maxMemory() / MEGABYTE;
    long heapFreeSize = Runtime.getRuntime().freeMemory() / MEGABYTE;

    log = "";
    log += "heapSize (MB) = " + heapSize + et;
    log += "heapMaxSize (MB) = " + heapMaxSize + et;
    log += "heapSize (MB) = " + heapFreeSize + et;
    System.out.println(log);
    
    // _obj
    System.out.println("--- Layout : _obj ---");
    System.out.println(ClassLayout.parseInstance(_obj).toPrintable());
    System.out.println(GraphLayout.parseInstance(_obj).totalSize());
    System.out.println(et);
    
    // _tmp
    if (_tmp != null){
      System.out.println("--- Layout : _tmp ---");
      System.out.println(ClassLayout.parseInstance(_tmp).toPrintable());
      System.out.println(GraphLayout.parseInstance(_tmp).totalSize());
      System.out.println(et);
    }
    
    // byteSession
    System.out.println("--- Layout : byteSession ---");
    System.out.println(ClassLayout.parseInstance(byteSession).toPrintable());
    System.out.println(GraphLayout.parseInstance(byteSession).totalSize());
    System.out.println(et);
  }
}
```



ArrayList 등을 걷어내고, 순수 Byte Array 로만 Session에 'byteSession' Key 의 Value 로 값을 저장한다.





## 3.9 Shallow Size of Byte Array

반복 호출 시마다 Session에 `byte[] _obj = new byte[500];` 만큼의 Data를 증분시킨다.

`_obj` 자체의 Shallow/Retained Size는 다음의 Java code 로 알 수 있다.

```java
    // _obj
    System.out.println("--- Layout : _obj ---");
    System.out.println("Shallow : " + ClassLayout.parseInstance(_obj).toPrintable());
    System.out.println("Retained : " + GraphLayout.parseInstance(_obj).totalSize());
    System.out.println(et);
```



> `_obj` 자체의 입장에서는, 더 이상 닿을 곳이 없는 root 그 자체이기 때문에 `520 bytes` 로 항상 동일하게 측정된다.



```
--- Layout : _obj ---
Shallow : [B object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x0000000000000001 (non-biasable; age: 0)
  8   4        (object header: class)    0x000007a8
 12   4        (array length)            500
 16 500   byte [B.<elements>             N/A
516   4        (object alignment gap)
Instance size: 520 bytes
Space losses: 0 bytes internal + 4 bytes external = 4 bytes total

Retained : 520
```



캡슐화를 위한 header(8+4=12 bytes)

_obj 배열 크기 Data 4 bytes

_obj 배열 Data 자체 500 bytes

그리고 **ObjectAlignmentInBytes** , Data 정렬을 위한 gap 으로 4 bytes 가 추가되어

_obj 객체 자체의 총크기는 520 bytes 가 된다.





## 3.10 What is ObjectAlignmentInBytes?

여기서 잠깐, **ObjectAlignmentInBytes** 를 살펴보면,

JVM에서는 Data를 Heap 에 저장할 때, 8 ~ 256 bytes 의 단위의 gap 을 유지하며 저장한다.

현재 나의 해당 설정값은, 8 bytes 이다.

```sh
$ java -XX:+PrintFlagsFinal | grep "ObjectAlignmentInBytes"
     intx ObjectAlignmentInBytes                    = 8                                   {lp64_product}
```



Heap Memory에 Data가 올라갈 때, 8의 배수를 유지하도록 한다는 것이다.

이 값이, 더 커질 경우 어떤 장/단점이 있는지는 구글링 자료에 많으나 이해가 되지 않았다.



가령 위에서 살펴본 _obj Object 의 Size는 header + length + Data = 12 + 4 + 500 = 516 bytes 이다.

Heap 에 저장될 때, 8 bytes 의 배수 단위로 Data의 정렬이 이루어져야 하므로,

`8 X 65 = 520 bytes` , 8의 65 배수로 Data가 정렬이 되어야 한다.

그리하여, **Data 정렬을 위한 gap 으로 4 bytes 를 마저 추가**한 것이다.





## 3.11 Shallow Size of byteSession

App에서 생성(_obj) 하여 Session에 집어넣을 때, byteSession (Session에 저장된 byte Array) 의 크기를 추적해본다.

추적 code는 다음과 같다.

```java
    // byteSession
    System.out.println("--- Layout : byteSession ---");
    System.out.println("Shallow : " + ClassLayout.parseInstance(byteSession).toPrintable());
    System.out.println("Retained : " + GraphLayout.parseInstance(byteSession).totalSize());
    System.out.println(et);
```



1회 호출 시에는, _obj Data와 다르지 않다.

```
--- Layout : byteSession ---
Shallow : [B object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x00000067e900d701 (hash: 0x67e900d7; age: 0)
  8   4        (object header: class)    0x000007a8
 12   4        (array length)            500
 16 500   byte [B.<elements>             N/A
516   4        (object alignment gap)
Instance size: 520 bytes
Space losses: 0 bytes internal + 4 bytes external = 4 bytes total

Retained : 520
```



2회 연속 호출 시에는,

```
--- Layout : _tmp ---
Shallow : [B object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x0000000000000001 (non-biasable; age: 0)
  8   4        (object header: class)    0x000007a8
 12   4        (array length)            1000
 16 1000   byte [B.<elements>             N/A
Instance size: 1016 bytes
Space losses: 0 bytes internal + 0 bytes external = 0 bytes total

Retained : 1016
```

`8 X 127 = 1016 Bytes`, 8의 127 배수로 정렬이 완료되므로 추가 Gap data가 없다.



3회 연속 호출 시에는,

```
--- Layout : byteSession ---
Shallow : [B object internals:
OFF  SZ   TYPE DESCRIPTION               VALUE
  0   8        (object header: mark)     0x00000036a33af901 (hash: 0x36a33af9; age: 0)
  8   4        (object header: class)    0x000007a8
 12   4        (array length)            1500
 16 1500   byte [B.<elements>             N/A
1516   4        (object alignment gap)
Instance size: 1520 bytes
Space losses: 0 bytes internal + 4 bytes external = 4 bytes total

Retained : 1520
```

다시금 4 bytes Gap 이 추가되었다.





# 4. Outcome

JOL Library 를 사용하여, 특정 또는 Class 자체가 JVM Heap Memory에 차지하는 실제 Size를 추적할 수 있음을 확인했다.

또한, Object Alignment Gap 에 대해서 알 수 있었다.





# 5. References

https://www.baeldung.com/jvm-measuring-object-sizes

https://github.com/openjdk/jol

[ObjectAlignmentInBytes](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/java.html)
