---
date: 2022-11-23 14:45:02 +0900
layout: post
title: "[WebLogic/J2EE] How to configure Cluster Weight - EJB"
tags: [Middleware, WebLogic, J2EE, EJB, Cluster, Weight, RMI, LoadBalancing]
typora-root-url: ..
---

# 1. 개요

Sample EJB App을 배포하여, Cluster Weight 기능을 테스트한다.

여기서 소개하는 EJB App의 Java Source Code나 Deployment Descriptor XML File의 내용은 올바르지 않을 수 있다.
{{ site.content.br_big }}
# 2. 요구 사항

* 다음의 환경에서 진행하였다.
  * Red Hat Enterprise Linux release 8.7
  * Oracle WebLogic Server 14c
  * Oracle JDK 1.8.0_351
  {{ site.content.br_big }}
### 2.1 WebLogic

* 다음의 3개 Instance를 구성하고, 일부만 Clustering 설정한다.

![EJB-ClusterWeight_1](/../assets/posts/images/WebLogic/EJB-ClusterWeight/EJB-ClusterWeight_1.png)

> 각 Instance는 Enable Tunneling 되었다. (중요하지 않아 보임)




* base_cluster 내의 Instance는 각각 `Configuration - Cluster - Cluster Weight` 설정값을 `50`과 `100` 으로 적용하였다.
{{ site.content.br_small }}
* `base_cluster - Configuration - Default Load Algorithm` 을 `weight-based` 설정
{{ site.content.br_small }}
* `2.2 EJB Application`의

  * `clientSide` 를 `M1` 에 배포한다.
  * `serverSide` 를 `base_cluster` 에 배포한다.

![EJB-ClusterWeight_2](/../assets/posts/images/WebLogic/EJB-ClusterWeight/EJB-ClusterWeight_2.png)


## 2.2 EJB Application

### 2.2.1 serverSide

serverSide EJB App은 Business Logic (`ejbHome.getMsg()`)이 구현되어 있다.
{{ site.content.br_small }}

* 다음의 EJB App을 준비한다.

```bash
$ tree serverSide/
serverSide/
├── index.jsp
├── META-INF
└── WEB-INF
    ├── classes
    │   └── serverSide
    │       ├── ejbHome.class
    │       └── ejbRemote.class
    ├── src
    │   └── serverSide
    │       ├── ejbHome.java
    │       └── ejbRemote.java
    ├── weblogic-ejb-jar.xml
    ├── weblogic.xml
    └── web.xml

6 directories, 8 files
```
{{ site.content.br_small }}
* serverSide/index.jsp

```jsp
<%@ page import="javax.ejb.EJB" %>
<%@ page import="javax.naming.*" %>
<%@ page import="java.util.*" %>
<%@ page import="serverSide.*" %>
<%

  Hashtable ht = new Hashtable();
  ht.put(Context.INITIAL_CONTEXT_FACTORY, "weblogic.jndi.WLInitialContextFactory");
  ht.put(Context.PROVIDER_URL, "http://wls.local:8003");

  try {
        Context ctx = new InitialContext(ht);
        ejbRemote eRemote;
        for (int i=0; i<10; i++){
                eRemote = (ejbRemote)ctx.lookup("java:global.serverSide.ejbHome!serverSide.ejbRemote");
                out.println(i + " : ");
                out.println(eRemote.getMsg());
                out.println("<br>");
        }
  } catch (Exception e) {
    out.println(e.toString());
  }
%>
```

> index.jsp는 clientSide를 통해 호출할 것이고, 미리 여기서 만들었을 뿐이다.
>
> 물론 serverSide 의 index.jsp 를 호출해도 동작한다.


* WEB-INF/src/serverSide/ejbHome.java

```java
package serverSide;

import javax.ejb.Stateless;
import javax.ejb.Remote;

@Stateless(name = "ejbHome", mappedName = "ejbHome")
@Remote(serverSide.ejbRemote.class)
public class ejbHome implements ejbRemote {
    public ejbHome(){}
    public String getMsg(){ return "Hello EJB"; }
}
```
{{ site.content.br_small }}
* WEB-INF/src/serverSide/ejbRemote.java

```java
package serverSide;

public interface ejbRemote {
    String getMsg();
}
```
{{ site.content.br_small }}
* Java Compile Tip

```bash
. ./setDomainEnv.sh
javac -d ./classes ./src/serverSide/*java
```
{{ site.content.br_small }}
* WEB-INF/web.xml

```xml
<web-app>
</web-app>
```
{{ site.content.br_small }}
* WEB-INF/weblogic.xml

```xml
<weblogic-web-app>
	<container-descriptor>
		<servlet-reload-check-secs>1</servlet-reload-check-secs>
		<resource-reload-check-secs>1</resource-reload-check-secs>
	</container-descriptor>
	
	<jsp-descriptor>
		<page-check-seconds>1</page-check-seconds>
	</jsp-descriptor>
</weblogic-web-app>
```

> 개인적으로 이번 테스트시에 사용한 설정일 뿐이다.
{{ site.content.br_small }}
* WEB-INF/weblogic-ejb-jar.xml

```xml
<weblogic-ejb-jar>
    <weblogic-enterprise-bean>
                <ejb-name>serverSide_ejb</ejb-name>


                <stateless-session-descriptor>
                        <stateless-clustering>
                                <!--
                                <home-is-clusterable>false</home-is-clusterable>
                                <stateless-bean-is-clusterable>false</stateless-bean-is-clusterable>
                                <stateless-bean-load-algorithm>random</stateless-bean-load-algorithm>
                                -->
                        </stateless-clustering>
                </stateless-session-descriptor>


    </weblogic-enterprise-bean>
</weblogic-ejb-jar>
```

> 주석을 하더라도 동작하는 부분은 아직 이해하지 못했다.
{{ site.content.br_small }}

### 2.2.2 clientSide

clientSide는 serverSide를 복제하여 준비하면 된다.

아래에서 차이점을 살펴보면, serverSide 에 있던 Business Logic class (`ejbHome.class`) 이없다.

clientSide App은 EJB App이 아니다.

interface class (ejbRemote.class) 만 가지고 있다.

EJB의 특징이 여기서 드러나는데, 외부의 client가 server의 Business Logic 을 interface를 이용해 Remote 접근할 수 있다.
{{ site.content.br_small }}
> index.jsp 가 serverSide에 있지만, 중요하지 않다.


* 다음의 EJB App을 준비한다.

```bash
$ cp -pR serverSide clientSide
```
{{ site.content.br_small }}
* 정말, 기본 기능(File)만 있어도 serverSide 의 Business Logic 실행이 가능한지 확인해보기 위해 과감히 삭제한다.

```bash
$ rm clientSide/WEB-INF/classes/serverSide/ejbHome.class
$ rm clientSide/WEB-INF/src/serverSide/ejbHome.java
$ rm clientSide/WEB-INF/weblogic-ejb-jar.xml
$ rm clientSide/WEB-INF/weblogic.xml
```
{{ site.content.br_big }}
# 3. Application 수행 및 설명

clientSide는 `M1`에 serverSide는 `base_cluster(M2, M3)` 에 배포되어 있다.
{{ site.content.br_small }}
`http://M1/clientSide/index.jsp` 을 호출하면, `M2 (8003)` 을

JNDI Lookup Access Point로 요청을 수행한다.
{{ site.content.br_small }}
`java:global.serverSide.ejbHome!serverSide.ejbRemote` 을 Lookup 하여

`base_cluster (M2, M3)` 에 배포된 serverSide EJB Remote Object를 조회한다.
{{ site.content.br_small }}
위 Global Name은 `<Instance> - Configuration - General - View JNDI Tree` 에서 확인할 수 있다.

![EJB-ClusterWeight_3](/../assets/posts/images/WebLogic/EJB-ClusterWeight/EJB-ClusterWeight_3.png)

조회 시에, `base_cluster` 에 설정한 `weight-base` Algorithm 에 따라 동작한다.
{{ site.content.br_small }}
`index.jsp` 는 한번에 10번의 lookup을 의도적으로 수행한다.
{{ site.content.br_small }}
다음의 통계 화면에서 결과를 확인할 수 있으며, 초기 요청시에는 분산 가중치가 엇비슷 할 수 있다.

![EJB-ClusterWeight_4](/../assets/posts/images/WebLogic/EJB-ClusterWeight/EJB-ClusterWeight_4.png)

# 4. Trouble Shooting

## 4.1 Naming Service

JNDI 호출이 잘 되지 않는 경우에는, 정확한 Naming을 확인해야 하는데, View JNDI Tree 를 참조하여 해결이 되었다.
{{ site.content.br_small }}
여기서는 **Global Naming Lookup**을 해야 Cluster Load Balancing이 적용되었다.

![EJB-ClusterWeight_5](/../assets/posts/images/WebLogic/EJB-ClusterWeight/EJB-ClusterWeight_5.png)


{{ site.content.br_big }}

## 4.2 Cluster Default Load Algorithm

\<Instance> 의 Cluster Weight 값 외에도 Cluster의 Default Load Algorithm 기본값을 round-robin에서 weight-based 으로 변경해야 된다.

이 부분은, 당연한 말이지만 메뉴얼 숙지를 하지 못한 탓에 놓친 부분이였다.
