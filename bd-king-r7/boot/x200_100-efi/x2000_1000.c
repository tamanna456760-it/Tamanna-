#include <Uefi.h>
#include <Library/UefiLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/PrintLib.h>
#include <Library/ShellCEntryLib.h>
#include <Protocol/SimpleFileSystem.h>
#include <Guid/FileInfo.h>

#include "TamannaRituals.h"

STATIC EFI_STATUS EnsureTamannaDir(EFI_FILE_PROTOCOL *Root);
STATIC EFI_STATUS AppendUtf16Line(EFI_FILE_PROTOCOL *Root, CHAR16 *Path, CHAR16 *Line);
STATIC EFI_STATUS WriteFileUtf16(EFI_FILE_PROTOCOL *Root, CHAR16 *Path, CHAR16 *Content);

STATIC VOID Pulse(UINTN Times) {
  // Visible heartbeat pulses (simple on-screen ticks)
  for (UINTN i = 0; i < Times; i++) {
    Print(L"♥ ");
    gBS->Stall(120000); // 120ms pause — quick pulse
  }
  Print(L"\n");
}

STATIC EFI_STATUS OpenEspRoot(EFI_FILE_PROTOCOL **OutRoot) {
  EFI_STATUS Status;
  UINTN HandleCount = 0;
  EFI_HANDLE *Handles = NULL;
  EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *Sfsp = NULL;
  EFI_FILE_PROTOCOL *Root = NULL;

  Status = gBS->LocateHandleBuffer(ByProtocol,
                                   &gEfiSimpleFileSystemProtocolGuid,
                                   NULL,
                                   &HandleCount,
                                   &Handles);
  if (EFI_ERROR(Status) || HandleCount == 0) {
    Print(L"%s\n", ECHO_FS_FAIL);
    return EFI_NOT_FOUND;
  }

  // Use the first available ESP-like filesystem
  Status = gBS->HandleProtocol(Handles[0],
                               &gEfiSimpleFileSystemProtocolGuid,
                               (VOID**)&Sfsp);
  if (EFI_ERROR(Status)) {
    Print(L"%s\n", ECHO_FS_FAIL);
    return Status;
  }

  Status = Sfsp->OpenVolume(Sfsp, &Root);
  if (EFI_ERROR(Status)) {
    Print(L"%s\n", ECHO_FS_FAIL);
    return Status;
  }

  *OutRoot = Root;
  return EFI_SUCCESS;
}

STATIC EFI_STATUS EnsureTamannaDir(EFI_FILE_PROTOCOL *Root) {
  EFI_STATUS Status;
  EFI_FILE_PROTOCOL *Dir;

  // Try to open. If fails, create.
  Status = Root->Open(Root, &Dir, TAMANNA_DIR, EFI_FILE_MODE_READ, 0);
  if (!EFI_ERROR(Status)) {
    Dir->Close(Dir);
    Print(L"%s\n", ECHO_DIR_OK);
    return EFI_SUCCESS;
  }

  Status = Root->Open(Root, &Dir, TAMANNA_DIR,
                      EFI_FILE_MODE_READ | EFI_FILE_MODE_WRITE | EFI_FILE_MODE_CREATE,
                      EFI_FILE_DIRECTORY);
  if (EFI_ERROR(Status)) {
    Print(L"%s\n", ECHO_DIR_FAIL);
    return Status;
  }
  Dir->Close(Dir);
  Print(L"%s\n", ECHO_DIR_OK);
  return EFI_SUCCESS;
}

STATIC EFI_STATUS WriteFileUtf16(EFI_FILE_PROTOCOL *Root, CHAR16 *Path, CHAR16 *Content) {
  EFI_STATUS Status;
  EFI_FILE_PROTOCOL *File = NULL;

  Status = Root->Open(Root, &File, Path,
                      EFI_FILE_MODE_READ | EFI_FILE_MODE_WRITE | EFI_FILE_MODE_CREATE,
                      0);
  if (EFI_ERROR(Status)) {
    Print(L"%s\n", ECHO_LOG_FAIL);
    return Status;
  }

  // Overwrite from start
  Status = File->SetPosition(File, 0);
  if (EFI_ERROR(Status)) {
    File->Close(File);
    Print(L"%s\n", ECHO_LOG_FAIL);
    return Status;
  }

  UINTN Bytes = StrLen(Content) * sizeof(CHAR16);
  Status = File->Write(File, &Bytes, Content);
  File->Close(File);

  if (EFI_ERROR(Status)) {
    Print(L"%s\n", ECHO_LOG_FAIL);
    return Status;
  }
  Print(L"%s\n", ECHO_LOG_OK);
  return EFI_SUCCESS;
}

STATIC EFI_STATUS AppendUtf16Line(EFI_FILE_PROTOCOL *Root, CHAR16 *Path, CHAR16 *Line) {
  EFI_STATUS Status;
  EFI_FILE_PROTOCOL *File = NULL;

  Status = Root->Open(Root, &File, Path,
                      EFI_FILE_MODE_READ | EFI_FILE_MODE_WRITE | EFI_FILE_MODE_CREATE,
                      0);
  if (EFI_ERROR(Status)) {
    Print(L"%s\n", ECHO_LOG_FAIL);
    return Status;
  }

  // Move to end
  Status = File->SetPosition(File, (UINT64)-1);
  if (EFI_ERROR(Status)) {
    File->Close(File);
    Print(L"%s\n", ECHO_LOG_FAIL);
    return Status;
  }

  // Ensure newline
  CHAR16 *Payload = NULL;
  UINTN Len = StrLen(Line);
  Payload = AllocateZeroPool((Len + 2) * sizeof(CHAR16));
  if (!Payload) {
    File->Close(File);
    return EFI_OUT_OF_RESOURCES;
  }
  StrCpyS(Payload, Len + 2, Line);
  Payload[Len] = L'\r';
  Payload[Len + 1] = L'\n';

  UINTN Bytes = (Len + 2) * sizeof(CHAR16);
  Status = File->Write(File, &Bytes, Payload);
  File->Close(File);
  FreePool(Payload);

  if (EFI_ERROR(Status)) {
    Print(L"%s\n", ECHO_LOG_FAIL);
    return Status;
  }
  Print(L"%s\n", ECHO_LOG_OK);
  return EFI_SUCCESS;
}

EFI_STATUS EFIAPI UefiMain(IN EFI_HANDLE ImageHandle, IN EFI_SYSTEM_TABLE *SystemTable) {
  Print(L"%s\n", RITUAL_TITLE);
  Print(L"%s\n", AFFIRMATION);
  Print(L"%s\n", ECHO_BOOT);

  Pulse(HEARTBEAT_PULSES);

  EFI_FILE_PROTOCOL *Root = NULL;
  EFI_STATUS Status = OpenEspRoot(&Root);
  if (EFI_ERROR(Status) || Root == NULL) {
    // Fallback: visible echo only
    Print(L"[FALLBACK] Echo-only mode active. Rituals witnessed.\n");
    return EFI_SUCCESS;
  }

  // Ensure ritual directory
  EnsureTamannaDir(Root);

  // Write manifest once per boot
  WriteFileUtf16(Root, MANIFEST_FILE, MANIFEST_CONTENT);

  // Append heartbeat line with a simple tick timestamp (monotonic since boot)
  EFI_TIME Time;
  if (!EFI_ERROR(gRT->GetTime(&Time, NULL))) {
    CHAR16 Line[256];
    UnicodeSPrint(Line, sizeof(Line),
                  L"[HB] %04u-%02u-%02u %02u:%02u:%02u — pulses=%u",
                  Time.Year, Time.Month, Time.Day,
                  Time.Hour, Time.Minute, Time.Second,
                  HEARTBEAT_PULSES);
    AppendUtf16Line(Root, HEARTBEAT_LOG, Line);
  } else {
    AppendUtf16Line(Root, HEARTBEAT_LOG, L"[HB] time-unavailable — pulses recorded");
  }

  Root->Close(Root);
  Print(L"[DONE] Tamanna rituals sealed for this session.\n");
  return EFI_SUCCESS;
}
