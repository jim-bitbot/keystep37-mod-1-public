# Arturia MIDI Control Center: technical breakdown for Linux/WSL design sharing

> **Status note (2026-09-20):** this document is the *first-pass* analysis
> (PE metadata, imports, strings). Since it was written, much deeper
> analysis has been done — actual disassembly of the installed binary with
> capstone and Ghidra, recovering the real SysEx wire format (header layout,
> checksum, 7-bit payload packing) and a partial opcode table, including
> firmware-transfer packet opcodes confirmed via an adjacent debug log
> string. The "What is the actual protocol model?" section below was written
> before that work and is now superseded by concrete findings — see
> `firmware-re/notes/findings-2026-09-20.md` for the real envelope format and
> opcode table. The architectural conclusions elsewhere in this document
> (JUCE-based native app, WinMM transport, device-registry/firmware-updater
> metadata model) still hold and are unaffected.

## Scope

This document is not about running MIDI Control Center under Linux. The purpose is to extract the real architecture, protocol model, and Windows dependencies so the important technical facts can be shared with a WSL-based project without guessing.

The analysis is based on the actual installed app and installer files discovered on this machine:

- C:\Program Files (x86)\Arturia\MIDI Control Center\MIDI Control Center.exe
- C:\Program Files (x86)\Arturia\MIDI Control Center\ArturiaMIDI_DriverSetup.exe
- C:\Users\jimcu\Downloads\MIDI_Control_Center__1_23_0_134.exe
- C:\ProgramData\Arturia\MIDI Control Center\Resources
- C:\ProgramData\Arturia\MIDI Control Center\Firmware

---

## Executive summary

MIDI Control Center is a native Windows C++ application, not a .NET or Electron app. It is built around:

- a Win32 GUI front end
- a device abstraction layer for USB MIDI hardware
- a firmware-update subsystem for Arturia devices
- a set of product JSON descriptors that define supported device identities, firmware files, protocol families, and update rules
- a separate Windows USB MIDI driver installer

The core product is therefore not “a GUI app you can port literally to Linux.” The portable part is the device model, protocol assumptions, and firmware/update flow. The Windows-only part is the UI runtime and the vendor driver layer.

---

## Verified binary evidence

### Installed app binary

From the PE metadata of the installed executable:

- Machine: 0x8664 (x64 PE)
- Subsystem: 2 (Windows GUI subsystem)
- Number of sections: 9
- ImageBase: 0x140000000
- Imports include WinMM, USER32, GDI32, OPENGL32, WS2_32, SHELL32, OLE32, ADVAPI32, CRYPT32

This is a direct indicator of a native Windows app using the standard Win32 stack.

### Installer binary

From the downloaded installer binary:

- Machine: 0x14c (32-bit PE)
- Subsystem: 2 (Windows GUI subsystem)
- “Inno Setup Setup Data (5.5.7)” strings are present
- It is a standard Inno Setup installer package, not a custom app runtime

This means the application distribution is an Inno Setup bootstrapper that installs the UI and the driver package.

### Driver package evidence

The runtime folder includes:

- ArturiaMIDI_DriverSetup.exe

String analysis of the driver package includes:

- Arturia_USBMidi v1.7.0
- x86\Arturia_USBMidi_v1.7.0_2025-08-20.msi
- x64\Arturia_USBMidi_v1.7.0_2025-08-20.msi

This shows the app depends on a vendor MIDI USB driver package that is installed separately from the main GUI.

---

## Actual technical architecture of the app

### 1) Native Windows UI layer

The binary contains many JUCE-oriented symbols and class names such as:

- JuceArturiaLib
- ArturiaDialog
- SampleBrowser
- TutoEditor
- SliderComposer
- ArturiaToolbarMidiConfig
- ContentWindow

This strongly indicates the app UI was built with a JUCE-like C++ toolkit and compiled as a native Windows application.

The app is definitely not:

- a .NET app
- a browser app
- a Python app
- an Electron app

### 2) MIDI transport layer

The imported WinMM functions include:

- midiOutOpen
- midiInOpen
- midiOutShortMsg
- midiOutLongMsg
- midiInStart
- midiInStop
- midiInReset
- midiOutGetNumDevs
- midiInGetNumDevs
- midiOutGetDevCapsW
- midiInGetDevCapsW

This is the key fact for understanding the app: it speaks to hardware through the Windows MIDI API layer, not through some custom Linux or cross-platform abstraction.

### 3) USB / driver dependency

The app emits strings such as:

- “The MIDI Driver is needed to use this device. Do you want to install it?”
- “Driver not found”
- “Missing MIDI driver.”
- “The MIDI driver is required for this operation.”

This means the Windows driver layer is mandatory for device communication. On Linux, an equivalent is needed through libusb, hidapi, or a Linux MIDI/USB transport layer; there is no direct equivalent of the Windows app’s installer/driver stack in WSL.

### 4) Device abstraction model

The binary contains repeated strings showing device identity and logic:

- MicroFreak
- MatrixBrute
- KeyStep
- MiniLab
- MiniBrute
- BeatStep
- DrumBrute
- KeyLab

The application also contains strings like:

- “Device not connected.”
- “Device found.”
- “Device not found.”
- “Device currently in bootloader mode.”
- “OpenDeviceForBurn”
- “Firmware Upgrade...”

This is direct evidence of a device model that is not generic MIDI control UI. It is a controller-manager system.

### 5) Firmware update subsystem

The strings in the app include:

- “Firmware Upgrade Mode”
- “Firmware Update Progress:”
- “Firmware Update Success”
- “Firmware Update Error”
- “Firmware file CRC error”
- “Firmware file corrupted”
- “Firmware file verify error”
- “Invalid Firmware File”
- “Firmware file empty”

This is a vendor-specific SysEx/firmware loader system, not just a control surface editor. A real Linux port would need to implement firmware update protocol handling for each device family.

---

## Resource metadata: the real “portable” part

The installed product data under C:\ProgramData\Arturia\MIDI Control Center\Resources is the most important artifact for a cross-platform design.

### Example: MicroFreak definition

The MicroFreak descriptor includes:

- name: MicroFreak
- usbVendorId: 7285
- manufacturerId: 00206B
- familyId: 0600
- protocol: mbrute
- firmware file pattern: *.mff
- minimalVersionRequired: 4.0.0.0

This is a product definition file, not just a GUI resource. It tells the app:

- which USB vendor and device family it belongs to
- how to identify the hardware
- which updater to use
- which firmware extension to expect
- which protocol family applies

### Example: KeyStep definition

The KeyStep descriptor includes:

- vendor ID 7285
- manufacturerId 00206B
- familyId 0200
- product id 42
- protocol arturia_v2
- firmware updater name midiplus
- productCode and productKey values
- firmware format $3.$2.$1
- minimalVersionRequired 1.0.0.5

This is extremely useful because it shows the app is driven by metadata, not hardcoded UI behavior alone.

### Observed pattern

Across the resource files there is a repeated architecture:

- product name
- USB vendor/product IDs
- family IDs
- manufacturer IDs
- firmware updater metadata
- protocol mapping
- minimal firmware version requirements
- UI template references

This is the most portable and reusable design layer for a Linux or WSL project.

---

## Firmware files installed on the system

The ProgramData tree contains firmware blobs for multiple products:

- microfreak_Firmware_Update_5.0.0.2084.mff
- matrixbrute_Firmware_Update_2.0.2.1186.mbf
- keystep37_Firmware_Update_1.1.6.579.led
- keystep-pro_Firmware_Update_2.5.20.0.kspf
- minilab-mkII_Firmware_Update_1.1.2.1689.mnl2
- keylab-49-mkII_Firmware_Update_1.3.1.1492.led
- etc.

This is evidence that the app manages many device families, each with their own firmware image format and update method.

---

## What is the actual protocol model?

The best interpretation is:

1. USB enumeration identifies the Arturia device using vendor/product/family IDs.
2. The app loads the matching device definition from JSON resources.
3. It selects the protocol family for that device, such as:
   - arturia_v2
   - mbrute
   - midiplus
4. It interacts with the hardware over USB MIDI using SysEx/MIDI messages.
5. It uses the matching firmware updater metadata to enter bootloader mode and flash the correct firmware file.
6. It validates firmware files, checks version compatibility, and updates the device state.

The strings in the binary confirm the protocol is message-based, with MIDI system-exclusive commands and firmware validation paths.

This is the correct layer to share with a Linux/WSL project: not the UI, but the protocol and metadata model.

---

## What is Windows-only vs portable

### Windows-only

- native Win32 GUI runtime
- WinMM MIDI API
- Windows USB MIDI driver installation
- OS-level device enumeration and driver management
- actual app windowing and UI behaviors

### Portable / shareable

- device identity metadata
- family/product mapping
- firmware updater metadata
- PER-device protocol selection
- firmware file version checking
- control assignment and preset representation concepts
- general SysEx-based device management approach

This distinction is critical. A Linux/WSL project should not attempt to re-use the desktop app binary. It should reuse the protocol model and the device metadata structure.

---

## WSL/Linux implications

### Direct running of MIDI Control Center in Linux

Not realistic.

Reasons:

- It is a native Windows GUI executable.
- It requires Windows MIDI drivers and USB support.
- It depends on Windows-specific device and service APIs.
- WSL is not a full replacement for the Windows hardware stack.

### What is still possible in Linux/WSL

- Build a Linux USB/MIDI client that uses the same vendor IDs and protocol logic
- Implement the device metadata layer in JSON/YAML/DB form
- Build an equivalent firmware update engine for supported hardware
- Expose the result to a WSL-based project as a service or API bridge

### Best strategy

If the goal is a WSL project with access to hardware, the clean model is:

- Linux service in WSL handles the protocol and data model
- Windows bridge or host process handles the actual USB/MIDI interaction when required
- shared JSON metadata is centralized and portable across both environments

---

## Recommended project architecture to take forward

A Linux-portable architecture should look like this:

1. Device Registry Layer
   - Product definitions keyed by vendor/product IDs
   - Family and firmware metadata
   - Protocol enums
   - Version compatibility rules

2. Transport Layer
   - USB enumeration
   - MIDI SysEx channels
   - Hardware communication abstraction
   - Linux compatibility implementation (libusb/hidapi/etc.)

3. Firmware Layer
   - firmware image packaging
   - CRC/validation checks
   - bootloader transitions
   - per-product updater mapping

4. Device Controller Layer
   - read/write operations
   - parameter mapping
   - preset upload/download
   - configuration sync

5. App/UX Layer
   - only for the Linux project UI or CLI
   - does not replicate the original Windows app binary

---

## Conclusion

The key fact is this: MIDI Control Center is a Windows-native device management app whose real value is not its GUI, but its device definition model and protocol logic.

For a Linux/WSL project, the correct sharing target is:

- device IDs and family mappings
- protocol families and firmware update behavior
- SysEx-based hardware management patterns
- product metadata and compatibility rules

The actual Windows app, driver installer, and UI runtime should be treated as environment-specific constraints, not as something to port directly.

This is the correct technical boundary for a WSL-based project that wants to “understand” MIDI Control Center without running it under Linux.
