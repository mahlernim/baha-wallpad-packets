# ESPHome 구현의 지원 범위와 버전별 차이

[README](../README.md) | [지식 지도](knowledge-map.md) | [난방 패킷](heater-node-40-90.md) | [출처 목록](../reference/sources.md)

ESPHome 외부 컴포넌트와 예제 YAML은 [mahlernim/esphome-samsung-baha-rs485](https://github.com/mahlernim/esphome-samsung-baha-rs485)에서 관리한다. 이 지식베이스는 패킷 해석과 실측 근거를 정리한다.

**[v0.1.1](https://github.com/mahlernim/esphome-samsung-baha-rs485/releases/tag/v0.1.1)은 외출 온도 디코더와 외출 해제 요청을 수정한다.** 초기 조사에서 확인한 `f9dfed0`의 분석은 아래에 이력으로 남겼다. 실제 장비에 배포된 펌웨어는 확인하지 않았으며, 릴리스가 곧 장비 업데이트를 뜻하지는 않는다. [수정 전 코드 S30](../reference/sources.md#s30), [v0.1.1 S35](../reference/sources.md#s35)

## v0.1.1의 수정 범위

현재 온도 응답 `81`과 목표 온도 응답 `85`에서 `0x80`이 설정된 인코딩 값은 하위 6비트(`value & 0x3F`)를 온도로 읽는다. `0x40` 외출 비트는 온도에 더하지 않으므로 `E0`는 32 C, `CA`는 10 C로 해석한다. `0x80`이 없는 raw 바이트를 그대로 온도로 읽는 기존 fallback은 유지한다. [S35](../reference/sources.md#s35)

목표온도의 숫자가 같아도 외출 상태에서 일반 설정으로 전환하는 요청은 생략하지 않는다. 현재·목표 응답은 따로 도착하므로, 어느 한쪽이라도 외출 상태이면 일반 설정 쓰기를 보낸다. 회귀 테스트에서는 현재 9 C, 외출 목표 10 C에서 기본 On(+1 C)을 요청하면 일반 목표 10 C 쓰기를 보내는지 확인한다. 이 경계 사례는 합성 패킷을 이용한 코드 검증이며, 디코더 수정 후에도 필요한 모드 전환 쓰기를 유지하기 위한 것이다. [S35](../reference/sources.md#s35)

설정 스키마, raw 바이트 fallback, 조명 4채널 지원, 난방 On / Off 증감값(델타)은 그대로다. 이 패치는 실제 장비의 버너·밸브 피드백이나 6채널 조명 지원을 추가하지 않는다.

## 수정 전 `f9dfed0`의 외출 온도 해석

수정 전 코드에서 현재 온도 응답 `81`과 목표 온도 응답 `85`는 같은 디코더를 사용한다. 이 디코더는 `0x80` 이상인 값에서 `0x80`만 빼므로, 외출 비트가 켜진 온도를 64 C 높게 계산한다. [디코더](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L467-L472), [두 응답 처리](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L294-L318)

| 인코딩 바이트 | 수정 전 `f9dfed0` | v0.1.1의 온도·실측 모드 해석 |
| --- | --- | --- |
| `A0` | 32 C | 일반, 32 C |
| `E0` | 96 C | 외출, 32 C |
| `CA` | 74 C | 외출, 10 C |

위 인코딩 값의 실측 규칙은 `temperature = value & 0x3F`, `away = (value & 0x40) != 0`이다. 표의 96 C는 수정 전 코드가 계산한 값이며 장비가 측정한 온도가 아니다. 모드는 패킷의 의미를 설명한 것으로, 별도 외출 엔티티의 제공 여부를 뜻하지 않는다. [7월 실측 정정](../reference/sources.md#s40)

수정 전 오류는 난방 요청에도 영향을 줄 수 있다. 잘못 계산한 현재 온도에 On / Off 델타를 더하면, 요청 목표가 상한인 35 C로 제한될 수 있다. 이는 해당 코드에서 도출한 영향이며 실제 장비에서 관찰한 동작은 아니다. v0.1.1은 인코딩 온도를 바로 읽도록 수정하며 델타와 범위 제한은 유지한다. [이전 요청 계산](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L119-L129), [이전 범위 제한](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L474-L476), [S35](../reference/sources.md#s35)

## 엔티티와 지원 범위

다음 범위는 v0.1.1에서도 유지된다. 이전 코드의 위치와 수정 릴리스를 함께 연결했다.

| 항목 | 코드의 동작 | 적용 범위와 한계 |
| --- | --- | --- |
| 조명 | `LIGHT_COUNT=4`, 노드 `10 04` 고정 | `10 06` 지원에는 코드 변경이 필요함 |
| 난방 switch | 현재 온도에 On / Off 델타를 더한 일반 설정온도를 요청 | `C0` / `CA` 외출 명령이나 릴레이 정지 명령과 다름 |
| switch 상태 | 목표 온도가 현재 온도보다 높은지 비교 | 실제 버너 / 밸브의 동작 피드백은 제공하지 않음 |
| 수신과 조회 | 응답이 없거나 오래되면 조회 프레임을 송신 | 수신만 하는 설정으로 취급하면 안 됨 |

근거: [이전 상수](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.h#L96-L104), [이전 난방 요청](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L106-L134), [이전 상태 비교](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L434-L443), [이전 fallback 조회](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L321-L342), [v0.1.1 소스](../reference/sources.md#s35).

## 프레이밍과 다른 구현

파서는 다섯 번째 바이트를 데이터 길이 `DL`로 읽고, 전체 길이 `DL + 7`, 마지막 `00`, XOR를 검사한다. 최대 버퍼 / 프레임 길이와 타이머 값은 이 구현의 설정이며 제조사 규격을 뜻하지 않는다. [수신 파서](https://github.com/mahlernim/esphome-samsung-baha-rs485/blob/f9dfed0b3806cecc10e8c323c0d61206ebb57789/components/baha_rs485/baha_rs485.cpp#L185-L224)

다른 `Samsung` 프로젝트를 비교할 때도 대상 모델을 먼저 확인한다. [S32](../reference/sources.md#s32), [S33](../reference/sources.md#s33), [S34](../reference/sources.md#s34)는 **Samsung SDS용**이라고 명시한 자료다. BAHA에 적용하려면 이름뿐 아니라 정확한 모델, 프레임 문법, 해당 커밋의 지원 범위를 대조해야 한다.
