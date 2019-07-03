#ifdef SB_WIN_BUILD
	#define PlugInExport __declspec(dllexport)
#else
	#define PlugInExport
#endif

class SerXInterface;
class TheSkyXFacadeForDriversInterface;
class SleeperInterface;
class BasicIniUtilInterface;
class LoggerInterface;
class MutexInterface;
class TickCountInterface;


extern "C" PlugInExport int sbPlugInDisplayName(BasicStringInterface& str);

extern "C" PlugInExport int sbPlugInFactory(	const char* pszSelection, 
												const int& nInstanceIndex,
												SerXInterface					* pSerXIn, 
												TheSkyXFacadeForDriversInterface* pTheSkyXIn, 
												SleeperInterface		* pSleeperIn,
												BasicIniUtilInterface  * pIniUtilIn,
												LoggerInterface			* pLoggerIn,
												MutexInterface			* pIOMutexIn,
												TickCountInterface		* pTickCountIn,
												void** ppObjectOut);