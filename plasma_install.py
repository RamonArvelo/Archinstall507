from pathlib import Path
from archinstall import Installer, ProfileConfiguration, profile_handler, User
from archinstall.default_profiles.desktops import KdePlasma
from archinstall.lib.disk.device_model import FilesystemType
from archinstall.lib.disk.filesystem import FilesystemHandler
from archinstall.lib.interactions.disk_conf import select_disk_config

# Configuración básica
hostname = 'Novum-Sinergia'
user_name = 'ramon'
user_password = '1234'  # Cambiar por una contraseña segura
fs_type = FilesystemType('btrfs')  # Usamos btrfs para snapshots

# Selección de disco (interactivo)
disk_config = select_disk_config()

# Configuración del sistema de archivos
fs_handler = FilesystemHandler(disk_config)
fs_handler.perform_filesystem_operations()

# Punto de montaje
mountpoint = Path('/mnt/archinstall')

with Installer(
        mountpoint,
        disk_config,
        kernels=['linux', 'linux-zen'],  # Kernel estándar + zen para mejor rendimiento
        kernel_params=['quiet', 'udev.log_level=3', 'mitigations=off']  # Optimizaciones de arranque
) as installation:
    # Instalación mínima
    installation.mount_ordered_layout()
    installation.minimal_installation(hostname=hostname)
    
    # Instalar KDE Plasma (perfil mínimo)
    profile_config = ProfileConfiguration(KdePlasma())
    profile_handler.install_profile_config(installation, profile_config)
    
    # Paquetes adicionales
    desktop_apps = [
        # Navegadores
        'firefox', 'chromium',
        # Oficina
        'libreoffice-fresh', 'okular',
        # Multimedia
        'vlc', 'gstreamer', 'gst-plugins-good', 'gst-plugins-bad', 'gst-plugins-ugly',
        # Utilidades
        'kcalc', 'kate', 'ark', 'gparted', 'htop', 'neofetch',
        # Comunicación
        'discord', 'telegram-desktop',
        # Optimizaciones
        'earlyoom', 'reflector', 'thermald', 'tlp'
    ]
    
    # Controladores y soporte
    drivers = [
        'mesa', 'xf86-video-amdgpu',  # AMD
        'xf86-video-intel',           # Intel
        'nvidia', 'nvidia-utils',      # Nvidia
        'alsa-utils', 'pulseaudio', 'pulseaudio-alsa',
        'cups', 'cups-pdf', 'hplip',  # Impresión
        'networkmanager', 'openvpn'    # Red
    ]
    
    installation.add_additional_packages(desktop_apps + drivers)
    
    # Crear usuario
    user = User(user_name, user_password, True)
    installation.create_users(user)
    
    # Habilitar servicios importantes
    services = [
        'NetworkManager.service',
        'bluetooth.service',
        'cups.service',
        'tlp.service',          # Optimización de batería para laptops
        'earlyoom.service',     # Manejo de memoria
        'reflector.timer'       # Actualización automática de mirrors
    ]
    
    for service in services:
        installation.enable_service(service)
    
    # Configuración adicional (ejemplo)
    installation.arch_chroot("systemctl enable sddm.service")  # Habilitar gestor de inicio de sesión
    
    # Optimización de mirrors (más rápidos para tu ubicación)
    installation.arch_chroot("reflector --country 'United States' --latest 10 --protocol https --sort rate --save /etc/pacman.d/mirrorlist")

# Post-instalación recomendada (ejecutar manualmente después del reinicio)
print("\nPost-instalación recomendada:")
print("1. Configurar teclado en Plasma: System Settings > Input Devices > Keyboard")
print("2. Configurar pantalla: System Settings > Display and Monitor")
print("3. Instalar codecs multimedia: sudo pacman -S ffmpegthumbs")
print("4. Configurar TLP para laptops: sudo tlp start")
print("5. Habilitar AUR (yay): https://wiki.archlinux.org/title/AUR_helpers")
