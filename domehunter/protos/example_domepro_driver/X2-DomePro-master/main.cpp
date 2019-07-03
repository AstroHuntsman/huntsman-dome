#include <stdio.h>
#include "licensedinterfaces/basicstringinterface.h"
#include "main.h"
#include "x2dome.h"


#define PLUGIN_NAME "X2Dome DomePro"

extern "C" PlugInExport int sbPlugInName2(BasicStringInterface& str)
{
	str = PLUGIN_NAME;

	return 0;
}

extern "C" PlugInExport int sbPlugInFactory2(	const char* pszSelection,
												const int& nInstanceIndex,
												SerXInterface					* pSerXIn,
												TheSkyXFacadeForDriversInterface* pTheSkyXIn,
												SleeperInterface		* pSleeperIn,
												BasicIniUtilInterface  * pIniUtilIn,
												LoggerInterface			* pLoggerIn,
												MutexInterface			* pIOMutexIn,
												TickCountInterface		* pTickCountIn,
												void** ppObjectOut)
{
	*ppObjectOut = NULL;
	X2Dome* gpMyImpl=NULL;

	if (NULL == gpMyImpl)
		gpMyImpl = new X2Dome(	pszSelection,
									nInstanceIndex,
									pSerXIn,
									pTheSkyXIn,
									pSleeperIn,
									pIniUtilIn,
									pLoggerIn,
									pIOMutexIn,
									pTickCountIn);

		*ppObjectOut = gpMyImpl;

	return 0;
}
