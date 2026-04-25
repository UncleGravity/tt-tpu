import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


ACC_WIDTH = 16
ACC_MASK = (1 << ACC_WIDTH) - 1
ACC_SIGN = 1 << (ACC_WIDTH - 1)


def to_signed(raw: int, width: int = ACC_WIDTH) -> int:
    raw &= (1 << width) - 1
    return raw - (1 << width) if raw & (1 << (width - 1)) else raw


def twos8(v: int) -> int:
    return v & 0xFF


def expected(w: int, a: int) -> int:
    return a if w else -a


async def init(dut):
    """Start clock, hold reset, then deassert on a falling edge for clean setup."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.acc_en.value = 0
    dut.acc_clear.value = 0
    dut.w.value = 0
    dut.a.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def step(dut, w: int, a: int):
    """Drive (w, a) at FallingEdge → flop samples new values at next RisingEdge."""
    await FallingEdge(dut.clk)
    dut.w.value = w
    dut.a.value = twos8(a)
    dut.acc_en.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.acc_en.value = 0


def read_acc(dut) -> int:
    return to_signed(int(dut.acc_out.value))


@cocotb.test()
async def resets_to_zero(dut):
    await init(dut)
    assert read_acc(dut) == 0


@cocotb.test()
async def w1_adds_positive_activation(dut):
    await init(dut)
    total = 0
    for v in [1, 2, 3, 10, 50, 127]:
        await step(dut, w=1, a=v)
        total += v
        assert read_acc(dut) == total, f"after +{v}: got {read_acc(dut)}, expected {total}"


@cocotb.test()
async def w0_subtracts(dut):
    await init(dut)
    for i in range(1, 6):
        await step(dut, w=0, a=7)
        assert read_acc(dut) == -7 * i


@cocotb.test()
async def handles_int8_min(dut):
    """a = -128, w = 0 → -(-128) = +128. Must not wrap to -128."""
    await init(dut)
    await step(dut, w=0, a=-128)
    assert read_acc(dut) == 128

    # And w=1 with a=-128 stores -128 directly.
    await FallingEdge(dut.clk)
    dut.acc_clear.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.acc_clear.value = 0
    await step(dut, w=1, a=-128)
    assert read_acc(dut) == -128


@cocotb.test()
async def clear_and_hold(dut):
    await init(dut)

    for _ in range(4):
        await step(dut, w=1, a=25)
    assert read_acc(dut) == 100

    await FallingEdge(dut.clk)
    dut.acc_clear.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.acc_clear.value = 0
    assert read_acc(dut) == 0

    # acc_en=0 → held at 0 even with driven inputs.
    dut.w.value = 1
    dut.a.value = twos8(50)
    dut.acc_en.value = 0
    await ClockCycles(dut.clk, 3)
    assert read_acc(dut) == 0


@cocotb.test()
async def random_32_element_dot_product(dut):
    """One Q8-block chunk: 32 cycles of (w_bit, int8) pairs vs. Python reference."""
    random.seed(0xBEEF)
    await init(dut)

    ref = 0
    for _ in range(32):
        w = random.randint(0, 1)
        a = random.randint(-128, 127)
        await step(dut, w, a)
        ref += expected(w, a)
    got = read_acc(dut)
    assert got == ref, f"expected {ref}, got {got}"
