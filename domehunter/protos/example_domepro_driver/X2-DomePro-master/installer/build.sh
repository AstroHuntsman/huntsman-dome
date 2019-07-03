#!/bin/bash

mkdir -p ROOT/tmp/DomePro_X2/
cp "../domepro.ui" ROOT/tmp/DomePro_X2/
cp "../domeprodiag.ui" ROOT/tmp/DomePro_X2/
cp "../domeshutter.ui" ROOT/tmp/DomePro_X2/
cp "../dometimeouts.ui" ROOT/tmp/DomePro_X2/
cp "../Astrometric.png" ROOT/tmp/DomePro_X2/
cp "../domelist DomePro.txt" ROOT/tmp/DomePro_X2/
cp "../build/Release/libDomePro.dylib" ROOT/tmp/DomePro_X2/

if [ ! -z "$installer_signature" ]; then
# signed package using env variable installer_signature
pkgbuild --root ROOT --identifier org.rti-zone.DomePro_X2 --sign "$installer_signature" --scripts Scripts --version 1.0 DomePro_X2.pkg
pkgutil --check-signature ./DomePro_X2.pkg
else
pkgbuild --root ROOT --identifier org.rti-zone.DomePro_X2 --scripts Scripts --version 1.0 DomePro_X2.pkg
fi

rm -rf ROOT
