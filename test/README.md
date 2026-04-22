# Tests

All tests use [cocotb](https://docs.cocotb.org/en/stable/) to drive the DUT and check the outputs.
[More Info](https://tinytapeout.com/hdl/testing/).

The Makefile requires `PDK_ROOT` to be set; the Nix devshell (`nix develop`) sets this automatically.

## How to run

RTL simulation:

```sh
make -B
```

Gate-level simulation (after running the harden flow — `./tt/tt_tool.py --harden --no-docker` from the repo root):

```sh
make -B GATES=yes
```

The Makefile picks up the netlist from `../runs/wokwi/final/pnl/<top_module>.pnl.v` automatically. If you want to test a different netlist, drop it in as `gate_level_netlist.v` and it'll be used instead.

If you wish to save the waveform in VCD format instead of FST, edit `tb.v` to use `$dumpfile("tb.vcd");` and then run:

```sh
make -B FST=
```

## How to view the waveform file

Waveforms are written under `sim_build/rtl/tb.fst` (RTL) or `sim_build/gl/tb.fst` (gate-level).

Using GTKWave

```sh
gtkwave sim_build/rtl/tb.fst tb.gtkw
```

Using Surfer

```sh
surfer sim_build/rtl/tb.fst
```
