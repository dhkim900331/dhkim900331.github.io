---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] Cluster�� Session Replication"
tags: [Middleware, WebLogic, Cluster, Session, Replication]
typora-root-url: ..
---


# 1. ����

WebLogic Cluster �� Session ���� ������ �˾ƺ���.



# 2. Session Replication ���

- ����ڰ� was1���� ���� ��, �̸� Primary Server�� �ϸ� Session�� ����.
- Primary Server�� ������ Session Backup�� Secondary Server�� ����.
- Secondary Server�� ���� Cluster�� Member�� Random�ϰ� �ϳ��� ����.
  - ���� ��������, ������ �ִ� (���������� ����). �Ʒ� �׸�.

- Primary Server�� shutdown �Ǵ���, Secondary Server�� backup ���� ����. -> Failover



# 3. Session Replication ����

Session ������ HttpSession.setAttribute() method���� �����.

��, ������� Request�� �ִٰ� Session Trigger(������ �ǹ̷� Session�� ��ȿ����)���� Page ���ΰ�ħ(F5)������ �߻��ϴ� ���� �ƴ϶� �ش� Page�� setAttribute()�� �־�� ��.



Primary Server�� shutdown�� �Ǵ���, Secondary Server�� backup Session�� ����������,

���̻� ������� Request�� ���� setAttribute()�� ȣ������ ������, �ش� Session�� Secondary Server���� �������� Primary Server�� ���� ��Ȳ�� �߻�.



����, ���� ǥ�� Cluster �� Member�� �� Session ���� �켱 ����.

![SessionReplication_1](/../assets/posts/images/01-WebLogic/SessionReplication/SessionReplication_1.png)



1���� - �ٸ� �ӽ�, ���� �׷�

2���� - ���� �ӽ�, ���� �׷�

3���� - ���� �ӽ�, �ٸ� �׷�

4���� - �ٸ� �ӽ�, �ٸ� �׷�



�ӽ��� ����ȭ ��� �ǹ�. �׷��� Console - Servers - <instance> - Configuration - Cluster���� Replication Group���� �����Ѵ�. ���, ������ �ý��� �Ǵ� Ư���� �䱸������ ���ٸ� �Ϲ������� �Ű澲�� �ʴ´�.



# 4. Instance Shutdown �ÿ� Primary�� Secondary Session �̵�

m1�� Primary 2, Secondary 1

m2�� Primary 1, Secondary 2

![SessionReplication_2](/../assets/posts/images/01-WebLogic/SessionReplication/SessionReplication_2.png)





m2 instance�� shutdown �ÿ�,

m1�� Secondary�� m1�� Primary�� �̵��Ѵ�.

![SessionReplication_3](/../assets/posts/images/01-WebLogic/SessionReplication/SessionReplication_3.png)





# 5. ���ÿ��� Replication Group �׽�Ʈ

�׽�Ʈ ���� : Ŭ�����͸� ������ Primary, Secondary ������ �������� �׽�Ʈ.

ȯ�� : Machine1�� Machine2 �� ���������� ������ �ٸ���.

Machine1 ���� �ν��Ͻ� M1, M2 �� ���� �����,

Machine2 ���� �ν��Ͻ� M3, M4 �� ���� �����.



M1, M2, M3, M4 �� Clustering �Ǿ���.



===== WLS =========================



AdminServer - 172.16.0.101



---- Clustering ----

Machine1 (M1, M2) - 172.16.0.101

Machine2 (M3, M4) - 172.16.0.99

\--------------------

===================================



������ �⺻ �˰��� ���ϸ�, ������ ���� Ŭ�����͸� ������ ������.

M1 - M3

M2 - M4

M3 - M1

M4 - M2

\* �⵿ ������ ���� �ణ�� ���̴� ������, ��ü�� ����ǥ�� ���յ�.





Replication Group�� �Ʒ��� ����,

M1 (Replication Group : M1) , (Preferred Secondary Group : M2)

M2 (Replication Group : M2) , (Preferred Secondary Group : M1)

M3 (Replication Group : M3) , (Preferred Secondary Group : M4)

M4 (Replication Group : M4) , (Preferred Secondary Group : M3)

�ְ� �Ǹ�



M1 - M2

M2 - M1

M3 - M4

M4 - M3

�� ���� ������ ������ �ȴ�.

����ǥ �����ϰ�, ���� ��ȣ���� ���� ����.

�ٸ�, ���� �⵿�Ͽ��� ��ȣ�ϴ� �׷����� ������ �����ϴ�.

\* Replication Group : ���� �׷��

\* Preferred Secondary Group : ��ȣ�ϴ� �����帮 �ν��Ͻ��� �׷��



# 6. ���ÿ��� Replication Group �׽�Ʈ - #2

�� �׽�Ʈ����, Replication Group, Preferred Group �� �����Ͽ���

�⵿ ������ ����, ������ �ʴ� ������ �ξ����� �� �˾Ҵµ�..



�⵿ �� ������ ���ǿ� ���յǵ��� Ŭ������ ������ ������ �ϰ� �ִ�.



���� ������ ���Ǵ�ζ��,

M1 - M2

M2 - M1

M3 - M4

M4 - M3 ���� Ŭ������ Primary/Secondary ������ �Ǿ�� �ϴµ�

�� �⵿������ �����Ͽ� ������ ���� ���ǿ� ���� �ʰ� �ٰ� �Ͽ���.



�׸�1. M1 , M3 �ν��Ͻ��� �⵿�Ͽ� ���� ���� Ŭ�����͸�

![SessionReplication_4](/../assets/posts/images/01-WebLogic/SessionReplication/SessionReplication_4.png)





�׸�2. M2 �ν��Ͻ��� �߰� �⵿�Ͽ�����, Ŭ������ ���� ������

![SessionReplication_5](/../assets/posts/images/01-WebLogic/SessionReplication/SessionReplication_5.png)





�׸�3. M4 �ν��Ͻ��� �߰� �⵿�Ͽ�����, Ŭ������ ���� ������

![SessionReplication_6](/../assets/posts/images/01-WebLogic/SessionReplication/SessionReplication_6.png)





Ŭ������ ������ �������Ǹ�, ������ �̵��ȴ�.

����� ���ſ� �ý��ۿ����� �̷��� ������ ���¿� ���ϰ� �߻��� �� ������..

���� ������ ����Ŭ �������� ã�� ���ߴ�.

