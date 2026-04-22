from pathlib import Path

from cocotb_tools.runner import get_runner

from helpers import RTL_DIR

HERE = Path(__file__).parent


def test_xnor1():
    build_dir = HERE / "sim_build" / "xnor1"
    runner = get_runner("icarus")
    runner.build(
        sources=[RTL_DIR / "xnor1.v"],
        hdl_toplevel="xnor1",
        build_dir=build_dir,
        timescale=("1ns", "1ps"),
    )
    runner.test(
        hdl_toplevel="xnor1",
        test_module="xnor1_cocotb",
        test_dir=HERE,
        build_dir=build_dir,
    )
