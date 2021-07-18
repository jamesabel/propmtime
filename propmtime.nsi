
# *** DO NOT EDIT ***
# Programmatically generated by pyship on 2020-11-03 18:57:35.663502.

!define COMPANYNAME abel
!define APPNAME propmtime
!define OSSPEC win64
!define EXENAME propmtime.exe
!define DESCRIPTION "None"
!define VERSIONMAJOR 0
!define VERSIONMINOR 6
!define VERSIONBUILD 0
!define HELPURL None
!define UPDATEURL None
!define ABOUTURL None
!define INSTALLSIZE 443886.658203125

RequestExecutionLevel admin ;Require admin rights on NT6+ (When UAC is turned on)

InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"

# rtf or txt file - remember if it is txt, it must be in the DOS text format (\r\n)
LicenseData "LICENSE"
# This will be in the installer/uninstaller's title bar
Name "${COMPANYNAME} - ${APPNAME}"
Icon C:\Users\james\projects\propmtime\propmtime.ico
outFile "installers\propmtime_installer_win64.exe"

!include LogicLib.nsh

page license
page directory
Page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
  messageBox mb_iconstop "Administrator rights required!"
  setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
  quit
${EndIf}
!macroend

function .onInit
  setShellVarContext all
  !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
  # Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
  setOutPath $INSTDIR
  # Files added here should be removed by the uninstaller (see section "uninstall")
  File /r C:\Users\james\projects\propmtime\app\propmtime\*

  # Uninstaller - See function un.onInit and section "uninstall" for configuration
  writeUninstaller "$INSTDIR\uninstall.exe"
  
  # Start Menu
  createDirectory "$SMPROGRAMS\${COMPANYNAME}"
  createShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\${APPNAME}\${EXENAME}" "" "$INSTDIR\${APPNAME}\${APPNAME}.ico"

  # run on Windows startup
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}" "$INSTDIR\${APPNAME}\${EXENAME}"

  # Registry information for add/remove programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\${APPNAME}\${APPNAME}.ico$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd
# Uninstaller
function un.onInit
	 SetShellVarContext all
  # Verify the uninstaller - last chance to back out
	 MessageBox MB_OKCANCEL "Permanently remove ${APPNAME}?" IDOK next
		Abort
	 next:
  !insertmacro VerifyUserIsAdmin
functionEnd
section "uninstall"
  # Remove Start Menu launcher
  delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
  # Try to remove the Start Menu folder - this will only happen if it is empty
  rmDir "$SMPROGRAMS\${COMPANYNAME}"
  # Remove files
  RMDir /r $INSTDIR\${APPNAME}
  RMDir /r $INSTDIR\${APPNAME}_0.6.0
  delete $INSTDIR\${APPNAME}_0.6.0.clip
  delete $INSTDIR\*.json
  delete $INSTDIR\LICENSE
  delete $INSTDIR\COPY
  # Always delete uninstaller as the last action
  delete $INSTDIR\uninstall.exe
  # Try to remove the install directory - this will only happen if it is empty
  rmDir $INSTDIR
  rmDir "$PROGRAMFILES\${COMPANYNAME}"
  # Remove uninstaller information from the registry
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
sectionEnd