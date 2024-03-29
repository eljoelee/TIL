## Container
### 도커 없이 컨테이너 구성
1. Cgroups(Control Groups)
    - 컨테이너 별로 자원을 분배하고 limit 내에서 운용
    - CPU나 메모리와 같은 시스템 자원 그루핑
        - 그룹 내부의 프로세스는 할당된 자원(limit)만큼만 사용함
    - 자원 할당과 제어를 파일시스템으로 제공한다(Cgroup Namespace)
        ```bash
        $tree -L 1 /sys/fs/cgroup/cpu
        /sys/fs/cgroup/cpu
        ├── cpu.cfs_period_us
        ├── cpu.cfs_quota_us
        ├── cpu.rt_period_us
        ├── cpu.rt_runtime_us
        ├── cpu.shares
        ├── cpu.stat
        ...

        # 준비
        $sudo su -
        $apt install -y cgroup-tools stress

        # 제어그룹 생성
        $cgcreate -a root -g cpu:mycgroup

        # 커널 생성 확인 - 파일시스템으로 관리됨을 확인
        $tree /sys/fs/cgroup/cpu/mycgroup
        sys/fs/cgroup/cpu/mycgroup/
        ├── cgroup.clone_children
        ├── cgroup.procs
        ├── cpu.cfs_period_us
        ├── cpu.cfs_quota_us
        ├── cpu.rt_period_us
        ├── cpu.rt_runtime_us
        ├── cpu.shares
        ├── cpu.stat
        ├── notify_on_release
        └── tasks

        # CPU 사용률 설정
        # 사용률 계산 : cpu.cfs_quota_us / cpu.cfs_period_us * 100
        $cgset -r cpu.cfs_quota_us=30000 mycgroup

        # 네임스페이스 실행 - cpu 사용률(%CPU) 확인
        $cgexec -g cpu:mycgroup stress -c 1
        $top
         PID USER PR  NI VIRT RES SHR S %CPU %MEM   TIME+ COMMAND
        1407 root 20   0 3700 108   0 R 30.0  0.0 0:02.74 stress
        ```
2. 도커 없이 컨테이너 만들기
- RED/BLUE
    ```bash
    # 베이스 이미지 구조 확인
    $tree myroot/
    myroot/
    ├── bin
    │   ├── ls
    │   ├── ps
    │   └── sh
    ├── escape_chroot
    ├── lib
    │   └── x86_64-linux-gnu
    │       ├── libc.so.6
    │       ├── libcap.so.2
    │       ├── libdl.so.2
    │       ├── libgcrypt.so.20
    │       ├── libgpg-error.so.0
    │       ├── liblz4.so.1
    │       ├── liblzma.so.5
    │       ├── libpcre.so.3
    │       ├── libpcre2-8.so.0
    │       ├── libprocps.so.8
    │       ├── libpthread.so.0
    │       ├── libselinux.so.1
    │       ├── libsystemd.so.0
    │       └── libzstd.so.1
    └── lib64
        └── ld-linux-x86-64.so.2

    #Lower Layer 2 - tools(hostname, ping, umount, stress)
    $wget https://raw.githubusercontent.com/sam0kim/container-internal/main/scripts/copy_tools.sh
    $bash copy_tools.sh
    $rsync -avhu /tmp/tools/ tools/
    $tree tools/

    # Network 네임스페이스 생성
    $ip netns add RED BLUE
    $ip link add veth0 netns RED type veth peer name veth1 netns BLUE
    $ip netns exec {RED/BLUE} ip l

    # IP 주소 부여
    $ip netns exec RED ip addr add dev veth0 11.11.11.2/24
    $ip netns exec RED ip link set veth0 up

    $ip netns exec BLUE ip addr add dev veth1 11.11.11.3/24
    $ip netns exec BLUE ip link set veth1 up

    # 컨테이너 격리와 자원 할당
    $mkdir /sys/fs/cgroup/cpu/red
    $mkdir /sys/fs/cgroup/memory/red
    $ls /sys/fs/cgroup/{cpu,memory}/red

    # CPU: 40%, Mem: 200MB & swapp off
    $echo 40000 > /sys/fs/cgroup/cpu/red/cpu.cfs_quota_us
    $echo 209715200 > /sys/fs/cgroup/memory/red/memory.limit_in_bytes
    $echo 0 > /sys/fs/cgroup/memory/red/memory.swappiness

    # RED 격리
    # m : 마운트
    # u : 호스트네임
    # i : IPC
    # fp : f(fork), p(PID)
    # --net : 네트워크
    # nsenter : 네임스페이스 진입
    $unshare -m -u -i -fp nsenter --net=/var/run/netns/RED /bin/sh

    # cgroup 할당
    # PID 네임스페이스 > 실행하고자 하는 프로세스를 자식 네임스페이스 내 PID 1번으로 등록함
    # PID 1번 프로세스는 red cpu & memory cgroup에 소속된다.
    $echo "1" > /sys/fs/cgroup/cpu/red/cgroup.procs
    $echo "1" > /sys/fs/cgroup/memory/red/cgroup.procs

    # 오버레이 마운트
    $mkdir /redfs
    $mkdir /redfs/{container,work,merge}
    $mount -t overlay overlay -o lowerdir=tools:myroot,upperdir=/redfs/container,workdir=/redfs/work /redfs/merge
    $tree /redfs/merge

    # pivot_root
    $mkdir -p /redfs/merge/put_old
    $cd /redfs/merge
    $pivot_root . put_old
    $cd /
    $ls /
    bin  escape_chroot  lib  lib64  put_old  usr

    # put_old umount - 컨테이너의 호스트 루트파일시스템이 put_old에 있으므로 삭제
    # umount를 하기 위해 proc 마운트
    $mkdir /proc
    $mount -t proc proc /proc
    $umount -l put_old
    $rm -rf put_old

    $ps -ef
    UID        PID  PPID  C STIME TTY          TIME CMD
    0            1     0  0 11:07 ?        00:00:00 /bin/sh

    $hostname RED

    # BLUE도 동일하게 생성하고, 테스트 진행
    $ping 11.11.11.3
    $stress -c 1
    $stress --vm 1 --vm-bytes 195M
    $stress --vm 1 --vm-bytes 200M
    $top
    ```
> 1. chroot 등장 - 탈옥 문제 발생(cd 또는 코드로 호스트 루트 디렉토리로 접근 가능)
> 2. pivot_root를 수행하기 위해 mount namespace가 개발
> 3. 파일시스템만으로 격리 환경 관리가 어려움 - uts, ipc, pid, cgroups 개발
> 4. network namespace 개발 - 호스트로부터 독립적인 네트워크 사용 가능
> 5. user namespace 개발 - 컨테이너 루트 권한 문제 해결
> 6. docker, k8s 개발
