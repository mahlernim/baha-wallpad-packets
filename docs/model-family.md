# BAHA 모델과 사업 계보

[지식 지도](knowledge-map.md) | [실물 하드웨어](hardware.md) | [출처 목록](../reference/sources.md)

## 모델 식별표

BAHA는 여러 모델을 포함한 제품군이다. 이 문서에서는 접미사까지 원문 그대로 적는다. `BHWP-2711`과 `BHWP-2711C/A`의 하드웨어·펌웨어가 같다고 가정하지 않으며, 외부 자료의 `BAHA-W-2030A`도 `BHWP-2030A`로 바꾸지 않는다.

| 모델·표기 | 알려진 내용 | 출처와 참고 사항 |
| --- | --- | --- |
| `BHWP-2711C/A` | 이 저장소에서 라벨·PCB를 촬영하고 RS485를 실측한 모델 | [하드웨어](hardware.md). 이 접미사까지 일치하는 공식 설명서는 아직 찾지 못함 |
| `BHWP-2711`, `BaHa-Cube Series 2` | 7인치 LCD를 갖춘 삼성중공업 BAHA 제품. INNOdesign의 디자인 기록에도 등장 | [S01](../reference/sources.md#s01), [S02](../reference/sources.md#s02). `C/A` 모델의 세부 규격은 확인되지 않음 |
| `BHWP-2001` | 10.2인치 LCD를 소개한 별도 모델 | [S06](../reference/sources.md#s06). `2711`과의 패킷 호환성은 미확인 |
| `BHWP-2720A` | 7인치 BAHA 월패드. 2008년 굿디자인 선정 | [S03](../reference/sources.md#s03). `2711C/A`와 구분되는 모델 |
| `BAHA-W-2030A` | 작성자가 이 모델명으로 `10 04`·`10 06` 조명 명령표를 공개 | [S31](../reference/sources.md#s31). 모델 사진과 응답 캡처가 없는 외부 제보 |
| `BHWP-2011C/AW`, `BHWP-2011C/A` | 수리 사례에 기재된 모델 | [S09](../reference/sources.md#s09). `2011`과 `2711`은 다르며, 개별 사례로 고장률이나 공통 수리법을 알 수는 없음 |

KIDP의 치수·무게에는 단위 오류로 보이는 값이 있다. `2711`의 길이는 `310 cm`, `2720A`의 무게는 `1000 kg`으로 표시되어 있다. 이를 사양으로 채택하거나 임의로 mm·g로 고치지 않았다. 실제 치수와 설치 규격은 별도 자료가 필요하다. [S02](../reference/sources.md#s02), [S03](../reference/sources.md#s03)

## 제품 소개에 나오는 기능

BHWP-2711의 제품 소개에는 조명·가스·커튼 제어, 통화, 비상 알림, 메모, 공지, 웹 원격제어가 나온다. 당시 소개된 기능의 범위이며, 모든 설치에 해당 기능이 갖춰졌다는 뜻은 아니다. 가스나 커튼을 제어하는 **BAHA RS485 주소와 프레임**도 이 자료에는 없다. [S02](../reference/sources.md#s02)

iF의 `BaHa-Cube Series 2` 기록은 영문 제품명과 제조사·디자이너를 찾을 때 유용하다. 직접 열면 일부 조회에서 403 오류가 발생해, 검색 색인의 설명을 다른 1차 자료와 함께 확인했다. [S01](../reference/sources.md#s01)

## 제품과 사업의 주요 이력

| 시점 | 이력 | 출처와 참고 사항 |
| --- | --- | --- |
| 2007 | BHWP-2711, KIDP 굿디자인 선정 | 제품 선정연도이며 실측 장비의 생산연도를 뜻하지 않음. [S02](../reference/sources.md#s02) |
| 2008 | INNOdesign 수상 이력에 Baha Cube Series2 기재. 별도로 BHWP-2720A 굿디자인 선정 | 서로 다른 모델·행사의 기록. [S07](../reference/sources.md#s07), [S03](../reference/sources.md#s03) |
| 2010 | Pentabreed가 삼성중공업 BAHA GUI 프로젝트 수상 소식 게시 | GUI 제작 이력으로, OS·펌웨어 버전은 알 수 없음. [S08](../reference/sources.md#s08) |
| 2015-06-22 | SK텔레콤이 YPP의 삼성 BAHA 솔루션 인수, VRID 브랜드와 스마트홈 제휴 소개 | 발표일이며 인수 완료일이나 현재 서비스 상태를 뜻하지 않음. [S04](../reference/sources.md#s04) |

## BAHA와 Samsung SDS

삼성중공업 BAHA와 YPP·VRID의 관계는 [2015년 SK텔레콤 발표](../reference/sources.md#s04)에서 확인할 수 있다. Samsung SDS의 공식 안내는 **자사** 도어락·월패드 사업의 매각과 직방의 지원을 설명한다. 이 안내에 삼성중공업 BAHA가 포함된다는 근거는 없다. [S05](../reference/sources.md#s05)

패킷 형식도 다르다. 이 저장소의 BAHA 예제는 시작 바이트 `02`, 길이 `DL`, XOR 체크섬, 끝 바이트 `00`을 사용한다. 공개 Samsung SDS 분석에는 `AC`·`AE` 등의 명령, `B0` 응답, 최상위 비트를 제거한 XOR가 나온다. 서로 다른 분석 대상이므로 SDS 주소표로 BAHA의 미확인 노드를 해석할 수는 없다. [프로토콜 개요](protocol-overview.md), [S32](../reference/sources.md#s32)

## 원격 서비스와 로컬 버스

제품 소개의 웹 원격제어와 2015년 플랫폼 제휴는 당시의 기능·사업을 설명한다. 제휴 발표에서도 신형과 구형 설치를 구분하고, 구형에는 추가 인프라 업그레이드가 필요하다고 밝혔다. 현재 월패드의 앱 지원 여부는 이 기록만으로 알 수 없다. [S02](../reference/sources.md#s02), [S04](../reference/sources.md#s04)

공개 BAHA 서버 프로토콜, 인증 절차, 현행 서비스 호환표는 아직 확인하지 못했으며 [미확인 사항](open-questions.md)에 남겨 두었다. 외부 저장소의 설명에 `삼성바하 월패드패킷 및 서버 데이터`가 등장하지만, 확인한 커밋에는 조명 README만 있어 서버 프로토콜의 근거로 삼을 수 없다. [S31](../reference/sources.md#s31)
