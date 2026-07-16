[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles
[SourceFiles]
SourceFiles0=C:\Users\Administrator\Desktop\Sentinel AI\installer_package
[SourceFiles0]
%FILE0%=
%FILE1%=
%FILE2%=
%FILE3%=
%FILE4%=
%FILE5%=
%FILE6%=
[Strings]
InstallPrompt=
DisplayLicense=
FinishMessage=Sentinel AI Agent setup completed.
TargetName=C:\Users\Administrator\Desktop\Sentinel AI\installer_package\SentinelAgentSetup.exe
FriendlyName=Sentinel AI Agent Setup
AppLaunched=cmd.exe /c SentinelAgent_Installer.bat
PostInstallCmd=<None>
AdminQuietInstCmd=cmd.exe /c SentinelAgent_Installer.bat
UserQuietInstCmd=cmd.exe /c SentinelAgent_Installer.bat
FILE0=SentinelAgent.exe
FILE1=SentinelAgent_Installer.bat
FILE2=SentinelAgent_Uninstaller.bat
FILE3=ConfigureSentinelAgent.ps1
FILE4=SentinelAgent_Diagnostics.bat
FILE5=config.json
FILE6=INSTALLATION_GUIDE.txt
