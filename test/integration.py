# SPDX-FileCopyrightText: © 2026 UncleGravity
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.triggers import Timer


TRUTH_TABLE = [
    # (ui_in[0]=w, ui_in[1]=a, expected uo_out[0]=y)
    (0, 0, 1),
    (0, 1, 0),
    (1, 0, 0),
    (1, 1, 1),
]


@cocotb.test()
async def chip_xnor_through_pins(dut):
    """Drive w, a via ui_in[0:1]; read y on uo_out[0]. No clocking needed."""
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.rst_n.value = 1  # held high; design is purely combinational

    for w, a, expected in TRUTH_TABLE:
        dut.ui_in.value = (a << 1) | w
        await Timer(1, unit="ns")
        got = int(dut.uo_out.value) & 0x1
        assert got == expected, f"w={w} a={a}: expected {expected}, got {got}"
