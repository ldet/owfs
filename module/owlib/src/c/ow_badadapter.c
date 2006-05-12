/*
$Id$
    OWFS -- One-Wire filesystem
    OWHTTPD -- One-Wire Web Server
    Written 2003 Paul H Alfille
    email: palfille@earthlink.net
    Released under the GPL
    See the header file: ow.h for full attribution
    1wire/iButton system from Dallas Semiconductor
*/

#include "owfs_config.h"
#include "ow.h"
#include "ow_connection.h"

/* All the rest of the program sees is the BadAdapter_detect and the entry in iroutines */

static int BadAdapter_reset( const struct parsedname * pn ) ;
static int BadAdapter_overdrive( const UINT ov, const struct parsedname * pn ) ;
static int BadAdapter_testoverdrive( const struct parsedname * pn ) ;
static int BadAdapter_ProgramPulse( const struct parsedname * pn ) ;
static int BadAdapter_sendback_bits( const BYTE * data, BYTE * resp, const size_t len, const struct parsedname * pn ) ;
static void BadAdapter_close( struct connection_in * in ) ;

/* Device-specific functions */
/* Note, the "Bad"adapter" ha not function, and returns "-ENOTSUP" (not supported) for most functions */
/* It does call lower level functions for higher ones, which of course is pointless since the lower ones don't work either */
int BadAdapter_detect( struct connection_in * in ) {
    in->fd = -1 ;
#ifdef OW_USB
    in->connin.usb.usb = NULL ;
#endif
    in->iroutines.detect        = BadAdapter_detect ;
    in->Adapter = adapter_Bad ; /* OWFS assigned value */
    in->iroutines.reset         = BadAdapter_reset         ;
    in->iroutines.next_both     = BUS_next_both_low        ;
    in->iroutines.overdrive     = BadAdapter_overdrive     ;
    in->iroutines.testoverdrive = BadAdapter_testoverdrive ;
    in->iroutines.PowerByte     = BUS_PowerByte_low        ;
    in->iroutines.ProgramPulse  = BadAdapter_ProgramPulse  ;
    in->iroutines.sendback_data = BUS_sendback_data_low    ;
    in->iroutines.sendback_bits = BadAdapter_sendback_bits ;
    in->iroutines.select        = BUS_select_low           ;
    in->iroutines.reconnect     = NULL                     ;
    in->iroutines.close         = BadAdapter_close         ;
    in->adapter_name="Bad Adapter" ;
    return 0 ;
}

static int BadAdapter_reset( const struct parsedname * pn ) {
    (void) pn ;
    return -ENOTSUP ;
}
static int BadAdapter_overdrive( const UINT ov, const struct parsedname * pn ) {
    (void) ov ;
    (void) pn ;
    STAT_ADD1_BUS(BUS_Overdrive_errors,pn->in) ;
    return -ENOTSUP ;
}
static int BadAdapter_testoverdrive( const struct parsedname * pn ) {
    (void) pn ;
    STAT_ADD1_BUS(BUS_TestOverdrive_errors,pn->in) ;
    return -ENOTSUP ;
}
static int BadAdapter_ProgramPulse( const struct parsedname * pn ) {
    (void) pn ;
    STAT_ADD1_BUS(BUS_ProgramPulse_errors,pn->in) ;
    return -ENOTSUP ;
}
static int BadAdapter_sendback_bits( const BYTE * data , BYTE * resp, const size_t len, const struct parsedname * pn ){
    (void) pn ;
    (void) data ;
    (void) resp ;
    (void) len ;
    return -ENOTSUP ;
}
static void BadAdapter_close( struct connection_in * in ) {
    (void) in ;
}
