# HVV Matter Multisensor v0.2.1 - Flashing

## Firmware files

| File | Offset |
|---|---:|
| bootloader.bin | 0x1000 |
| partition-table.bin | 0x8000 |
| hvv_matter_multisensor.bin | 0x10000 |

## Recommended

Use the webflasher / ESP Web Tools with `manifest.json`.

## Manual esptool command

```bash
python -m esptool --chip esp32 -b 115200 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size 4MB --flash_freq 40m 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 hvv_matter_multisensor.bin
