Target amd64-unicode
Unicode true
!include "MUI2.nsh"
!include "x64.nsh"
!ifndef APP_NAME
!error "APP_NAME is required"
!endif
Name "${APP_NAME}"
VIProductVersion "0.9.0.2"
VIAddVersionKey /LANG=1046 "ProductName" "${APP_NAME}"
VIAddVersionKey /LANG=1046 "FileVersion" "0.9.0.2"
VIAddVersionKey /LANG=1046 "FileDescription" "Instalador do Word Tab e Excel Tab"
VIAddVersionKey /LANG=1046 "LegalCopyright" "Autores WordCraft e GridCraft; consulte as licenças."
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Programs\${APP_NAME}"
RequestExecutionLevel user
SetCompressor /SOLID lzma
Icon "${ICON}"
UninstallIcon "${ICON}"
!define MUI_ICON "${ICON}"
!define MUI_UNICON "${ICON}"
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${SOURCE}/LICENSE-MIT"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"
Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_OK|MB_ICONSTOP "Este instalador requer Windows de 64 bits."
    Abort
  ${EndIf}
FunctionEnd
Section "Instalar"
  SetOutPath "$INSTDIR"
  File /oname=${APP_EXE} "${BINARY}"
  File /oname=ExcelTab.exe "${SECOND_BINARY}"
  CreateShortcut "$SMPROGRAMS\Word Tab.lnk" "$INSTDIR\WordTab.exe"
  CreateShortcut "$DESKTOP\Word Tab.lnk" "$INSTDIR\WordTab.exe"
  CreateShortcut "$SMPROGRAMS\Excel Tab.lnk" "$INSTDIR\ExcelTab.exe"
  CreateShortcut "$DESKTOP\Excel Tab.lnk" "$INSTDIR\ExcelTab.exe"
  SetOutPath "$INSTDIR\Licencas\Word Tab"
  File "${SOURCE}/LICENSE-MIT"
  File "${SOURCE}/LICENSE-APACHE"
  File "${SOURCE}/NOTICE"
  File "${SOURCE}/ATTRIBUTION.md"
  File "${SOURCE}/TAB-ORIGIN.txt"
  File "${SOURCE}/assets/fonts/*.txt"
  SetOutPath "$INSTDIR\Licencas\Excel Tab"
  File "${SECOND_SOURCE}/LICENSE-MIT"
  File "${SECOND_SOURCE}/LICENSE-APACHE"
  File "${SECOND_SOURCE}/NOTICE"
  File "${SECOND_SOURCE}/ATTRIBUTION.md"
  File "${SECOND_SOURCE}/TAB-ORIGIN.txt"
  SetOutPath "$INSTDIR"
  File /oname=IDENTIDADE-VISUAL.md "${SOURCE}/../../assets/ATRIBUICAO.md"
  ; Keep any spelling dictionary the user already installed. Preferences and
  ; dictionaries are user data and remain available after uninstalling.
  SetOutPath "$LOCALAPPDATA\Word Tab\dictionaries"
  SetOverwrite off
  File "${SOURCE}/../../dictionaries/pt-BR/pt_BR.aff"
  File "${SOURCE}/../../dictionaries/pt-BR/pt_BR.dic"
  File "${SOURCE}/../../dictionaries/pt-BR/*.txt"
  SetOverwrite on
  SetOutPath "$INSTDIR"
  WriteUninstaller "$INSTDIR\Desinstalar.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "0.9.0.2"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Desinstalar.exe"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
SectionEnd
Section "Uninstall"
  Delete "$SMPROGRAMS\Word Tab.lnk"
  Delete "$DESKTOP\Word Tab.lnk"
  Delete "$SMPROGRAMS\Excel Tab.lnk"
  Delete "$DESKTOP\Excel Tab.lnk"
  Delete "$INSTDIR\WordTab.exe"
  Delete "$INSTDIR\ExcelTab.exe"
  Delete "$INSTDIR\IDENTIDADE-VISUAL.md"
  Delete "$INSTDIR\Licencas\Word Tab\LICENSE-MIT"
  Delete "$INSTDIR\Licencas\Word Tab\LICENSE-APACHE"
  Delete "$INSTDIR\Licencas\Word Tab\NOTICE"
  Delete "$INSTDIR\Licencas\Word Tab\ATTRIBUTION.md"
  Delete "$INSTDIR\Licencas\Word Tab\TAB-ORIGIN.txt"
  Delete "$INSTDIR\Licencas\Word Tab\OFL-*.txt"
  Delete "$INSTDIR\Licencas\Excel Tab\LICENSE-MIT"
  Delete "$INSTDIR\Licencas\Excel Tab\LICENSE-APACHE"
  Delete "$INSTDIR\Licencas\Excel Tab\NOTICE"
  Delete "$INSTDIR\Licencas\Excel Tab\ATTRIBUTION.md"
  Delete "$INSTDIR\Licencas\Excel Tab\TAB-ORIGIN.txt"
  RMDir "$INSTDIR\Licencas\Word Tab"
  RMDir "$INSTDIR\Licencas\Excel Tab"
  RMDir "$INSTDIR\Licencas"
  Delete "$INSTDIR\Desinstalar.exe"
  RMDir "$INSTDIR"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
