# qemu-system-x86_64 -audiodev sdl,id=snd0 -machine q35,kernel_irqchip=on,pcspk-audiodev=snd0,accel=kvm -cdrom ZealOS-*.iso -hda ZealOS.qcow2 -m 2G -smp $(nproc) -rtc base=localtime -nic user,model=pcnet

# qemu-system-x86_64 -audiodev sdl,id=snd0 -machine q35,kernel_irqchip=on,pcspk-audiodev=snd0,accel=kvm -hda ZealOS.qcow2 -m 2G -smp $(nproc) -rtc base=localtime -nic user,model=pcnet



qemu-system-x86_64 -audiodev sdl,id=snd0 -machine q35,kernel_irqchip=on,pcspk-audiodev=snd0,accel=kvm \
    -device AC97,audiodev=snd0 \
    -cdrom ZealOS-PublicDomain-BIOS-2026-07-17-22_04_05.iso \
    -drive file=ZealOS.qcow2,format=qcow2,if=ide \
    -m 2G -smp "$(nproc)" -rtc base=localtime -nic user,model=pcnet