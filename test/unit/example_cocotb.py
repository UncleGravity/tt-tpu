import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def reset_yields_digit_zero(dut):
    """After reset, the 7-seg output should encode digit 0 (lower 7 bits = 0x3F)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    assert (int(dut.uo_out.value) & 0x7F) == 0x3F
