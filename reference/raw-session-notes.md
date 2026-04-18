# Protocol Notes

Curated docs: [README](../README.md) | [프로토콜 개요](../docs/protocol-overview.md) | [하드웨어](../docs/hardware.md) | [거실 조명](../docs/lighting-node-10-04.md) | [현관 / 일괄소등](../docs/master-switch-node-1f0f.md) | [난방](../docs/heater-node-40-90.md) | [참고 자료](README.md)

## Environment

- Date of first successful session: 2026-04-18
- Host location/timezone during capture: Asia/Seoul
- USB-RS485 adapter: Silicon Labs CP210x
- Working host serial port during testing: `COM5`
- Verified UART settings: `9600 8N1`

## Framing Notes

Observed frames commonly end with `00`.

The penultimate byte behaves like an XOR checksum over the preceding bytes in the frame payload.

Examples:

- `02 30 80 01 00 B3 00`
  - `02 ^ 30 ^ 80 ^ 01 ^ 00 = B3`
- `02 10 04 02 02 01 01 16 00`
  - `02 ^ 10 ^ 04 ^ 02 ^ 02 ^ 01 ^ 01 = 16`
- `02 10 04 02 02 01 00 17 00`
  - `02 ^ 10 ^ 04 ^ 02 ^ 02 ^ 01 ^ 00 = 17`

## Idle / Background Traffic

Periodic frames seen while the system was idle:

```text
02 30 80 01 00 B3 00
02 31 80 01 00 B2 00
02 1F 0F 01 00 13 00
```

These appear to be heartbeat or periodic polling traffic on the wider RS485 network.

## Lighting Node

The lighting-related node/function bytes appear to be:

```text
10 04
```

### Likely Poll Request

```text
02 10 04 01 00 17 00
```

This frame repeats frequently and is followed by the lighting status reply.

### Likely Status Response

Observed replies:

```text
02 10 04 81 02 0F 00 9A 00
02 10 04 81 02 0F 01 9B 00
```

Confirmed interpretation:

- `81` is the response to request type `01`
- the sixth byte `0F` is the fixed 4-channel capability mask for this node
- the seventh byte is the live light-state bitmask

## Verified Light Commands

These commands were transmitted and confirmed by physical light behavior.

### On Commands

```text
l1_on  = 02 10 04 02 02 01 01 16 00
l2_on  = 02 10 04 02 02 02 02 16 00
l3_on  = 02 10 04 02 02 04 04 16 00
l4_on  = 02 10 04 02 02 08 08 16 00
```

### Off Commands

```text
l1_off = 02 10 04 02 02 01 00 17 00
l2_off = 02 10 04 02 02 02 00 14 00
l3_off = 02 10 04 02 02 04 00 12 00
l4_off = 02 10 04 02 02 08 00 1E 00
```

## Verified Living Room Button Mapping

The living room wallpad buttons were pressed in this order during capture:

1. light 1
2. light 2
3. light 3
4. light 4
5. all off
6. all on

The starting state was all lights off.

### Initial Status

```text
02 10 04 81 02 0F 00 9A 00
```

Current interpretation:

- the seventh byte is a light-state bitmask
- `00` means all four lights off

### Individual Light Buttons

Pressing each individual wallpad button produced the following command and status transitions:

```text
light 1: 02 10 04 02 02 01 01 16 00 -> status 01
light 2: 02 10 04 02 02 02 02 16 00 -> status 03
light 3: 02 10 04 02 02 04 04 16 00 -> status 07
light 4: 02 10 04 02 02 08 08 16 00 -> status 0F
```

Observed status response frames:

```text
02 10 04 81 02 0F 01 9B 00
02 10 04 81 02 0F 03 99 00
02 10 04 81 02 0F 07 9D 00
02 10 04 81 02 0F 0F 95 00
```

This confirms a four-bit light state mask:

```text
01 = light 1
02 = light 2
04 = light 3
08 = light 4
```

### All Off Button Behavior

The wallpad "all off" button did not emit a special aggregate command in the observed capture.

Instead, it emitted four ordinary per-light off commands in rapid succession:

```text
02 10 04 02 02 01 00 17 00 -> status 0E
02 10 04 02 02 02 00 14 00 -> status 0C
02 10 04 02 02 04 00 12 00 -> status 08
02 10 04 02 02 08 00 1E 00 -> status 00
```

### All On Button Behavior

The wallpad "all on" button also appeared to emit four ordinary per-light on commands in rapid succession:

```text
02 10 04 02 02 01 01 16 00 -> status 01
02 10 04 02 02 02 02 16 00 -> status 03
02 10 04 02 02 04 04 16 00 -> status 07
02 10 04 02 02 08 08 16 00 -> status 0F
```

### Confirmed Status Byte Mapping

From the observed transitions:

```text
00 = all off
01 = light 1 on
03 = lights 1 and 2 on
07 = lights 1, 2, and 3 on
0F = lights 1, 2, 3, and 4 on
0E = lights 2, 3, and 4 on
0C = lights 3 and 4 on
08 = light 4 on
```

This strongly confirms that the status byte is a straightforward ORed light mask.

### Confirmed Compound Light Commands

Live tests on 2026-04-18 confirmed that `10 04` accepts aggregate bitmasks directly, not just single-light writes.

Observed working examples:

```text
lights 1+2 on  = 02 10 04 02 02 03 03 16 00 -> status 03
lights 1+2 off = 02 10 04 02 02 03 00 15 00 -> status 00

all lights on  = 02 10 04 02 02 0F 0F 16 00 -> status 0F
all lights off = 02 10 04 02 02 0F 00 19 00 -> status 00
```

## Entrance "Master Lights Off" Switch

After connecting the entrance switch, a new repeating request/response pair was observed:

```text
02 1F 0F 01 00 13 00
02 1F 0F 81 01 0A 98 00
```

Current interpretation:

- `1F 0F` is a distinct node/function pair from the living room lighting node `10 04`
- `02 1F 0F 01 00 13 00` looks like a poll/read request
- `02 1F 0F 81 01 0A 98 00` looks like the corresponding response

What is known:

- this traffic appeared only after the entrance switch wiring was added
- the `81` response pattern matches the request/response model seen on the living room lighting node

What is not yet proven:

- whether `1F 0F` is the entrance switch itself, a controller associated with it, or just a status participant introduced by that branch
- whether pressing the physical entrance button emits a unique command on `1F 0F`
- whether the entrance switch directly commands lights, or causes another controller to emit standard `10 04` lighting commands

Current best hypothesis:

- `1F 0F` is related to the entrance switch branch and is actively polled on the bus
- the actual living room light control commands still appear on `10 04`
- the entrance "master lights off" function may be implemented by triggering a burst of normal `10 04` per-light off commands rather than a dedicated broadcast frame

## `1F 0F` Active Probing Results

Direct polling was verified:

```text
02 1F 0F 01 00 13 00 -> 02 1F 0F 81 01 0A 98 00
```

Checksum validation was verified by sending an invalid checksum frame and receiving no response.

### Likely Writable Command Family

The node accepted a family of write-like frames of the form:

```text
02 1F 0F 02 01 <value> <xor_checksum> 00
```

Observed examples:

```text
02 1F 0F 02 01 08 19 00 -> immediate reply 02 1F 0F 81 01 08 9A 00
02 1F 0F 02 01 09 18 00 -> immediate reply 02 1F 0F 81 01 09 9B 00
02 1F 0F 02 01 0A 1B 00 -> immediate reply 02 1F 0F 81 01 0A 98 00
```

Rejected examples:

```text
02 1F 0F 02 01 00 11 00 -> no response
02 1F 0F 02 01 0B 1A 00 -> no response
02 1F 0F 02 01 0E 1F 00 -> no response
```

### Important Outcome

During active probing, the user confirmed that the master light switch behavior actually worked.

This means:

- `1F 0F` is not just a passive status node
- it does accept action/state-setting frames
- at least one accepted `02 01 <value>` command affects the real master-light function

### Current Interpretation

Working model for the entrance/master-switch node:

```text
02 1F 0F 01 00 13 00           ; read/poll current state
02 1F 0F 81 01 <value> <chk> 00 ; response/current state
02 1F 0F 02 01 <value> <chk> 00 ; set/request state
```

Confirmed observed state values:

```text
08
09
0A
```

Current best semantic mapping:

```text
09 = OFF
0A = ON
08 = transient/non-latched state
```

Additional conclusion about `08`:

- `08` is not the regular poll/read message
- `08` is accepted as a valid write value
- `08` produces an immediate `81 01 08` response
- the node returns to `0A` on the next poll when the stable state is ON
- `08` did not change the living-room light state during direct testing

Practical guidance:

- keep `08` documented for protocol completeness
- do not treat `08` as a normal user-facing ON/OFF state
- do not display `08` as a primary selectable state in a human-facing UI unless later evidence gives it a clear end-user meaning

## Confirmed Light Command Format

Working structure for light control:

```text
02 10 04 02 02 <channel_mask> <value_mask> <xor_checksum> 00
```

Where:

- `<channel_mask>` is the target light bit:
  - `01`, `02`, `04`, `08`
- `<value_mask>` is the desired state for that bit:
  - same as `<channel_mask>` for ON
  - `00` for OFF

This is consistent with the verified commands for four lights.

For compound writes, the same rule applies bitwise across the mask.

Examples:

```text
02 10 04 02 02 03 03 16 00 ; lights 1 and 2 ON
02 10 04 02 02 03 00 15 00 ; lights 1 and 2 OFF
02 10 04 02 02 0F 0F 16 00 ; all four ON
02 10 04 02 02 0F 00 19 00 ; all four OFF
```

## Heater Node `40 90`

After reversing the heater RS485 A/B pair, the heater node began responding consistently.

### Verified Poll Frames

```text
02 40 90 01 00 D3 00
02 40 90 05 00 D7 00
```

### Verified Response Frames

The heater responds with request/response opcode pairs similar to the other nodes:

```text
02 40 90 01 00 D3 00 -> 02 40 90 81 ...
02 40 90 05 00 D7 00 -> 02 40 90 85 ...
```

Clean polled responses captured from the current state:

```text
02 40 90 81 06 02 97 96 95 95 95 C3 00
02 40 90 85 06 02 93 94 94 94 88 DC 00
```

These are checksum-valid and each carries 5 room bytes, which fits the 5 heating rooms.

### Published Architecture Hints

Published Honeywell/Honeywell-service material changes the interpretation of these BAHA packets:

- The Honeywell `DT300F-S` manual and the associated service error sheet distinguish two different communication links:
  - `Err FE`: `MC200F` <-> `DT300F` `PLC` communication error
  - `Err FF`: `MC200F` <-> `FCU` `RS485` communication error
- The same `DT300F-S` manual describes local temperature adjustment as: press `up/down`, the setpoint flashes for about 5 seconds, then stops. That implies local user changes are applied automatically on the thermostat/controller side without any visible BAHA-side `Apply` UI.
- The older Honeywell `LT200` manual confirms the multi-room shape of the product family and shows a 5-room layout plus living room selection on the controller UI.
- The user-provided `KOCOM` ESPHome example uses the same Honeywell room model and indexes rooms in this order:

```text
0 = living room
1 = master bedroom
2 = playroom
3 = study
4 = bedroom
```

- LG U+ documentation for `DT300W-M` says homes with `MC200` keep the `MC200` controller and replace only the thermostat. That same UI documentation says changing temperature remotely requires selecting an explicit `Apply` button after adjusting the target temperature.

Current architectural conclusion:

- local wall thermostats are probably not speaking on the same BAHA RS485 segment we are sniffing
- they likely talk to `MC200F` over `PLC`
- the BAHA bus appears to see an aggregated `MC200` state interface, not necessarily the native thermostat command stream
- this explains why room-temperature button presses were often invisible on the BAHA capture, while polling still exposed stable 5-room tables

### Current Best Interpretation

Response layout:

```text
02 40 90 81 06 02 [r1] [r2] [r3] [r4] [r5] [chk] 00
02 40 90 85 06 02 [r1] [r2] [r3] [r4] [r5] [chk] 00
```

The `85` response currently matches known setpoints best.

At the time of polling, the user reported:

- master bedroom: 20 C
- study: 20 C
- playroom: 20 C
- living room: 19 C
- kids bedroom: expected to follow the same slot/value model as the other rooms; direct display confirmation was unavailable because the display is broken

Observed `85` payload:

```text
93 94 94 94 88
```

Working setpoint encoding hypothesis:

```text
encoded_temperature = 0x80 + temperature_celsius
```

This maps cleanly for the known rooms:

```text
0x93 = 19
0x94 = 20
```

So the current `85` payload is best interpreted as:

```text
[19, 20, 20, 20, 8]
```

or, more cautiously:

```text
[19, 20, 20, 20, unknown_low_or_fault_value]
```

The last byte `0x88` is treated as the kids-bedroom setpoint value in the same confirmed room ordering used by the other slots.

### Room Order

A plausible room ordering for the `85` payload is:

```text
living room, master bedroom, playroom, study, kids bedroom
```

Reasons:

- the first byte cleanly matches the only unique known setpoint at the time, the living room at `19 C`
- the published Honeywell multi-room manuals and the user-provided `KOCOM` example use a consistent five-room model
- the `KOCOM` example orders rooms as `living, master, playroom, study, bedroom`

This ordering is now treated as confirmed on BAHA by the later room-specific away, clear-away, and direct setpoint tests.

### About the `81` Response

Current `81` payload:

```text
97 96 95 95 95
```

This is clearly another 5-room table, but it does not map cleanly to the reported setpoints.

If the same `0x80 + value` encoding is applied here, then:

```text
97 96 95 95 95 -> 23, 22, 21, 21, 21
```

That is much more believable as current room temperatures than as target temperatures.

Confirmed interpretation:

- `85` = target temperature / configured setpoint table
- `81` = current measured temperature table on the same 5-room ordering

### Attempted Heater Write Hypotheses

Goal of the tests below:

- decrease the master bedroom setpoint by 1 C
- baseline `85` payload before testing:

```text
93 94 94 94 88
```

Target payload if the master bedroom is the second room byte:

```text
93 93 94 94 88
```

Tested hypotheses:

```text
bulk_cmd05      = 02 40 90 05 06 02 93 93 94 94 88 5B 00
bulk_cmd02      = 02 40 90 02 06 02 93 93 94 94 88 5C 00
room1_cmd05     = 02 40 90 05 03 02 01 93 44 00
room1_cmd06     = 02 40 90 06 03 02 01 93 47 00
room1_cmd02     = 02 40 90 02 03 02 01 93 43 00

room1_cmd06_raw = 02 40 90 06 03 02 01 13 C7 00
room1_cmd05_raw = 02 40 90 05 03 02 01 13 C4 00
room1_cmd06_np  = 02 40 90 06 02 01 13 C4 00
room1_cmd06_11  = 02 40 90 06 03 11 01 13 D4 00

bulk_cmd05_raw  = 02 40 90 05 06 02 13 13 14 14 08 DB 00
bulk_cmd06_raw  = 02 40 90 06 06 02 13 13 14 14 08 D8 00
```

Observed results:

- none of the tested write hypotheses changed the `85` setpoint table
- the table remained:

```text
02 40 90 85 06 02 93 94 94 94 88 DC 00
```

- frames using opcode `02` produced a generic reply:

```text
02 40 90 80 00 52 00
```

Earlier interpretation of `80 00`:

- initially treated as likely generic reject / unsupported-command response

Revised interpretation after later wallpad capture:

- `02 40 90 80 00 52 00` also appears immediately after real wallpad-originated `02 06 ...` command frames that do change heater state
- so it should no longer be treated as a confirmed reject
- it is more likely a generic command ACK/receipt or a controller-side response for command family `02`

Practical conclusion:

- the heater is structurally readable on `40 90`
- at this stage in the investigation, the direct write format for changing a room setpoint was still not mapped
- later tests did confirm a working room setpoint write on the same `02 06` action family

One useful clue from early passive captures:

- when the heater first became visible, the `85` room table changed over time while only `01/81` and `05/85` traffic was clearly visible
- this suggests the actual wallpad-originated write may not be an obvious `40 90` write frame from the perspective of the current tap point

### Heater Model Summary

Confirmed model after the live tests:

1. `40 90` is the BAHA-side aggregate heater state/control interface.
2. `05 -> 85` is the 5-room setpoint table.
3. `01 -> 81` is the 5-room current-temperature table.
4. Room writes are room-specific `02 06 ...` action frames on the same node.
5. Reply subtype `02` means not-all-away, and reply subtype `03` means all rooms away.

### Active Write Matrix: Master Bedroom Setpoint

Fresh baseline at the time of testing:

```text
81 current table : 97 96 95 96 95
85 setpoint table: 93 94 94 94 88
```

Target for a successful master-bedroom down-1C write:

```text
93 93 94 94 88
```

Tested candidate frames:

```text
02 40 90 06 03 02 01 93 47 00
02 40 90 06 03 02 02 93 44 00
02 40 90 06 03 02 01 13 C7 00
02 40 90 06 03 02 02 13 C4 00
02 40 90 04 03 02 01 93 45 00
02 40 90 04 03 02 02 93 46 00
02 40 90 07 03 02 01 93 46 00
02 40 90 07 03 02 02 93 45 00
02 40 90 06 06 02 93 93 94 94 88 58 00
02 40 90 07 06 02 93 93 94 94 88 59 00
02 40 90 06 04 02 01 93 00 40 00
02 40 90 06 04 02 02 93 00 43 00
```

Observed result:

- none of the above changed the `85` table
- the setpoint table remained:

```text
02 40 90 85 06 02 93 94 94 94 88 DC 00
```

Most important behavioral clue from this matrix:

- opcode `06` repeatedly elicited an immediate `85` readback even when the payload varied
- that behavior is more consistent with `06` acting as a read/report trigger or a benign ignored command than a real write opcode
- opcodes `04` and `07` produced no useful ACK and no state change

Current interpretation after this matrix:

- the straightforward room-specific and bulk write guesses are not correct
- `40 90` still looks highly reliable for reads
- but at this stage the real BAHA write path for room setpoints still looked unmapped
- later testing showed that the correct write path is in fact a room-specific `02 06 00 ...` frame, not the `06`, `04`, `07`, or bulk-table guesses above

### Confirmed Normal Setpoint Write

Later active testing confirmed that normal setpoint writes use the same opcode family as the away/clear-away commands:

```text
02 40 90 02 06 00 T1 T2 T3 T4 T5 CS 00
```

Working interpretation:

- opcode `02` = heater action/set command
- `DL = 06`
- the leading byte after `DL` is `00` for the normal setpoint write path
- `T1..T5` are the five room values
- a non-zero room value sets that room's normal target temperature
- a zero room value leaves that room unchanged
- normal setpoints use:

```text
encoded_setpoint = 0x80 + temperature_celsius
```

Confirmed example: master bedroom to `21 C`

```text
02 40 90 02 06 00 00 95 00 00 00 43 00
-> 02 40 90 80 00 52 00
-> 02 40 90 85 06 02 93 95 94 94 88 DD 00
```

That changed the setpoint table from:

```text
93 94 94 94 88
```

to:

```text
93 95 94 94 88
```

which is exactly `master bedroom: 20 C -> 21 C`.

Confirmed reverse change: master bedroom back to `20 C`

```text
02 40 90 02 06 00 00 94 00 00 00 42 00
-> 02 40 90 80 00 52 00
-> 02 40 90 85 06 02 93 94 94 94 88 DC 00
```

This restored the original table.

Important semantic result from live re-tests on 2026-04-18:

```text
02 40 90 02 06 02 00 95 00 00 00 41 00
```

Observed behavior:

- on a normal master-bedroom baseline, this frame produced the usual `80 00 52 00` receipt but did not change the `85` table
- after the master bedroom was put into away with `02 40 90 02 06 00 00 C0 00 00 00 16 00`, the same `T0=02` frame cleared away but restored the stored normal setpoint `20 C`, not the supplied `21 C`
- a normal `T0=00` setpoint write does work even from away; for example, `02 40 90 02 06 00 94 00 00 00 00 42 00` changed the living room from away `10 C` back to normal `20 C` in one step

So the current best interpretation is:

- `T0 = 00` is the working normal setpoint write path on both normal and away rooms
- `T0 = 02` is not a new-setpoint write path
- `T0 = 02` acts like a room-normalization / restore-to-stored-setpoint control when the addressed room is away
- `T0 = 02` has no observed effect when the addressed room is already normal

### Observed Wallpad Action Frames

In a later passive capture while the user manipulated the wallpad, the first clearly state-changing heater action family appeared on the BAHA bus.

Observed command family:

```text
02 40 90 02 06 00 <r1> <r2> <r3> <r4> <r5> 16 00
```

Observed examples:

```text
02 40 90 02 06 00 C0 00 00 00 00 16 00
02 40 90 02 06 00 00 C0 00 00 00 16 00
02 40 90 02 06 00 00 00 C0 00 00 16 00
02 40 90 02 06 00 00 00 00 C0 00 16 00
02 40 90 02 06 00 00 00 00 00 C0 16 00
```

Behavior:

- in each observed frame, exactly one room byte carries `C0`
- these frames are followed by:

```text
02 40 90 80 00 52 00
```

- unlike the earlier blind-write tests, these wallpad-originated frames are definitely associated with real state changes in both the `81` and `85` response tables

This is the strongest heater action family known so far.

What it means:

- opcode `02` is the heater action command family
- the six data bytes after `02 06` are:

```text
<mode_or_subtype> <room1> <room2> <room3> <room4> <room5>
```

- the leading `00` is the normal write/away-clear-away action selector
- `C0` marks the target room for away

Confirmed room ordering on BAHA:

```text
slot 1 = living room
slot 2 = master bedroom
slot 3 = playroom
slot 4 = study
slot 5 = kids bedroom
```

This matches the published Honeywell/KOCOM room model and the later active away, clear-away, and direct setpoint tests across the slots.

Observed state transitions tied to this family:

- before the first single-room action:

```text
81: 97 96 95 96 95
85: 93 94 94 94 88
```

- after a single-room `C0` action:

```text
81: 97 96 95 D6 95
85: 93 94 94 CA 88
```

- after a later burst covering all five rooms:

```text
81: D7 D6 D5 D6 D5   ; within frame 02 40 90 81 06 03 ...
85: CA CA CA CA CA   ; within frame 02 40 90 85 06 03 ...
```

This strongly suggests:

- `C0` is not a temperature value
- it is a room-targeted action marker
- `CA` and `D5/D6/D7` are mode/state encodings reached after that action, not ordinary temperature encodings

### Active Confirmation: Away and Clear-Away

Later active tests were run from an all-away baseline:

```text
81: 02 40 90 81 06 03 D7 D6 D5 D6 D5 81 00
85: 02 40 90 85 06 03 CA CA CA CA CA 98 00
```

Single-slot `80` frames were then transmitted.

Confirmed clear-away commands:

```text
slot 2 normal = 02 40 90 02 06 00 00 80 00 00 00 56 00
slot 3 normal = 02 40 90 02 06 00 00 00 80 00 00 56 00
slot 4 normal = 02 40 90 02 06 00 00 00 00 80 00 56 00
slot 5 normal = 02 40 90 02 06 00 00 00 00 00 80 56 00
```

Observed results:

- each frame produced the generic heater command receipt:

```text
02 40 90 80 00 52 00
```

- each frame also changed the corresponding room back from away to its normal table values in both the `81` and `85` replies
- the response subtype byte dropped from `03` back to `02` as soon as not all rooms were in away

Examples:

```text
slot 5 clear -> 81: D7 D6 D5 D6 95 / 85: CA CA CA CA 88
slot 4 clear -> 81: D7 D6 D5 96 95 / 85: CA CA CA 94 88
slot 3 clear -> 81: D7 D6 95 96 95 / 85: CA CA 94 94 88
slot 2 clear -> 81: D7 96 95 96 95 / 85: CA 94 94 94 88
```

2026-04-18 live re-test:

```text
slot 1 normal = 02 40 90 02 06 00 80 00 00 00 00 56 00
-> 02 40 90 80 00 52 00
-> 81: 97 96 95 96 95
-> 85: 93 94 94 94 88
```

This confirms that slot 1 clear-away works and that slot 1 is the living room for the `80` action as well.

### Current Best Semantic Mapping

Working interpretation of the heater action family:

```text
02 40 90 02 06 00 <slot1> <slot2> <slot3> <slot4> <slot5> <chk> 00
```

Where:

- one-hot `C0` in a slot sets that room to away / frost-protect mode
- one-hot `80` in a slot clears away and returns that room to its stored normal thermostat setpoint
- the controller replies with:

```text
02 40 90 80 00 52 00
```

Practical mapping:

```text
slot 1 away = 02 40 90 02 06 00 C0 00 00 00 00 16 00
slot 1 normal = 02 40 90 02 06 00 80 00 00 00 00 56 00
slot 2 away = 02 40 90 02 06 00 00 C0 00 00 00 16 00
slot 3 away = 02 40 90 02 06 00 00 00 C0 00 00 16 00
slot 4 away = 02 40 90 02 06 00 00 00 00 C0 00 16 00
slot 5 away = 02 40 90 02 06 00 00 00 00 00 C0 16 00
```

Most useful confirmed room commands:

```text
living room away      = 02 40 90 02 06 00 C0 00 00 00 00 16 00
living room normal    = 02 40 90 02 06 00 80 00 00 00 00 56 00

master bedroom away   = 02 40 90 02 06 00 00 C0 00 00 00 16 00
master bedroom normal = 02 40 90 02 06 00 00 80 00 00 00 56 00

playroom away         = 02 40 90 02 06 00 00 00 C0 00 00 16 00
playroom normal       = 02 40 90 02 06 00 00 00 80 00 00 56 00

study away            = 02 40 90 02 06 00 00 00 00 C0 00 16 00
study normal          = 02 40 90 02 06 00 00 00 00 80 00 56 00

kids bedroom away     = 02 40 90 02 06 00 00 00 00 00 C0 16 00
kids bedroom normal   = 02 40 90 02 06 00 00 00 00 00 80 56 00
```

Working interpretation of the table values:

- normal setpoints use `0x80 + temperature_celsius`
- away setpoint `10 C` is represented as `0xCA`
- away current-like values appear as the normal value plus `0x40`, for example:

```text
95 -> D5
96 -> D6
97 -> D7
```

Practical conclusion:

- on this system, a user-visible heater `off` state appears to behave as away / 10 C frost-protect, not as a distinct hard-off value
- the actionable heater commands we know today are therefore:
  - set room to away
  - clear away and return room to its stored normal setpoint
  - set a room's normal target temperature with a room-specific `02 06 00 ...` frame using `0x80 + tempC`; if the room is currently away, the same direct setpoint write also exits away and applies the new target

### Setpoint Formula

Confirmed formula for a direct room setpoint write:

```text
02 40 90 02 06 00 T1 T2 T3 T4 T5 CS 00
```

Rules:

- exactly one of `T1..T5` is non-zero
- the non-zero byte is:

```text
0x80 + target_temperature_celsius
```

- the other room bytes stay `00`, which leaves them unchanged
- if the addressed room is currently away, the same `T0=00` setpoint frame also clears away and returns the `81` / `85` tables to normal-coded values in one step

Room slots:

```text
T1 = living room
T2 = master bedroom
T3 = playroom
T4 = study
T5 = kids bedroom
```

### Confirmed Setpoint Limits

The master bedroom was used to probe the accepted numeric range.

Starting point:

```text
02 40 90 85 06 02 93 94 94 94 88 DC 00
```

Confirmed accepted values:

```text
5 C  -> 02 40 90 02 06 00 00 85 00 00 00 53 00 -> 02 40 90 85 06 02 93 85 94 94 88 CD 00
35 C -> 02 40 90 02 06 00 00 A3 00 00 00 75 00 -> 02 40 90 85 06 02 93 A3 94 94 88 EB 00
```

Confirmed rejected out-of-range values:

```text
4 C  -> 02 40 90 02 06 00 00 84 00 00 00 52 00 -> table stayed at 5 C
36 C -> 02 40 90 02 06 00 00 A4 00 00 00 72 00 -> table stayed at 35 C
```

Current conclusion:

- the accepted direct setpoint range is `5 C` through `35 C`
- writes outside that range still receive the generic `02 40 90 80 00 52 00` receipt
- but the setpoint table does not change beyond the nearest valid limit

## Related Protocol Reference: Samsung SDS Homenet

There is public community reverse-engineering material for older Samsung SDS Homenet / EasyOn wallpads.

This is not the same wire protocol as the BAHA captures in this workspace, but it is still useful as a structural reference.

### Source Quality

- Samsung SDS does not appear to publish a public wire-level RS485 frame specification for these systems.
- A community reverse-engineered implementation exists as a GitHub Gist:
  - `SDS WALLPAD RS485 EW11`
- A Korean HA blog post confirms that Samsung SDS EasyOn wallpads do use proprietary RS485 packets locally and that serial tapping works better than socket bridging for that setup.
- A Navien installation manual shows `Samsung SDS` as a specific `홈넷(RS485)` vendor choice, which supports the idea that Samsung SDS had a distinct home-network protocol family rather than using a shared generic thermostat bus.

### Samsung SDS Thermostat Frame Shape

From the reverse-engineered Samsung SDS implementation:

- thermostat state frames start with `b0 7c`
- thermostat power command frames start with `ae 7d`
- thermostat setpoint command frames start with `ae 7f`
- thermostat ACK frames use the same function bytes `7d` and `7f`

Examples from that implementation:

```text
state prefix room 1 ON : b0 7c 01 01 ...
state prefix room 1 OFF: b0 7c 01 00 ...

room 1 heat on  : ae 7d 01 01 00 00 00 53
room 1 heat off : ae 7d 01 00 00 00 00 52

room 1 set temp : ae 7f 01 <temp> 00 00 00 <chk>
```

The same pattern repeats for rooms `1` through `5`.

### Samsung SDS Thermostat Semantics

What this tells us:

- Samsung SDS encodes thermostat control per room, not as a single 5-room bulk write
- power and setpoint use different opcodes
- state frames expose at least:
  - room number
  - power mode
  - set temperature
  - current temperature
- commands are acknowledged explicitly

The Samsung SDS parser treats an 8-byte thermostat state frame as:

```text
b0 7c <room> <power> <set_temp> <cur_temp> ...
```

and then publishes:

- `power`
- `setTemp`
- `curTemp`

### Samsung SDS Checksum Hint

The reverse-engineered Samsung SDS thermostat setpoint command computes the last byte as:

```text
byte0 ^ byte1 ^ byte2 ^ byte3 ^ 0x80
```

For thermostat frames, the unused payload bytes are zero.

This is not the same checksum rule as the BAHA `02 ... chk 00` format, but it is another strong example of a compact XOR-based proprietary apartment bus.

### Why Samsung SDS Still Helps Here

Even though BAHA is a different frame format, Samsung SDS strengthens a few heater hypotheses:

1. Korean apartment thermostat protocols commonly use room-specific writes, not 5-room bulk writes.
2. Separate opcodes for:
   - status
   - power
   - setpoint
   are normal.
3. Explicit ACK behavior is normal.
4. A room thermostat protocol can be much more direct than the aggregated BAHA `40 90` read tables.

So the Samsung SDS reference pushes the BAHA heater write hypotheses further toward:

- per-room writes
- separate power vs setpoint commands
- possible ACK/commit behavior
- and away from the idea that `40 90` should necessarily accept a whole 5-room table write directly

## Confidence

High confidence:

- serial parameters `9600 8N1`
- XOR checksum model
- light #1/#2/#3/#4 ON and OFF commands above
- presence of request/response traffic on the bus

Medium confidence:

- `02 10 04 01 00 17 00` is a poll/read request
- `02 10 04 81 ...` is the corresponding response

Light-side status:

- living-room light control on `10 04` is functionally mapped
- the status reply format and masked write behavior are confirmed
- the entrance/master-switch node `1F 0F` is operationally mapped enough for control, even if its exact architectural role on the bus is still descriptive rather than formal

## Next Good Experiments

1. Save captures to timestamped files under [captures](C:\Syncthing\인제대\공부\rs485\captures).
2. Identify other node/function pairs besides `10 04`, `1F 0F`, and `40 90`.
