"""
doPlateAll_test.py
Python equivalent of doPlateAll_test.bat

Iterates over all 16x32 e-chip 19 channels, plates each pixel at the
configured current, then runs an impedance measurement and captures USB data.

Author: converted from BAT [pd 2025.02]
"""

import subprocess
import time
import sys

# ---------------------------
# Config (edit as needed)
# ---------------------------
NTIMES = 1          # number of plate+measure iterations per channel
TWAIT  = 1          # plating dwell time in seconds

# ---------------------------
# Register / token constants
# All values are decimal equivalents of 0x1Bxxx chip addresses
# Base offset: 0x1B000 = 110592
# ---------------------------
TOK1       = 131073   # handshake / session token
DO_RESET   = 111424   # 0x1B340  — chip reset

# Plating DAC: 110592 + DAC_setting
# DAC n=4 is BiasPlate (5-bit, 0–31); full scale ≈ 200 nA
DAC_SETTING = 31                        # 0–31
DAC_VAL     = 110592 + DAC_SETTING      # 110623 → max plating current

DAC_REG     = 111172  # 0x1B244 — address the DAC register (T=1,C=2,D=0x44)
WRITE_REG   = 111368  # 0x1B308 — commit write to register  (T=1,C=3,D=0x08)

# Pixel register values  (format: 0b00_D_U_0_GGG)
# GGG=011 → gain=20 ; U=1 → Plate UP ON (+1V compliance) ; D=0
WRITE_PIX   = 110611  # 0x1B013 — 0b00010011 — plating ON
WRITE_POX   = 110595  # 0x1B003 — 0b00000011 — plating OFF (U=0, D=0)

# Row/col base addresses
ROW_BASE    = 110848  # 0x1B100  → 0x1B100 + r  selects row r
COL_BASE    = 111104  # 0x1B200  → 0x1B200 + c  selects col c

# ---------------------------
# Helpers
# ---------------------------

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run an external command, printing it first for transparency."""
    print("  CMD:", " ".join(str(a) for a in cmd))
    return subprocess.run(
        [str(a) for a in cmd],
        check=check,          # raise CalledProcessError on non-zero exit
    )


def echip_write(value: int) -> None:
    run(["echip_write", value])


# ---------------------------
# One-time setup
# ---------------------------

def setup() -> None:
    print("[setup] Writing DAC LUT file...")
    run(["write_daclut_file", "EC3sine.txt"])


# ---------------------------
# Per-channel plating + measurement
# ---------------------------

def plate_and_measure(row: int, col: int, iteration: int) -> None:
    """
    Full sequence for one (row, col) iteration:
      1. Reset chip
      2. Set BiasPlate DAC
      3. Select pixel and turn plating ON
      4. Dwell
      5. Turn plating OFF
      6. Measure impedance
      7. Stream USB data
    """
    write_row = ROW_BASE + row
    write_col = COL_BASE + col

    print(f"    [iter {iteration}] r={row} c={col}")

    # --- 1. Initialise / reset ---
    echip_write(TOK1)
    echip_write(DO_RESET)

    # --- 2. Program BiasPlate DAC ---
    # Batch sequence: dac_val → dac_reg  (no write_reg here)
    echip_write(DAC_VAL)    # data:    0x1B000 + DAC_SETTING
    echip_write(DAC_REG)    # address: 0x1B244  (T=1 C=2 D=0x44 → BiasPlate)

    # --- 3. Select pixel and turn plating ON ---
    # Batch sequence: write_reg → write_pix → row → col → write_reg
    echip_write(WRITE_REG)   # select/enable  ← was missing
    echip_write(WRITE_PIX)   # pixel reg: U=1 (Plate UP ON), gain=20
    echip_write(write_row)   # 0x1B100 + r
    echip_write(write_col)   # 0x1B200 + c
    echip_write(WRITE_REG)   # commit

    print("    [plating ON]")

    # --- 4. Plating dwell ---
    time.sleep(TWAIT)

    print("    [plating OFF]")

    # --- 5. Turn plating OFF ---
    # Pixel register with U=0, D=0 → no current
    echip_write(WRITE_POX)   # 0x1B003
    echip_write(WRITE_REG)   # commit

    # --- 6. Configure + run impedance measurement ---
    # -g 4  : gain setting
    # -m 0  : measurement mode
    # -r/-c : target channel
    # -s 192: number of samples (or sample rate setting)
    run(["set_zparameters", "-g", "4", "-m", "0",
         "-r", row, "-c", col, "-s", "192"])
    run(["run_zmeasurement", "1"])   # start measurement

    # --- 7. Stream USB data ---
    # -c 512 : chunk/packet count
    # -p 6000: points to capture (~100–200 cycles at 1 kHz / 30 pts per cycle)
    run(["streamUSB", "-c", "512", "-p", "6000"])

    # Stop impedance measurement
    run(["run_zmeasurement", "0"])

    # --- Optional: save output file ---
    # Uncomment and adjust path as needed:
    # out_name = f"z{row:02d}{col:02d}{iteration}.dat"
    # out_dir  = r"C:\Users\lorenlab\Desktop\kyu\echip\new_scripts\plating_data"
    # import shutil, os
    # shutil.move("hsdata.dat", os.path.join(out_dir, out_name))


# ---------------------------
# Main loop
# ---------------------------

def main() -> None:
    setup()

    total_channels = 16 * 32
    done = 0

    for r in range(16):          # rows  0–15
        for c in range(32):      # cols  0–31  (note: PDF says <31, but chip has 32 cols)
            done += 1
            print(f"\n[channel {done}/{total_channels}] r={r} c={c}")

            for g in range(1, NTIMES + 1):
                plate_and_measure(row=r, col=c, iteration=g)

    print("\n[done] All channels processed.")


if __name__ == "__main__":
    sys.exit(main())
