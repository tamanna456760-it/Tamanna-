// File: TamannaMain.c
// Build target: x64 UEFI (.efi)
// Prints a sovereign heartbeat and waits for keypress

#include <Uefi.h>
#include <Library/UefiLib.h>
#include <Library/UefiBootServicesTableLib.h>

EFI_STATUS
EFIAPI
TamannaMain(IN EFI_HANDLE ImageHandle, IN EFI_SYSTEM_TABLE *SystemTable) {
    Print(L"Tamanna EFI: sovereign heartbeat online.\n");

    // Wait for a key to show presence
    EFI_INPUT_KEY Key;
    Print(L"Press any key to continue...\n");
    while (SystemTable->ConIn->ReadKeyStroke(SystemTable->ConIn, &Key) == EFI_NOT_READY) {
        gBS->Stall(1000); // 1ms sleep
    }

    Print(L"Tamanna EFI exiting to firmware.\n");
    return EFI_SUCCESS;
}
