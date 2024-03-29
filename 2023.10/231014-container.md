## Container
### 도커 없이 컨테이너 구성
1. Overlay File system
    - 이미지 중복 문제를 해결하기 위해 여러 이미지 레이어를 하나로 마운트
    - Merged View : Lower Layer(ReadOnly)와 Upper Layer(Writable)을 병합한 이미지
    - Copy On Write : Lower Layer에 수정이 필요한 경우 Upper Layer에 원본을 복제하여 수정
    ```bash
    # Lower Dir 1
    $tree myroot

    # Lower Dir 2 - which 프로세스 복사
    $mkdir tools
    $ldd /usr/bin/which
    $mkdir -p tools/user/bin
    $cp /usr/bin/which tools/usr/bin

    # 오버레이 마운트 준비 및 생성
    # container : Upper Layer
    # work : upper를 보장하기 위한 디렉토리
    # merge : Merged View
    $mkdir -p rootfs/{container,work,merge}

    $mount -t overlay overlay -o \
    lowerdir=tools:myroot,upperdir=rootfs/container,workdir=rootfs/work \
    rootfs/merge

    # myroot/rootfs 비교 - tools(Lower layer - 2) > which 프로세스
    $tree -L 2 myroot/{bin,usr}
    myroot/bin
    ├── ls
    ├── ps
    └── sh
    $tree -L 2 rootfs/merge/{bin,usr}
    merge/bin
    ├── ls
    ├── ps
    └── sh
    merge/usr
    └── bin
        └── which

    # COW 검증
    # escape_chroot 파일 삭제
    $rm rootfs/merge/escape_chroot
    
    # Lower layer - 1 > 삭제되지 않음
    $ls myroot

    # merged view > 노란색 마킹(white out) : 삭제 마킹
    # Lower Layer 내용을 변경하지 않고 Upper Layer에서 변경된 정보 관리 - 원본 보장
    $tree -L 2 rootfs
    rootfs
    ├── container
    │   └── escape_chroot
    ├── merge
    │   ├── bin
    │   ├── lib
    │   ├── lib64
    │   └── usr
    └── work
        └── work

    $umount rootfs/merge
    ```
2. 컨테이너 격리
- namespace 특징
    - 모든 프로세스는 타입별(Network, PID, User...)로 네임스페이스에 속함
    - 자식 프로세스는 부모의 네임스페이스를 상속함
- namespace 이전 문제점
    - 호스트의 다른 프로세스들이 보인다. - PID
    - 호스트의 포트를 사용한다. - Network
    - 루트 권한이 있다. - User
    - ...
- 네임스페이스 조회
    - mnt 프로세스 격리 확인(pid, nprocs, command)
        ```bash
        $unshare -m
        $lsns -p $$
        NS TYPE   NPROCS   PID USER COMMAND
        4026531835 cgroup     13     1 root /init
        4026531837 user       16     1 root /init
        4026531992 net        13     1 root /init
        4026532192 uts        13     1 root /init
        4026532193 ipc        13     1 root /init
        4026532194 pid        16     1 root /init
        4026533190 mnt         2   654 root -bash
        ```
- PID 네임스페이스
    - PID 넘버스페이스 격리
    - 부모-자식 네임스페이스 중첩
        - 부모 > 자식 네임스페이스 조회 가능
    - unshare 수행 시 fork 수행
        - 실행하고자 하는 프로세스를 자식 네임스페이스 내 PID 1번으로 등록한다.
        - unshare -fp --mount-proc /bin/sh
            - p : pid namespace
            - f : fork
            - mount-proc : proc 파일 시스템 마운트
            ```bash
            $unshare -fp --mount-proc /bin/sh

            # 네임스페이스 - 호스트와 비교
            $ps -ef
            UID        PID  PPID  C STIME TTY          TIME CMD
            root         1     0  0 15:16 pts/3    00:00:00 /bin/sh
            # 동일한 NS 확인
            $lsns -t pid -p 1
                    NS TYPE NPROCS PID USER COMMAND
            4026533191 pid       2   1 root /bin/sh

            # 호스트 - unshare 자식 프로세스 > /bin/sh
            $ps -ef | grep "/bin/sh"
            root       708   707  0 15:16 pts/3    00:00:00 sudo unshare -fp --mount-proc /bin/sh
            root       709   708  0 15:16 pts/3    00:00:00 unshare -fp --mount-proc /bin/sh
            root       710   709  0 15:16 pts/3    00:00:00 /bin/sh
            # 동일한 NS 확인
            $sudo lsns -t pid -p 710
                    NS TYPE NPROCS   PID USER COMMAND
            4026533191 pid       1   710 root /bin/sh
            # 호스트에서 /bin/sh 프로세스 종료 시, 컨테이너도 자동으로 종료됨
            $kill -SIGKILL 710
            ```
- Network 네임스페이스
    - 네트워크 스택 격리
    - 네트워크 가상화, 가상 인터페이스 사용
    - 특징
        - 여러 네트워크 네임스페이스에 걸쳐 있을 수 있다.
        - 다른 네트워크 네임스페이스로 이동 가능
        - veth, bridge, vxian...
        - 네트워크 네임스페이스 삭제 시 가상 인터페이스도 같이 삭제, 물리 장치들은 기존 네임스페이스로 복원
    - 일대일 통신 실습
        ```bash
        # veth pair : 양 끝이 veth0, veth1인 랜선 생성
        $ip link add veth0 type veth peer name veth1
        $ip link
        ...
        7: veth1@veth0: <BROADCAST,MULTICAST,M-DOWN> mtu 1500 qdisc noop state DOWN mode DEFAULT group default qlen 1000
        link/ether 9e:7a:b4:84:f4:fb brd ff:ff:ff:ff:ff:ff
        8: veth0@veth1: <BROADCAST,MULTICAST,M-DOWN> mtu 1500 qdisc noop state DOWN mode DEFAULT    group default qlen 1000
        link/ether b6:ea:c3:4f:2a:44 brd ff:ff:ff:ff:ff:ff

        # 네트워크 네임스페이스 생성
        $ip netns add RED
        $ip netns add BLUE

        # 각 네임스페이스에 veth 연결
        $ip link set veth0 netns RED
        $ip link set veth1 netns BLUE

        # 각 장치 활성화
        $ip netns exec RED ip link set veth0 up
        $ip netns exec BLUE ip link set veth1 up

        # IP 주소 부여
        $ip netns exec RED ip addr add 11.11.11.2/24 dev veth0
        $ip netns exec BLUE ip addr add 11.11.11.3/24 dev veth1

        # 네임스페이스 생성 시 /var/run/netns 하위에 파일 생성
        $ls /var/run/netns

        # nsenter : 네임스페이스 진입, --net : 네트워크 네임스페이스
        $nsenter --net=/var/run/netns/{NS이름}
        
        $ip a
        1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1000
            link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        2: tunl0@NONE: <NOARP> mtu 1480 qdisc noop state DOWN group default qlen 1000
            link/ipip 0.0.0.0 brd 0.0.0.0
        3: sit0@NONE: <NOARP> mtu 1480 qdisc noop state DOWN group default qlen 1000
            link/sit 0.0.0.0 brd 0.0.0.0
        8: veth0@if7: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
            link/ether b6:ea:c3:4f:2a:44 brd ff:ff:ff:ff:ff:ff link-netns BLUE
            inet 11.11.11.2/24 scope global veth0
            valid_lft forever preferred_lft forever
            inet6 fe80::b4ea:c3ff:fe4f:2a44/64 scope link
            valid_lft forever preferred_lft forever
        
        $ip route
        11.11.11.0/24 dev veth0 proto kernel scope link src 11.11.11.2

        # 호스트와 비교
        $ ip a
        1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
            link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
            inet 127.0.0.1/8 scope host lo
            valid_lft forever preferred_lft forever
            inet6 ::1/128 scope host
            valid_lft forever preferred_lft forever
        ...
        6: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
            link/ether 00:15:5d:2c:e3:94 brd ff:ff:ff:ff:ff:ff
            inet 172.31.130.181/20 brd 172.31.143.255 scope global eth0
            valid_lft forever preferred_lft forever
            inet6 fe80::215:5dff:fe2c:e394/64 scope link
            valid_lft forever preferred_lft forever
        
        $ip route
        default via 172.31.128.1 dev eth0
        172.31.128.0/20 dev eth0 proto kernel scope link src 172.31.130.181

        # ping RED > BLUE
        $ping 11.11.11.3
        
        # 네트워크 네임스페이스 삭제
        $ip netns del RED
        $ip netns del BLUE
        $ls /var/run/netns
        ```
- USER 네임스페이스
    - UID/GID 넘버스페이스 격리
    - 컨테이너의 루트 권한 문제 해결
    - 부모-자식 네임스페이스 중첩
    - 권한 실습
        ```bash
        # 일반 계정으로 도커 우분투 실행
        # 호스트 > 일반유저
        $id
        uid=1000(eljoelee) gid=1000(eljoelee) groups=1000(eljoelee)

        # 도커 컨테이너 안은 root 유저
        $docker run -it ubuntu /bin/sh
        $id
        uid=0(root) gid=0(root) groups=0(root)
        
        # 호스트에서 /bin/sh 프로세스 조회 시 루트 권한으로 실행 확인
        # 즉, 일반 계정으로 실행했음에도 권한 문제 발생
        $ps -ef | grep "/bin/sh"

        # 호스트
        $readlink /proc/$$/ns/user
        user:[4026531837]
        
        # 컨테이너
        $readlink /proc/$$/ns/user
        user:[4026531837]

        # 컨테이너, 호스트의 유저 아이디, 그룹아이디 넘버스페이스가 동일함(동일 계정)
        # 컨테이너의 루트가 호스트의 유저와 동일하다.
        ```
    - User 네임스페이스 격리
        ```bash
        # 호스트 > 일반유저
        $id
        uid=1000(eljoelee) gid=1000(eljoelee) groups=1000(eljoelee)

        # User 네임스페이스 격리
        $unshare -U --map-root-user /bin/sh
        $id
        uid=0(root) gid=0(root) groups=0(root)

        # 호스트에서 /bin/sh 프로세스 조회 시 일반 계정으로 실행 확인
        $ps -ef | grep "/bin/sh"

        # 호스트
        $readlink /proc/$$/ns/user
        user:[4026531837]
        
        # 컨테이너 > 값이 다름을 확인
        $readlink /proc/$$/ns/user
        user:[4026533190]
        ```
    - 결론
        - 컨테이너 내부에서만 root
        - USER 네임스페이스간 UID/GID Remap
