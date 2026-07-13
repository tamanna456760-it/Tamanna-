[Defines]
  PLATFORM_NAME           = TamannaPlatform
  DSC_SPECIFICATION       = 0x0001001A
  OUTPUT_DIRECTORY        = Build
  SUPPORTED_ARCHITECTURES = X64
  TARGET                  = DEBUG

[LibraryClasses]
  UefiLib                 | MdePkg/Library/UefiLib/UefiLib.inf
  UefiBootServicesTableLib| MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf

[Components]
  Tamanna.inf
