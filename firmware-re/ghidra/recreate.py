# Ghidra headless post-script: name confirmed KeyStep 37 functions.
#
# Import the STRIPPED flash extract, not the framed .led decode:
#
# analyzeHeadless <projectDir> <projectName> \
#   -import firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin \
#   -processor "ARM:LE:32:Cortex" -loader BinaryLoader \
#   -loader-baseAddr 0x08000000 \
#   -postScript recreate.py
#
# Safe to re-run: createFunction + setName are idempotent enough for our purposes.

from ghidra.program.model.symbol import SourceType

NAMES = [
    (0x08005E84, "get_param"),
    (0x08005DF8, "chord_test_dispatch"),
    (0x08005CCC, "mode_byte_get"),
    (0x08006024, "id_to_index"),
    (0x0800606C, "index_to_id"),
    (0x080060A2, "knob_index_to_cc"),
    (0x080067F4, "test20_cc_press"),
    (0x080068C8, "test20_cc_value"),
    (0x08006914, "test20_cc_value2"),
    (0x08004388, "strip_process_b"),
    (0x08004918, "analog_knob_process"),
    (0x08004BF8, "shift_strip_pickup"),
    (0x0801A7AC, "button_debounce"),
    (0x08017260, "panel_button_dispatch"),
    (0x08016BC4, "cc_notify"),
    (0x0801CC5C, "subscribe"),
    (0x0800E4D2, "vtable_init"),
    (0x0800E4FE, "vtable_assign"),
    (0x0800E3E8, "vtable_slot8"),
    (0x0800EA7E, "msg_tbb"),
    (0x0800DD30, "seq_slot_base"),
    (0x080129CC, "arp_seq_tick"),
    (0x08013E8C, "play_time_step"),
    (0x080130E8, "seq_step_note"),
    (0x080130F4, "seq_step_gate"),
    (0x08011874, "get_arp_mode"),
    (0x08011878, "order_hold_walk"),
    (0x08014418, "seq_step_store"),
    (0x08011794, "set_arp_mode"),
    (0x08011A1C, "rebuild_order"),
    (0x08011A38, "mode_tbh"),
    (0x08011C88, "pattern_or_order_builder"),
    (0x08016A26, "mode_knob_apply"),
    (0x0801BA9C, "voice_interval_load"),
    (0x0801C3CA, "noteval"),
    (0x0801BAB8, "voice_note_on"),
    (0x0800F054, "param_field_dispatch"),
    (0x0801D310, "Reset_Handler"),
]


def create_named(addr_int, name):
    addr = toAddr(addr_int)
    fn = getFunctionAt(addr)
    if fn is None:
        fn = createFunction(addr, name)
    if fn is not None:
        fn.setName(name, SourceType.USER_DEFINED)
        print("named %s @ %s" % (name, addr))
    else:
        print("FAILED %s @ %s" % (name, addr))


for va, name in NAMES:
    create_named(va, name)
