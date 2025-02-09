
#include "av-module/core.h"
#include "av-module/logger.h"

#include <fcntl.h>
#include <unistd.h>

const char* PATH_CAMERA__module_output = "/tmp/camera-module-output";
const char* PATH_CAMERA__module_input  = "/tmp/camera-module-input";
const char* PATH_CAMERA__logger        = "/tmp/camera-module-logger";

const char* CAMERA_command = "libcamera-vid -t 0 -o - --width 720 --height 480 --bitrate 1000000";

const char* CAMERA_result_file = "AV_Camera_Result";

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
    FILE* cameraResult   = nullptr;

    logger << "Succesfully opened Camera Module" << LogLevel::SUCCESS;

    while ( 1 ) {
        if (cameraSoftware != nullptr) {
            int rem = SIZE - offset;
            int res = readFromSoftware(cameraSoftware, buffer, rem);
            if (res < 0) {
                pclose(cameraSoftware);
                fclose(cameraResult);
                cameraSoftware = nullptr;
                cameraResult   = nullptr;
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

            fwrite( buffer, 1, size_to_send, cameraResult );
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
            cameraResult   = fopen(CAMERA_result_file, "w");
            offset = 0;
            logger << "Successfully opened software\n" << LogLevel::SUCCESS;
        } else if (command == "STOP") {
            if (cameraSoftware == nullptr) {
                logger << "Cannot stop camera software if there are no running" << LogLevel::ERROR;
                continue ;
            }
            pclose(cameraSoftware);
            fclose(cameraResult);
            cameraSoftware = nullptr;
            cameraResult   = nullptr;
            offset = 0;
            logger << "Successfully closed software\n" << LogLevel::SUCCESS;
        }
    }
}
