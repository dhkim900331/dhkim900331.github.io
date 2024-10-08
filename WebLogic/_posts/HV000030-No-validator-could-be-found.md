---
layout: post
title: "[WebLogic/Hibernate] HV000030 No validator could be found for constraint 'javax.validation.constraints.Email'"
tags: [Middleware, WebLogic, Hibernate, JSR]
typora-root-url: ..
---

# 1. Overview
WebLogic 12cR2 에 배포된 App이 Hibernate 사용 시 Exceptio이 발생하였다.
```
javax.validation.unexpectedTypeException: HV000030: No validator could be found for constraint ‘javax.validation.constraints.Email’ validating type ‘javax.lang.String’. Check configuration for ‘email’
 at org.hibernate.validator.internal.engine.Constraintvalidation.ConstraintTree.throwExceptionForNullValidator(ConstraintTree.java)
```


# 2. Descriptions
`-verbose:class` 로 추적해보면 Bean Validation 사용 시 App의 jakarta.validation-api-2.0.2.jar와 WebLogic의 hibernate.validator.jar에서 각각 필요한 Validation Class들이 Loaded 된다.

WebLogic 12cR2 에는 wlserver/modules/hibernate.validator.jar Hibenate library가 위치하며, 12.2.1.4 Release 기준으로 다음의 MF를 갖는다.
```
:META-INF/MANIFEST.MF
  Bundle-SymbolicName: org.hibernate.validator
  Implementation-Version: 5.2.5.Final
  Implementation-Vendor-Id: org.hibernate
  Bundle-Name: Hibernate Validator Engine
  Bundle-Version: 5.2.5.Final
  Build-Jdk: 1.8.0_121
```

[Hibernate Validator 5.X Release](https://hibernate.org/validator/releases/5.2/)는 다음의 환경에서 호환된다.
 - J2EE 6,7 or 8
 - Bean Validation 1.1
 
[Hibernate Validator 6.X Release](https://hibernate.org/validator/releases/6.2/)는 다음의 환경에서 호환된다.
 - Java 8,11 or 17
 - J2EE 8
 - Bean Validation 2.0
 
WebLogic 12cR2는 [J2EE 7 Support](https://docs.oracle.com/middleware/1221/wls/NOTES/whatsnew.htm#A1011612131)를 하므로, Hibernate Validator 5.X Release가 적절하게 포함되어 있다.
 
 
그러나 `App/WEB-INF/lib/jakarta.validation-api-2.0.2.jar`는 Bean Validation 2.0 의 Interface와 Annotation만을 명세한 JSR 380 파일이다.
Bean Validation 2.0의 실제 구현을 위해서는 Hibernate Validator 6.X Release를 사용 해야 한다. (위에서 언급한 호환성 정보)


JSR 303, 349, 380을 다음과 같이 간단하게 정리할 수 있다.
 - Application에서 데이터 검증을 위한 JSR(Java Specification Request)
 - JSR 303: Bean Validation 1.0 을 정의한 명세, Java 객체의 속성에 제약 조건을 정의하고, 그 조건을 검증하는 표준을 제공
 - JSR 349: Bean Validation 1.1 명세서로, JSR 303의 확장판. 추가 기능 및 개선 사항을 포함
 - JSR 380: Bean Validation 2.0 명세서, Java EE 8에서 지원되며, 더 많은 기능과 Java 8에서 추가된 기능을 활용할 수 있도록 개선

위 명세를 구현하기 위한 실제 구현(implementation)이 Hibernate Team이 만든 Hibernate Validator
 - Hibernate Validator
 - Hibernate Team에서 JSR 303,349,380 설계에 따른 실제 구현을 개발
 - Hibernate Validator 6.X 부터 JSR 380. 즉 Bean Validation 2.0 의 구현체를 사용해야 한다.


App에 포함된 jakarta.validation-api-2.0.2.jar와 Weblogic에 포함된 hibernate.validator.jar가 서로 호환되지 않고 있으며,
JSR-380의 최신 Bean Validation 기능을 사용하기 위해서 App에 Hibernate Validator 6.X Release를 포함시키고 다음의 weblogic.xml 설정을 통해 사용토록 해야 한다.

```xml
 <container-descriptor>
      <prefer-application-packages>  
       <!-- Bean Validation 2.0 사용을 위함 -->
       <package-name>javax.validation.*</package-name>  
       
       <!-- Hibernate Validatior 6.X 사용을 위함 -->
       <package-name>org.hibernate.validator.*</package-name>  
   </prefer-application-packages>
 </container-descriptor>
```


# 3. References
After Applying Patch 33699205 Application Fails with Message "HV000030: No validator could be found for constraint javax.validation.constraints.NotEmpty" (Doc ID 2883321.1)
Bean Validation 사용 시 Exception "HV000030: No validator could be found for constraint javax.validation.constraints.Email" (Doc ID 3048836.1)	
