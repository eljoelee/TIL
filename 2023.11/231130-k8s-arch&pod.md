# 쿠버네티스 정리
- 아키텍처
    - Master
        1. kube-apiserver
            - 마스터로 전달되는 모든 요청을 받아 적절한 응답을 반환하는 REST API 서버
            - kubectl : api 서버에 명령을 보내고 결과를 반환 받음
        2. etcd
            - 클러스터 내 모든 메타데이터를 저장하는 K:V 저장소
        3. kube-controller-manager
            - control-loop를 통해 current state와 desired state를 비교하고, 상태를 변경하는 역할
    - Node
        1. kubelet
            - 마스터로부터 특정 컨테이너의 spec을 받아 실행 시키고, 정상 동작하는지 모니터링한다.
        2. kube-proxy
            - Service마다 개별 IP를 부여하고 클러스터 내/외부의 트래픽을 Pod로 전달할 수 있도록 패킷을 라우팅한다.
- 장점
    1. Container Runtime이 설치된 곳이라면 정상적으로 동작하는 것을 보장한다.
    2. 클러스터 시스템의 전반적인 리소스를 관리할 수 있다.
    3. 내장 스케쥴러가 최적의 노드를 찾아 컨테이너를 자동으로 배치해준다.
    4. kube-apiserver에 요청하면 해당하는 프로세스를 손쉽게 제어할 수 있다.
    5. 프로세스마다 리소스 사용량을 제한할 수 있다.
    6. 컨테이너에 문제가 발생하여 죽더라도 현재 상태(current state)와 바라는 상태(desired state)가 달라진 것을 인지하고 컨테이너를 다시 실행한다.
    7. 사용자가 바라는 상태를 지정하면 자동으로 적절한 노드를 선택하고 컨테이너를 배치한다.
- Pod
    - 클러스터 내에서 접근 가능한 고유의 IP를 할당받는다.
    - Pod 내의 컨테이너들은 서로 IP를 공유하기 때문에 컨테이너끼리는 localhost를 통해 서로 접근이 가능하고 포트를 통해 구분한다.
    - 컨테이너 관리
        ```yaml
        ...
        spec:
        containers:
        - name: nginx
            image: nginx
            resources:
            requests:
                cpu: "250m" # 0.25core
                memory: "500Mi" # 500MiB
            limits:
                cpu: "500m" # 초과 시, Throttling 발생
                memory: "1Gi" # 초과 시, OOM 발생
            volumeMounts:
            - mountPath: /container-volume
            name: my-volume
            env:
            - name: hello
            value: "world"
            readinessProbe:
            httpGet:
                path: /
                port: 80
        initContainers:
        - name: git
          image: alpine/git
        volumes:
        - name: my-volume
            hostPath:
            path: /home
        nodeSelector:
            disktype: ssd
        ...
        ```
        - nodeSelector를 통해 특정 노드에 할당되도록 스케줄링할 수 있다.
        - env property를 활용하여 환경변수 설정이 가능하다.
        - Pod가 삭제되면 내부 스토리지도 삭제되므로 지속적으로 데이터를 저장하고 싶다면 볼륨을 연결한다.
        - requests와 limits로 Pod 리소스의 최소/최대 사용량을 정의할 수 있다.
        - Probe를 통해 Pod의 Health Check를 수행할 수 있다.
            - livenessProbe : Pod가 살아있는지 확인
            - readinessProbe : Pod 생성 직후, 트래픽을 받을 준비가 완료되었는지 확인
        - initContainers를 통해 메인 컨테이너 실행에 앞서 초기화를 위해 먼저 실행할 컨테이너를 정의할 수 있다.