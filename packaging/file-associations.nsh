!macro RegisterApp APP NAME DESCRIPTION
  WriteRegStr HKCU "Software\Classes\Applications\${APP}.exe" "FriendlyAppName" "${NAME}"
  WriteRegStr HKCU "Software\Classes\Applications\${APP}.exe\DefaultIcon" "" '$\"$INSTDIR\${APP}.exe$\",0'
  WriteRegStr HKCU "Software\Classes\Applications\${APP}.exe\shell\open\command" "" '$\"$INSTDIR\${APP}.exe$\" $\"%1$\"'
  WriteRegStr HKCU "Software\${APP}\Capabilities" "ApplicationName" "${NAME}"
  WriteRegStr HKCU "Software\${APP}\Capabilities" "ApplicationDescription" "${DESCRIPTION}"
  WriteRegStr HKCU "Software\${APP}\Capabilities" "ApplicationIcon" '$\"$INSTDIR\${APP}.exe$\",0'
  WriteRegStr HKCU "Software\RegisteredApplications" "${NAME}" "Software\${APP}\Capabilities"
!macroend

!macro UnregisterApp APP NAME DESCRIPTION
  DeleteRegKey HKCU "Software\Classes\Applications\${APP}.exe"
  DeleteRegKey HKCU "Software\${APP}\Capabilities"
  DeleteRegKey /ifempty HKCU "Software\${APP}"
  DeleteRegValue HKCU "Software\RegisteredApplications" "${NAME}"
!macroend

!macro RegisterType APP EXT TYPE DESCRIPTION
  WriteRegStr HKCU "Software\Classes\${APP}.${TYPE}" "" "${DESCRIPTION}"
  WriteRegStr HKCU "Software\Classes\${APP}.${TYPE}" "FriendlyTypeName" "${DESCRIPTION}"
  WriteRegStr HKCU "Software\Classes\${APP}.${TYPE}\DefaultIcon" "" '$\"$INSTDIR\${APP}.exe$\",0'
  WriteRegStr HKCU "Software\Classes\${APP}.${TYPE}\shell\open\command" "" '$\"$INSTDIR\${APP}.exe$\" $\"%1$\"'
  WriteRegStr HKCU "Software\Classes\${EXT}\OpenWithProgids" "${APP}.${TYPE}" ""
  WriteRegStr HKCU "Software\Classes\Applications\${APP}.exe\SupportedTypes" "${EXT}" ""
  WriteRegStr HKCU "Software\${APP}\Capabilities\FileAssociations" "${EXT}" "${APP}.${TYPE}"
!macroend

!macro UnregisterType APP EXT TYPE DESCRIPTION
  DeleteRegValue HKCU "Software\Classes\${EXT}\OpenWithProgids" "${APP}.${TYPE}"
  DeleteRegKey /ifempty HKCU "Software\Classes\${EXT}\OpenWithProgids"
  DeleteRegKey /ifempty HKCU "Software\Classes\${EXT}"
  DeleteRegKey HKCU "Software\Classes\${APP}.${TYPE}"
!macroend

; Per-user registration only. Never write extension defaults or UserChoice.
!macro TabAssociations ACTION
  SetRegView 64
  !insertmacro ${ACTION}App WordTab "Word Tab" "Editor de documentos"
  !insertmacro ${ACTION}App ExcelTab "Excel Tab" "Editor de planilhas"
  !insertmacro ${ACTION}Type WordTab .docx Document "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .docm DocumentMacroEnabled "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .dotx Template "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .dotm TemplateMacroEnabled "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .doc LegacyDocument "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .dot LegacyTemplate "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .rtf RichText "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .odt OpenDocumentText "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .md Markdown "Documento do Word Tab"
  !insertmacro ${ACTION}Type WordTab .txt PlainText "Documento do Word Tab"
  !insertmacro ${ACTION}Type ExcelTab .xlsx Workbook "Planilha do Excel Tab"
  !insertmacro ${ACTION}Type ExcelTab .xlsm Workbook "Planilha do Excel Tab"
  !insertmacro ${ACTION}Type ExcelTab .xlsb Workbook "Planilha do Excel Tab"
  !insertmacro ${ACTION}Type ExcelTab .ods Workbook "Planilha do Excel Tab"
  !insertmacro ${ACTION}Type ExcelTab .csv TextData "Planilha do Excel Tab"
  !insertmacro ${ACTION}Type ExcelTab .tsv TextData "Planilha do Excel Tab"
  System::Call 'shell32::SHChangeNotify(i 0x08000000, i 0, p 0, p 0)'
!macroend
