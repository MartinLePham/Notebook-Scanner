import serial


class Sync:

    def __init__(self, port, baud, timeout=0):
        self.arduino = serial.Serial(port, baud, timeout=timeout)

    def write(self, data):
        self.arduino.write(data)

    def wait(self):
        while(1):
            buff = self.arduino.readline()
            if('b' in buff):
                break

    def flush(self):
        self.arduino.flush()


PORT = '/dev/ttyACM0'
arduinoData = Sync(PORT, 9600, timeout=0)

'''

system = pyspin.System.GetInstance()
cam_list = system.GetCameras()
cam = cam_list[0]

nodemap_tldevice = cam.GetTLDeviceNodeMap()
cam.Init()
nodemap = cam.GetNodeMap()

node_acquisition_framerate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
framerate_to_set = node_acquisition_framerate.GetValue()
print('[INFO] Frame rate to be set to %d...' % framerate_to_set)

cam.BeginAcquisition()

image_result = cam.GetNextImage()
'''




arduinoData.write(b'r6400\n')
arduinoData.wait()
arduinoData.write(b'l6400')
