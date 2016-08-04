#!/usr/bin/env python3
# coding=utf-8

import rfconf


def get_s0a_bits_value(module):
    s0a_bit_values = []

    for i in range(16):
        resp = module.register_read_bit("S0A", i)
        s0a_bit_values.append(int(resp[1]))

    s0a_bit_values.reverse()

    return s0a_bit_values


def main():
    module = rfconf.ETRXModule("COM22")
    s0a_value = int(module.register_read("S0A")[1], 16)
    s0a_bits_value = get_s0a_bits_value(module)
    converted_value = int("".join(str(x) for x in s0a_bits_value), 2)
    assert converted_value == s0a_value, (converted_value, s0a_value)


if __name__ == "__main__":
    main()
