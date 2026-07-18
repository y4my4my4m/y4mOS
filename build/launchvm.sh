# qemu-system-x86_64 -audiodev sdl,id=snd0 -machine q35,kernel_irqchip=on,pcspk-audiodev=snd0,accel=kvm -cdrom ZealOS-*.iso -hda ZealOS.qcow2 -m 2G -smp $(nproc) -rtc base=localtime -nic user,model=pcnet

# qemu-system-x86_64 -audiodev sdl,id=snd0 -machine q35,kernel_irqchip=on,pcspk-audiodev=snd0,accel=kvm -hda ZealOS.qcow2 -m 2G -smp $(nproc) -rtc base=localtime -nic user,model=pcnet



# Audio backend: this host runs PipeWire. The 'sdl' audiodev is often silent
# here; 'pipewire' is native. Fall back to 'pa' then 'sdl' if unavailable.
AUDIODEV="pipewire"
qemu-system-x86_64 -audiodev help 2>/dev/null | grep -qx "$AUDIODEV" || AUDIODEV="pa"

qemu-system-x86_64 -audiodev ${AUDIODEV},id=snd0 -machine q35,kernel_irqchip=on,pcspk-audiodev=snd0,accel=kvm \
    -device AC97,audiodev=snd0 \
    -cdrom ZealOS-PublicDomain-BIOS-2026-07-17-22_04_05.iso \
    -drive file=ZealOS.qcow2,format=qcow2,if=ide \
    -m 2G -smp "$(nproc)" -rtc base=localtime -nic user,model=pcnet