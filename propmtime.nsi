
!include MUI2.nsh

!include EnvVarUpdate.nsh

Name "propmtime"

; The file to write
OutFile "dist\install_propmtime.exe"

!define SUITENAME "abel"
!define APPNAME "propmtime"
!define APPEXE "${APPNAME}.exe"

; The default installation directory
InstallDir $PROGRAMFILES\${SUITENAME}

; Request application privileges for Windows
RequestExecutionLevel admin

;--------------------------------

; Pages

Page directory
Page instfiles

;--------------------------------

Section "Install"
  SetOutPath $INSTDIR
  File "dist\${APPEXE}"

  ; for PyQt
  ;File "dist\*.dll"
  ;File "dist\platforms\*.dll"

  writeUninstaller "$INSTDIR\uninstall.exe"
  ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR"
SectionEnd

Section "Uninstall"
	# Remove Start Menu launcher
	delete "$SMPROGRAMS\${SUITENAME}\${APPNAME}.lnk"

	# Remove uninstall link
	delete "$SMPROGRAMS\${SUITENAME}\Uninstall.lnk"

	# Try to remove the Start Menu folder - this will only happen if it is empty
	rmDir "$SMPROGRAMS\${SUITENAME}"

	# Remove files
	delete $INSTDIR\${APPEXE}

	# Always delete uninstaller as the last action
	delete $INSTDIR\uninstall.exe

	# Try to remove the install directory - this will only happen if it is empty
	rmDir $INSTDIR

	# Try to remove the suite directory - this will only happen if it is empty
	rmDir ${SUITENAME}
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\${SUITENAME}"
  CreateShortcut "$SMPROGRAMS\${SUITENAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortcut "$SMPROGRAMS\${SUITENAME}\${APPNAME}.lnk" "$INSTDIR\${APPEXE}" "" "$INSTDIR\${APPEXE}" 0

SectionEnd

