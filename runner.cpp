
#include "communication/communication/rpi_spi.h"
#include <unistd.h>
#include <stdio.h>

unsigned char rx_buffer[1024 * 1024];
unsigned char tx_buffer[1024 * 1024];

void read (unsigned char* page, int size) {
    while (size > 0) {
        char c = getchar();
        page[0] = c;
        page ++;
        size --;
    }
}

int main () {
    buffer_t rxbf = create_buffer(1024, 1924, rx_buffer);
    buffer_t txbf = create_buffer(1024, 1924, tx_buffer);

    rpi_spi_init(&rxbf);

    while (1) {
        rpi_spi_tick();

        unsigned char* page = readable_page(&rxbf);
        if (page != 0) {
            send(fd, page, 1024, 0);
            free_read(&rxbf);
        }
    }
}
