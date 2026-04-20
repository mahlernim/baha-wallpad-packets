# ESPHome 구현 저장소

상위 문서: [README](../README.md)  
관련 문서: [프로토콜 개요](protocol-overview.md) | [거실 조명 `10 04`](lighting-node-10-04.md) | [현관 / 일괄소등 `1F 0F`](master-switch-node-1f0f.md) | [난방 `40 90`](heater-node-40-90.md)

ESPHome 구현은 패킷 문서 저장소와 분리해 별도 저장소로 옮김.

저장소:

- [esphome-samsung-baha-rs485](https://github.com/mahlernim/esphome-samsung-baha-rs485)

## 분리한 이유

- 이 저장소는 패킷 구조, 노드 의미, 실측 근거를 남기는 쪽이 중심임.
- ESPHome 코드는 사용법, 이슈, 배포 방식이 달라 별도 저장소가 더 깔끔함.
- 두 저장소는 서로 참조만 하고 역할은 분리하는 편이 유지보수에 유리함.

## 그쪽 저장소에 들어 있는 것

- ESPHome 외부 컴포넌트
- 공개용 예제 YAML
- `climate` 대신 `switch`를 쓴 이유와 현재 제약
- 패킷 문서 저장소로 가는 링크

그 구현은 온도조절기처럼 목표 온도를 오래 유지하는 방식보다, 자동화에서 짧게 난방 요청을 넣는 운용을 기준으로 잡아 두었음.

패킷 해석과 근거는 계속 이 저장소를 기준으로 보면 됨.
