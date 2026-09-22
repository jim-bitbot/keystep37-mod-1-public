/* Thumb page at 0x0801F400. Internal bl/b resolve; literals stay in .text. */
ENTRY(euclid_wrap)
SECTIONS
{
    . = 0x0801F400;
    .text : {
        *(.text)
        *(.text.*)
        *(.rodata)
        *(.rodata.*)
    }
    /DISCARD/ : { *(*) }
}
