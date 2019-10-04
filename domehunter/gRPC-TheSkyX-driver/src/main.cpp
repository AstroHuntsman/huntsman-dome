#include <stdio.h>
#include "licensedinterfaces/basicstringinterface.h"
#include "main.h"
#include "x2dome.h"

#include <iostream>
#include <memory>
#include <string>

#include <grpcpp/grpcpp.h>

#include "hx2dome.grpc.pb.h"

#define PLUGIN_NAME "X2Dome HuntsmanDome"

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
		// In order to connect to the appropriate gRPC server, update the
		// first grpc::CreateChannel() parameter to "serverip:port"
		// where the port is 50051 by default. If you are running the server
		// on a local machine you would use "localhost:50051"
		gpMyImpl = new X2Dome(	pszSelection,
									nInstanceIndex,
									pSerXIn,
									pTheSkyXIn,
									pSleeperIn,
									pIniUtilIn,
									pLoggerIn,
									pIOMutexIn,
									pTickCountIn,
									grpc::CreateChannel("localhost:50051", grpc::InsecureChannelCredentials()) );

	*ppObjectOut = gpMyImpl;

	return 0;
}
