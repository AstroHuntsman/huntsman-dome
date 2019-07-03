#ifndef _ADDFITSKETINTERFACE_H
#define _ADDFITSKETINTERFACE_H

#define AddFITSKeyInterface_Name "com.bisque.TheSkyX.AddFITSKeyInterface/1.0"

class BasicStringInterface;

/*!
\brief The AddFITSKeyInterface allows camera drivers to add any number of additional FITS keys to the FITS header.

This interface is optional. TheSkyX queries camera drivers for implementation of this interface
after every exposure is complete and if supported allows the camera to add additional information that will
be recorded in the FITS header of photos taken by TheSkyX.  

Each FITS header key must be of type integer, double, or string. TheSkyX will automatically format integer and double values 
according the the FITS definition, but for string keys, it is left up to the camera driver to format correctly.
If this interface is supported, Cameras will first be queried for the number (count) of each type of FITS header key they wish to add, 
after which TheSkyX will query the value for each key using a 0-based index for each type of key.

Please note, TheSkyX automatically adds a number of FITS keys to each photo acquired and this interface does not
allow changing or overriding those keys and their values.  

TheSkyX build 8598 or later is required for this interface to work.  Earlier TheSkyX builds simply ignore this interface and adding FITS key is not possible. 

See TheSkyXFacadeForDriversInterface::build() to determine the build of TheSky in use an act accordingly based on your requirements. 

Speical note, build 8346 to 8597 this inteface was incorrectly called before the exposure started which may or may not matter depending upon the keywords being
added.  

\ingroup Interface
*/

class AddFITSKeyInterface
{
public:
	virtual int countOfIntegerFields(int &nCount) = 0;
	virtual int valueForIntegerField(int nIndex, BasicStringInterface& sFieldName, BasicStringInterface& sFieldComment, int &nFieldValue) = 0;

	virtual int countOfDoubleFields (int &nCount) = 0;
	virtual int valueForDoubleField (int nIndex, BasicStringInterface& sFieldName, BasicStringInterface& sFieldComment, double &dFieldValue) = 0;

	virtual int countOfStringFields (int &nCount) = 0;
	virtual int valueForStringField (int nIndex, BasicStringInterface& sFieldName, BasicStringInterface& sFieldComment, BasicStringInterface &sFieldValue) = 0;

	virtual ~AddFITSKeyInterface(){}

public:

};

#endif