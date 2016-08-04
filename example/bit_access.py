#!/usr/bin/env python3
# coding=utf-8

import rfconf


def get_reg_bits_value(module, reg, reg_size):
    reg_bit_values = []

    for i in range(reg_size):
        resp = module.register_read_bit(reg, i)
        reg_bit_values.append(int(resp[1]))

    reg_bit_values.reverse()

    return reg_bit_values


def main():
    module = rfconf.ETRXModule("COM22")
    s0a_value = int(module.register_read("S0A")[1], 16)
    s0a_bits_value = get_reg_bits_value(module, "S0A", 16)
    converted_value = int("".join(str(x) for x in s0a_bits_value), 2)
    assert converted_value == s0a_value, (converted_value, s0a_value)

    s16_value = int(module.register_read("S16")[1], 16)
    s16_bits_value = get_reg_bits_value(module, "S16", 32)
    converted_value = int("".join(str(x) for x in s16_bits_value), 2)
    assert converted_value == s16_value, (converted_value, s16_value)


if __name__ == "__main__":
    main()
