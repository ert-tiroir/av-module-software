
#include "av-core/context.h"

unsigned char tx_char_buffer[1024 * 1024];
unsigned char rx_char_buffer[1024 * 1024];

const char* PATH_CAMERA__module_output = "/tmp/camera-module-output";
const char* PATH_CAMERA__module_input  = "/tmp/camera-module-input";
const char* PATH_CAMERA__logger        = "/tmp/camera-module-logger";

void set_priority (pthread_t id, int prio) {
    sched_param sch;
    int policy;
    pthread_getschedparam(id, &policy, &sch);

    sch.sched_priority = prio;
    pthread_setschedparam(id, SCHED_FIFO, &sch);
}

int main () {
    buffer_t tx_buffer = create_buffer(1024, 1024, tx_char_buffer);
    buffer_t rx_buffer = create_buffer(1024, 1024, rx_char_buffer);

    CoreContext context;
    CoreLogger  logger(&context);
    CoreTransceiver transceiver (&context, &tx_buffer, &rx_buffer);
    CorePhysical    physical    (&context, &tx_buffer, &rx_buffer);

    context.register_module(
        "AV CAM",
        PATH_CAMERA__module_output,
        PATH_CAMERA__module_input,
        PATH_CAMERA__logger
    );
    context.register_module(
        "AV SEN",
        "/tmp/sensors-module-output",
        "/tmp/sensors-module-input",
        "/tmp/sensors-logger"
    );

    pthread_t logger_id = logger     .start(); set_priority(logger_id, 98);
    pthread_t transc_id = transceiver.start(); set_priority(transc_id, 99);
    pthread_t physic_id = physical   .start(); set_priority(physic_id, 99);

    void* result;
    pthread_join(logger_id, &result);
    pthread_join(transc_id, &result);
    pthread_join(physic_id, &result);
}
