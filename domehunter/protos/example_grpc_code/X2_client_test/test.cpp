#include <stdio.h>
#include <iostream>
#include <memory>
#include <string>

#include "../../src/x2dome.h"


int main(int argc, char** argv) {

	// create a bunch of null pointers to feed into an X2Dome instance
  const char                         *pszSelection=NULL;
  const int                          &nInstanceIndex=1;
  SerXInterface					             *pSerXIn=NULL;
  TheSkyXFacadeForDriversInterface   *pTheSkyXIn=NULL;
  SleeperInterface		               *pSleeperIn=NULL;
  BasicIniUtilInterface              *pIniUtilIn=NULL;
  LoggerInterface			               *pLoggerIn=NULL;
  MutexInterface			               *pIOMutexIn=NULL;
  TickCountInterface		             *pTickCountIn=NULL;

	// create an X2Dome with a grpc channel/stub
	X2Dome testDome( pszSelection,
											 	 nInstanceIndex,
											 	 pSerXIn,
											 	 pTheSkyXIn,
											 	 pSleeperIn,
											 	 pIniUtilIn,
											 	 pLoggerIn,
											 	 pIOMutexIn,
											 	 pTickCountIn,
											 	 grpc::CreateChannel("localhost:50051", grpc::InsecureChannelCredentials()) );

	// using the X2Dome establishLink() member function to test the connection
  int result;
  result = testDome.establishLink();
  //
  //std::cout << "HX2Dome received: " << result << std::endl;

  return 0;
}
