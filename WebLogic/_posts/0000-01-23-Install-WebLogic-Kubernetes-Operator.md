---
date: 2025-11-18 13:53:50 +0900
layout: post
title: "[WebLogic/] "
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview

WebLogic Kubernetes Operator 설치 스크립트.

내부망에 설치하기 위해 Proxy를 경유하여 설치하였다.

<br><br>


# 2. Descriptions

다음은 모든 설치 과정에 필요한 환경 변수들이 집약된다.

```sh
# --------------------
# 디렉터리 경로
# --------------------
export WKO_HOME="/sw/wko"            # 작업 홈 (Dockerfile, zip, yaml, model, apps)
export BUILD_DIR="${WKO_HOME}/build" # 이미지 빌드 컨텍스트 디렉터리
export MODEL_DIR="${WKO_HOME}/model" # 모델 파일 위치
export APPS_DIR="${WKO_HOME}/apps"   # 앱(배포 WAR/EAR 등) 위치

# --------------------
# 내부망 특성상 필요한 Proxy
# - PROXY를 통해 외부망에 접근한다.
# - NO_PROXY 에 있는 목록은 외부망이 아닌 내부 호출 또는 k8s network 접근 목록을 선언한다.
#	선언하지 않으면, 이 목록을 접근할 때도 PROXY를 타게 된다.
# --------------------
export PROXY="http://...:80"
export NO_PROXY="127.0.0.1,localhost,*.svc,*.cluster.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

# curl로 외부망에 접근 시 PROXY 경유한다.
export CURL="curl -L -f --retry 3 --connect-timeout 15 --proxy ${PROXY}"

# --------------------
# 패키지 설치 공통 옵션
# --------------------
export DNF_OPTS="-y --setopt=install_weak_deps=False"

# --------------------
# Kubernetes/CRI-O/Helm 버전 및 Repo
# - libcon/crio/k8s 패키지는 외부 reop에 있으므로, repo 파일을 직접 가져온다.
# --------------------
export K8S_VERSION="1.28"
export HELM_VERSION="v3.14.4"

# openSUSE libcontainers 저장소(EL9 계열용) — DNF 자체는 프록시를 태우지 않음
# DNF는 환경변수 기반 proxy를 사용하지 않으므로 repo 파일에 직접 proxy를 지정해야 한다.
export LIBCON_REPO_URL="https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/CentOS_9_Stream/devel:kubic:libcontainers:stable.repo"
export CRIO_REPO_URL="https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/${K8S_VERSION}/CentOS_9_Stream/devel:kubic:libcontainers:stable:cri-o:${K8S_VERSION}.repo"

# --------------------
# WDT(WebLogic Deploy Tooling)
# --------------------
export WDT_VERSION="4.3.7"
export WDT_ZIP="${WKO_HOME}/weblogic-deploy.zip"
export WDT_URL="https://github.com/oracle/weblogic-deploy-tooling/releases/download/release-${WDT_VERSION}/weblogic-deploy.zip"

# --------------------
# WebLogic 베이스 이미지
# --------------------
export WLS_IMAGE="container-registry.oracle.com/middleware/weblogic:14.1.1.0"

# --------------------
# 도메인/MII 이미지
# --------------------
export DOMAIN_UID="sample-domain"
export MII_IMAGE="localhost/${DOMAIN_UID}-mii:full-jq"

# --------------------
# K8s 네임스페이스/클러스터
# --------------------
export OP_NS="weblogic-operator-ns"  # Operator 배포 NS
export DOM_NS="wls-domain-ns"        # Domain 배포 NS
export CLUSTER_NAME="cluster-1"
export CLUSTER_SIZE="1"
export ADMIN_NODEPORT="30001"        # AdminServer NodePort

# --------------------
# 레지스트리/이미지 풀 시크릿
# --------------------
export WLS_IMAGE_REG="container-registry.oracle.com"
export IMAGE_PULL_SECRET="regcred"
export IMAGE_REG_USERNAME="..." # OCR 로그인 이메일
export IMAGE_REG_PASSWORD="..."	# OCR에서 auth token을 획득

# --------------------
# WebLogic 관리자/런타임 암호
# --------------------
export ADMIN_USER="weblogic"
export ADMIN_PWD="welcome1"
export WDT_RUNTIME_PASSPHRASE="welcome1"

# --------------------
# WKO(Helm) 차트 버전
# --------------------
export WKO_CHART_VER="4.3.2"

# --------------------
# kubectl 은 k8s 내부 network 조회에 사용되므로, NO_PROXY를 적용한다.
# --------------------
export KCTL="env -u HTTPS_PROXY -u HTTP_PROXY -u ALL_PROXY -u https_proxy -u http_proxy -u all_proxy NO_PROXY=${NO_PROXY} kubectl"
```

<br>

다음은 CRI-O / K8S 를 설치 및 클러스터링 구성 한다.

```sh
# --------------------
# 기본 유틸리티 설치
# - WKO 이미지 내에서 사용하기 위하여 설치하는 것(jq 등)들이 대부분이다.
# --------------------
dnf clean all -y
dnf makecache -y
dnf install ${DNF_OPTS} -y iproute iptables ebtables ethtool socat conntrack-tools wget tar gzip jq curl

# --------------------
# libcon/crio 설치를 위한 repo 등록
# --------------------
${CURL} -o /etc/yum.repos.d/devel:kubic:libcontainers:stable.repo "${LIBCON_REPO_URL}"
${CURL} -o "/etc/yum.repos.d/devel:kubic:libcontainers:stable:cri-o:${K8S_VERSION}.repo" "${CRIO_REPO_URL}"
echo "proxy=${PROXY}" >> /etc/yum.repos.d/devel:kubic:libcontainers:stable.repo
echo "proxy=${PROXY}" >> /etc/yum.repos.d/devel:kubic:libcontainers:stable:cri-o:${K8S_VERSION}.repo

# --------------------
# CRI-O 설치 후 활성화
# --------------------
dnf install ${DNF_OPTS} cri-o cri-tools
systemctl enable crio

# --------------------
# K8S repo 파일은 아래와 같이 직접 생성해야 한다.
# --------------------
cat >/etc/yum.repos.d/kubernetes.repo <<EOF
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION}/rpm/
enabled=1
gpgcheck=0
repo_gpgcheck=0
proxy=${PROXY}
EOF

# --------------------
# kubelet(Node agent)/kubeadm(Cluster joiner)/kubectl(CLI) 를 설치하고 활성화 한다.
# --------------------
dnf install ${DNF_OPTS} kubelet kubeadm kubectl
systemctl enable kubelet

# --------------------
# CRI-O, Kubelet systemd 등록 및 PROXY/NO_PROXY 환경변수 지정
# - CRI-O는 외부 레지스트리 Pull 시, kubelet은 일부 외부 연동 시 proxy가 필요하다.
# 다만 이번 설치 사례에서는 kubelet은 외부 연동을 하지 않으므로 proxy가 필요하진 않다.
# --------------------
mkdir -p /etc/systemd/system/crio.service.d /etc/systemd/system/kubelet.service.d
cat >/etc/systemd/system/crio.service.d/proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=${PROXY}"
Environment="HTTPS_PROXY=${PROXY}"
Environment="NO_PROXY=${NO_PROXY}"
EOF

cat >/etc/systemd/system/kubelet.service.d/10-proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=${PROXY}"
Environment="HTTPS_PROXY=${PROXY}"
Environment="NO_PROXY=${NO_PROXY}"
EOF

systemctl daemon-reload
systemctl restart crio
# kubelet은 init 전에 crashloop가 날 수 있으므로 실패 허용
systemctl restart kubelet || true

# --------------------
# 기타 정리
# - swp 비활성화(kubelet 요구사항)
# - 다른 CNI 구성 제거 후, 단순한 Pod 네트워크 플러그인인 Flannel만 사용
# - k8s 환경 구성에 필요한 커널 모듈 등록
# --------------------
# swp 비활성화(kubelet 요구사항)
swapoff -a || true
sed -ri '/\sswap\s/s/^#?/#/' /etc/fstab || true

# 다른 CNI 구성 제거 후, 단순한 Pod 네트워크 플러그인인 Flannel만 사용
systemctl stop crio || true
mkdir -p /root/cni-backup
mv -f /etc/cni/net.d/* /root/cni-backup/ 2>/dev/null || true
ip link set cni0 down 2>/dev/null || true
ip link del cni0 2>/dev/null || true
rm -rf /var/lib/cni/* /var/lib/cni/networks/* /run/flannel/* 2>/dev/null || true
systemctl start crio

# k8s 환경 구성에 필요한 커널 모듈 등록
cat >/etc/modules-load.d/k8s.conf <<'EOF'
br_netfilter
EOF
modprobe br_netfilter || true
cat >/etc/sysctl.d/99-kubernetes-cri.conf <<'EOF'
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF
sysctl --system

# --------------------
# k8s 클러스터 생성
# - init으로 현재 노드를 k8s control-plane으로 초기화한다
# - 현재 node에서 kubectl을 사용할 수 있게 한다.
# - Flannel 설치 및 클러스터에 배포
# --------------------
# init으로 현재 노드를 k8s control-plane으로 초기화한다
kubeadm init   --pod-network-cidr="10.244.0.0/16"   --cri-socket=unix:///var/run/crio/crio.sock

# 현재 node에서 kubectl을 사용할 수 있게 한다. (root 유저 및 다른 non-root user도 진행)
mkdir -p $HOME/.kube
cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
chmod 600 $HOME/.kube/config

# Flannel 설치 및 클러스터에 배포
${CURL} -o /tmp/kube-flannel.yml https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
${KCTL} apply -f /tmp/kube-flannel.yml
${KCTL} -n kube-flannel rollout status ds/kube-flannel-ds --timeout=90s || true

# 상태 확인
${KCTL} get nodes -o wide
${KCTL} -n kube-system get pods -o wide
```

<br>

다음은 K8S에 WKO를 배포하고, Dockerfile을 만들어 배포하면 WKO가 이를 감지하여 컨트롤 한다.

```sh
# --------------------
# Helm 설치
# - k8s에 설치를 빠르게 돕는 패키지 매니저다.
# --------------------
${CURL} -o /tmp/helm.tgz "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz"
tar -xzf /tmp/helm.tgz -C /tmp
install -m 0755 /tmp/linux-amd64/helm /usr/local/bin/helm
helm version

# --------------------
# WKO 를 통해 배포될 WebLogic 이미지 준비
# --------------------
# 디렉터리 준비
mkdir -p "${WKO_HOME}" "${BUILD_DIR}" "${MODEL_DIR}" "${APPS_DIR}"
cd "${WKO_HOME}"

# WDT 다운로드 및 검증
# WDT(WebLogic Deploy Tooling): WebLogic 도메인 구성을 YAML(Model)로 정의·배포하는 도구
${CURL} -o "${WDT_ZIP}" "${WDT_URL}"
unzip -t "${WDT_ZIP}" >/dev/null

# 빌드할 컨텍스트(홈 디렉터리)들 정리
rm -rf "${BUILD_DIR:?}"/*
mkdir -p "${BUILD_DIR}/wdt" "${BUILD_DIR}/model" "${BUILD_DIR}/apps"

# Dockerfile(이미지)에 빌드할 리소스들을 준비
cp "$(command -v jq)" "${BUILD_DIR}/jq"; chmod 0755 "${BUILD_DIR}/jq"
cp "${WDT_ZIP}" "${BUILD_DIR}/wdt/weblogic-deploy.zip"
rsync -a "${MODEL_DIR}/" "${BUILD_DIR}/model/" || true
rsync -a "${APPS_DIR}/"  "${BUILD_DIR}/apps/"  || true

# WDT yaml 생성
cat > /tmp/mii-fixed.yaml <<'YAML'
domainInfo:
  AdminUserName: '@@SECRET:wls-admin-credentials:username@@'
  AdminPassword: '@@SECRET:wls-admin-credentials:password@@'
topology:
  Name: sample-domain
  AdminServerName: admin-server
  Server:
    admin-server:
      ListenPort: 7001
  ServerTemplate:
    ms-tpl:
      ListenPort: 8001
  Cluster:
    cluster-1:
      DynamicServers:
        ServerTemplate: ms-tpl
        ServerNamePrefix: managed-server
        DynamicClusterSize: 1
        MaxDynamicClusterSize: 5
        CalculatedListenPorts: false
YAML
cp /tmp/mii-fixed.yaml "${BUILD_DIR}/model/"

# Dockerfile 작성
cat > "${WKO_HOME}/Dockerfile" <<EOF
FROM ${WLS_IMAGE}
USER root
COPY build/jq /usr/local/bin/jq
RUN chmod 0755 /usr/local/bin/jq
RUN mkdir -p /u01/wdt/model /u01/wdt/apps && chown -R oracle:root /u01/wdt
USER oracle
COPY build/wdt/weblogic-deploy.zip /u01/wdt/
RUN cd /u01/wdt && unzip -q weblogic-deploy.zip && rm weblogic-deploy.zip
COPY build/model/ /u01/wdt/model/
COPY build/apps/  /u01/wdt/apps/
ENV WDT_INSTALL_HOME=/u01/wdt/weblogic-deploy
ENV LANG=C.UTF-8
EOF

# (검증) Dockerfile FROM 값이 실제로 확장되었는지 확인
# 일부 진행 과정에서 Dockerfile이 제대로 생성되지 않았던 이슈가 있어 추가함
sed -n '1,4p' "${WKO_HOME}/Dockerfile"

# 이미지 빌드를 위해 podman이 OCR에 로그인 해야 하므로 PROXY가 필요하다.
export HTTP_PROXY="${PROXY:-}"
export HTTPS_PROXY="${PROXY:-}"
export NO_PROXY="${NO_PROXY:-}"

podman login "${WLS_IMAGE_REG}" -u "$IMAGE_REG_USERNAME" -p "$IMAGE_REG_PASSWORD"
podman build --no-cache -t "${MII_IMAGE}" "${WKO_HOME}"

# (검증) 이미지 내 모델 유무 즉시 확인 (없으면 중단)
# 일부 진행 과정에서 생성한 이미지에 모델 파일들이 제대로 동기화 되지 않았던 이슈가 있어 추가함
podman run --rm --entrypoint bash "${MII_IMAGE}" -lc '
  set -e
  echo "[list]"; ls -l /u01/wdt/model
  test -s /u01/wdt/model/mii-fixed.yaml
'

# --------------------
# 도메인 네임스페이스/시크릿/CM 준비
# --------------------
${KCTL} create namespace "${DOM_NS}" --dry-run=client -o yaml | ${KCTL} apply -f -

${KCTL} label ns "${DOM_NS}" weblogic-operator=enabled --overwrite

${KCTL} -n "${DOM_NS}" create secret docker-registry "${IMAGE_PULL_SECRET}"   --docker-server="${WLS_IMAGE_REG}"   --docker-username="${IMAGE_REG_USERNAME}"   --docker-password="${IMAGE_REG_PASSWORD}"   --dry-run=client -o yaml | ${KCTL} apply -f -

${KCTL} -n "${DOM_NS}" create secret generic wls-admin-credentials   --from-literal=username="${ADMIN_USER}"   --from-literal=password="${ADMIN_PWD}"   --dry-run=client -o yaml | ${KCTL} apply -f -

${KCTL} -n "${DOM_NS}" create secret generic wdt-runtime-secret   --from-literal=password="${WDT_RUNTIME_PASSPHRASE}"   --dry-run=client -o yaml | ${KCTL} apply -f -

${KCTL} -n "${DOM_NS}" create configmap "${DOMAIN_UID}-model-fixed"   --from-file=mii-fixed.yaml=/tmp/mii-fixed.yaml   --dry-run=client -o yaml | ${KCTL} apply -f -

# --------------------
# WKO 설치
# - k8s cluster가 single node(master node)이므로 master node에도 deploy가 가능하도록 한다.
# - WKO 가 설치될 Namespace 생성
# - Helm을 이용해 WKO를 K8S에 쉽게 배포
# --------------------
# k8s cluster가 single node(master node)이므로 master node에도 deploy가 가능하도록 한다.
kubectl taint nodes --all node-role.kubernetes.io/control-plane- || true
# WKO 가 설치될 Namespace 생성
kubectl create namespace "${OP_NS}" 2>/dev/null || true

# Helm을 이용해 WKO를 K8S에 쉽게 배포
helm repo add weblogic-operator https://oracle.github.io/weblogic-kubernetes-operator/charts --force-update
helm repo update
helm pull weblogic-operator/weblogic-operator --version "${WKO_CHART_VER}" --destination /tmp
CHART="/tmp/weblogic-operator-${WKO_CHART_VER}.tgz"

# SA 사전 생성(+ 문자열로 전달)
kubectl -n "${OP_NS}" create serviceaccount weblogic-operator-sa 2>/dev/null || true
helm upgrade --install wko "${CHART}"   -n "${OP_NS}" --create-namespace --wait   --set image="ghcr.io/oracle/weblogic-kubernetes-operator:${WKO_CHART_VER}"   --set serviceAccount=weblogic-operator-sa   --set domainNamespaceSelectionStrategy=LabelSelector   --set domainNamespaceLabelSelector='weblogic-operator=enabled'

# init 컨테이너(copy-container) 리소스 패치
# WKO는 최소 요구 사항(cpu/memory)가 있는데, 초기 설치 시 이를 충족하지 못하므로 패치 해야 한다.
# 패치 후, 리소스 재생성이 진행될 때 패치가 자연스럽게 적용되어 문제가 해결된다.
kubectl -n "${OP_NS}" patch deploy weblogic-operator --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/initContainers/0/resources",
   "value":{"requests":{"cpu":"50m","memory":"16Mi"},
            "limits":{"cpu":"200m","memory":"32Mi"}}}
]'
kubectl -n "${OP_NS}" delete pod -l app=weblogic-operator --ignore-not-found
kubectl -n "${OP_NS}" rollout status deploy/weblogic-operator --timeout=10m
kubectl -n "${OP_NS}" rollout status deploy/weblogic-operator-webhook --timeout=10m

# --------------------
# WKO 리소스 배포
# - WKO가 관리할 WebLogic 도메인 리소스 생성
# --------------------
cat > "${WKO_HOME}/cluster.yaml" <<EOF
apiVersion: weblogic.oracle/v1
kind: Cluster
metadata:
  name: ${CLUSTER_NAME}
  namespace: ${DOM_NS}
  labels:
    weblogic.domainUID: ${DOMAIN_UID}
spec:
  clusterName: ${CLUSTER_NAME}
  replicas: ${CLUSTER_SIZE}
EOF

cat > "${WKO_HOME}/domain.yaml" <<EOF
apiVersion: weblogic.oracle/v9
kind: Domain
metadata:
  name: ${DOMAIN_UID}
  namespace: ${DOM_NS}
  labels:
    weblogic.domainUID: ${DOMAIN_UID}
spec:
  domainUID: ${DOMAIN_UID}
  domainHomeSourceType: FromModel
  image: ${MII_IMAGE}
  imagePullPolicy: IfNotPresent
  imagePullSecrets:
  - name: ${IMAGE_PULL_SECRET}

  webLogicCredentialsSecret:
    name: wls-admin-credentials

  includeServerOutInPodLog: true
  serverStartPolicy: IfNeeded

  configuration:
    secrets:
    - wls-admin-credentials
    - wdt-runtime-secret
    model:
      domainType: WLS
      runtimeEncryptionSecret: wdt-runtime-secret
      modelHome: /u01/wdt/model
      wdtInstallHome: /u01/wdt/weblogic-deploy
      configMap: ${DOMAIN_UID}-model-fixed
      onlineUpdate:
        enabled: false
    introspectorJobActiveDeadlineSeconds: 600

  adminServer:
    serverStartPolicy: IfNeeded
    adminService:
      channels:
      - channelName: default
        nodePort: ${ADMIN_NODEPORT}

  clusters:
  - name: ${CLUSTER_NAME}
EOF

${KCTL} apply -f "${WKO_HOME}/cluster.yaml"
${KCTL} apply -f "${WKO_HOME}/domain.yaml"

# 위 클러스터/도메인 yaml을 다시 생성 유도하기 위해 version을 갱신한다.
# 일반적으로는 현재 설치 사례에서는 불필요하지만, yaml 변경 후 반영을 위해서 사용하는 편.
${KCTL} -n "${DOM_NS}" patch domain "${DOMAIN_UID}" --type=merge -p '{"spec":{"introspectVersion":"'"$(date +%s)"'"}}'
```


<br><br>


# 3. References

