; NSIS installer hooks for Travelprep MCP
; PREINSTALL / PREUNINSTALL kill both backend and operator processes
; to prevent file-lock conflicts during installation/uninstallation.

!macro PREINSTALL
  DetailPrint "Killing any running Travelprep MCP processes..."
  ExecWait 'taskkill /F /IM travelprep-mcp-backend.exe /T'
  ExecWait 'taskkill /F /IM travelprep-mcp-native.exe /T'
!macroend

!macro PREUNINSTALL
  DetailPrint "Killing any running Travelprep MCP processes before uninstall..."
  ExecWait 'taskkill /F /IM travelprep-mcp-backend.exe /T'
  ExecWait 'taskkill /F /IM travelprep-mcp-native.exe /T'
!macroend
