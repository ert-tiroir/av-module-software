
core:
	g++ -o AV_Core \
		`find av-core -name \*.cpp` \
		`find av-module -name \*.cpp` \
		`find utils -name \*.cpp` \
		communication/communication/buffer.cpp \
		communication/communication/rpi_spi.c \
		-I./ -I./communication -lwiringPi -lpthread -lm -lcrypt
camera:
	g++ -o AV_Camera_Module \
		`find av-camera -name \*.cpp` \
		`find av-module -name \*.cpp` \
		`find utils -name \*.cpp` \
		-I./ -I./communication
