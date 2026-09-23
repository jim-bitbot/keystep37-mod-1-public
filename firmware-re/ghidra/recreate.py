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
    (0x08016A26, "mode_knob_apply"),
    (0x08013028, "seq_block_promote_pending"),
    (0x0801C3CA, "noteval"),
    (0x0800F054, "param_field_dispatch"),
    (0x0801D310, "Reset_Handler"),
    (0x08006E20, "clock_rcc_init"),
    (0x0801D8C8, "libc_init_array"),
    (0x080150B4, "ctor_sweep_wrapper_live"),
    (0x080150C2, "ctor_sweep_wrapper_dead"),
    (0x08014D08, "ctor_sweep"),
    (0x08004768, "analog_knob_ctor"),
    (0x08004224, "strip_b_ctor"),
    (0x08013E40, "play_time_step_obj_ctor"),
    (0x0801306C, "seq_block_ptrs_ctor"),
    (0x0801161C, "arp_note_pool_ctor"),
    (0x08013C9A, "note_pool_pair_ctor"),
    (0x0800DAD4, "notify_013fc"),
    (0x08005A20, "mode_skip_apply"),
    (0x08005AB8, "timediv_skip_apply"),
    (0x08019FC4, "shift_press_fn"),
    (0x0801A53C, "shift_release_fn"),
    (0x080150D0, "app_main_loop"),
    (0x0801D358, "default_irq_stub"),
    (0x08018200, "SysTick_Handler"),
    (0x08009662, "usb_isr_common"),
    (0x08018624, "USART1_IRQ"),
    (0x08018584, "TIM2_IRQ"),
    (0x0800CC48, "key_scan"),
    (0x08019F8C, "small_indexed_obj_ctor"),
    (0x0801D6E4, "subscriber_obj_ctor"),
    (0x0800C7F0, "key_scan_obj_ctor"),
    (0x08011D7C, "tick_obj_ctor"),
    (0x08005A08, "mode_obj_ctor"),
    (0x08005AA4, "timediv_obj_ctor"),
    (0x0801ACB0, "port_vtable_ctor"),
    (0x0801B384, "port_switch"),
    (0x0801AD20, "port_emit_key"),
    (0x0801AE56, "port_emit_seq"),
    (0x0801B6C4, "seq_send"),
    (0x0800614C, "get_param_b"),
    (0x080060C4, "get_param_c"),
    (0x0800FFE0, "midi_realtime_dispatch"),
    (0x08012334, "transport_cmd"),
    (0x0800D26E, "led_write"),
    (0x0800D1F8, "led_refresh"),
    (0x08012048, "tempo_clamp"),
    (0x0801509A, "ring_consume"),
    (0x08008290, "flash_unlock"),
    (0x08008338, "flash_busy_guard"),
    (0x08005E74, "init_array_slot2_wrapper"),
    (0x08011528, "init_array_slot3_wrapper"),
    (0x0801611A, "init_array_slot5_wrapper"),
    (0x08015F74, "shared_block_init"),
    (0x08008804, "gpio_idr_test"),
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
