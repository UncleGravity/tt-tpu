/*
 * Copyright (c) 2026 UncleGravity
 * SPDX-License-Identifier: Apache-2.0
 *
 * Pin map:
 *   ui_in[0]   = w           (weight bit)
 *   ui_in[1]   = acc_en
 *   ui_in[2]   = acc_clear
 *   ui_in[3]   = readout_hi  (0 → uo_out = acc[7:0]; 1 → uo_out = acc[15:8])
 *   ui_in[7:4] = unused
 *   uio_in[7:0]= a           (int8 activation, two's-complement)
 *   uio_out/oe = 0           (uio used as input this version)
 *   uo_out[7:0]= accumulator byte, selected by readout_hi
 */

`default_nettype none

module tt_um_unclegravity_tpu (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    wire w          = ui_in[0];
    wire acc_en     = ui_in[1];
    wire acc_clear  = ui_in[2];
    wire readout_hi = ui_in[3];

    wire signed [7:0]  a   = uio_in;
    wire signed [15:0] acc;

    pe1 #(.ACT_WIDTH(8), .ACC_WIDTH(16)) u_pe1 (
        .clk      (clk),
        .rst_n    (rst_n),
        .acc_en   (acc_en),
        .acc_clear(acc_clear),
        .w        (w),
        .a        (a),
        .acc_out  (acc)
    );

    assign uo_out  = readout_hi ? acc[15:8] : acc[7:0];
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    wire _unused = &{ena, ui_in[7:4], 1'b0};

endmodule
