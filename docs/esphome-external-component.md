# 공개 ESPHome 구현과 패킷 문서의 차이

[README](../README.md) | [지식 지도](knowledge-map.md) | [난방 패킷](heater-node-40-90.md) | [출처 목록](../reference/sources.md)

ESPHome 외부 컴포넌트와 예제 YAML은 [mahlernim/esphome-samsung-baha-rs485](https://github.com/mahlernim/esphome-samsung-baha-rs485)에서 관리한다. 이 지식베이스는 패킷 해석과 실측 근거를 정리한다.

**2026-09-05 기준 공개 커밋 `f9dfed0`에는 2026년 7월에 확인한 외출 온도 해석이 반영되지 않았다.** 아래 비교는 이 커밋의 코드 분석 결과다. 실제 장비에 배포된 펌웨어는 확인하지 않았다. [S30](../reference/sources.md#s30)

## 외출 온도 디코더

현재 온도 응답 `81`과 목표 온도 응답 `85`는 같은 디코더를 사용한다. 이 디코더는 `0x80` 이상인 값에서 `0x80`만 빼므로, 외출 비트가 켜진 온도를 64 C 높게 계산한다. [디코더](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L467-L472), [두 응답 처리](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L294-L318)

| 바이트 | 해당 코드의 계산 | 실측에 맞는 비트 해석 |
| --- | --- | --- |
| `A0` | 32 C | 일반, 32 C |
| `E0` | 96 C | 외출, 32 C |
| `CA` | 74 C | 외출, 10 C |

실측에 맞는 규칙은 `temperature = value & 0x3F`, `away = (value & 0x40) != 0`이다. 표의 96 C는 코드가 계산한 값이며 장비가 측정한 온도가 아니다. [7월 실측 정정](../reference/sources.md#s40)

이 오류는 난방 요청에도 영향을 줄 수 있다. 잘못 계산한 현재 온도에 On / Off 증감값(델타)을 더하면, 요청 목표가 상한인 35 C로 제한될 수 있다. 이는 코드에서 도출한 영향이며 실제 장비에서 관찰한 동작은 아니다. [요청 계산](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L119-L129), [범위 제한](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L474-L476)

## 엔티티와 지원 범위

| 항목 | 코드의 동작 | 적용 범위와 한계 |
| --- | --- | --- |
| 조명 | `LIGHT_COUNT=4`, 노드 `10 04` 고정 | `10 06` 지원에는 코드 변경이 필요함 |
| 난방 switch | 현재 온도에 On / Off 델타를 더한 일반 설정온도를 요청 | `C0` / `CA` 외출 명령이나 릴레이 정지 명령과 다름 |
| switch 상태 | 목표 온도가 현재 온도보다 높은지 비교 | 실제 버너 / 밸브의 동작 피드백은 제공하지 않음 |
| 수신과 조회 | 응답이 없거나 오래되면 조회 프레임을 송신 | 수신만 하는 설정으로 취급하면 안 됨 |

근거: [상수](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.h#L96-L104), [난방 요청](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L106-L134), [상태 비교](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L434-L443), [fallback 조회](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L321-L342).

## 프레이밍과 다른 구현

파서는 다섯 번째 바이트를 데이터 길이 `DL`로 읽고, 전체 길이 `DL + 7`, 마지막 `00`, XOR를 검사한다. 최대 버퍼 / 프레임 길이와 타이머 값은 이 구현의 설정이며 제조사 규격을 뜻하지 않는다. [수신 파서](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L185-L224)

다른 `Samsung` 프로젝트를 비교할 때도 대상 모델을 먼저 확인한다. [S32](../reference/sources.md#s32), [S33](../reference/sources.md#s33), [S34](../reference/sources.md#s34)는 **Samsung SDS용**이라고 명시한 자료다. BAHA에 적용하려면 이름뿐 아니라 정확한 모델, 프레임 문법, 해당 커밋의 지원 범위를 대조해야 한다.
