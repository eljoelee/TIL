## Network
### 1. 기초
* 패킷 교환 방식 : 데이터를 패킷 단위로 분할 후 헤더를 붙여 전송
* 프로토콜 : 패킷 처리 규칙
* 계층 구조 : 프로토콜로 정의된 다양한 통신 기능을 계층별로 정의한 구조
* PDU : 각 계층 데이터 단위, 헤더 + 페이로드
* VPN : 인터넷을 통해 가상의 전용선(또는 터널)을 만들고 IPsec 프로토콜을 이용하여 일대일 통신을 하는 기능
### 2. DataLink
* L2 Switch
    - 송신지 MAC 주소와 물리포트 번호를 MAC 주소 테이블로 관리
    - L2 Switching
        1. 송/수신지 MAC 주소가 담긴 이더넷 프레임을 케이블을 통해 전송
        2. 테이블이 비어있다면 송신지 MAC 주소와 물리포트 번호 저장
        3. 송신지를 제외한 모든 물리포트로 프레임 사본 전달 - Flooding, Broadcast
        4. 사본을 전달받은 수신지는 응답 프레임을 케이블을 통해 전송
            - 관계 없는 단말은 프레임 파기
        5. 응답 프레임의 MAC 주소와 물리포트 번호 저장
        6. 이후 스위치가 송/수신지 간 통신 직접 전송, 일정시간 미사용 시 해당 정보 삭제
* VLAN : 1대의 물리 Switch를 여러 대의 가상 Switch로 분할
    - Port : 물리포트 하나에 VLAN 할당
    - Tag : VLAN 정보를 프레임에 TAG로 붙임, 하나의 물리 포트/케이블로 여러 VLAN 프레임 전송
* Wireless LAN 연결 과정
    1. Association
        - 스캔
            - 무선 LAN 단말기는 AP로부터 SSID(무선 LAN 식별자)와 같은 정보 수집
            - 접속할 SSID를 발견하면 Probe Req를 AP로 전송
            - 전달받은 AP는 SSID와 같은 정보가 일치하면 Probe Resp 전송
        - 인증
        - 확인
            - 단말과 AP간 Association Req & Resp을 통해 접속 확립
    2. 인증
        - Association 단계 이후 AP는 비밀번호(퍼스널), 인증서 등(엔터프라이즈)으로 인증 수행
        - 인증 완료 시, 단말과 AP 간 마스터 키 생성
    3. 공유키 생성
        - 마스터 키를 통해 실제 암/복호화에서 사용하는 공유키 생성(4-way Handshake)
    4. 암호화 통신
        - 공유키 기반으로 암호화 통신
        - WPA2 : AES 암호화
* ARP
    - Operation Code : ARP 프레임 종류
        - 1(Request) : Broadcast
            ```
            Ethernet II, Src: 90:61:ae:fd:41:43, Dst: Broadcast (ff:ff:ff:ff:ff:ff)
            Address Resolution Protocol (request)
                Hardware type: Ethernet (1)
                Protocol type: IPv4 (0x0800)
                Hardware size: 6
                Protocol size: 4
                Opcode: request (1)
                Sender MAC address: 90:61:ae:fd:41:43
                Sender IP address: 192.168.0.80
                Target MAC address: 00:00:00:00:00:00
                Target IP address: 192.168.0.1
            ```
        - 2(Reply) : Unicast
            ```
            Ethernet II, Src: 90:5c:44:cc:03:a6, Dst: 90:61:ae:fd:41:43
            Address Resolution Protocol (reply)
                Hardware type: Ethernet (1)
                Protocol type: IPv4 (0x0800)
                Hardware size: 6
                Protocol size: 4
                Opcode: reply (2)
                Sender MAC address: 90:5c:44:cc:03:a6
                Sender IP address: 192.168.0.1
                Target MAC address: 90:61:ae:fd:41:43
                Target IP address: 192.168.0.80
            ```
    - 단계
        1. 데이터 송신 시 송신측 단말은 IP 패킷에 포함된 수신지 IP 주소를 자신의 ARP 테이블에서 조회 후 없는 경우 ARP Request 준비
        2. ARP Request의 각 필드를 조합한다.
            - OPcode : 1(ARP Request)
            - Sender MAC/IP 주소 : 송신측 단말 MAC/IP 주소 
            - Target MAC/IP 주소 : Dummy MAC 주소(00:00...)와 수신지 IP 주소
        3. 같은 네트워크의 모든 단말에 ARP Request를 전달한다.
            - 이더넷 프레임의 수신지 MAC 주소 : Broadcast 주소(ff:ff...)
            - 수신측 단말은 요청을 받아들이고 ARP Reply 준비
            - 그외 단말은 프레임을 파기한다.
        4. ARP Reply의 각 필드를 조합한다.
            - OPcode : 2(ARP Reply)
            - Sender MAC/IP 주소 : 수신측 단말 MAC/IP 주소 
            - Target MAC/IP 주소 : 송신측 단말 MAC/IP 주소
        5. 송신측 단말에 ARP Reply를 전달한다.
            - 이더넷 프레임의 수신지 MAC 주소 : 송신측 단말 MAC 주소 - Unicast
        6. 송신측 단말은 전달받은 ARP Reply의 Sender MAC/IP 주소를 인식하고 ARP 테이블에 일정 기간 등록한다.(ARP Cache)
### 3. Network
- IP Header field
    1. Version : IPv4(0100)
    2. Header Length : 5(IPv4 : 20Byte = 32bit * 5)
    3. Type of Service : IPv4 패킷 우선도
    4. Packet Length : 패킷 전체 길이(=MTU), IPv4 Header(20Byte) + IPv4 Payload(1480Byte)
    5. IP fragmentation field : 패킷이 MTU보다 커서 분할할 때 사용하는 필드
        - Identification : Packet ID, 분할된 패킷을 받은 단말이 재결합할 때 참조하는 필드
        - Flag 
            - 1st : 사용 X
            - 2nd : Don't Fragment(0: Allow, 1: Deny)
            - 3rd : More Fragments(0: End, 1: Continue)
        - Offset : 패킷 분할 순서, 0부터 시작
    6. Time To Live : Hop Count, 라우터 경유할 때마다 1씩 감소, 0이면 패킷 파기
        - 파기한 라우터는 Time to live exceed라는 ICMPv4 패킷을 송신지에 반환
    7. Protocol Number : IPv4 Payload 프로토콜 종류, TCP = 6
    8. Header Checksum : 오류 체크
    9. 송/수신지 IPv4 주소
- Subnet Mask
    - 192.168.100.1/24
        - 네트워크 주소 : 어떤 IPv4 네트워크에 속해있는가
        - 호스트 주소 : 어떤 단말인가
    - 예외 주소
        - 네트워크 주소 : 호스트 비트가 모두 '0', 네트워크 자체
            - 192.168.100.0
            - 0.0.0.0/0 : 기본 경로 주소
        - 브로드캐스트 주소 : 호스트 비트가 모두 '1', 같은 네트워크에 속한 모든 단말
            - 192.168.100.255
            - 255.255.255.255/32 : 리미티드 브로드캐스트 주소, 모든 단말
        - 루프백 주소 : localhost
            - 127.0.0.1/8
- Dynamic Allocation
    - DHCPv4 : 네트워크에 연결하기 위해 필요한 설정(IPv4 주소, Default G/W, DNS IP 주소 등
)을 제공하는 프로토콜
        - 클라이언트가 브로드캐스트로 요청 전송하면 해당 DHCPv4 서버가 필요한 설정을 유니캐스트로 전달
    - DHCP Relay Agent : 많은 네트워크가 있는 경우 1대의 DHCP 서버로 관리 가능하도록 DHCP 패킷을 유니캐스트로 변환하여 클라이언트로부터 첫 번째 라우터(또는 홉)까지 전달되도록 설정하는 기능
