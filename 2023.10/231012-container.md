## Container
### 도커 없이 컨테이너 구성
1. host/container root directory는 다르다.
    - ls
    - ps aux > PID 1번이 다름
    - ip l > 네트워크 다름
    - hostname > 다름
2. chroot : fake root를 생성하여 해커가 바깥으로 못나가게 격리
    - chroot fakeroot /bin/sh(격리)
        - /bin/sh > 의존성(.so) 파일이 없다
    - ldd로 지정한 프로그램(/bib/sh) 의존성 확인 후 cp(패키징)
    - docker export $(docker create nginx) | tar -C nginx-root -xvf -;
        - nginx 이미지를 압축 스트림으로 가져와서 nginx-root에 압축 해제
    - cd ../../../ or out을 시도하면 호스트 루트 디렉토리로 탈출한다.
    - 실제 컨테이너 용도로는 부적합
3. pivot_root : 루트 파일 시스템을 pivot하는 기능
    > 호스트의 루트 파일 시스템에 의존하지 않고, 자체 생성한 루트 파일 시스템에서 관련 라이브러리, 바이너리 파일 사용 가능!
    - pivot_root {새 루트 디렉토리} {기존 루트 파일 시스템이 부착될 위치}
    - 최상위 파일시스템(/ :: /bin, /lib, /etc 등)
        - 루트 디렉토리를 포함, 하위 모든 파일시스템들이 마운트
        - 호스트에 영향을 주지 않으면서 pivot 기능을 수행하기 위해 namespace 개발
    - namespace : 프로세스 격리 환경 제공
        - 마운트 네임스페이스 : 특정 파일 시스템을 루트 파일시스템의 하위 디렉토리로 부착하는 위치 정보(마운트 포인트) 격리
            -  System call
                - unshare --mount /bin/sh
                    - 마운트 네임스페이스 격리
                    - 부모 프로세스의 네임스페이스 정보를 Copy on write
                - mount -t tmpfs none new_root
                    - 격리 공간에서 마운트
                - mount | grep new_root
                    - 호스트에서 조회 시 보이지 않음
            - 네임스페이스에서 의존성 cp 작업 후 호스트와 비교(tree new_root)
                - 호스트 : 내용 조회 x, 네임스페이스 : 내용 조회 o
            - cd new_root && pivot_root . put_old && cd / && ls /
                - 네임스페이스는 new_root 디렉토리를 루트 디렉토리로 인식한다.
            - cd ../../../ or out을 시도하면 호스트 루트 디렉토리로 탈출하지 않음