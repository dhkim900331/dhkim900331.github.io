---
date: 2023-11-23 16:29:01 +0900
layout: post
title: "[WebLogic/JDBC] Why Doest It Show Different JDBC Driver Version?"
tags: [Middleware, WebLogic, JDBC, Driver]
typora-root-url: ..
---

# 1. Overview
JDBC Driver version을 확인하기 위해, ojdbc 파일을 압축해제 하여 직접 확인하거나,

`-getversion` 명령어 등으로 확인할 수 있다.

이 Driver version을 확인하는데, 상황에 따라 다른 version이 표시되면 왜 그런지 추적해보자.


<br><br>


# 2. Descriptions
## 2.1 일반적인 Driver version 확인 방법

일반적으로 다음의 명령어를 통해 표시된다.

```bash
java -jar ojdbc6.jar
또는
java -jar ojdbc6.jar -getversion
```


결과는 아래와 같다.

```bash
$ /sw/jdk/jdk1.8.0_381/bin/java -jar ojdbc6.jar
Oracle 11.2.0.4.0 JDBC 4.0 compiled with JDK6 on Thu_Jul_03_18:17:32_PDT_2014
```


혹은 ojdbc6.jar 를 Decompile(jd-gui 등을 활용)하면 `oracle.jdbc.OracleDatabaseMetaData.class`에 Hard coding 된 값을 확인할 수 있다. 

```java
package oracle.jdbc;
  ...
public class OracleDatabaseMetaData implements AdditionalDatabaseMetaData {
  private static String DRIVER_NAME = "Oracle JDBC driver";
  
  private static String DRIVER_VERSION = "11.2.0.4.0";
  
  private static int DRIVER_MAJOR_VERSION = 11;
  
  private static int DRIVER_MINOR_VERSION = 2;
  ...
```


즉, 이 value를 단순히 출력하는 것이다.

Hard coding 되어 있으므로 상황에 따라 다른 version을 보여주어서는 안된다.


<br><br>


## 2.2 다른 Driver version이 확인 되는 경우

JDK 1.8.0_381 Version으로 확인 결과와, JDK 1.7.0_80 Version으로 ojdbc6.jar 의 Driver version 확인 결과가 아래와 같이 보여진다.

```bash
$ /sw/jdk/jdk1.7.0_80/bin/java -jar ojdbc6.jar
Oracle 11.2.0.1.0 JDBC 4.0 compiled with JDK6

$ /sw/jdk/jdk1.8.0_381/bin/java -jar ojdbc6.jar
Oracle 11.2.0.4.0 JDBC 4.0 compiled with JDK6 on Thu_Jul_03_18:17:32_PDT_2014
```


동일한 ojdbc6.jar 가 각각 `11.2.0.1.0` 과 `11.2.0.4.0` 으로 확인된다.

앞서 살펴봤듯이, version은 hard coding 되어 있기 때문에 어떤 환경에서든 다른 version이 확인 되면 안된다.

<br>

보통 이러한 경우에는, 한가지 짐작할 수 있는 것이 다른 ojdbcX.jar 가 이미 사전에 CLASSPATH 삽입되어 있는 경우다.

검증을 하기 위해 `-verbose:class` 옵션으로 추적을 하기 위해 다음을 실행한다.

```bash
$ /sw/jdk/jdk1.7.0_80/bin/java -verbose:class -jar ojdbc6.jar > jdk1.7_verbose_class.txt
$ /sw/jdk/jdk1.8.0_381/bin/java -verbose:class -jar ojdbc6.jar > jdk1.8_verbose_class.txt
```


두 txt 파일에서 ojdbc jar가 load 된 것을 확인해본다.

jdk1.8_verbose_class.txt 파일에서는 다음처럼 특이점이 없다.

```bash
$ grep -i "ojdbc" jdk1.8_verbose_class.txt
[Loaded oracle.jdbc.driver.OracleDriver from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.OracleDriver from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.OracleDriverExtension from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.OracleDriver$1 from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.ClassRef from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.ClassRef$XMLTypeClassRef from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.ClassRef$Locale from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.ClassRef$LocaleCategoryClassRef from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.DiagnosabilityMXBean from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.OracleDiagnosabilityMBean from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.DatabaseError from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.OracleSQLException from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.SQLStateMapping from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.SQLStateMapping$Tokenizer from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.Message from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.Message11 from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.OracleConnection from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.internal.OracleConnection from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.internal.ClientDataSupport from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.OracleConnectionWrapper from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.OracleConnection from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.PhysicalConnection from file:/tmp/ojdbc6.jar]
[Loaded oracle.jdbc.driver.BuildInfo from file:/tmp/ojdbc6.jar]
```


jdk1.7_verbose_class.txt 파일에서는 Extension 클래스로더 디렉토리에 예전에 백업해둔 Driver가 있었다.

```bash
$ grep -i "ojdbc" jdk1.7_verbose_class.txt
[Loaded oracle.jdbc.driver.OracleDriver from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.OracleDriver from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.OracleDriverExtension from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.OracleDriver$1 from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.ClassRef from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.DiagnosabilityMXBean from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.OracleDiagnosabilityMBean from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.DatabaseError from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.OracleSQLException from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.net.ns.NetException from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.SQLStateMapping from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.SQLStateMapping$Tokenizer from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.Message from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.driver.Message11 from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.internal.ObjectDataFactory from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.sql.ORADataFactory from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.sql.AnyDataFactory from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.jdbc.internal.ObjectData from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.sql.ORAData from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
[Loaded oracle.sql.TypeDescriptorFactory from file:/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak]
```


`/sw/jdk/jdk1.7.0_80/jre/lib/ext/ojdbc6.jar.bak` 파일을 확인해보니 `Oracle 11.2.0.1.0` version으로 확인된다.

Extension 클래스로더 부터 class를 찾게 되어 다른 환경(서로 다른 JDK Version)에서 다른 Driver version이 출력된 것처럼 보여진 것이다.


<br><br>


# 3. References

**Why Does It Show Different JDBC Driver Version? (Doc ID 2988932.1)**
