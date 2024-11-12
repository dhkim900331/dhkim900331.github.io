---
date: 2022-02-15 12:26:08 +0900
layout: post
title: "[RHCSA/LVM] LVM 생성"
tags: [Linux, RHCSA, LVM]
---

# 1. Overview

물리 디스크를 쓸 수 있게 포맷하고 마운트를 하는 방법을

- [[RHCSA] Storage 파티셔닝]({{ site.url }}/rhcsa/StoragePartitioning)
- [[RHCSA] Swap 파티셔닝]({{ site.url }}/rhcsa/SwapPartitioning)

에서 학습하였다.

<br>

여기서는 LVM 개념을 배운다.

LVM은 물리 디스크를 초기화 한 이후에, 그룹핑 개념을 도입하여

여러 물리 디스크를 하나의 그룹처럼 묶어줄 수 있게 된다.

논리적인 개념으로 만들어주기 때문에 원하는 크기의 가상의 디스크 장치를 만들 수 있다.


<br><br>


# 2. 디스크 초기화 및 파티셔닝

```bash
# lsblk --fs
NAME   FSTYPE LABEL UUID                                 MOUNTPOINT
vda                                                     
├─vda1                                                  
├─vda2 vfat         399C-0F7D                            /boot/efi
└─vda3 xfs    root  3cd0d4ca-93f6-423b-a469-70ab2b10b667 /
vdb                                                     
vdc                                                     
vdd
```

> 초기화되지 않은 신규 디스크 장치는 vdb, vdc, vdd


```bash
# parted -s /dev/vdb mkpart part1 1M 256MB
# parted -s /dev/vdb mkpart part2 257M 513MB
```

> xfs / ext4 등의 type을 명시하지 않는 것이 특징이다.
>
> 두 개(part1, part2)의 파티셔닝을 하였다.


```bash
# parted /dev/vdb set 1 lvm on
# parted /dev/vdb set 2 lvm on
```

> lvm type으로 지정한다.
>
> 위에서 lvm type을 일괄 지정하는 방법은 보이지 않는다.


```bash
# parted /dev/vdb print
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End    Size   File system  Name   Flags
 1      1049kB  256MB  255MB               part1  lvm
 2      257MB   513MB  256MB               part2  lvm
```

> 총 2개의 파티션이 LVM으로 잘 준비되었다.


```bash
# udevadm settle
```

> 디스크 장치가 준비되기를 기다리는 것을 잊지 말자...!


# 3. 물리 볼륨

phyisical voulume 으로 만들어야 다음 volume group에서 묶을 수 있다.

* 개별적인 물리 디스크 장치를 논리적으로 묶기 위해 하는 과정

<br>

```bash
# pvcreate /dev/vdb1 /dev/vdb2
```

> 각 장치를 volume으로 만들어 컨트롤할 수 있게 된다.


```bash
# pvs
  PV         VG Fmt  Attr PSize   PFree 
  /dev/vdb1     lvm2 ---  243.00m 243.00m
  /dev/vdb2     lvm2 ---  244.00m 244.00m
```

> pvs명령으로 간략하게 확인할 수 있다.


```bash
# pvdisplay
  "/dev/vdb1" is a new physical volume of "243.00 MiB"
  --- NEW Physical volume ---
  PV Name               /dev/vdb1
  VG Name              
  PV Size               243.00 MiB
  Allocatable           NO
  PE Size               0  
  Total PE              0
  Free PE               0
  Allocated PE          0
  PV UUID               qDxeX0-e7my-KvdJ-m8Vs-lvq7-c0lv-wczCWl
  
  "/dev/vdb2" is a new physical volume of "244.00 MiB"
  --- NEW Physical volume ---
  PV Name               /dev/vdb2
  VG Name              
  PV Size               244.00 MiB
  Allocatable           NO
  PE Size               0  
  Total PE              0
  Free PE               0
  Allocated PE          0
  PV UUID               aEQNQ1-nprf-fuHY-2U2d-puIi-2dlN-3lm5dM
```

> pvdisplay 명령으로 모든 volume을 확인할 수 있다.
>
> 장치명(_PV Name_)을 보면 이해가 쉽다.


# 4. 볼륨 그룹

앞서 만든 볼륨을 묶어 그룹으로 만들 수 있다.

<br>

```bash
# vgcreate myvg /dev/vdb1 /dev/vdb2
```

```bash
# vgs
  VG   #PV #LV #SN Attr   VSize   VFree 
  myvg   2   0   0 wz--n- 480.00m 480.00m
```

> vgs 명령으로 간략히 확인할 수 있다.


```bash
# vgdisplay
  --- Volume group ---
  VG Name               myvg
  System ID            
  Format                lvm2
  Metadata Areas        2
  Metadata Sequence No  1
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                0
  Open LV               0
  Max PV                0
  Cur PV                2
  Act PV                2
  VG Size               480.00 MiB
  PE Size               4.00 MiB
  Total PE              120
  Alloc PE / Size       0 / 0  
  Free  PE / Size       120 / 480.00 MiB
  VG UUID               2NvDjK-sZyV-BK9C-OlE0-If4P-lLcA-WGn4dZ
```

> VG Size: /dev/vdb1과 vdb2의 총합과 같다.
>
> PE : LVM 개념으로 만들어진 디스크에서 사용되는 단위. 해당 단위만큼 디스크 용량을 축소/확대 할 수 있다.

<br>


# 5. 논리 볼륨

생성한 그룹은 하나의 물리 디스크와 같다고 볼 수 있다.

해당 디스크를 논리 볼륨이라는 단위로 파티셔닝 하여 쓸 수 있다.
{{ site.content.br_small }}
```bash
# lvcreate -n mylv -L 400MB myvg
```

> myvg (/dev/vdb1, vdb2의 합)에서 400MB 만큼만 잘라서 파티셔닝 한다.


```bash
# lvs
  LV   VG   Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  mylv myvg -wi-a----- 400.00m  
```

> 간략히 확인할 수 있다.


```bash
# lvdisplay
  --- Logical volume ---
  LV Path                /dev/myvg/mylv
  LV Name                mylv
  VG Name                myvg
  LV UUID                Mrx6lv-G0O9-4bhX-r5ef-ISjw-d0aA-qQvDGl
  LV Write Access        read/write
  LV Creation host, time servera.lab.example.com, 2021-12-08 22:56:00 -0500
  LV Status              available
  # open                 0
  LV Size                400.00 MiB
  Current LE             100
  Segments               2
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     8192
  Block device           253:0
```

> 눈여겨 볼 것은 _LV Path_ 이다. 마치 실제 디스크 장치와 같다.
>
> 그리고, 여기도 PE같이 LE 개념이 있다.


```bash
# parted /dev/myvg/mylv print
Error: /dev/dm-0: unrecognised disk label
Model: Linux device-mapper (linear) (dm)                                 
Disk /dev/dm-0: 419MB
Sector size (logical/physical): 512B/512B
Partition Table: unknown
Disk Flags:
```

> (가상의) 디스크 장치가 초기화 되지 않은 로그 내용.


```bash
# mkfs.xfs /dev/myvg/mylv
meta-data=/dev/myvg/mylv         isize=512    agcount=4, agsize=25600 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=1        finobt=1, sparse=1, rmapbt=0
         =                       reflink=1
data     =                       bsize=4096   blocks=102400, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0, ftype=1
log      =internal log           bsize=4096   blocks=1368, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
```

> xfs(또는 원하는) 타입으로 초기화.


```bash
# parted /dev/myvg/mylv print
Model: Linux device-mapper (linear) (dm)
Disk /dev/dm-0: 419MB
Sector size (logical/physical): 512B/512B
Partition Table: loop
Disk Flags:

Number  Start  End    Size   File system  Flags
 1      0.00B  419MB  419MB  xfs
```

> xfs 타입으로 초기화하니, 파티셔닝된 디스크로써 모든 준비가 완료되었다.


```bash
# mount /path /dev/myvg/mylv
```

> 와 같이 마운트할 수 있다.
