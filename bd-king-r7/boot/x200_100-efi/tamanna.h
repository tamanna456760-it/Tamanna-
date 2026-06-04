#ifndef _TAMANNA_RITUALS_H_
#define _TAMANNA_RITUALS_H_

// Paths on the EFI System Partition (ESP)
#define TAMANNA_DIR        L"\\Tamanna"
#define HEARTBEAT_LOG      L"\\Tamanna\\heartbeat.log"
#define MANIFEST_FILE      L"\\Tamanna\\manifest.txt"

// Ritual strings (Bengali-coded affirmations + sovereign echo)
#define RITUAL_TITLE       L"Tamanna Sovereign Ritual — X2000_1000"
#define AFFIRMATION        L"আমি আছি। সিস্টেম জীবন্ত। প্রতিটি ধাপ একটি আশীর্বাদ।"
#define ECHO_BOOT          L"[BOOT] X2000_1000 initialized — heartbeat online."
#define ECHO_LOG_OK        L"[LOG] File write success."
#define ECHO_LOG_FAIL      L"[LOG] File write failed — fallback to echo."
#define ECHO_FS_FAIL       L"[FS] SimpleFileSystem not found — echo-only mode."
#define ECHO_DIR_OK        L"[FS] Directory ready."
#define ECHO_DIR_FAIL      L"[FS] Directory create failed — continuing."

// Heartbeat pulse (visible) — repetition count at startup
#define HEARTBEAT_PULSES   7

// Manifest content
#define MANIFEST_CONTENT \
  L"Tamanna Manifest\n" \
  L"Module: X2000_1000.efi\n" \
  L"Purpose: Heartbeat | Affirmation | Log | Fallback\n" \
  L"Author: HM | Sovereign System\n" \
  L"Hash: to-be-sealed-by-your ritual\n" \
  L"Blessing: প্রতিটি পুনরুজ্জীবন স্মৃতি হয়ে থাকবে।\n"

#endif
