//
//  DomePro.cpp
//  ATCL Dome X2 plugin
//
//  Created by Rodolphe Pineau on 6/11/2017.


#include "domepro.h"

CDomePro::CDomePro()
{
    // set some sane values
    m_bDebugLog = true;

    m_pSerx = NULL;
    m_bIsConnected = false;

    m_nNbStepPerRev = 0;

    m_dHomeAz = 0;
    m_dParkAz = 0;

    m_dCurrentAzPosition = 0.0;
    m_dCurrentElPosition = 0.0;

    m_bCalibrating = false;

    m_bHasShutter = false;
    m_bShutterOpened = false;

    m_bParked = true;   // assume we were parked.
    m_bHomed = false;

    m_nLearning = 0;
    m_nLeftCPR = 0;
    m_nRightCPR = 0;

    m_bShutterGotoEnabled = false;
    
    memset(m_szFirmwareVersion,0,SERIAL_BUFFER_SIZE);
    memset(m_szLogBuffer,0,DP2_LOG_BUFFER_SIZE);

#ifdef ATCL_DEBUG
#if defined(SB_WIN_BUILD)
    m_sLogfilePath = getenv("HOMEDRIVE");
    m_sLogfilePath += getenv("HOMEPATH");
    m_sLogfilePath += "\\DomeProLog.txt";
#elif defined(SB_LINUX_BUILD)
    m_sLogfilePath = getenv("HOME");
    m_sLogfilePath += "/DomeProLog.txt";
#elif defined(SB_MAC_BUILD)
    m_sLogfilePath = getenv("HOME");
    m_sLogfilePath += "/DomeProLog.txt";
#endif
    Logfile = fopen(m_sLogfilePath.c_str(), "w");
#endif

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] CDomePro Constructor Called\n", timestamp);
    fflush(Logfile);
#endif


}

CDomePro::~CDomePro()
{
#ifdef	ATCL_DEBUG
    if (Logfile)
        fclose(Logfile);
#endif
}

#pragma mark - Dome Communication

int CDomePro::Connect(const char *pszPort)
{
    int nErr;
    int nState;

    if(!m_pSerx)
        return ERR_COMMNOLINK;

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::Connect] Connect called.\n", timestamp);
    fflush(Logfile);
#endif

    // 19200 8N1
    nErr = m_pSerx->open(pszPort, 19200, SerXInterface::B_NOPARITY, "-DTR_CONTROL 1");
    if(nErr) {
        m_bIsConnected = false;
        return nErr;
    }
    m_bIsConnected = true;

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::Connect] connected to %s\n", timestamp, pszPort);
    fflush(Logfile);
#endif

    if (m_bDebugLog) {
        snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::Connect] Connected.\n");
        m_pLogger->out(m_szLogBuffer);

        snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::Connect] Getting Firmware.\n");
        m_pLogger->out(m_szLogBuffer);
    }

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::Connect] getting Firmware.\n", timestamp);
    fflush(Logfile);
#endif

    // if this fails we're not properly connected.
    nErr = getFirmwareVersion(m_szFirmwareVersion, SERIAL_BUFFER_SIZE);
    if(nErr) {
        if (m_bDebugLog) {
            snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::Connect] Error Getting Firmware.\n");
            m_pLogger->out(m_szLogBuffer);
        }
#ifdef ATCL_DEBUG
        ltime = time(NULL);
        timestamp = asctime(localtime(&ltime));
        timestamp[strlen(timestamp) - 1] = 0;
        fprintf(Logfile, "[%s] [CDomePro::Connect] Error %d Getting Firmware : %s\n", timestamp, nErr, m_szFirmwareVersion);
        fflush(Logfile);
#endif

        m_bIsConnected = false;
        m_pSerx->close();
        return ERR_COMMNOLINK;
    }

    if (m_bDebugLog) {
        snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::Connect] Got Firmware.\n");
        m_pLogger->out(m_szLogBuffer);
    }

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::Connect] firmware  %s\n", timestamp, m_szFirmwareVersion);
    fflush(Logfile);
#endif


    // get dome home az and park az
    setDomeHomeAzimuth(0); // we need to make sure we manage the offset to the Home position
    setDomeParkAzimuth(0);
    
    getDomeAzCPR(m_nNbStepPerRev);
    getDomeParkAz(m_dParkAz);

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::Connect] m_nNbStepPerRev = %d\n", timestamp, m_nNbStepPerRev);
    fprintf(Logfile, "[%s] [CDomePro::Connect] m_dHomeAz = %3.2f\n", timestamp, m_dHomeAz);
    fprintf(Logfile, "[%s] [CDomePro::Connect] m_dParkAz = %3.2f\n", timestamp, m_dParkAz);
    fflush(Logfile);
#endif


    // Check if the dome is at park
    getDomeLimits();
    if(m_nAtParkSate == ACTIVE) {
        nErr = getDomeParkAz(m_dCurrentAzPosition);
        if(!nErr)
            syncDome(m_dCurrentAzPosition, m_dCurrentElPosition);
    }

    nErr = getDomeShutterStatus(nState);
    nErr = getDomeLimits();

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::Connect] m_dCurrentAzPosition : %3.2f\n", timestamp, m_dCurrentAzPosition);
    fflush(Logfile);
#endif

    if(nState != NOT_FITTED )
        m_bHasShutter = true;

    return SB_OK;
}


void CDomePro::Disconnect()
{
    if(m_bIsConnected) {
        m_pSerx->purgeTxRx();
        m_pSerx->close();
    }
    m_bIsConnected = false;
}


#pragma mark - Dome API call

int CDomePro::syncDome(double dAz, double dEl)
{
    int nErr = DP2_OK;
    int nPos;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    m_dCurrentAzPosition = dAz;
    AzToTicks(dAz, nPos);
    nErr = calibrateDomeAzimuth(nPos);
    return nErr;
}

int CDomePro::gotoDomePark(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return nErr;

    nErr = domeCommand("!DSgp;", szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::unparkDome()
{
    m_bParked = false;
    m_dCurrentAzPosition = m_dParkAz;

    syncDome(m_dCurrentAzPosition, m_dCurrentElPosition);
    return 0;
}

int CDomePro::gotoAzimuth(double dNewAz)
{

    int nErr = DP2_OK;
    int nPos;
    if(!m_bIsConnected)
        return NOT_CONNECTED;

    AzToTicks(dNewAz, nPos);

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::gotoAzimuth]  dNewAz : %3.2f\n", timestamp, dNewAz);
    fprintf(Logfile, "[%s] [CDomePro::gotoAzimuth]  nPos : %d\n", timestamp, nPos);
    fflush(Logfile);
#endif

    nErr = goToDomeAzimuth(nPos);
    m_dGotoAz = dNewAz;

    return nErr;
}

int CDomePro::gotoElevation(double dNewEl)
{

    int nErr = DP2_OK;
    if(!m_bIsConnected)
        return NOT_CONNECTED;

    m_nTargetAdc = (int) floor(0.5 + ((m_Shutter1CloseAngle - dNewEl) * m_ADC_Ratio1));

    nErr = goToDomeElevation(m_nTargetAdc, 0);

    m_dGotoEl = dNewEl;

    return nErr;
}


int CDomePro::openDomeShutters()
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    nErr = domeCommand("!DSso;", szResp, SERIAL_BUFFER_SIZE);
    return nErr;
}

int CDomePro::CloseDomeShutters()
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    nErr = domeCommand("!DSsc;", szResp, SERIAL_BUFFER_SIZE);
    return nErr;
}

int CDomePro::abortCurrentCommand()
{
    int nErr;
    if(!m_bIsConnected)
        return NOT_CONNECTED;

    m_bCalibrating = false;

    nErr = killDomeAzimuthMovement();
    if(m_bHasShutter)
        nErr |= killDomeShutterMovement();
    return nErr;
}

int CDomePro::goHome()
{
    int nErr = DP2_OK;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = homeDomeAzimuth();
    return nErr;
}

#pragma mark TODO : Calibrate test
int CDomePro::learnAzimuthCprRight()
{
    int nErr = DP2_OK;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    // get the number of CPR going right.
    startDomeAzGaugeRight();

    m_bCalibrating = true;
    m_nLearning = RIGHT;
    return nErr;
}

int CDomePro::learnAzimuthCprLeft()
{
    int nErr = DP2_OK;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    // get the number of CPR going right.
    startDomeAzGaugeLeft();

    m_bCalibrating = true;
    m_nLearning = LEFT;

    return nErr;
}

#pragma mark - dome controller informations

int CDomePro::getFirmwareVersion(char *pszVersion, int nStrMaxLen)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned long nFirmwareVersion;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    nErr = domeCommand("!DGfv;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    nFirmwareVersion = strtoul(szResp, NULL, 16);
    snprintf(pszVersion, nStrMaxLen, "%lu", nFirmwareVersion);
    return nErr;
}

int CDomePro::getModel(char *pszModel, int nStrMaxLen)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    nErr = domeCommand("!DGhc;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    m_nModel = (int)strtoul(szResp, NULL, 16);
    switch(m_nModel) {
        case CLASSIC_DOME :
            strncpy(pszModel, "DomePro2-d", nStrMaxLen);
            break;

        case CLAMSHELL :
            strncpy(pszModel, "DomePro2-c", nStrMaxLen);
            break;

        case ROR :
            strncpy(pszModel, "DomePro2-r", nStrMaxLen);
            break;

        default:
            strncpy(pszModel, "Unknown", nStrMaxLen);
            break;
    }

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::getModel] Model =  %s\n", timestamp, pszModel);
    fflush(Logfile);
#endif


    return nErr;
}

int CDomePro::getModelType()
{
    return m_nModel;
}

int CDomePro::getModuleType(int &nModuleType)
{
    int nErr;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    nErr = domeCommand("!DGmy;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Az")) {
        m_nModuleType = MODULE_AZ;
    }
    else if(strstr(szResp,"Az")) {
        m_nModuleType = MODULE_SHUT;
    }
    else {
        m_nModuleType = MODULE_UKNOWN;
    }

    return nErr;
}

int CDomePro::setDomeAzMotorPolarity(int nPolarity)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    m_nMotorPolarity = nPolarity;

    switch(m_nNbStepPerRev) {
        case POSITIVE :
            nErr = domeCommand("!DSmpPositive;", szResp, SERIAL_BUFFER_SIZE);

            break;
        case NEGATIVE :
            nErr = domeCommand("!DSmpNegative;", szResp, SERIAL_BUFFER_SIZE);
            break;
        default:
            nErr = ERR_CMDFAILED;
            break;
    }

    return nErr;
}


int CDomePro::getDomeAzMotorPolarity(int &nPolarity)
{
    int nErr;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    nErr = domeCommand("!DGmp;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Positive")) {
        m_nMotorPolarity = POSITIVE;
    }
    else if(strstr(szResp,"Negative")) {
        m_nMotorPolarity = NEGATIVE;
    }

    else {
        m_nMotorPolarity = POLARITY_UKNOWN;
    }

    nPolarity = m_nMotorPolarity;
    return nErr;
}


int CDomePro::setDomeAzEncoderPolarity(int nPolarity)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    m_nAzEncoderPolarity = nPolarity;

    switch(m_nAzEncoderPolarity) {
        case POSITIVE :
            nErr = domeCommand("!DSepPositive;", szResp, SERIAL_BUFFER_SIZE);
            break;

        case NEGATIVE :
            nErr = domeCommand("!DSepNegative;", szResp, SERIAL_BUFFER_SIZE);
            break;

        default:
            nErr = ERR_CMDFAILED;
            break;
    }
    return nErr;
}

int CDomePro::getDomeAzEncoderPolarity(int &nPolarity)
{
    int nErr;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return SB_OK;

    nErr = domeCommand("!DGep;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Positive")) {
        m_nAzEncoderPolarity = POSITIVE;
    }
    else if(strstr(szResp,"Negative")) {
        m_nAzEncoderPolarity = NEGATIVE;
    }

    else {
        m_nAzEncoderPolarity = POLARITY_UKNOWN;
    }

    nPolarity = m_nAzEncoderPolarity;
    return nErr;
}


bool CDomePro::hasShutterUnit() {
    return m_bHasShutter;
}


#pragma mark - command complete functions

int CDomePro::isGoToComplete(bool &bComplete)
{
    int nErr = 0;
    double dDomeAz = 0;
    bool bIsMoving = false;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = isDomeMoving(bIsMoving);
    if(nErr) {
#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
        ltime = time(NULL);
        timestamp = asctime(localtime(&ltime));
        timestamp[strlen(timestamp) - 1] = 0;
        fprintf(Logfile, "[%s] [CDomePro::isGoToComplete] bIsMoving   =  %d\n", timestamp, bIsMoving);
#endif
        return nErr;
        }

    getDomeAzPosition(dDomeAz);

    if(bIsMoving) {
        bComplete = false;
        return nErr;
    }

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::isGoToComplete] dDomeAz   =  %3.2f\n", timestamp, dDomeAz);
    fprintf(Logfile, "[%s] [CDomePro::isGoToComplete] m_dGotoAz =  %3.2f\n", timestamp, m_dGotoAz);
    fprintf(Logfile, "[%s] [CDomePro::isGoToComplete] floor(dDomeAz)   =  %3.2f\n", timestamp, floor(dDomeAz));
    fprintf(Logfile, "[%s] [CDomePro::isGoToComplete] floor(m_dGotoAz) =  %3.2f\n", timestamp, floor(m_dGotoAz));
    fflush(Logfile);
#endif

    if ((floor(m_dGotoAz) <= floor(dDomeAz)+2) && (floor(m_dGotoAz) >= floor(dDomeAz)-2)) {
#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
        ltime = time(NULL);
        timestamp = asctime(localtime(&ltime));
        timestamp[strlen(timestamp) - 1] = 0;
        fprintf(Logfile, "[%s] [CDomePro::isGoToComplete] Goto finished\n", timestamp);
#endif
        bComplete = true;
    }
    else {
        // we're not moving and we're not at the final destination !!!
        if (m_bDebugLog) {
            snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::isGoToComplete] domeAz = %f, mGotoAz = %f\n", ceil(dDomeAz), ceil(m_dGotoAz));
            m_pLogger->out(m_szLogBuffer);
        }
        bComplete = false;
        nErr = ERR_CMDFAILED;
    }

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::isGoToComplete] bComplete   =  %d\n", timestamp, bComplete);
#endif

    return nErr;
}

int CDomePro::isGoToElComplete(bool &bComplete)
{
    int nErr = 0;
    int nADC;

    bComplete = false;
    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = getDomeShutter1_ADC(nADC);
    if(nErr)
        return nErr;

    if(m_nTargetAdc == nADC) {
        bComplete = true;
    }

    return nErr;
}

int CDomePro::isOpenComplete(bool &bComplete)
{
    int nErr = 0;
    int nState;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = getDomeShutterStatus(nState);
    if(nErr)
        return ERR_CMDFAILED;
    if(nState == OPEN){
        m_bShutterOpened = true;
        bComplete = true;
        m_dCurrentElPosition = 90.0;
    }
    else {
        m_bShutterOpened = false;
        bComplete = false;
        m_dCurrentElPosition = 0.0;
    }

    return nErr;
}

int CDomePro::isCloseComplete(bool &bComplete)
{
    int err=0;
    int nState;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    err = getDomeShutterStatus(nState);
    if(err)
        return ERR_CMDFAILED;
    if(nState == CLOSED){
        m_bShutterOpened = false;
        bComplete = true;
        m_dCurrentElPosition = 0.0;
    }
    else {
        m_bShutterOpened = true;
        bComplete = false;
        m_dCurrentElPosition = 90.0;
    }

    return err;
}


int CDomePro::isParkComplete(bool &bComplete)
{
    int nErr = 0;
    int nMode;
    double dDomeAz=0;
    bool bIsMoving = false;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = getDomeAzMoveMode(nMode);
    if(nMode == PARKING)
    {
        bComplete = false;
        return nErr;
    }

    getDomeAzPosition(dDomeAz);
    nErr = isDomeMoving(bIsMoving);
    if(nErr)
        return nErr;

    if(bIsMoving) { // this should not happen
        bComplete = false;
        return nErr;
    }

    if ((floor(m_dParkAz) <= floor(dDomeAz)+1) && (floor(m_dParkAz) >= floor(dDomeAz)-1))
    {
        m_bParked = true;
        bComplete = true;
    }
    else {
        // we're not moving and we're not at the final destination !!!
        bComplete = false;
        m_bHomed = false;
        m_bParked = false;
        nErr = ERR_CMDFAILED;
    }

    return nErr;
}

int CDomePro::isUnparkComplete(bool &bComplete)
{
    int nErr = 0;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    m_bParked = false;
    bComplete = true;

    return nErr;
}

int CDomePro::isFindHomeComplete(bool &bComplete)
{
    int nErr = 0;
    bool bIsMoving = false;
    bool bIsAtHome = false;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = isDomeMoving(bIsMoving);
    if(nErr) {
#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
        ltime = time(NULL);
        timestamp = asctime(localtime(&ltime));
        timestamp[strlen(timestamp) - 1] = 0;
        fprintf(Logfile, "[%s] [CDomePro::isFindHomeComplete] error checking if dome is moving : %dX\n", timestamp, nErr);
        fflush(Logfile);
#endif
        return nErr;
    }
    if(bIsMoving) {
        m_bHomed = false;
        bComplete = false;
        return nErr;
    }

    nErr = isDomeAtHome(bIsAtHome);
    if(nErr)
        return nErr;

    if(bIsAtHome){
        m_bHomed = true;
        bComplete = true;
    }
    else {
        // we're not moving and we're not at the home position !!!
        if (m_bDebugLog) {
            snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::isFindHomeComplete] Not moving and not at home !!!\n");
            m_pLogger->out(m_szLogBuffer);
        }
        bComplete = false;
        m_bHomed = false;
        m_bParked = false;
        nErr = ERR_CMDFAILED;
    }

    return nErr;
}


int CDomePro::isLearningCPRComplete(bool &bComplete)
{
    int nErr = DP2_OK;
    int nMode;
    int nSteps;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = getDomeAzMoveMode(nMode);
    if(nErr) {
        killDomeAzimuthMovement();
        m_bCalibrating = false;
        // restore previous value as there was an error
        m_nNbStepPerRev = m_nNbStepPerRev_save;
    }

    if(nMode == GAUGING)
    {
        bComplete = false;
        return nErr;
    }

    // Gauging is done. let's read the value
    if(m_nLearning == RIGHT) {
        nErr = getDomeAzGaugeRight(nSteps);
        m_nRightCPR = nSteps;
        }
    else {
        nErr = getDomeAzGaugeLeft(nSteps);
        m_nLeftCPR = nSteps;
    }
    if(nErr) {
        killDomeAzimuthMovement();
        m_bCalibrating = false;
        m_nLearning = 0;
        return nErr;
    }
    bComplete = true;
    return nErr;
}

int CDomePro::isPassingHomeComplete(bool &bComplete)
{
    int nErr = DP2_OK;
    bComplete = false;
    nErr = getDomeLimits();
    if(nErr) {
        return nErr;
    }
    if(m_nAtHomeSwitchState != ACTIVE)
        bComplete = true;

    return nErr;
}


#pragma mark - Getter / Setter

int CDomePro::setHomeAz(double dAz)
{
    int nErr = DP2_OK;

    m_dHomeAz = dAz;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    return nErr;
}

int CDomePro::setDomeAzCoast(double dAz)
{
    int nErr = DP2_OK;
    int nPos;

    nPos = (int) ((16385/360) * dAz);
    nErr = setDomeAzCoast(nPos);
    return nErr;

}

int CDomePro::getDomeAzCoast(double &dAz)
{
    int nErr = DP2_OK;
    int nPos;

    nErr = getDomeAzCoast(nPos);
    if(nErr)
        return nErr;

    dAz = (nPos/16385.0) * 360.0;

    return nErr;
}


int CDomePro::setParkAz(double dAz)
{
    int nErr = DP2_OK;
    int nPos;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    m_dParkAz = dAz;

    AzToTicks(dAz, nPos);

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::setParkAz] nPos : %d\n", timestamp, nPos);
    fprintf(Logfile, "[%s] [CDomePro::setParkAz] dAz : %3.3f\n", timestamp, dAz);
    fflush(Logfile);
#endif

    setDomeParkAzimuth(nPos);
    return nErr;
}


double CDomePro::getCurrentAz()
{
    if(m_bIsConnected)
        getDomeAzPosition(m_dCurrentAzPosition);

    return m_dCurrentAzPosition;
}

double CDomePro::getCurrentEl()
{
    if(m_bIsConnected)
        getDomeEl(m_dCurrentElPosition);

    return m_dCurrentElPosition;
}

int CDomePro::getCurrentShutterState()
{
    if(m_bIsConnected)
        getDomeShutterStatus(m_nShutterState);

    return m_nShutterState;
}

void CDomePro::setShutterAngleCalibration(int nShutter1OpenAngle, int nShutter1rOpenAngleADC,
                                int nShutter1CloseAngle, int nShutter1CloseAngleADC,
                                int nShutter2OpenAngle, int nShutter2rOpenAngleADC,
                                int nShutter2CloseAngle, int nShutter2CloseAngleADC,
                                bool bShutterGotoEnabled)
{
    m_Shutter1OpenAngle = nShutter1OpenAngle;
    m_Shutter1OpenAngle_ADC = nShutter1rOpenAngleADC;
    m_Shutter1CloseAngle = nShutter1CloseAngle;
    m_Shutter1CloseAngle_ADC = nShutter1CloseAngleADC;
    m_ADC_Ratio1 = (m_Shutter1OpenAngle_ADC - m_Shutter1CloseAngle_ADC) / (m_Shutter1OpenAngle - m_Shutter1CloseAngle);

    m_Shutter2OpenAngle = nShutter2OpenAngle;
    m_Shutter2OpenAngle_ADC = nShutter2rOpenAngleADC;
    m_Shutter2CloseAngle = nShutter2CloseAngle;
    m_Shutter2CloseAngle_ADC = nShutter2CloseAngleADC;
    m_ADC_Ratio2 = (m_Shutter2OpenAngle_ADC - m_Shutter2CloseAngle_ADC) / (m_Shutter2OpenAngle - m_Shutter2CloseAngle);

    m_bShutterGotoEnabled = bShutterGotoEnabled;

}


void CDomePro::setDebugLog(bool bEnable)
{
    m_bDebugLog = bEnable;
}


#pragma mark - protected methods

#pragma mark - dome communication

int CDomePro::domeCommand(const char *pszCmd, char *pszResult, int nResultMaxLen)
{
    int nErr = DP2_OK;
    unsigned char szResp[SERIAL_BUFFER_SIZE];
    unsigned long ulBytesWrite;

    m_pSerx->purgeTxRx();
    if (m_bDebugLog) {
        snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::domeCommand] Sending %s\n",pszCmd);
        m_pLogger->out(m_szLogBuffer);
    }

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::domeCommand] Sending %s\n", timestamp, pszCmd);
    fflush(Logfile);
#endif

    nErr = m_pSerx->writeFile((void *)pszCmd, strlen(pszCmd), ulBytesWrite);
    m_pSerx->flushTx();
    if(nErr)
        return nErr;
    // read response
    if (m_bDebugLog) {
        snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::domeCommand] Getting response.\n");
        m_pLogger->out(m_szLogBuffer);
    }
    nErr = readResponse(szResp, SERIAL_BUFFER_SIZE);
    if(nErr) {

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
        ltime = time(NULL);
        timestamp = asctime(localtime(&ltime));
        timestamp[strlen(timestamp) - 1] = 0;
        fprintf(Logfile, "[%s] [CDomePro::domeCommand] error %d reading response : %s\n", timestamp, nErr, szResp);
        fflush(Logfile);
#endif
        return nErr;
    }
    if(pszResult)
        strncpy(pszResult, (const char *)szResp, nResultMaxLen);

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::domeCommand] got response : '%s'\n", timestamp, szResp);
    fflush(Logfile);
#endif

    return nErr;

}


int CDomePro::readResponse(unsigned char *pszRespBuffer, int nBufferLen)
{
    int nErr = DP2_OK;
    unsigned long ulBytesRead = 0;
    unsigned long ulTotalBytesRead = 0;
    unsigned char *pszBufPtr;

    memset(pszRespBuffer, 0, (size_t) nBufferLen);
    pszBufPtr = pszRespBuffer;

    do {
        nErr = m_pSerx->readFile(pszBufPtr, 1, ulBytesRead, MAX_TIMEOUT);
        if(nErr) {
            if (m_bDebugLog) {
                snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::readResponse] readFile error.\n");
                m_pLogger->out(m_szLogBuffer);
            }
            return nErr;
        }

#if defined ATCL_DEBUG && ATCL_DEBUG >= 4
        ltime = time(NULL);
        timestamp = asctime(localtime(&ltime));
        timestamp[strlen(timestamp) - 1] = 0;
        fprintf(Logfile, "[%s] [CDomePro::readResponse] *pszBufPtr = %02X\n", timestamp, *pszBufPtr);
        fflush(Logfile);
#endif

        if (ulBytesRead !=1) {// timeout
            if (m_bDebugLog) {
                snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::readResponse] readFile Timeout.\n");
                m_pLogger->out(m_szLogBuffer);
            }
            nErr = DP2_BAD_CMD_RESPONSE;
            break;
        }
        ulTotalBytesRead += ulBytesRead;
        if (m_bDebugLog) {
            snprintf(m_szLogBuffer,DP2_LOG_BUFFER_SIZE,"[CDomePro::readResponse] nBytesRead = %lu\n",ulBytesRead);
            m_pLogger->out(m_szLogBuffer);
        }
        // check for  errors or single ACK
        if(*pszBufPtr == ATCL_NACK) {
            nErr = DP2_BAD_CMD_RESPONSE;
            break;
        }

        if(*pszBufPtr == ATCL_ACK) {
            nErr = DP2_OK;
            break;
        }


    } while (*pszBufPtr++ != ';' && ulTotalBytesRead < nBufferLen );

    if(ulTotalBytesRead && *(pszBufPtr-1) == ';')
        *(pszBufPtr-1) = 0; //remove the ; to zero terminate the string

    return nErr;
}

#pragma mark - conversion functions

//	Convert pdAz to number of ticks from home.
void CDomePro::AzToTicks(double pdAz, int &ticks)
{
    if(!m_nNbStepPerRev)
        getDomeAzCPR(m_nNbStepPerRev);

    ticks = (int) floor(0.5 + (pdAz - m_dHomeAz) * m_nNbStepPerRev / 360.0);
    while (ticks > m_nNbStepPerRev) ticks -= m_nNbStepPerRev;
    while (ticks < 0) ticks += m_nNbStepPerRev;
}


// Convert ticks from home to Az
void CDomePro::TicksToAz(int ticks, double &pdAz)
{
    if(!m_nNbStepPerRev)
        getDomeAzCPR(m_nNbStepPerRev);

    pdAz = m_dHomeAz + (ticks * 360.0 / m_nNbStepPerRev);
    while (pdAz < 0) pdAz += 360;
    while (pdAz >= 360) pdAz -= 360;
}


#pragma mark - Dome movements

int CDomePro::setDomeLeftOn(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = domeCommand("!DSol;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::setDomeRightOn(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    nErr = domeCommand("!DSor;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::killDomeAzimuthMovement(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(!m_bIsConnected)
        return NOT_CONNECTED;


    nErr = domeCommand("!DXxa;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

#pragma mark - getter / setter

int CDomePro::getDomeAzPosition(double &dDomeAz)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    int nTmp;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    if(m_bCalibrating)
        return nErr;

    nErr = domeCommand("!DGap;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert Az hex string to long
    nTmp = (int)strtoul(szResp, NULL, 16);

    TicksToAz(nTmp, dDomeAz);

    m_dCurrentAzPosition = dDomeAz;

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::getDomeAzPosition] nTmp = %s\n", timestamp, szResp);
    fprintf(Logfile, "[%s] [CDomePro::getDomeAzPosition] nTmp = %d\n", timestamp, nTmp);
    fprintf(Logfile, "[%s] [CDomePro::getDomeAzPosition] dDomeAz = %3.2f\n", timestamp, dDomeAz);
    fflush(Logfile);
#endif

    return nErr;
}

int CDomePro::getDomeEl(double &dDomeEl)
{
    int nErr = DP2_OK;
    int nShutterState;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    getDomeShutterStatus(nShutterState);

    if(!m_bShutterOpened || !m_bHasShutter)
    {
        dDomeEl = 0.0;
    }
    else {
        dDomeEl = 90.0;
    }

    m_dCurrentElPosition = dDomeEl;

    return nErr;
}


int CDomePro::getDomeHomeAz(double &dAz)
{
    int nErr = DP2_OK;

    dAz = m_dHomeAz;

    return nErr;
}

int CDomePro::getDomeParkAz(double &dAz)
{
    int nErr = DP2_OK;
    int nPos;

    nErr = getDomeParkAzimuth(nPos);
    if(nErr)
        return nErr;

    TicksToAz(nPos, dAz);

    return nErr;
}

int CDomePro::getDomeShutterStatus(int &nState)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    int nShutterState;

    nErr = domeCommand("!DGsx;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    nShutterState = (int)strtoul(szResp, NULL, 16);

    switch(nShutterState) {
        case OPEN:
            m_bShutterOpened = true;
            break;

        case CLOSED:
            m_bShutterOpened = false;
            break;

        case NOT_FITTED:
            m_bShutterOpened = false;
            m_bHasShutter = false;
            break;
        default:
            m_bShutterOpened = false;

    }

    nState = nShutterState;

    return nErr;
}


#pragma mark - command completion/state

int CDomePro::isDomeMoving(bool &bIsMoving)
{
    int nErr = DP2_OK;
    int nMode;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    bIsMoving = false;

    nErr = getDomeAzMoveMode(nMode);
    if(nErr)
        return nErr;

    if(nMode != FIXED && nMode != AZ_TO)
        bIsMoving = true;

    return nErr;
}

int CDomePro::isDomeAtHome(bool &bAtHome)
{
    int nErr = DP2_OK;

    if(!m_bIsConnected)
        return NOT_CONNECTED;

    bAtHome = false;

    nErr = getDomeLimits();
    if(nErr) {
        return nErr;
    }
    if(m_nAtHomeState == ACTIVE)
        bAtHome = true;

    return nErr;
}

#pragma mark - DomePro getter/setter

int CDomePro::setDomeAzCPR(int nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    // nCpr must be betweem 0x20 and 0x40000000 and be even
    if(nValue < 0x20 )
        nValue = 0x20;
    if(nValue>0x40000000)
        nValue = 0x40000000;
    nValue &= 0XFFFFFFFE; // makes it an even number

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DScp0x%08X;", nValue);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeAzCPR(int &nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGcp;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nValue = (int)strtoul(szResp, NULL, 16);
    return nErr;
}

int CDomePro::getLeftCPR()
{
    return m_nLeftCPR;
}

int CDomePro::getRightCPR()
{
    return m_nRightCPR;

}


#pragma mark not yet implemented in the firmware
int CDomePro::setDomeMaxVel(int nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    // nValue must be betweem 0x01 and 0x7C (124)
    if(nValue < 0x1 )
        nValue = 0x1;
    if(nValue>0x7C)
        nValue = 0x7C;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSmv0x%08X;", nValue);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::getDomeMaxVel(int &nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGmv;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nValue = (int)strtoul(szResp, NULL, 16);
    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::setDomeAccel(int nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    // nValue must be betweem 0x01 and 0xFF (255)
    if(nValue < 0x1 )
        nValue = 0x1;
    if(nValue>0xFF)
        nValue = 0xFF;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSma0x%08X;", nValue);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::getDomeAccel(int &nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGma;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nValue = (int)strtoul(szResp, NULL, 16);
    return nErr;
}



int CDomePro::setDomeAzCoast(int nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    // nCpr must be betweem 0x20 and 0x40000000 and be even
    if(nValue < 0x1 )
        nValue = 0x1;
    if(nValue>0x7C)
        nValue = 0x7C;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSco0x%08X;", nValue);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeAzCoast(int &nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGco;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nValue = (int)strtoul(szResp, NULL, 16);
    return nErr;
}

int CDomePro::getDomeAzDiagPosition(int &nValue)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGdp;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nValue = (int)strtoul(szResp, NULL, 16);
    return nErr;
}

int CDomePro::clearDomeAzDiagPosition(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DCdp;", szResp, SERIAL_BUFFER_SIZE);
    return nErr;
}

int CDomePro::getDomeAzMoveMode(int &mode)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGam;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    if(strstr(szResp, "Fixed")) {
        mode = FIXED;
    }
    else if(strstr(szResp, "Left")) {
        mode = LEFT;
    }
    else if(strstr(szResp, "Right")) {
        mode = RIGHT;
    }
    else if(strstr(szResp, "GoTo")) {
        mode = GOTO;
    }
    else if(strstr(szResp, "Homing")) {
        mode = HOMING;
    }
    else if(strstr(szResp, "AzimuthTO")) {
        mode = AZ_TO;
    }
    else if(strstr(szResp, "Gauging")) {
        mode = GAUGING;
    }
    else if(strstr(szResp, "Parking")) {
        mode = PARKING;
    }
    return nErr;
}

int CDomePro::getDomeLimits(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    uint16_t nLimits;

    nErr = domeCommand("!DGdl;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    nLimits = (uint16_t)strtoul(szResp, NULL, 16);

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] nLimits : %04X\n", timestamp, nLimits);
    fflush(Logfile);
#endif

    m_nShutter1OpenedSwitchState = (nLimits & BitShutter1_Opened ? ACTIVE : INNACTIVE);
    m_nShutter1ClosedSwitchState = (nLimits & BitShutter1_Closed ? ACTIVE : INNACTIVE);

    m_nShutter2OpenedSwitchState = (nLimits & BitShutter2_Opened ? ACTIVE : INNACTIVE);
    m_nShutter2ClosedSwitchState = (nLimits & BitShutter2_Closed ? ACTIVE : INNACTIVE);

    m_nAtHomeState = (nLimits & BitAtHome ? ACTIVE : INNACTIVE);
    m_nAtHomeSwitchState = (nLimits & BitHomeSwitchState ? ACTIVE : INNACTIVE);
    m_nAtParkSate = (nLimits & BitAtPark ? ACTIVE : INNACTIVE);

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] m_nShutter1OpenedSwitchState : %d\n", timestamp, m_nShutter1OpenedSwitchState);
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] m_nShutter1ClosedSwitchState : %d\n", timestamp, m_nShutter1ClosedSwitchState);
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] m_nShutter2OpenedSwitchState : %d\n", timestamp, m_nShutter2OpenedSwitchState);
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] m_nShutter2ClosedSwitchState : %d\n", timestamp, m_nShutter2ClosedSwitchState);
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] m_nAtHomeState               : %d\n", timestamp, m_nAtHomeState);
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] m_nAtHomeSwitchState         : %d\n", timestamp, m_nAtHomeSwitchState);
    fprintf(Logfile, "[%s] [CDomePro::getDomeLimits] m_nAtParkSate                : %d\n", timestamp, m_nAtParkSate);
    fflush(Logfile);
#endif

    return nErr;
}


int CDomePro::setDomeHomeDirection(int nDir)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    if(nDir == LEFT) {
        nErr = domeCommand("!DShdLeft;", szResp, SERIAL_BUFFER_SIZE);
    }
    else if (nDir == RIGHT) {
        nErr = domeCommand("!DShdRight;", szResp, SERIAL_BUFFER_SIZE);
    }
    else {
        return INVALID_COMMAND;
    }

    return nErr;
}

int CDomePro::getDomeHomeDirection(int &nDir)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGhd;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    if(strstr(szResp, "Left")) {
        nDir = LEFT;
    }
    else if(strstr(szResp, "Right")) {
        nDir = RIGHT;
    }
    return nErr;
}


int CDomePro::setDomeHomeAzimuth(int nPos)
{

    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nPos < 0 && nPos> m_nNbStepPerRev)
        return COMMAND_FAILED;

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::setDomeHomeAzimuth] nPos : %d\n", timestamp, nPos);
    fflush(Logfile);
#endif

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSha0x%08X;", nPos);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::setDomeAzimuthOCP_Limit(double dLimit)
{

    int nErr = DP2_OK;
    int ulTmp;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    ulTmp = (int)floor((dLimit/0.0468f)+0.5);

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSxa0x%08X;", ulTmp);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeAzimuthOCP_Limit(double &dLimit)
{
    int nErr = DP2_OK;
    int ulTmp;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGxa;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dLimit = (double)ulTmp * 0.0468f;

    return nErr;
}


int CDomePro::getDomeHomeAzimuth(int &nPos)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGha;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nPos = (int)strtoul(szResp, NULL, 16);
#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::getDomeHomeAzimuth] szResp : %s\n", timestamp, szResp);
    fprintf(Logfile, "[%s] [CDomePro::getDomeHomeAzimuth] nPos   : %d\n", timestamp, nPos);
    fflush(Logfile);
#endif

    return nErr;
}

int CDomePro::homeDomeAzimuth(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSah;", szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}


int CDomePro::goToDomeAzimuth(int nPos)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nPos < 0 && nPos> m_nNbStepPerRev)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSgo0x%08X;", nPos);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::goToDomeElevation(int nADC1, int nADC2)
{
    int nErr = DP2_OK;

    if(nADC1 < 0 && nADC2> 4095)
        return COMMAND_FAILED;

    if(nADC2 < 0 && nADC2> 4095)
        return COMMAND_FAILED;

    nErr = GoToDomeShutter1_ADC(nADC1);
    if(nErr)
        return nErr;
    nErr = GoToDomeShutter1_ADC(nADC2);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::GoToDomeShutter1_ADC(int nADC)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nADC < 0 && nADC> 4095)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSg10x%08X;", nADC);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::GoToDomeShutter2_ADC(int nADC)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nADC < 0 && nADC> 4095)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSg20x%08X;", nADC);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}


int CDomePro::setDomeParkAzimuth(int nPos)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nPos < 0 && nPos> m_nNbStepPerRev)
        return COMMAND_FAILED;

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::setDomeParkAzimuth] nPos : %d\n", timestamp, nPos);
    fflush(Logfile);
#endif

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSpa0x%08X;", nPos);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeParkAzimuth(int &nPos)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGpa;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nPos = (int)strtoul(szResp, NULL, 16);

#if defined ATCL_DEBUG && ATCL_DEBUG >= 2
    ltime = time(NULL);
    timestamp = asctime(localtime(&ltime));
    timestamp[strlen(timestamp) - 1] = 0;
    fprintf(Logfile, "[%s] [CDomePro::getDomeParkAzimuth] szResp : %s\n", timestamp, szResp);
    fprintf(Logfile, "[%s] [CDomePro::getDomeParkAzimuth] nPos : %d\n", timestamp, nPos);
    fflush(Logfile);
#endif

    return nErr;
}

int CDomePro::calibrateDomeAzimuth(int nPos)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nPos < 0 && nPos> m_nNbStepPerRev)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSca0x%08X;", nPos);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::startDomeAzGaugeRight()
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSgr;", szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeAzGaugeRight(int &nSteps)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGgr;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nSteps = (int)strtoul(szResp, NULL, 16);
    if(!nSteps) { // if we get 0x00000000 there was an error
        // restore old value
        m_nNbStepPerRev = m_nNbStepPerRev_save;
        return ERR_CMDFAILED;
    }
    m_nNbStepPerRev = nSteps;

    return nErr;
}

int CDomePro::startDomeAzGaugeLeft()
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSgl;", szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeAzGaugeLeft(int &nSteps)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGgl;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nSteps = (int)strtoul(szResp, NULL, 16);
    if(!nSteps) { // if we get 0x00000000 there was an error
        // restore old value
        m_nNbStepPerRev = m_nNbStepPerRev_save;
        return ERR_CMDFAILED;
    }
    m_nNbStepPerRev = nSteps;

    return nErr;
}



int CDomePro::killDomeShutterMovement(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DXxs;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::getDomeDebug(char *pszDebugStrBuff, int nStrMaxLen)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGdg;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    strncpy(pszDebugStrBuff, szResp, nStrMaxLen);

    return nErr;
}

#pragma mark - low level dome data getter/setter

int CDomePro::getDomeSupplyVoltageAzimuthL(double &dVolts)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGva;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dVolts = (double)ulTmp * 0.00812763;

    return nErr;
}

int CDomePro::getDomeSupplyVoltageShutterL(double &dVolts)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGvs;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dVolts = (double)ulTmp * 0.00812763;
    
    return nErr;
}

#pragma mark FIX VOLTAGE MULTIPLIER
int CDomePro::getDomeSupplyVoltageAzimuthM(double &dVolts)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGoa;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dVolts = (double)ulTmp * 1; // TBD

    return nErr;
}


#pragma mark FIX VOLTAGE MULTIPLIER
int CDomePro::getDomeSupplyVoltageShutterM(double &dVolts)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGos;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dVolts = (double)ulTmp * 1; // TBD

    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::getDomeRotationSenseAnalog(double &dVolts)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGra;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dVolts = (double)ulTmp / 255 * 5; // FF = 5v, 0 = 0v
    
    return nErr;

}

int CDomePro::setDomeShutter1_OpTimeOut(int nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nTimeout < 10 && nTimeout > 500)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSt10x%08X;", nTimeout);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeShutter1_OpTimeOut(int &nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGt1;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nTimeout = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::setDomeShutter2_OpTimeOut(int nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nTimeout < 10 && nTimeout > 500)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSt20x%08X;", nTimeout);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;

}

int CDomePro::getDomeShutter2_OpTimeOut(int &nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGt2;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nTimeout = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::setDomeShutODirTimeOut(int nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nTimeout < 10 && nTimeout > 500)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSto0x%08X;", nTimeout);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeShutODirTimeOut(int &nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGto;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nTimeout = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::setDomeAzimuthTimeOutEnabled(bool bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnable)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSaeYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSaeNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;

}

int CDomePro::getDomeAzimuthTimeOutEnabled(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGae;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;

    return nErr;
}

int CDomePro::setDomeAzimuthTimeOut(int nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nTimeout < 10 && nTimeout > 500)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSta0x%08X;", nTimeout);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeAzimuthTimeOut(int &nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGta;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nTimeout = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::setDomeShutCloseOnLinkTimeOut(bool bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnable)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DStsYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DStsNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
    
}

int CDomePro::getDomeShutCloseOnLinkTimeOut(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGts;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;

    return nErr;
}

int CDomePro::setDomeShutCloseOnClientTimeOut(bool bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnable)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSteYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSteNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeShutCloseOnClientTimeOut(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGte;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;
    
    return nErr;
}

int CDomePro::setDomeShutCloseClientTimeOut(int nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(nTimeout < 10 && nTimeout > 500)
        return COMMAND_FAILED;

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DStc0x%08X;", nTimeout);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeShutCloseClientTimeOut(int &nTimeout)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGtc;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nTimeout = (int)strtoul(szResp, NULL, 16);
    
    return nErr;
}

int CDomePro::setShutterAutoCloseEnabled(bool bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnable)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSanYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSanNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;

}

int CDomePro::getShutterAutoCloseEnabled(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGan;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;

    return nErr;
}


#pragma mark not yet implemented in the firmware
int CDomePro::setDomeShutOpAtHome(bool bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnable)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSshYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSshNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::getDomeShutOpAtHome(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGsh;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;

    return nErr;
}

int CDomePro::getDomeShutdownInputState(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGsi;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;

    return nErr;
}

int CDomePro::getDomePowerGoodInputState(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGpi;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;

    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::getLastDomeShutdownEvent(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGlv;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // need to parse output and set some varaible/structure representing the event

    return nErr;
}

int CDomePro::setDomeSingleShutterMode(bool bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnable)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSssYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSssNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeSingleShutterMode(bool &bEnable)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnable = false;

    nErr = domeCommand("!DGss;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;
    if(strstr(szResp,"Yes"))
        bEnable = true;

    return nErr;
}

int CDomePro::getDomeLinkErrCnt(int &nErrCnt)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGle;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nErrCnt = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::clearDomeLinkErrCnt(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DCle;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::getDomeComErr(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGce;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // need to parse output and set some varaible/structure representing the comms errors
    
    return nErr;
}

#pragma mark not yet implemented in the firmware
int CDomePro::clearDomeComErr(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DCce;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::openDomeShutter1(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSo1;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::openDomeShutter2(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSo2;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::closeDomeShutter1(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSc1;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::closeDomeShutter2(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSc2;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::stopDomeShutter1(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSs1;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}

int CDomePro::stopDomeShutter2(void)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DSs2;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    return nErr;
}


int CDomePro::getDomeShutter1_ADC(int &nPos)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGa1;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nPos = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::getDomeShutter2_ADC(int &nPos)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGa2;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nPos = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::setDomeShutterOpenFirst(int nShutter)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSof0x%02X;", nShutter);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;

}

int CDomePro::getDomeShutterOpenFirst(int &nShutter)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGof;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nShutter = (int)strtoul(szResp, NULL, 16);

    return nErr;
}

int CDomePro::setDomeShutterCloseFirst(int nShutter)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DScf0x%02X;", nShutter);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;

}

int CDomePro::getDomeShutterCloseFirst(int &nShutter)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGcf;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    nShutter = (int)strtoul(szResp, NULL, 16);
    
    return nErr;
}

int CDomePro::getDomeShutterMotorADC(double &dVolts)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGsc;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dVolts = (double)ulTmp / 1023.0 * 3.3;
    dVolts = (dVolts - 1.721) / 0.068847;
    if (dVolts < 0.0)
        dVolts = 0.0;

    return nErr;
}

int CDomePro::getDomeAzimuthMotorADC(double &dVolts)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGac;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dVolts = (double)ulTmp / 1023.0 * 3.3;
    dVolts = (dVolts - 1.721) / 0.068847;
    if (dVolts < 0.0)
        dVolts = 0.0;

    return nErr;
}

int CDomePro::getDomeShutterTempADC(double &dTemp)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGst;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dTemp = (double)ulTmp / 1023.0 * 3.3 - 0.5;
    dTemp = dTemp / 0.01;

    return nErr;
}

int CDomePro::getDomeAzimuthTempADC(double &dTemp)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    unsigned int ulTmp;

    nErr = domeCommand("!DGat;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dTemp = (double)ulTmp / 1023.0 * 3.3 - 0.5;
    dTemp = dTemp / 0.01;

    return nErr;
}

int CDomePro::setDomeShutOpOnHome(bool bEnabled)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnabled)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSshYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSshNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeShutOpOnHome(bool &bEnabled)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnabled = false;

    nErr = domeCommand("!DGsh;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    if(strstr(szResp,"Yes"))
        bEnabled = true;

    return nErr;
}


int CDomePro::setHomeWithShutterClose(bool bEnabled)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnabled)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSchYes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSchNo;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getHomeWithShutterClose(bool &bEnabled)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnabled = false;

    nErr = domeCommand("!DGch;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    if(strstr(szResp,"Yes"))
        bEnabled = true;

    return nErr;
}

int CDomePro::setShutter1_LimitFaultCheckEnabled(bool bEnabled)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnabled)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSl1Yes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSl1No;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getShutter1_LimitFaultCheckEnabled(bool &bEnabled)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnabled = false;

    nErr = domeCommand("!DGl1;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    if(strstr(szResp,"Yes"))
        bEnabled = true;

    return nErr;
}

int CDomePro::setShutter2_LimitFaultCheckEnabled(bool bEnabled)
{    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    if(bEnabled)
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSl2Yes;");
    else
        snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSl2No;");

    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getShutter2_LimitFaultCheckEnabled(bool &bEnabled)
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    bEnabled = false;

    nErr = domeCommand("!DGl2;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    if(strstr(szResp,"Yes"))
        bEnabled = true;

    return nErr;
}

int CDomePro::setDomeShutter1_OCP_Limit(double dLimit)
{
    int nErr = DP2_OK;
    int ulTmp;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    ulTmp = (int)floor((dLimit/0.0468f)+0.5);

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSx10x%08X;", ulTmp);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeShutter1_OCP_Limit(double &dLimit)
{
    int nErr = DP2_OK;
    int ulTmp;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGx1;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dLimit = (double)ulTmp * 0.0468f;

    return nErr;

}

int CDomePro::setDomeShutter2_OCP_Limit(double dLimit)
{
    int nErr = DP2_OK;
    int ulTmp;
    char szResp[SERIAL_BUFFER_SIZE];
    char szCmd[SERIAL_BUFFER_SIZE];

    ulTmp = (int)floor((dLimit/0.0468f)+0.5);

    snprintf(szCmd, SERIAL_BUFFER_SIZE, "!DSx20x%08X;", ulTmp);
    nErr = domeCommand(szCmd, szResp, SERIAL_BUFFER_SIZE);

    return nErr;
}

int CDomePro::getDomeShutter2_OCP_Limit(double &dLimit)
{
    int nErr = DP2_OK;
    int ulTmp;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DGx2;", szResp, SERIAL_BUFFER_SIZE);
    if(nErr)
        return nErr;

    // convert result hex string to long
    ulTmp = (int)strtoul(szResp, NULL, 16);

    dLimit = (double)ulTmp * 0.0468f;

    return nErr;

}



int CDomePro::clearDomeLimitFault()
{
    int nErr = DP2_OK;
    char szResp[SERIAL_BUFFER_SIZE];

    nErr = domeCommand("!DClf;", szResp, SERIAL_BUFFER_SIZE);
    return nErr;
}



void  CDomePro::hexdump(const char* inputData, char *outBuffer, int size)
{
    char *buf = outBuffer;
    int idx=0;
    for(idx=0; idx<size; idx++){
        snprintf((char *)buf,4,"%02X ", inputData[idx]);
        buf+=3;
    }
    *buf = 0;
}


