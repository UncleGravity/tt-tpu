import cocotb
from cocotb.triggers import Timer


TRUTH_TABLE = [
    # (w, a, expected_y)
    (0, 0, 1),   # -1 * -1 = +1
    (0, 1, 0),   # -1 * +1 = -1
    (1, 0, 0),   # +1 * -1 = -1
    (1, 1, 1),   # +1 * +1 = +1
]


@cocotb.test()
async def xnor1_truth_table(dut):
    """Drive every (w, a) combination and read y. No clock, no reset."""
    for w, a, expected in TRUTH_TABLE:
        dut.w.value = w
        dut.a.value = a
        await Timer(1, unit="ns")  # let combinational logic settle
        got = int(dut.y.value)
        assert got == expected, f"w={w} a={a}: expected {expected}, got {got}"
