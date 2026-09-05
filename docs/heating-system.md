# Honeywell / Resideo 난방 시스템

[지식 지도](knowledge-map.md) | [BAHA 난방 패킷](heater-node-40-90.md) | [출처 목록](../reference/sources.md)

제조사 설명서에서 확인한 통신 구조와 모델별 동작을 정리한다. BAHA `40 90`, `81` / `85`, XOR, `T0`, 외출 비트 `0x40`의 해석은 설명서가 아닌 [저장소의 실측](heater-node-40-90.md)에 근거한다.

## 통신 구간

MC200 계열은 난방과 홈네트워크에 서로 다른 통신 구간을 사용한다. 아래는 문서에 나온 기본 구조이며, 세부 구성은 모델에 따라 다르다. [S10, p23](../reference/sources.md#s10)

```mermaid
flowchart LR
    T["난방 온도조절기"] <-->|"DC 12V PLC"| C["MC200 계열 제어기"]
    C <-->|"RS485"| H["홈네트워크"]
    classDef device fill:#f1f5f9,stroke:#94a3b8,color:#1e293b
    class T,C,H device
```

| 자료와 대상 | 확인된 내용 | 근거 |
| --- | --- | --- |
| Resideo 2025 카탈로그의 MC200 계열 | 난방 DC12V PLC와 홈네트워크 RS485를 별도 인터페이스로 기재 | [S10, p23](../reference/sources.md#s10) |
| DT350IF-T / DT300F-S 설명서 | `FE`: MC200F ↔ DT300F의 PLC 통신 오류 | [S11, 인쇄 p13](../reference/sources.md#s11) |
| 같은 설명서 | `FF`: MC200F ↔ FCU의 RS485 통신 오류 | [S11, 인쇄 p13](../reference/sources.md#s11) |

FCU의 RS485와 홈네트워크의 RS485는 구분해야 한다. BAHA `40 90`을 이 구조의 어느 제어기나 변환기에 대응시킬지는 아직 **추론**이다. 통신 구간이 나뉘어 있다면 월패드에서 방별 온도 테이블은 보여도 온도조절기 버튼의 원래 통신은 보이지 않을 수 있다.

## 방 수와 모델명

BAHA 실측의 `DL=06` 테이블은 타입 1바이트와 방 5바이트로 구성된다. 방 이름과 순서는 시험 환경에서 확인한 매핑이다.

- MC200-00~70 / HT 계열은 6존, 소형 N / TFT 계열은 4존 또는 6존으로 기재된다. [S10, p23](../reference/sources.md#s10)
- LT200 화면은 **거실 + 방 1~5**, 총 6개 위치를 표시한다. BAHA의 5슬롯과는 다르다. [S15, 인쇄 p1 / PDF p3](../reference/sources.md#s15)
- `MC200-50`의 `-50`은 보일러 통신 변형을 가리키며 방 개수가 아니다. [S16](../reference/sources.md#s16)
- DT100 / DT200도 접미사에 따라 전원과 배선이 다르다. DT200-R은 DC12V PLC / MC10 호환, DT100-R은 AC220V 3선 독립형이다. [S10, p22](../reference/sources.md#s10)

## 외출과 OFF

외출과 OFF의 의미는 제품과 조작 경로에 따라 다르다.

| 대상 | 외출 / OFF 동작 | 근거 |
| --- | --- | --- |
| 본 저장소의 BAHA `40 90` | `C0` 명령 뒤 외출 목표 `CA` = 10 C 관찰. 단일 방 `CA` 직접 쓰기도 확인 | [실측 패킷](heater-node-40-90.md) |
| LT200 | 초기 외출 목표 10 C; 외출 해제 시 이전 설정온도로 복귀 | [S15, 인쇄 p4 / PDF p6](../reference/sources.md#s15) |
| DT350IF-T / DT300F-S | 외출 해제 시 이전 설정 복귀. 별도 장기 정지 `OFF`에서도 5 C 이하 자동 난방 | [S11, 인쇄 p4~5, p9](../reference/sources.md#s11) |
| 구형 DT100, 2002년 설명서 | 외출 기본값 15 C, 조절 가능. 물리 전원 OFF 시 동파방지 비활성 | [S12, PDF p1](../reference/sources.md#s12) |
| LG U+ DT300W-M / R 앱 | 전체 난방 끄기 = 외출 전환. 10 C 이하 자동 난방 | [S14](../reference/sources.md#s14) |

BAHA에서 실제 저온의 자동 난방은 시험하지 않았다. 다른 모델의 동파방지 설명을 이 실측의 근거로 삼지 않는다. 공개 ESPHome 구현의 OFF 처리도 별도로 확인해야 한다. [구현 비교](esphome-external-component.md)

## 설정온도와 적용 시점

DT350IF-T / DT300F-S와 LT200의 난방 설정 범위는 5~35 C로, BAHA 실측 기록의 범위와 같다. 다만 각 온도조절기의 사양이지 BAHA 쓰기 프레임의 검증 결과는 아니다. [S11](../reference/sources.md#s11), [S15](../reference/sources.md#s15)

LG U+ 앱은 1 C씩 변경한 뒤 `적용`을 눌러야 한다. 같은 안내는 MC200을 유지하고 온도조절기만 DT300W-M으로 교체하는 경우를 설명한다. 이 절차는 해당 제품에 한정되며 BAHA의 호환성이나 명령 적용 시점을 뜻하지 않는다. [S14](../reference/sources.md#s14)

## 설명서를 더 찾을 때

MC200-XX와 DT100 / DT200의 다른 개정판은 [자료실 목록 S13](../reference/sources.md#s13)에서 찾을 수 있다. 검색 색인에서만 발견한 자료는 본문을 확인한 자료와 구분해 표시했다.

중국어권 DT200-M01 Modbus 문서와 산업용 MC200 제어기는 이름이 겹치는 별개 제품이다. 한국형 난방 시스템이나 BAHA의 UART 설정·주소표로 사용하지 않는다.
