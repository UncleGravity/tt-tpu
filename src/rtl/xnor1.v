/*
 * Copyright (c) 2026 UncleGravity
 * SPDX-License-Identifier: Apache-2.0
 *
 * xnor1 — 1-bit binary "multiply": y = XNOR(w, a).
 *   +1 (y=1) when w == a
 *   -1 (y=0) when w != a
 */

`default_nettype none

module xnor1 (
    input  wire w,
    input  wire a,
    output wire y
);
    assign y = ~(w ^ a);
endmodule
