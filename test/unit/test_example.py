from pathlib import Path

from cocotb_tools.runner import get_runner

from helpers import RTL_DIR, chip_top_module

HERE = Path(__file__).parent


def test_example():
    top = chip_top_module()
    build_dir = HERE / "sim_build" / "example"
    runner = get_runner("icarus")
    runner.build(
        sources=[RTL_DIR / "project.v"],
        hdl_toplevel=top,
        build_dir=build_dir,
        timescale=("1ns", "1ps"),
    )
    runner.test(
        hdl_toplevel=top,
        test_module="example_cocotb",
        test_dir=HERE,
        build_dir=build_dir,
    )
