// File: TamannaPing.c
// Build: cl TamannaPing.c /link /out:TamannaPing.exe
#include <windows.h>
#include <stdio.h>

#define IOCTL_TAMANNA_PING \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)

int main(void) {
    HANDLE h = CreateFileA("\\\\.\\LDTamanna",
                           GENERIC_READ | GENERIC_WRITE,
                           0, NULL, OPEN_EXISTING,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) {
        printf("Open failed: %lu\n", GetLastError());
        return 1;
    }

    BYTE outBuf[128] = {0};
    DWORD bytes = 0;
    BOOL ok = DeviceIoControl(h, IOCTL_TAMANNA_PING,
                              NULL, 0, outBuf, sizeof(outBuf),
                              &bytes, NULL);
    if (!ok) {
        printf("IOCTL failed: %lu\n", GetLastError());
    } else {
        printf("Driver says: %.*s", (int)bytes, (char*)outBuf);
    }

    CloseHandle(h);
    return 0;
}
