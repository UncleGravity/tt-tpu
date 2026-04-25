# SPDX-FileCopyrightText: © 2026 UncleGravity
# SPDX-License-Identifier: Apache-2.0

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


# ui_in layout (src/rtl/project.v):
#   [0] w, [1] acc_en, [2] acc_clear, [3] readout_hi
def pack_ctl(w=0, acc_en=0, acc_clear=0, readout_hi=0) -> int:
    return (readout_hi << 3) | (acc_clear << 2) | (acc_en << 1) | w


def twos8(v: int) -> int:
    return v & 0xFF


def expected(w: int, a: int) -> int:
    return a if w else -a


async def init(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def step(dut, w: int, a: int):
    await FallingEdge(dut.clk)
    dut.ui_in.value = pack_ctl(w=w, acc_en=1)
    dut.uio_in.value = twos8(a)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.ui_in.value = pack_ctl()


async def read_acc16(dut) -> int:
    """Select low then high byte via readout_hi, return signed 16-bit value."""
    await FallingEdge(dut.clk)
    dut.ui_in.value = pack_ctl(readout_hi=0)
    await RisingEdge(dut.clk)
    lo = int(dut.uo_out.value) & 0xFF

    await FallingEdge(dut.clk)
    dut.ui_in.value = pack_ctl(readout_hi=1)
    await RisingEdge(dut.clk)
    hi = int(dut.uo_out.value) & 0xFF

    raw = (hi << 8) | lo
    return raw - (1 << 16) if raw & 0x8000 else raw


@cocotb.test()
async def chip_dot_product_32_elements(dut):
    """Stream 32 (w_bit, int8) pairs through pins; verify against Python reference."""
    random.seed(0xDEAD)
    await init(dut)

    ref = 0
    for _ in range(32):
        w = random.randint(0, 1)
        a = random.randint(-128, 127)
        await step(dut, w, a)
        ref += expected(w, a)

    got = await read_acc16(dut)
    assert got == ref, f"expected {ref}, got {got}"


@cocotb.test()
async def chip_clear_mid_stream(dut):
    await init(dut)

    for _ in range(3):
        await step(dut, w=1, a=10)

    await FallingEdge(dut.clk)
    dut.ui_in.value = pack_ctl(acc_clear=1)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.ui_in.value = pack_ctl()

    got = await read_acc16(dut)
    assert got == 0

    await step(dut, w=0, a=5)
    got = await read_acc16(dut)
    assert got == -5
