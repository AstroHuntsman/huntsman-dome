//
// X2Dome Declaration
//

#include <stdio.h>
#include <string.h>

#include "licensedinterfaces/sberrorx.h"
#include "licensedinterfaces/basicstringinterface.h"
#include "licensedinterfaces/serxinterface.h"
#include "licensedinterfaces/basiciniutilinterface.h"
#include "licensedinterfaces/theskyxfacadefordriversinterface.h"
#include "licensedinterfaces/sleeperinterface.h"
#include "licensedinterfaces/loggerinterface.h"
#include "licensedinterfaces/basiciniutilinterface.h"
#include "licensedinterfaces/mutexinterface.h"
#include "licensedinterfaces/tickcountinterface.h"
#include "licensedinterfaces/serialportparams2interface.h"
#include "licensedinterfaces/domedriverinterface.h"
#include "licensedinterfaces/serialportparams2interface.h"
#include "licensedinterfaces/modalsettingsdialoginterface.h"
#include "licensedinterfaces/x2guiinterface.h"

#include "domepro.h"
#include "UI_map.h"

#define DRIVER_VERSION      1.0

#define PARENT_KEY			"DomePro"
#define CHILD_KEY_PORTNAME	"PortName"
#define CHILD_KEY_TICKS_PER_REV "NbTicksPerRev"
#define CHILD_KEY_HOME_AZ "HomeAzimuth"
#define CHILD_KEY_PARK_AZ "ParkAzimuth"
#define CHILD_KEY_SHUTTER_CONTROL "ShutterCtrl"
#define CHILD_KEY_SHUTTER_OPEN_UPPER_ONLY "ShutterOpenUpperOnly"
#define CHILD_KEY_ROOL_OFF_ROOF "RollOffRoof"
#define CHILD_KEY_SHUTTER_OPER_ANY_Az "ShutterOperAnyAz"

#define CHILD_KEY_SHUTTER1_OPEN_ANGLE   "Shutter1OpenAngle"
#define CHILD_KEY_SHUTTER1_OPEN_ANGLE_ADC   "Shutter1OpenAngleADC"
#define CHILD_KEY_SHUTTER1_CLOSE_ANGLE   "Shutter1CloseAngle"
#define CHILD_KEY_SHUTTER1_CLOSE_ANGLE_ADC   "Shutter1CloseAngleADC"

#define CHILD_KEY_SHUTTER2_OPEN_ANGLE   "Shutter2OpenAngle"
#define CHILD_KEY_SHUTTER2_OPEN_ANGLE_ADC   "Shutter2OpenAngleADC"
#define CHILD_KEY_SHUTTER2_CLOSE_ANGLE   "Shutter2CloseAngle"
#define CHILD_KEY_SHUTTER2_CLOSE_ANGLE_ADC   "Shutter2CloseAngleADC"

#define CHILD_KEY_SHUTTER_GOTO  "ShutterGotoEnabled"

#if defined(SB_WIN_BUILD)
#define DEF_PORT_NAME					"COM1"
#elif defined(SB_MAC_BUILD)
#define DEF_PORT_NAME					"/dev/cu.KeySerial1"
#elif defined(SB_LINUX_BUILD)
#define DEF_PORT_NAME					"/dev/COM0"
#endif

#define LOG_BUFFER_SIZE 256

enum DIALOGS {MAIN, SHUTTER, TIMEOUTS, DIAG };

class X2Dome: public DomeDriverInterface, public SerialPortParams2Interface, public ModalSettingsDialogInterface, public X2GUIEventInterface
{
public:

	/*!Standard X2 constructor*/
	X2Dome(	const char* pszSelectionString,
					const int& nISIndex,
					SerXInterface*						pSerX,
					TheSkyXFacadeForDriversInterface* pTheSkyXForMounts,
					SleeperInterface*				pSleeper,
					BasicIniUtilInterface*			pIniUtil,
					LoggerInterface*					pLogger,
					MutexInterface*					pIOMutex,
					TickCountInterface*				pTickCount);
	virtual ~X2Dome();

	/*!\name DriverRootInterface Implementation
	See DriverRootInterface.*/
	//@{
	virtual DeviceType							deviceType(void) {return DriverRootInterface::DT_DOME;}
	virtual int									queryAbstraction(const char* pszName, void** ppVal);
	//@}

	/*!\name LinkInterface Implementation
	See LinkInterface.*/
	//@{
	virtual int									establishLink(void)						;
	virtual int									terminateLink(void)						;
	virtual bool								isLinked(void) const					;
	//@}

    virtual int initModalSettingsDialog(void){return 0;}
    virtual int execModalSettingsDialog(void);

	/*!\name HardwareInfoInterface Implementation
	See HardwareInfoInterface.*/
	//@{
	virtual void deviceInfoNameShort(BasicStringInterface& str) const					;
	virtual void deviceInfoNameLong(BasicStringInterface& str) const					;
	virtual void deviceInfoDetailedDescription(BasicStringInterface& str) const		;
	virtual void deviceInfoFirmwareVersion(BasicStringInterface& str)					;
	virtual void deviceInfoModel(BasicStringInterface& str)							;
	//@}

	/*!\name DriverInfoInterface Implementation
	See DriverInfoInterface.*/
	//@{
	virtual void								driverInfoDetailedInfo(BasicStringInterface& str) const	;
	virtual double								driverInfoVersion(void) const								;
	//@}

	//DomeDriverInterface
	virtual int dapiGetAzEl(double* pdAz, double* pdEl);
	virtual int dapiGotoAzEl(double dAz, double dEl);
	virtual int dapiAbort(void);
	virtual int dapiOpen(void);
	virtual int dapiClose(void);
	virtual int dapiPark(void);
	virtual int dapiUnpark(void);
	virtual int dapiFindHome(void);
	virtual int dapiIsGotoComplete(bool* pbComplete);
	virtual int dapiIsOpenComplete(bool* pbComplete);
	virtual int	dapiIsCloseComplete(bool* pbComplete);
	virtual int dapiIsParkComplete(bool* pbComplete);
	virtual int dapiIsUnparkComplete(bool* pbComplete);
	virtual int dapiIsFindHomeComplete(bool* pbComplete);
	virtual int dapiSync(double dAz, double dEl);

    //SerialPortParams2Interface
    virtual void			portName(BasicStringInterface& str) const			;
    virtual void			setPortName(const char* szPort)						;
    virtual unsigned int	baudRate() const			{return 115200;};
    virtual void			setBaudRate(unsigned int)	{};
    virtual bool			isBaudRateFixed() const		{return true;}

    virtual SerXInterface::Parity	parity() const				{return SerXInterface::B_NOPARITY;}
    virtual void					setParity(const SerXInterface::Parity& parity){parity;};
    virtual bool					isParityFixed() const		{return true;}



    virtual void uiEvent(X2GUIExchangeInterface* uiex, const char* pszEvent);

private:

	SerXInterface 									*	GetSerX() {return m_pSerX; }
	TheSkyXFacadeForDriversInterface				*	GetTheSkyXFacadeForDrivers() {return m_pTheSkyXFacadeForDriversInterface;}
	SleeperInterface								*	GetSleeper() {return m_pSleeper; }
	BasicIniUtilInterface							*	GetSimpleIniUtil() {return m_pIniUtil; }
	LoggerInterface									*	GetLogger() {return m_pLogger; }
	MutexInterface									*	GetMutex()  {return m_pIOMutex;}
	TickCountInterface								*	GetTickCountInterface() {return m_pTickCount;}

	SerXInterface									*	m_pSerX;
	TheSkyXFacadeForDriversInterface				*	m_pTheSkyXFacadeForDriversInterface;
	SleeperInterface								*	m_pSleeper;
	BasicIniUtilInterface							*	m_pIniUtil;
	LoggerInterface									*	m_pLogger;
	MutexInterface									*	m_pIOMutex;
	TickCountInterface								*	m_pTickCount;

    int doMainDialogEvents(X2GUIExchangeInterface* uiex, const char* pszEvent);

    int doDomeProShutter(bool& bPressedOK);
    int doShutterDialogEvents(X2GUIExchangeInterface* uiex, const char* pszEvent);

    int doDomeProTimeouts(bool& bPressedOK);
    int doTimeoutsDialogEvents(X2GUIExchangeInterface* uiex, const char* pszEvent);

    int doDomeProDiag(bool& bPressedOK);
    int doDiagDialogEvents(X2GUIExchangeInterface* uiex, const char* pszEvent);

    void setMainDialogControlState(X2GUIExchangeInterface* uiex, bool enabeled);

    void portNameOnToCharPtr(char* pszPort, const int& nMaxSize) const;


	int         m_nPrivateISIndex;
	bool        m_bLinked;
    CDomePro    m_DomePro;
    bool        m_bHasShutterControl;
    bool        m_bOpenUpperShutterOnly;
    int         m_nLearningDomeCPR;
    int         m_bBattRequest;
    int         m_nCurrentDialog;

    int         m_Shutter1OpenAngle;
    int         m_Shutter1OpenAngle_ADC;
    int         m_Shutter1CloseAngle;
    int         m_Shutter1CloseAngle_ADC;
    double      m_ADC_Ratio1;

    int         m_Shutter2OpenAngle;
    int         m_Shutter2OpenAngle_ADC;
    int         m_Shutter2CloseAngle;
    int         m_Shutter2CloseAngle_ADC;
    double      m_ADC_Ratio2;

    bool        m_bShutterGotoEnabled;


};
