# BAHA 월패드 지식베이스

빠른 이동: [지식 지도](docs/knowledge-map.md) | [프로토콜 개요](docs/protocol-overview.md) | [공개 출처 목록](reference/sources.md) | [미확인 사항](docs/open-questions.md) | [자료 기여](CONTRIBUTING.md)

삼성중공업 BAHA 월패드의 모델 정보, RS485 패킷, 난방 설명서와 공개 구현을 정리한다. `BHWP-2711C/A`의 실측을 중심으로, 다른 모델의 자료에는 출처와 확인 범위를 함께 표시한다.

**자료 확인일: 2026-09-05** · [출처 목록](reference/sources.md) · [검색 범위](reference/search-coverage.md)

## 확인된 패킷

| 노드 | 용도 | 상태 |
| --- | --- | --- |
| [`10 04`](docs/lighting-node-10-04.md) | 4채널 조명 | 상태 응답과 제어 동작 실측 |
| [`10 06`](docs/lighting-node-10-04.md) | 6채널 조명 | 외부 작성자의 쓰기 명령; 조회·응답 미확인 |
| [`1F 0F`](docs/master-switch-node-1f0f.md) | 현관·일괄소등 | 상태 응답과 제어 동작 실측; 내부 역할 미확인 |
| [`40 90`](docs/heater-node-40-90.md) | 난방 | 5개 방 슬롯의 온도·외출 상태와 쓰기 실측 |
| `30 80`, `31 80` | 역할 미확인 | 반복 조회 프레임만 관찰 |

실측 버스의 기본 형식:

| 항목 | 값 |
| --- | --- |
| UART | `9600 8N1` |
| 프레임 길이 | 데이터 길이 `DL` + 7바이트 |
| 체크섬 | 시작 `02`부터 데이터 끝까지 XOR |
| 종료 바이트 | `00` |

조명은 비트마스크로 제어한다. 예를 들어 4채널의 capability는 `0F`로, 채널 수를 나타내는 노드 바이트 `04`와 다르다. 자세한 형식과 6채널의 확인 범위는 [조명 문서](docs/lighting-node-10-04.md)를 참고한다.

## 읽을 거리

| 목적 | 문서 |
| --- | --- |
| 모델과 제품 계보 확인 | [모델 식별표](docs/model-family.md), [실물 라벨·PCB 사진](docs/hardware.md) |
| 패킷 구조와 체크섬 이해 | [프로토콜 개요](docs/protocol-overview.md) |
| 난방 장치의 연결과 모드 비교 | [난방 시스템](docs/heating-system.md) |
| ESPHome 구현 검토 | [지원 범위와 알려진 차이](docs/esphome-external-component.md) |
| 원문과 실측 근거 확인 | [출처 목록](reference/sources.md), [과거 조사 기록](reference/README.md) |
| 다른 주제 찾기·자료 추가 | [지식 지도](docs/knowledge-map.md), [미확인 사항](docs/open-questions.md), [기여 안내](CONTRIBUTING.md) |

## 적용 범위

실측 결과는 한 설치 환경에서 확인한 동작이다. 모델·펌웨어·배선에 따라 차이가 있을 수 있으며, 제품 소개의 지원 기능만으로 특정 패킷의 동작을 판단할 수는 없다. 각 문서에서 실측, 외부 제보, 제품 자료와 추론을 구분한다.

공개 [ESPHome 컴포넌트](https://github.com/mahlernim/esphome-samsung-baha-rs485)는 별도 저장소에서 관리한다. 확인한 버전에는 난방 외출 온도 해석과 지원 채널 수의 제약이 있으므로 [구현 비교](docs/esphome-external-component.md)를 먼저 읽는다.

## 문서 검증

Python 3.10 이상에서 실행한다. 문서 내부 링크와 완전한 패킷 예제의 길이·XOR를 검사하며, 장치나 네트워크에 접속하지 않는다.

```sh
python scripts/check_knowledgebase.py
```

검색 별칭: **BAHA · BaHa-Cube · 삼성중공업 · Samsung Heavy Industries · BHWP-2711 · BHWP-2711C/A · BAHA-W-2030A · RS485 · Honeywell MC200**
