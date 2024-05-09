
#include "av-module/core.h"
#include "av-module/logger.h"

#include <fcntl.h>
#include <unistd.h>

const char* PATH_CAMERA__module_output = "/tmp/camera-module-output";
const char* PATH_CAMERA__module_input  = "/tmp/camera-module-input";
const char* PATH_CAMERA__logger        = "/tmp/camera-module-logger";

const char* CAMERA_command = "libcamera-vid -t 0 -o - --width 720 --height 480 --bitrate 1000000";

FILE* openCameraSoftware () {
    FILE* software = popen(CAMERA_command, "r");

    int uuid = fileno(software);
    fcntl(uuid, F_SETFL, fcntl(uuid, F_GETFL) | O_NONBLOCK);

    return software;
}
int readFromSoftware (FILE* file, char* buffer, int size) {
    int fd = fileno(file);

    int res = read(fd, buffer, size);
    if (res == -1 && errno == EAGAIN) return 0;
    
    return res;
}

const int DATA_SIZE = 1016;
const int READ_CNT  = 16;

const int SIZE = DATA_SIZE * READ_CNT;

int offset = 0;
char buffer[SIZE];

int main () {
    CoreTarget target(
        PATH_CAMERA__module_output,
        PATH_CAMERA__module_input,
        PATH_CAMERA__logger
    );
    ModuleLogger logger (&target);

    FILE* cameraSoftware = nullptr;

    logger << "Succesfully opened Camera Module" << LogLevel::SUCCESS;

    while ( 1 ) {
        if (cameraSoftware != nullptr) {
            int rem = SIZE - offset;
            int res = readFromSoftware(cameraSoftware, buffer, rem);
            if (res < 0) {
                pclose(cameraSoftware);
                cameraSoftware = nullptr;
                logger << "Unexpected close from camera software" << LogLevel::ERROR;
                continue ;
            }

            offset += res;
            if (offset < DATA_SIZE) continue ;
            int to_displace  = offset % DATA_SIZE;
            int size_to_send = offset - to_displace;

            std::string str(size_to_send, '*');
            for (int i = 0; i < size_to_send; i ++) str[i] = buffer[i];

            target.write_string_to_core(str);
            logger << "Sent buffer of size " << size_to_send << " to radio" << LogLevel::INFO;
            for (int i = 0; i < to_displace; i ++)
                buffer[i] = buffer[i + size_to_send];
            offset = to_displace;
        }

        bool found;
        std::string command = target.read_string_from_core(&found);
        if (!found) continue ;

        if (command == "START") {
            if (cameraSoftware != nullptr) {
                logger << "Cannot start camera software if one is still running" << LogLevel::ERROR;
                continue ;
            }
            cameraSoftware = openCameraSoftware();
            offset = 0;
        } else if (command == "STOP") {
            if (cameraSoftware == nullptr) {
                logger << "Cannot stop camera software if there are no running" << LogLevel::ERROR;
                continue ;
            }
            pclose(cameraSoftware);
            cameraSoftware = nullptr;
            offset = 0;
        }
    }
}
