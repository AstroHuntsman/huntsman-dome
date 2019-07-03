#!/bin/bash


TheSkyX_Install=`/usr/bin/find ~/Library/Application\ Support/Software\ Bisque/ -name TheSkyXInstallPath.txt`
echo "TheSkyX_Install = $TheSkyX_Install"

if [ ! -f "$TheSkyX_Install" ]; then
    echo TheSkyXInstallPath.txt not found
    TheSkyX_Path=`/usr/bin/find ~/ -maxdepth 3 -name TheSkyX`
    if [ -d "$TheSkyX_Path" ]; then
		TheSkyX_Path="${TheSkyX_Path}/Contents"
    else
	   echo TheSkyX application was not found.
    	exit 1
	 fi
else
	TheSkyX_Path=$(<"$TheSkyX_Install")
fi

echo "Installing to $TheSkyX_Path"


if [ ! -d "$TheSkyX_Path" ]; then
    echo TheSkyX Install dir not exist
    exit 1
fi

if [ -d "$TheSkyX_Path/Resources/Common/PlugIns64" ]; then
	PLUGINS_DIR="PlugIns64"
else
	PLUGINS_DIR="PlugIns"
fi

cp "./domelist ExampleX2Dome.txt" "$TheSkyX_Path/Resources/Common/Miscellaneous Files/"
#cp "./domepro.ui" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
#cp "./domeprodiag.ui" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
#cp "./domeshutter.ui" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
#cp "./dometimeouts.ui" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
#cp "./Astrometric.png" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
cp "./libx2dome.so" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
#cp "./libx2dome.so.1" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
#cp "./libx2dome.so.1.0" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"
#cp "./libx2dome.so.1.0.0" "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/"

app_owner=`/usr/bin/stat -c "%u" "$TheSkyX_Path" | xargs id -n -u`
if [ ! -z "$app_owner" ]; then
	chown $app_owner "$TheSkyX_Path/Resources/Common/Miscellaneous Files/domelist ExampleX2Dome.txt"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/domepro.ui"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/domeprodiag.ui"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/domeshutter.ui"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/dometimeouts.ui"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/Astrometric.png"
	chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so.1"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so.1.0"
	#chown $app_owner "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so.1.0.0"
fi
chmod  755 "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so"
#chmod  755 "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so.1"
#chmod  755 "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so.1.0"
#chmod  755 "$TheSkyX_Path/Resources/Common/$PLUGINS_DIR/DomePlugIns/libx2dome.so.1.0.0"
