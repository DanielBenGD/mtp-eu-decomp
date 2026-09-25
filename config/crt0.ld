SECTIONS
{
    . = 0;
    .text : { *(.text.startup) }
    /DISCARD/ : { *(.ARM.attributes) *(.comment) *(.note*) }
}
