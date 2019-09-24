//Copyright Software Bisque 2017

#ifndef SBERRORX_H
#define SBERRORX_H


#define SB_OK                                             0                   //No error.
#define ERR_NOERROR                                       0                   //|No error.|


#define ERR_COMMNOLINK                                    200                 //|The operation failed because there is no connection to the device.|
#define ERR_COMMOPENING                                   201                 //|Could not open communications port.  The port is either in use by another application or not recognized by the system.|
#define ERR_COMMSETTINGS                                  202                 //|The communications port could not support the specified settings.|
#define ERR_NORESPONSE                                    203                 //|No response from the device.|
#define ERR_MEMORY                                        205                 //|Error: memory error.|
#define ERR_CMDFAILED                                     206                 //|Error: command failed.|
#define ERR_DATAOUT                                       207                 //|Transmit time-out.|
#define ERR_TXTIMEOUT                                     208                 //|Transmission time-out.|
#define ERR_RXTIMEOUT                                     209                 //|Receive time-out.|
#define ERR_POSTMESSAGE                                   210                 //|Post message failed.|
#define ERR_POINTER                                       211                 //|Pointer error.|
#define ERR_ABORTEDPROCESS                                212                 //|Process aborted.|
#define ERR_AUTOTERMINATE                                 213                 //|Error, poor communication, connection automatically terminated.|
#define ERR_INTERNETSETTINGS                              214                 //|Error, cannot connect to host.|
#define ERR_NOLINK                                        215                 //|No connection to the device.|
#define ERR_DEVICEPARKED                                  216                 //|Error, the device is parked and must be unparked using the Unpark command before proceeding.|
#define ERR_DRIVERNOTFOUND                                217                 //|A necessary driver was not found.|
#define ERR_LIMITSEXCEEDED                                218                 //|Limits exceeded.|
#define ERR_COMMANDINPROGRESS                             219                 //|Command in progress.|


#define ERR_CMD_IN_PROGRESS_MODELESSDLG                   110                 //|A Window command is already is already in progress.|
#define ERR_CMD_IN_PROGRESS_DBQRY                         111                 //|A Database Query command is already is already in progress.|
#define ERR_CMD_IN_PROGRESS_IMGSYS                        112                 //|An Imaging System command is already in progress.|
#define ERR_CMD_IN_PROGRESS_FW                            113                 //|A Filter Wheel command is already is in progress.|
#define ERR_CMD_IN_PROGRESS_SATTRACK                      114                 //|A Satellite Tracking command is already is in progress.|
#define ERR_CMD_IN_PROGRESS_CAL_RUN                       115                 //|A TPoint calibration run is already in progress.|
#define ERR_CMD_IN_PROGRESS_THEATER                       116                 //|A Threater Suite Command in already in progress.|
#define ERR_CMD_IN_PROGRESS_FOC                           117                 //|A Focuser command is already is in progress.|
#define ERR_CMD_IN_PROGRESS_OTA                           118                 //|An OTA command is already in progress.|
#define ERR_CMD_IN_PROGRESS_APR                           119                 //|An Automated Pointing Calibration run is already in progress.|
#define ERR_CMD_IN_PROGRESS_CAM                           120                 //|A Camera command is already in progress.|
#define ERR_CMD_IN_PROGRESS_MNT                           121                 //|A Mount command is already in progress.|
#define ERR_CMD_IN_PROGRESS_CLS                           122                 //|A Closed Loop Slew command already in progress.|
#define ERR_CMD_IN_PROGRESS_DOME                          123                 //|A Dome command is already in progress.|
#define ERR_CMD_IN_PROGRESS_ROT                           124                 //|A Rotator command is already in progress.|


#define ERR_WAITING_CAM_CMD                               130                 //|Error waiting on camera command to complete.|
#define ERR_UNEXPECTED_CALLING_THREAD                     131                 //|Unexpected error.|
#define ERR_WAITING_FOR_CAM_TEMP                          132                 //|Error waiting on camera temperature to complete.|
#define ERR_EXITING_CAM                                   133                 //|Error deleting camera.|


#define ERR_DEVICENOTSUPPORTED                            220                 //|Device not supported.|
#define ERR_NOTPOINT                                      221                 //|TPoint model not available.|
#define ERR_MOUNTNOTSYNCED                                222                 //|The operation failed because the mount not yet been synchronized to a known star.|
#define ERR_USERASCLIENT                                  223                 //|You must use the RASClient application to connect to a remote observatory.|
#define ERR_THESKYNOTRUNNING                              224                 //|The attempted operation requires the TheSky5 Level IV or TheSky6/TheSkyX Professional Edition and it must be running.|
#define ERR_NODEVICESELECTED                              225                 //|No device has been selected.|
#define ERR_CANTLAUNCHTHESKY                              226                 //|Unable to launch TheSky.|
#define ERR_NOTINITIALIZED                                227                 //|Telescope not initialized. The telescope must be initialized in order to perform this operation.|
#define ERR_COMMANDNOTSUPPORTED                           228                 //|This command is not supported by the selected device.|
#define ERR_LX200DESTBELOWHORIZ                           229                 //|The Slew command failed because the LX200/Autostar reports that the destination coordinates are below the horizon.|
#define ERR_LX200OUTSIDELIMIT                             230                 //|The Slew command failed because the LX200/Autostar reports that slewing to the destination coordinates is not possible. Was the telescope synchronized?|
#define ERR_MOUNTNOTHOMED                                 231                 //|The operation failed because the mount is not yet homed.|
#define ERR_TPOINT_NO_MORE_SAMPLES                        232                 //|TPoint not accepting additional pointing samples.|
#define ERR_JOYSTICKING                                   233                 //|The operation failed because the joystick is being activated or the device is under manual control.|
#define ERR_NOPARKPOSITION                                234                 //|Error, no park position has been set.|
#define ERR_BADPOINTINGSAMPLE                             235                 //|The pointing sample was rejected because it is too far out to be valid.This error is typically the result of an exceedingly poor polar alignment or an improperly initialized mount, for example an incorrect star synchronization.To avoid this error, double check your polar alignment with the 'Rough Polar Alignment' (Paramount's only) and or telescope initialization.|
#define ERR_DSSRXTIMEOUT                                  236                 //|Time-out downloading DSS photo.|
#define ERR_BADSYNCINTOMODEL                              237                 //|The 'Sync mount into the existing model' is rejected because it is too far out.Double check polar alignment, date and time and location.|
#define ERR_MOUNT1NOTPARKED                               238                 //|The mount is not parked.|
#define ERR_MOUNT2NOTPARKED                               239                 //|The mount number 2 is not parked.|
#define ERR_MOUNT3NOTPARKED                               240                 //|The mount number 3 is not parked.|


#define FLASH_REPROGRAMMED                                3015                //|Turn off power, move dip switches to off position, then turn power on and reconnect.|
#define FLASH_NEEDSREPROGRAMMED                           3016                //|Firmware needs re-programmed.  This will reset all limit minimum and maximum values.|
#define FIRMWARE_NOT_SUPPORTED                            3017                //|Firmware version is not supported.|
#define FLASH_IN_PROGRAM_MODE                             3018                //|The mount firmware in is program mode and cannot be communicated with.Please turn the mount off.Wait at least 5 seconds.Then turn it back on to proceed.|
#define FLASH_NOT_IN_PROGRAM_MODE                         3019                //|The mount firmware is not in the correct state to be re-programmed.|


#define ERR_OBJECTNOTFOUND                                250                 //|Object not found.|
#define ERR_OBJECTTOOLOW                                  251                 //|Object too low.|
#define ERR_MISSING_NIGHTVISIONMODE_THEME                 252                 //|Setting Night Vision Mode failed.On Windows, make sure the required file 'TheSkyX Night Vision Mode.Theme' is available to the Windows Display Properties dialog.|
#define ERR_DISPLAY_PROPS_ALREADY_RUNNING                 253                 //|The Windows Display Properties dialog is open.  Please close it and try again.|
#define ERR_THEME_NOT_SAVED                               254                 //|Night Vision cannot be invoked because the current theme has been modified without being saved. Please save the current theme by clicking Start, Control Panel, Display, and from the Themes tab, click Save As.|
#define ERR_NOOBJECTSELECTED                              255                 //|The command failed because there is no target.  Find or click on a target.|
#define ERR_BADDOMEGEOMETRY                               256                 //|Invalid dome geometry.|


#define ERR_BADPACKET                                     300                 //|Bad packet.|
#define ERR_BADCHECKSUM                                   301                 //|Bad checksum.|
#define ERR_UNKNOWNRESPONSE                               302                 //|Unknown response.|
#define ERR_UNKNOWNCMD                                    303                 //|Unknown command.|
#define ERR_BADSEQUENCENUM                                304                 //|Bad sequence number.|
#define ERR_ENCRYPTION                                    305                 //|Packet encryption failed.|


#define ERR_TASHIFT                                       400                 //|Track and Accumulate Shift Error.|
#define ERR_TAACCUM                                       401                 //|Track and Accumulate Accumulation Error.|
#define ERR_TACENTROID                                    402                 //|Track and Accumulate Centroid Error.|
#define ERR_TAREMOVEPEDESTAL                              403                 //|Track and Accumulate Pedestal Error.|
#define ERR_TASUBOFFSET                                   404                 //|Track and Accumulate Subtract Offset.|
#define ERR_TARESIZEIMAGE                                 405                 //|Track and Accumulate Resize Error.|
#define ERR_TACLEARBUF                                    406                 //|Track and Accumulate Clear Buffer.|
#define ERR_TAFINDMINMAX                                  407                 //|Track and Accumulate find min/max error.|
#define ERR_TASTARBRTDOWN50                               408                 //|Track and Accumulate star brightness down 50%.|
#define ERR_TAUSERRECTNOTFOUND                            409                 //|Track and Accumulate rectangle not found.|


#define ERR_COMBINE_BPP                                   500                 //|Combine not available for the image bits-per-pixel.|
#define ERR_COMBINE_FILETYPE                              501                 //|Incorrect file type for this combine function.|
#define ERR_COMBINE_READTRKLST                            502                 //|Error reading track list.|
#define ERR_OUTOFDISKSPACE                                503                 //|Out of disk space.|
#define ERR_SATURATEDPIXELS                               504                 //|Cannot proceed, saturated pixels found. If possible lower your exposure time.|
#define ERR_FILEAREREADONLY                               505                 //|Unable to complete the operation because one or more files are read only (Windows) or locked (Mac).|
#define ERR_PATHNOTFOUND                                  506                 //|Unable to create or access the folder.|
#define ERR_FILEMUSTBESAVED                               507                 //|Please save the photo before using this command.|
#define ERR_FILEISSTALE                                   508                 //|The data file is stale.|


#define ERR_STARTOODIM1                                   550                 //|Star too dim.  Lost during +X move.|
#define ERR_STARTOODIM2                                   551                 //|Star too dim.  Lost during -X move.|
#define ERR_STARTOODIM3                                   552                 //|Star too dim.  Lost during +Y move.|
#define ERR_STARTOODIM4                                   553                 //|Star too dim.  Lost during -Y move.|
#define ERR_MOVEMENTTOOSMALL1                             554                 //|Motion too small during +X move.  Increase calibration time.|
#define ERR_MOVEMENTTOOSMALL2                             555                 //|Motion too small during -X move.  Increase calibration time.|
#define ERR_MOVEMENTTOOSMALL3                             556                 //|Motion too small during +Y move.  Increase calibration time.|
#define ERR_MOVEMENTTOOSMALL4                             557                 //|Motion too small during -Y move.  Increase calibration time.|
#define ERR_STARTOOCLOSETOEDGE1                           558                 //|Star too close to edge after +X move.|
#define ERR_STARTOOCLOSETOEDGE2                           559                 //|Star too close to edge after -X move.|
#define ERR_STARTOOCLOSETOEDGE3                           560                 //|Star too close to edge after +Y move.|
#define ERR_STARTOOCLOSETOEDGE4                           561                 //|Star too close to edge after -Y move.|
#define ERR_AXISNOTPERPENDICULAR1                         562                 //|Invalid motion in X axis.|
#define ERR_AXISNOTPERPENDICULAR2                         563                 //|Invalid motion in Y axis.|
#define ERR_BOTHAXISDISABLED                              564                 //|Unable to calibrate, both axis are disabled.  At least one axis must be enabled to calibrate.|
#define ERR_RECALIBRATE                                   565                 //|Autoguider calibration is required.  The Declination at calibration is unknown, but declination is now known.|
#define ERR_NOBRIGHTOBJECTFOUND                           566                 //|No bright object found on image.|
#define ERR_INSUFFICIENTCORRELATION                       567                 //|Insufficient correlation between target image and image under analysis.|
#define ERR_ROTATORCONNECTED                              568                 //|Autoguider calibration is required.  A camera rotator was connected after calibration was performed.|
#define ENUM_ERR_ROTATORDISCONNECTED                      569                 //|Autoguider calibration is required.  A camera rotator was disconnected after calibration was performed.|
#define ERR_IMAGESIZECHANGED                              570                 //|Autoguider calibration is required.  Image size changed since most recent calibration.|
#define ENUM_ERR_PARAMOUNT_SYNC_NOT_REQ                   572                 //|The Paramount does not require star synchronization.|


#define ERR_DSSNAMETOLONG                                 600                 //|The file name and/or path is too long.|
#define ERR_DSSNOTINITED                                  601                 //|The Digitized Sky Survey Setup is not properly initialized, please check Digitized Sky Survey Setup parameters.|
#define ERR_DSSSYSERROR                                   602                 //|System error.  Please verify Digitized Sky Survey Setup parameters are correct and make sure the data is present.|
#define ERR_DSSWRONGDISK                                  603                 //|Wrong Disk.|
#define ERR_DSSNOIMAGE                                    604                 //|No image found to extract.|
#define ERR_DSSINVALIDCOORDINATE                          605                 //|Invalid coordinate(s).|
#define ERR_DSSINVALIDSIZE                                606                 //|Invalid size.|
#define ERR_DSSDLLOLD                                     607                 //|The file DSS_DLL.DLL is old and not compatible with this program. Please obtain the latest DSS_DLL.DLL.|
#define ERR_DSSCDROM                                      608                 //|Unable to access the Digitized Sky Survey data.  Make sure the volume or drive is valid.|
#define ERR_DSSHEADERSPATH                                609                 //|Unable to access the headers path specified in Digitized Sky Survey Setup.  Please correct the path.|
#define ERR_DSSNODSSDISK                                  610                 //|The Digitized Sky Survey data is not present in the specified location.|
#define ERR_DSSNOTINSURVEY                                611                 //|Not in survey.|
#define ERR_SE_INTERNAL_ERROR                             612                 //|An error occured within Source Extraction.|


#define ERR_ILINK_NOSCALE                                 650                 //|Image Link has no image scale.|
#define ERR_ILINK_TOOFEWBMP                               651                 //|Image Link failed because there are not enough stars in the photo.  Possible solutions include:<ol><li>Try a longer exposure.</li> <li>Lower the <b><i>Detection Threshold</i></b> in the <b><i>Source Extraction Setup</i></b> window to detect fainter stars in the photo.</li><li>Lower the <b><i>Minimum Number of Pixels Above Threshold</i></b> in the <b><i>Source Extraction Setup</i></b> window to extract stars near the background.</li></ol>|
#define ERR_ILINK_TOOFEWSKY                               652                 //|Image Link failed because there are an insufficient number of matching cataloged stars.  There must be at least eight cataloged stars in each image to perform an Image Link. Verify which star databases are active.|
#define ERR_ILINK_NOMATCHFOUND                            653                 //|Image Link failed, no pattern matching found.  Make sure the RA/Dec coordinates in the FITS header are correct, and double-check the image scale.|
#define ERR_ILINK_NOIMAGE                                 654                 //|Image Link failed because there is no FITS photo to compare.  Click the <b>Open Fits</b> button on the <b>Search</b> tab to proceed.|
#define ERR_ILINK_ERR_ASTROM_SOLN_FAILED                  655                 //|The astrometric solution failed.|
#define ERR_ILINK_TOO_FEW_PAIRS                           656                 //|Not enough photo-catalog pairs for an astrometric solution.|
#define ERR_ILINK_INVALID_SCALE                           657                 //|The astrometric solution returned an invalid image scale.|
#define ERR_ILINK_SOLN_QUESTIONABLE                       658                 //|The astrometric solution appears invalid.|
#define ERR_ILINK_RMS_POOR                                659                 //|The astrometric solution RMS appears invalid.|
#define ERR_ILINK_WRITING_INTERMEDIATE_FILE               660                 //|Error writing intermediate astrometry file.|
#define ERR_ILINK_TOO_MANY_OBJECTS                        661                 //|Too many light sources were found in the photo, increase the Source Extraction Setup's <b>Detection threshold</b> setting (Setup tab).|
#define ERR_ILINK_REQUIRED                                662                 //|This operation requires a successful Image Link and one has not been performed.|


#define ERR_SKIPIMAGE                                     700                 //|Skip image error.|
#define ERR_BADFORMAT                                     701                 //|Unrecognized or bad file format.|
#define ERR_OPENINGFILE                                   702                 //|Unable to open file.|
#define ERR_FEATURENAINLEVEL                              703                 //|This edition does not support the requested feature.|
#define ERR_SOCKETEXCEPTION                               704                 //|An error occurred during a network call.|
#define ERR_CANTCREATETHREAD                              705                 //|Unable to create a new thread.|


#define ERR_F_DOESNOTEXIST                                709                 //|The file or folder does not exist.|
#define ERR_F_ACCESS_WRITE                                707                 //|Access denied. You do not have write access to the file or folder or item.|
#define ERR_F_ACCESS_READ                                 706                 //|Access denied. You do not have read access to the file or folder or item.|
#define ERR_F_ACCESS_RW                                   708                 //|Access denied. You do not have read/write access to the file or folder or item.|


#define ERR_OPENGL_NOT_COMPAT                             711                 //|A newer version of OpenGL is required to run this application.|


#define ERR_CHANGE_PASSWORD                               730                 //|You are required to change your password before you can access this site.|
#define ERR_OP_REQUIRES_OPENGL                            732                 //|This feature requires hardware 3D acceleration.<br><br>Click <a href='http://www.bisque.com/videocards'>here</a> for a list of recommended video cards.<br><br>|
#define ERR_INDEX_OUT_OF_RANGE                            733                 //|The index is out of range.|
#define ERR_TRIAL_EXPIRED                                 734                 //|The trial period has expired.|
#define ERR_INVALID_SNUM                                  735                 //|Invalid serial number.|
#define ERR_OP_REQUIRES_OPENGL2PLUS                       736                 //|This feature requires <b>advanced capabilities</b> of OpenGL 2.0 or later.<br><br>Go to Preferences, Advanced tab (on Mac, TheSkyX Menu, on Windows Tools Menu) and enable 'OpenGL 2 Plus Features' to see if it works with your video card hardware.<br><br><div style='color:OliveDrab'>Warning, your video card might not be capable of this feature.</div>  <br><br>Click <a href='http://www.bisque.com/videocards'>here</a> for a list of recommended video cards. |
#define ERR_BADWEATHER                                    737                 //|Bad weather prohibits this operation.|
#define ERR_WEATHERSTATION_NOT_READY1                     738                 //|The weather station is not connected.|
#define ERR_WEATHERSTATION_NOT_READY2                     739                 //|The weather station is still initializing.|
#define ERR_WEATHERSTATION_NOT_READY3                     740                 //|Communication with the weather station is poor or lost.|
#define ERR_WEATHERSTATION_NOT_READY4                     741                 //|The weather station is in an unknown state.|


#define ERR_SGSTARBRTDOWN50                               800                 //|Self-guide star brightness down 50%.|
#define ERR_SGNEXT                                        801                 //|Self-guide next error.|
#define ERR_SGNEXT2                                       802                 //|Self-guide next two error.|


#define ERR_MNCPFIRSTERROR                                900                 //|MNCP first error.|


#define ERR_MNCPLASTERROR                                 999                 //|MNCP last error.|


#define ERR_AUTOSAVE                                      1130                //|Auto-save error.|


#define ERR_UPLOADNOTST6FILE                              1150                //|Unable to load ST-6 file.|
#define ERR_NOHEADADJNEEDED                               1151                //|No head adjustment needed.|
#define ERR_NOTCFW6A                                      1152                //|Not a CFW 6A.|
#define ERR_NOINTERFACE                                   1153                //|No interface has been selected.|
#define ERR_CAMERANOTFOUND                                1154                //|Camera not found.|
#define ERR_BAUDSWITCHFAILED                              1155                //|Baud switch failed.|
#define ERR_CANNOTUPLOADDARK                              1156                //|Unable to upload dark frame.|
#define ERR_SKIPPINGDARK                                  1157                //|Skipping dark.|
#define ERR_SKIPPINGLIGHT                                 1158                //|Skipping light.|
#define ERR_SELFGUIDENA                                   1159                //|Self guide not available.|
#define ERR_TRACKLOGNA                                    1160                //|Tracking log not available.|
#define ERR_AOREQUIREST78                                 1161                //|AO not available for this camera.|
#define ERR_CALIBRATEAONOTON                              1162                //|AO not calibrated.|
#define ERR_WRONGCAMERAFOUND                              1163                //|A camera was detected, but it does not match the one selected.|
#define ERR_PIXEL_MATH_OPERAND                            1164                //|Cannot multiply or divide the image pixels by an operand less than 0.001.|
#define ERR_IMAGE_SIZE                                    1165                //|Enlarged image would exceed maximum image size. Try cropping it first.|
#define ERR_CANNOT_COLORGRAB                              1166                //|There is not a color filter wheel attached.|
#define ERR_WRONGCFWFOUND                                 1167                //|A filter wheel was detected, but it does not match the one selected.|
#define FILTERNOTFOUND                                    1168                //|The filter name is not valid, please correct it.|


#define ERR_APOGEECFGNAME                                 1200                //|A required initialization file was not found.  Go to Camera, Setup, and press the Settings button to choose the correct file.|
#define ERR_APOGEECFGDATA                                 1201                //|Error in Apogee INI file.|
#define ERR_APOGEELOAD                                    1202                //|Error transferring APCCD.INI data to camera.|


#define ERR_APOGEEOPENOFFSET                              1220                //|Invalid base I/O address passed to function.|
#define ERR_APOGEEOPENOFFSET1                             1221                //|Register access operation error.|
#define ERR_APOGEEOPENOFFSET2                             1222                //|Invalid CCD geometry.|
#define ERR_APOGEEOPENOFFSET3                             1223                //|Invalid horizontal binning factor.|
#define ERR_APOGEEOPENOFFSET4                             1224                //|Invalid vertical binning factor.|
#define ERR_APOGEEOPENOFFSET5                             1225                //|Invalid AIC value.|
#define ERR_APOGEEOPENOFFSET6                             1226                //|Invalid BIC value.|
#define ERR_APOGEEOPENOFFSET7                             1227                //|Invalid line offset value.|
#define ERR_APOGEEOPENOFFSET8                             1228                //|CCD controller sub-system not initialized.|
#define ERR_APOGEEOPENOFFSET9                             1229                //|CCD cooler failure.|
#define ERR_APOGEEOPENOFFSET10                            1230                //|Failure reading image data.|
#define ERR_APOGEEOPENOFFSET11                            1231                //|Invalid buffer pointer specified.|
#define ERR_APOGEEOPENOFFSET12                            1232                //|File not found or not valid.|
#define ERR_APOGEEOPENOFFSET13                            1233                //|Camera configuration data is invalid.|
#define ERR_APOGEEOPENOFFSET14                            1234                //|Invalid CCD handle passed to function.|
#define ERR_APOGEEOPENOFFSET15                            1235                //|Invalid parameter passed to function.|


#define ERR_GPSTFPNOTRUNNING                              1300                //|Shutter timing is enabled, but the GPSTFP application is not running.|


#define ERR_IMAGECALWRONGBPP                              5000                //|Unable to reduce. The image being reduced doesn't have the same bits per pixel as the reduction frames.|
#define ERR_IMAGECALWRONGSIZE                             5001                //|Unable to reduce. The image being reduced is larger than the reduction frames.|
#define ERR_IMAGECALWRONGBIN                              5002                //|Unable to reduce. The image being reduced doesn't have the same bin mode as the reduction frames.|
#define ERR_IMAGECALWRONGSUBFRAME                         5003                //|Unable to reduce. The image being reduced doesn't entirely overlap the reduction frames. Make sure the subframes overlap.|
#define ERR_IMAGECALGROUPINUSE                            5004                //|Unable to proceed. The image reduction group is currently in use.|
#define ERR_IMAGECALNOSUCHGROUP                           5005                //|Unable to proceed. The selected image reduction group no longer exists.|
#define ERR_IMAGECALNOFRAMES                              5006                //|Unable to proceed. The selected image reduction group does not contain any reduction frames.|


#define ERR_WRONGBPP                                      5020                //|Unable to proceed. The images don't have the same bits per pixel.|
#define ERR_WRONGSIZE                                     5021                //|Unable to proceed. The images don't have the same dimensions.|
#define ERR_WRONGTYPE                                     5022                //|Unable to proceed. The images don't have the same format.|


#define ERR_NOIMAGESINFOLDER                              5050                //|Unable to proceed. The folder doesn't contain any readable images.|
#define ERR_NOPATTERNMATCH                                5051                //|The files could not be aligned. No pattern match was found.|


#define ERR_NOTFITS                                       5070                //|This operation requires a FITS file.|


#define ERR_KVW_NOMINIMA                                  6000                //|KVW_NOMINIMA.|
#define ERR_KVW_DETERMINANTZERO                           6001                //|KVW_DETERMINANTZERO.|
#define ERR_KVW_DIVISIONBYZERO                            6002                //|KVW_DIVISIONBYZERO.|
#define ERR_KVW_NOTENOUGHPOINTS                           6003                //|KVW_NOTENOUGHPOINTS.|


#define ERR_AF_ERRORFIRST                                 7000                //|@Focus error.|
#define ERR_AF_DIVERGED                                   7001                //|@Focus diverged. |
#define ERR_AF_UNDERSAMPLED                               7003                //|Insufficient data to measure focus, increase exposure time. |


#define ERR_LT_TARGET_LOST_DEC_TOO_HIGH                   7500                //|Target lost, declination too high to maintain tracking.|
#define ERR_LT_TARGET_LOST_CANNOT_TRACK                   7501                //|Target lost, unable to maintain tracking.|
#define ERR_LT_TARGET_LOST_BELOW_HORIZON                  7502                //|Target lost, below horizon.|
#define ERR_LT_TARGET_NOT_A_SATELLITE                     7503                //|Target not a satellite.|


#define ERR_FLICCD_E_FIRST                                8000                //|ERR_FLICCD_E_FIRST|
#define ERR_FLICCD_E_NOTSUPP                              8001                //|ERR_FLICCD_E_NOTSUPP|
#define ERR_FLICCD_E_INVALID_PARAMETER                    8002                //|ERR_FLICCD_E_INVALID_PARAMETER|
#define ERR_FLICCD_E_INVALID_COMPORT                      8003                //|ERR_FLICCD_E_INVALID_COMPORT|
#define ERR_FLICCD_E_COMPORT_ERROR                        8004                //|ERR_FLICCD_E_COMPORT_ERROR|
#define ERR_FLICCD_E_FAILED_RESET                         8005                //|ERR_FLICCD_E_FAILED_RESET|
#define ERR_FLICCD_E_COMMTIMEOUT                          8006                //|ERR_FLICCD_E_COMMTIMEOUT|
#define ERR_FLICCD_E_BADDATA                              8007                //|ERR_FLICCD_E_BADDATA|
#define ERR_FLICCD_E_NOCALIBRATE                          8008                //|ERR_FLICCD_E_NOCALIBRATE|
#define ERR_FLICCD_E_DEVICE_NOT_CONFIGURED                8009                //|ERR_FLICCD_E_DEVICE_NOT_CONFIGUR|
#define ERR_FLICCD_E_COMMWRITE                            8010                //|ERR_FLICCD_E_COMMWRITE|
#define ERR_FLICCD_E_INVALID_DEVICE                       8011                //|ERR_FLICCD_E_INVALID_DEVICE|
#define ERR_FLICCD_E_FUNCTION_NOT_SUPPORTED               8012                //|ERR_FLICCD_E_FUNCTION_NOT_SUPPORTED|
#define ERR_FLICCD_E_BAD_BOUNDS                           8013                //|ERR_FLICCD_E_BAD_BOUNDS|
#define ERR_FLICCD_E_GRABTIMEOUT                          8014                //|ERR_FLICCD_E_GRABTIMEOUT|
#define ERR_FLICCD_E_TODATAHB                             8015                //|ERR_FLICCD_E_TODATAHB|
#define ERR_FLICCD_E_TODATALB                             8016                //|ERR_FLICCD_E_TODATALB|
#define ERR_FLICCD_E_ECPNOTREADY                          8017                //|ERR_FLICCD_E_ECPNOTREADY|
#define ERR_FLICCD_E_ECPREADTIMEOUTHB                     8018                //|ERR_FLICCD_E_ECPREADTIMEOUTHB|
#define ERR_FLICCD_E_ECPREADTIMEOUTLB                     8019                //|ERR_FLICCD_E_ECPREADTIMEOUTLB|
#define ERR_FLICCD_E_ECPREADTIMEOUT                       8020                //|ERR_FLICCD_E_ECPREADTIMEOUT|
#define ERR_FLICCD_E_ECPREVERSETIMEOUT                    8021                //|ERR_FLICCD_E_ECPREVERSETIMEOUT|
#define ERR_FLICCD_E_ECPWRITETIMEOUTHB                    8022                //|ERR_FLICCD_E_ECPWRITETIMEOUTHB|
#define ERR_FLICCD_E_ECPWRITETIMEOUTLB                    8023                //|ERR_FLICCD_E_ECPWRITETIMEOUTLB|
#define ERR_FLICCD_E_ECPWRITETIMEOUT                      8024                //|ERR_FLICCD_E_ECPWRITETIMEOUT|
#define ERR_FLICCD_E_FORWARDTIMEOUT                       8025                //|ERR_FLICCD_E_FORWARDTIMEOUT|
#define ERR_FLICCD_E_NOTECP                               8026                //|ERR_FLICCD_E_NOTECP|
#define ERR_FLICCD_E_FUNCTIONNOTSUPP                      8027                //|ERR_FLICCD_E_FUNCTIONNOTSUPP|
#define ERR_FLICCD_E_NODEVICES                            8028                //|ERR_FLICCD_E_NODEVICES|
#define ERR_FLICCD_E_WRONGOS                              8029                //|ERR_FLICCD_E_WRONGOS|
#define ERR_TEMMA_RAERROR                                 8030                //|Slew/sync error: Temma reports the right ascension is incorrect for go to or synchronization.|
#define ERR_TEMMA_DECERROR                                8031                //|Slew/sync error: Temma reports the declination is incorrect for go to or synchronization.|
#define ERR_TEMMA_TOOMANYDIGITS                           8032                //|Slew/sync error: Temma reports the format error for go to or synchronization.|
#define ERR_TEMMA_BELOWHORIZON                            8033                //|Slew/sync error: Temma reports the object is below the horizon.|
#define ERR_TEMMA_STANDBYMODE                             8034                //|Slew error: Temma reports the mount is in standby mode.|


#define ERR_ACLUNDEFINEDERR                               1                   //|ACL undefined error.|
#define ERR_ACLSYNTAX                                     2                   //|ACL syntax error.|


#define ERR_ACLTYPEMISMATCH                               10                  //|ACL type mismatch error.|
#define ERR_ACLRANGE                                      11                  //|ACL range error.|
#define ERR_ACLVALREADONLY                                12                  //|ACL value is read only.|
#define ERR_ACLCMDUNSUPPORTED                             13                  //|ACL command is unsupported.|
#define ERR_ACLUNSUPPORTID                                14                  //|ACL unsupported id.|
#define ERR_ACLCMDINACTIVE                                15                  //|ACL command inactive.|


#define ERR_ACLGOTOILLEGAL                                100                 //|ACL illegal go to command.|
#define ERR_ACLGOTOBELOWHRZ                               101                 //|ACL error: destination is below the horizon.|
#define ERR_ACLGOTOLIMITS                                 102                 //|ACL go to limit.|


#define ERR_NOT_IMPL                                      11000               //|This command is not supported.|
#define ERR_NOT_IMPL_IN_MODEL                             11001               //|This command is not implemented in the model.|
#define ERR_OPENING_FOVI_FILES                            11002               //|One of the Field of View Indicator database files cannot be found. (Abnormal installation.)|
#define ERR_NO_IRIDIUM_SATELLITES                         11003               //|No Iridium satellite two-line elements are currently loaded.|
#define ERR_ACCESS_DENIED                                 11004               //|Access is denied.  Check your username and or password.|
#define ERR_ALL_TLES_DATE_REJECTED                        11005               //|All TLEs were date rejected, so no satellites will be loaded. Check the date of the TLEs and make sure TheSkyX's date is within 45 days of this date.|


#define ERR_SBSCODEBASE                                   1000                //|Base offset for creating wire safe scodes|


#define ERR_SBIGST7FIRST                                  30000               //|SBIG ST7 first error.|


#define ERR_SBIGCCCFWFIRST                                31000               //|SBIG first cfw error.|


#define ENUM_ERR_CFISIOFIRST                              33000               //|CFITSIO first error.|


#define ERR_CUSTOMAPIFIRST                                1400                //|Custom api error code first.|


#define ERR_CUSTOMAPILAST                                 1499                //|Custom api error code last.|
#define ERR_IPLSUITEERR                                   1500                //|IPL suite error first|


#define ERR_GDIERR_BASE                                   1600                //|GDI error base|


#define ERR_SBIGTCEEXTFIRST                               1050                //|SBIG TCE error first.|


#define ERR_SBIGTCEEXTLAST                                1099                //|SBIG TCE error last.|
#define ERR_SBIGSERIALFIRST                               1100                //|SBIG serial error first.|


#define ERR_SBIGSERIALLAST                                1125                //|SBIG serial error last.|


#define ERR_MKS_ERROR_FIRST                               20000               //|MKS first error.|


#define ERR_MKS_ERROR_LAST                                25000               //|MKS last error.|


#define ERR_SOCKET_ERROR_FIRST                            27000               //|Socket first error.|


#define ERR_SOCKET_ERROR_LAST                             27100               //|Socket last error.|


#define ERR_MKS_COMM_BASE                                 21000               //|COMM_BASE.|
#define ERR_MKS_COMM_OKPACKET                             21000               //|COMM_OKPACKET.|
#define ERR_MKS_COMM_NOPACKET                             21001               //|Serial command packet not included with command. COMM_NOPACKET.|
#define ERR_MKS_COMM_TIMEOUT                              21002               //|Receive time-out.COMM_TIMEOUT.|
#define ERR_MKS_COMM_COMMERROR                            21003               //|Serial communication error. COMM_COMMERROR.|
#define ERR_MKS_COMM_BADCHAR                              21004               //|Invalid serial command error. COMM_BADCHAR.|
#define ERR_MKS_COMM_OVERRUN                              21005               //|Packet overrun error. COMM_OVERRUN.|
#define ERR_MKS_COMM_BADCHECKSUM                          21006               //|Bad checksum error. COMM_BADCHECKSU.|
#define ERR_MKS_COMM_BADLEN                               21007               //|Invalid length of serial command error. COMM_BADLEN.|
#define ERR_MKS_COMM_BADCOMMAND                           21008               //|Invalid serial command error. COMM_BADCOMMAND.|
#define ERR_MKS_COMM_INITFAIL                             21009               //|Could not open communications port.  The port is either in use by another application or not recognized by the system. COMM_INITFAIL|
#define ERR_MKS_COMM_NACK                                 21010               //|No acknowledgement of command from device. COMM_NACK.|
#define ERR_MKS_COMM_BADID                                21011               //|Invalid identifier. COMM_BADID.|
#define ERR_MKS_COMM_BADSEQ                               21012               //|Invalid command sequence. COMM_BADSEQ.|
#define ERR_MKS_COMM_BADVALCODE                           21013               //|Invalid command code. COMM_BADVALCODE.|


#define ERR_MKS_MAIN_BASE                                 22000               //|MAIN_BASE.|
#define ERR_MKS_MAIN_WRONG_UNIT                           22001               //|MAIN_WRONG_UNIT.|
#define ERR_MKS_MAIN_BADMOTORINIT                         22002               //|MAIN_BADMOTORINIT.|
#define ERR_MKS_MAIN_BADMOTORSTATE                        22003               //|Unable to slew because the mount has not been homed. Click Telescope, Options, Find Home to home the mount.|
#define ERR_MKS_MAIN_BADSERVOSTATE                        22004               //|Indexing before finding switch 1.|
#define ERR_MKS_MAIN_SERVOBUSY                            22005               //|Indexing before finding switch 2.|
#define ERR_MKS_MAIN_BAD_PEC_LENGTH                       22006               //|Invalid length of PEC table. MAIN_BAD_PEC_LENGTH.|
#define ERR_MKS_MAIN_AT_LIMIT                             22007               //|The mount is at a minimum or maximum position limit and cannot be slewed.  This error may be the result of improper synchronization near the meridian. When syncing near the meridian, be sure the optical tube assembly and the synchronization star are on opposite sides of the meridian.|
#define ERR_MKS_MAIN_NOT_HOMED                            22008               //|Mount has not been homed. Click Telescope, Options, Find Home to home the mount.|
#define ERR_MKS_MAIN_BAD_POINT_ADD                        22009               //|Object-Tracking point error.|
#define ERR_MKS_MAIN_INVALID_PEC                          22010               //|The PEC table is invalid.|
#define ERR_MKS_SLEW_PAST_LIMIT                           22011               //|The slew is not possible because the target is beyond a slew limit.Slew limits prevent the mount from colliding with the pier and or encountering a physical hard stop.  In other words, a target beyond a slew limit is mechanically unreachable.|


#define ERR_MKS_MAIN_BAD_CONTROL_CODE                     22020               //|MKS4000: Command-code is invalid.|
#define ERR_MKS_MAIN_BAD_SYSTEM_ID                        22021               //|Unknown system type (not an MKS 3000 or MKS 4000)|


#define ERR_MKS_FLASH_BASE                                23000               //|FLASH_BASE.|
#define ERR_MKS_FLASH_PROGERR                             23001               //|FLASH_PROGERR.|
#define ERR_MKS_FLASH_ERASEERR                            23002               //|FLASH_ERASEERR.|
#define ERR_MKS_FLASH_TIMEOUT                             23003               //|FLASH_TIMEOUT.|
#define ERR_MKS_FLASH_CANT_OPEN_FILE                      23004               //|FLASH_CANT_OPEN_FILE.|
#define ERR_MKS_FLASH_BAD_FILE                            23005               //|FLASH_BAD_FILE.|
#define ERR_MKS_FLASH_FILE_READ_ERR                       23006               //|FLASH_FILE_READ_ERR.|
#define ERR_MKS_FLASH_BADVALID                            23007               //|FLASH_BADVALID.|
#define ERR_MKS_FLASH_INVALID_SECTION                     23008               //|MKS4000: Invalid FLASH section.|
#define ERR_MKS_FLASH_INVALID_ADDRESS                     23009               //|MKS4000: Invalid FLASH address.|


#define ERR_MKS_MOTOR_BASE                                24000               //|MOTOR_BASE.|
#define ERR_MKS_MOTOR_OK                                  24000               //|MOTOR_OK.|
#define ERR_MKS_MOTOR_OVERCURRENT                         24001               //|MOTOR_OVERCURRENT.|
#define ERR_MKS_MOTOR_POSERRORLIM                         24002               //|<b>The mount cannot slew. See the list of likely reasons below.<br><br>To recover, turn the mount off, wait a few moments and then turn the mount back on.<br><br></b><table border=1><tr><th>Possible Reasons In Order of Likelihood</th><th>Solution</th></tr><tr><td>1. The mount payload is too far out of balance.</td><td>Carefully balance the payload.</td></tr><tr><td>2. A transport lock knob is in the lock position.</td><td>Unlock the transport lock knob(s).</td></tr><tr><td>3. The mount has encountered a physical obstacle.</td><td>Move the obstacle.</td></tr><tr><td>4. You've recently added through the mount cabling.</td><td>Make sure you did not accidentally unplug an internal mount cable.  Also make sure the added cabling is not binding a mount axis from rotating.</td></tr><tr><td>5. The worm block cam adjustment has been adjusted recently and it is too tight.</td><td>See the tehnical article on adjusting the worm block.</td></tr><tr><td>6. The ambient temperature is near or below freezing.</td><td>Lower mount speed/acceleration.</td></tr></table><br><br>|
#define ERR_MKS_MOTOR_STILL_ON                            24003               //|Motor still on but command needs it stopped.|
#define ERR_MKS_MOTOR_NOT_ON                              24004               //|Motor off.|
#define ERR_MKS_MOTOR_STILL_MOVING                        24005               //|Motor still slewing but command needs it stopped.|
#define ERR_MKS_MOTOR_FIELD_TIMEOUT                       24006               //|Timed out while fielding.|
#define ERR_MKS_MOTOR_BAD_CONTROL_STATE                   24007               //|MOTOR_BAD_CONTROL_STATE.|
#define ERR_MKS_MOTOR_BAD_SERVO_STATE                     24005               //|MOTOR_BAD_SERVO_STATE.|


#define ERR_GEMINI_OBJECT_BELOW_HORIZON                   275                 //|Gemini - Object below the horizon.|
#define ERR_GEMINI_NO_OBJECT_SELECTED                     276                 //|Gemini - No object selected.|
#define ERR_GEMINI_MANUAL_CONTROL                         277                 //|Gemini - Hand paddle is in manual control mode or the Prevent Slews option is turned on.|
#define ERR_GEMINI_POSITION_UNREACHABLE                   278                 //|Gemini - Position is unreachable.|
#define ERR_GEMINI_NOT_ALIGNED                            279                 //|Gemini - Gemini not aligned.|
#define ERR_GEMINI_OUTSIDE_LIMITS                         280                 //|Gemini - Outside slew limits.|
#define ERR_GEMINI_VERSION_NOT_SUPPORTED                  281                 //|Gemini - Version 4 or later is required. Please update your Gemini firmware.|


#define ERR_VIXEN_UNKNOWN                                 290                 //|Star Book - Unknown error accessing mount.|
#define ERR_VIXEN_URLNOTSET                               291                 //|Star Book - The specified URL appears to be invalid.|
#define ERR_VIXEN_STATUSINVALID                           292                 //|Star Book - No or invalid data received.|
#define ERR_VIXEN_STATUSNOTAVAILABLE                      293                 //|Star Book - Error reading mount status.|
#define ERR_VIXEN_ILLEGALSTATE                            294                 //|Star Book - Mount in wrong state to accept this command.|
#define ERR_VIXEN_SETRADECERROR                           295                 //|Star Book - Error when trying to set RA/Dec.  Make sure the new alignment object is more than 10 degrees from the previous alignment object.|
#define ERR_VIXEN_INVALIDFORMAT                           296                 //|Star Book - Command incorrectly formatted.|
#define ERR_VIXEN_BELOWHORIZON                            297                 //|Star Book - Target below the horizon.|
#define ERR_VIXEN_HOMEERROR                               298                 //|Star Book - Error with HOME command.|


#define ERR_OPEN_NV_THEME                                 11101               //|Error opening TheSkyX Night Vision Mode Theme.  Click the Night Vision Mode Setup command on the Display menu and verify that the Night Vision Mode them file name is correct and the theme exists.|
#define ERR_OPEN_STANDARD_THEME                           11102               //|Error opening the Standard Theme.  Click the Night Vision Mode Setup command on the Display menu and verify that the Standard Theme file name is correct and the theme exists.|
#define ERR_INVALID_DATA                                  11103               //|The comet or minor planet orbital element data contains invalid data and cannot be used to display this object.|



#endif // SBERRORX_H