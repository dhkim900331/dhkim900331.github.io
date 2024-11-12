---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] Encryption/Decryption (암/복호화)"
tags: [Middleware, WebLogic, Encrypt, Decrypt, Password]
typora-root-url: ..
---


# 1. Overview

Encryption/Decryption (암/복호화)


<br><br>


# 2. Encryption

WebLogic 8 ~ 12cR2 사용 가능

```sh
[weblogic@was base_domain]$ . ./bin/setDomainEnv.sh
[weblogic@was base_domain]$ java weblogic.security.Encrypt string
{AES256}WSq0iT981CeH2J+qbftpo0NN+IAT9689J+pk/Ecj5mw=
```

string 이라는 plain text는 {AES256}WSq0iT981CeH2J+qbftpo0NN+IAT9689J+pk/Ecj5mw= 으로 암호화됨


<br><br>


# 3. Decryption

## 2.1 WebLogic WLST 패키지 있는 경우

```py
# decrypt.py 파일 내용
import weblogic.security.internal as int

def decrypt(domainPath, encryptedPwd):
es = int.SerializedSystemIni.getEncryptionService(domainPath)
ces = int.encryption.ClearOrEncryptedService(es)
clear = ces.decrypt(encryptedPwd)
print encryptedPwd + " -> " + clear

decrypt(sys.argv[1], sys.argv[2])
```

<br>

```sh
[weblogic@was base_domain]$ . ./bin/setDomainEnv.sh
[weblogic@was base_domain]$ java weblogic.WLST decrypt.py $DOMAIN_HOME {AES256}WSq0iT981CeH2J+qbftpo0NN+IAT9689J+pk/Ecj5mw=

Initializing WebLogic Scripting Tool (WLST) ...

Welcome to WebLogic Server Administration Scripting Shell

Type help() for help on available commands

{AES256}WSq0iT981CeH2J+qbftpo0NN+IAT9689J+pk/Ecj5mw= -> string
```

<br>


### 2.2 그 외(Pure Java)

```java
# decrypt.java 파일 내용
    import weblogic.security.internal.SerializedSystemIni;
import weblogic.security.internal.encryption.ClearOrEncryptedService;
import weblogic.security.internal.encryption.EncryptionService;

public class decrypt{
  public static void main(String[] args) {
    EncryptionService es = SerializedSystemIni.getEncryptionService(args[0]);
    ClearOrEncryptedService ces = new ClearOrEncryptedService(es);
    String clear = ces.decrypt(args[1]);
    System.out.println(args[1] + " -> " + clear);
  }
}
```

<br>

```sh
[weblogic@was base_domain]$ . ./bin/setDomainEnv.sh
[weblogic@was base_domain]$ javac decrypt.java
[weblogic@was base_domain]$ java decrypt $DOMAIN_HOME {AES256}WSq0iT981CeH2J+qbftpo0NN+IAT9689J+pk/Ecj5mw=
{AES256}WSq0iT981CeH2J+qbftpo0NN+IAT9689J+pk/Ecj5mw= -> string
```

