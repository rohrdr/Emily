import cv2 as cv
import numpy as np
import time
from PIL import Image


class Eyes:

    def __init__(self, config, weights, width, height):

        print('initialize Eyes')

        pass

    def run(self, image):

        import time

        time.sleep(10)

        return []

#     def __init__(self, config, weights, width, height):
#
#         # need to initialize some stuff
#         self.config = config  #The path to the config file
#         self.weights = weights #The path to the weights file
#         self.width = width
#         self.height = height
#
#         self.net = cv.dnn.readNetFromDarknet(self.config, self.weights)
#         self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
#         self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
#
#
#         return
#
#     def run(self, image):
#
#         name = 'dummy.jpg'
#         img = Image.fromarray(np.uint8(image))
#         img.save(name)
# #        time.sleep(1)
# #        bbox = 'bla'
#         cap = cv.VideoCapture(name)
#         hasframe, frame = cap.read()
#
#         start = time.time()
#         bbox = self.inference(frame)
#         end = time.time()
#         print('inference took ', end-start)
#
#         return bbox

    def getOutputsNames(self):
        # Get the names of all the layers in the network
        layersNames = self.net.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layersNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def postprocess(self, frame, outs, confThreshold, nmsThreshold):

        #Helper function to process the output of Yolo

        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        #We initialize with an empty list that we will returm at the end

        ans = []

        classIds = []
        confidences = []
        boxes = []
        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            #print("out.shape : ", out.shape)
            for detection in out:
                #if detection[4]>0.001:
                scores = detection[5:]
                classId = np.argmax(scores)

                #if scores[classId]>confThreshold:


                confidence = scores[classId]
#                if detection[4]>confThreshold:
                   # print(detection[4], " - ", scores[classId], " - th : ", confThreshold)
#                   print(detection)


                if confidence > confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)

        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            center_x= (left+width/2)
            center_y= (top+height/2)
            ans.append([classIds[i],confidences[i],center_x/frameWidth,center_y/frameHeight,width/frameWidth,height/frameHeight])

        return ans



    def inference(self,
                frame,
#                inpWidth = int(1536 / 2),
#                inpHeight = int(1152 / 2),
                confThreshold = 0.3,
                nmsThreshold = 0.1,
                ):
        # takes an image, runs a forward pass, and removes the overlapping pictures. Returns a list of list
        # each element of the list is a list containing [classID,Confidence interval, center_x, center_y, width, height]



#       We convert the image we got into a blob with the good dimensions

        blob = cv.dnn.blobFromImage(frame, 1/255, (self.width, self.height), [0,0,0], 1, crop=False)

        # Sets the input to the network


        self.net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = self.net.forward(self.getOutputsNames())

        # Remove the bounding boxes with low confidence, add the resulting boxes to ans
        ans = self.postprocess(frame, outs, confThreshold, nmsThreshold)

        if len(ans)==0:
            print('nothing has been found, moving forward')
        else:
            print('yeah I found a cigarette!')

        return ans
