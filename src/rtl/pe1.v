/*
 * Copyright (c) 2026 UncleGravity
 * SPDX-License-Identifier: Apache-2.0
 *
 * pe1 — V1 Processing Element.
 *   1-bit weight × int8 activation, accumulated into a signed accumulator.
 *   contrib = w ? +a : -a   (conditional two's-complement negate)
 *
 * Structured so V2 (weight-stationary systolic) can be layered on by:
 *   - replacing the `w` port with a local weight shift register,
 *   - adding a `psum_in` port into the adder,
 *   - adding `a_out` / `psum_out` 1-cycle forwarding registers.
 */

`default_nettype none

module pe1 #(
    parameter ACT_WIDTH = 8, // Activation (inputs)
    parameter ACC_WIDTH = 16 // Accumulator (outputs)
) (
    input  wire                             clk,
    input  wire                             rst_n,
    input  wire                             acc_en,
    input  wire                             acc_clear,
    input  wire                             w,    // 1 → +a, 0 → -a
    input  wire signed [ACT_WIDTH-1:0]      a,
    output wire signed [ACC_WIDTH-1:0]      acc_out
);

    // Sign-extend one bit so -(-128) = +128 fits without overflow.
    localparam CW = ACT_WIDTH + 1;  // contrib width
    wire signed [CW-1:0] a_ext   = {a[ACT_WIDTH-1], a};
    wire signed [CW-1:0] contrib = w ? a_ext : -a_ext;

    reg signed [ACC_WIDTH-1:0] acc;
    always @(posedge clk) begin
        if (!rst_n)         acc <= {ACC_WIDTH{1'b0}};
        else if (acc_clear) acc <= {ACC_WIDTH{1'b0}};
        else if (acc_en)    acc <= acc + { {(ACC_WIDTH-CW){contrib[CW-1]}}, contrib };
    end

    assign acc_out = acc;

endmodule
