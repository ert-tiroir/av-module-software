
core:
	g++ -o AV_Core \
		`find av-core -name \*.cpp -and -not -name physical.cpp` \
		`find av-module -name \*.cpp` \
		`find utils -name \*.cpp` \
		communication/communication/buffer.cpp \
		-I./ -I./communication
camera:
	g++ -o AV_Camera_Module \
		`find av-camera -name \*.cpp` \
		`find av-module -name \*.cpp` \
		`find utils -name \*.cpp` \
		-I./ -I./communication
