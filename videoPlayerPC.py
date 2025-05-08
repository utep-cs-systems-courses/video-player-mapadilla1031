#!/usr/bin/env python3
#Last Edited by Marko Padilla
#Video Player Producer–Consumer Lab
#Operating Systems
import cv2
import threading

extractionQueue = [] #the frames
grayscaleQueue = [] #converted the frames

extractionLock = threading.Lock()
extractionEmpty = threading.Semaphore(10) #queue size
extractionFull = threading.Semaphore(0)
grayscaleLock = threading.Lock()
grayscaleEmpty = threading.Semaphore(10) #queue size
grayscaleFull = threading.Semaphore(0)

#Extract frames into extractionQueue
def extractFrames(filename, extractionQueue, maxFrames):
    cap = cv2.VideoCapture(filename)
    count = 0
    success, frame = cap.read()
    
    # If first read fails, print error and return
    if not success:
        print(f'Error reading "{filename}"')
        return
        
    while success and count < maxFrames:
        print(f'Reading the frame {count}') #first thread, the producer
        extractionEmpty.acquire() #wait if the queue is full
        
        extractionLock.acquire() # acquire lock
        extractionQueue.append(frame) #then add frame to the Queue
        extractionLock.release() # release lock
        
        extractionFull.release() #new frame is available
        count += 1
        success, frame = cap.read()
    cap.release()
    print(f'Frame extraction complete {count} frames')

#Convert the 72 frames from extractionQueue to grayscaleQueue
def convertFrames(extractionQueue, grayscaleQueue): #consumer and producer
    count = 0
    while count < 72: #already know we have 72 grayscale frames
        extractionFull.acquire()
        
        extractionLock.acquire() # acquire lock
        frame = extractionQueue.pop(0) # get the frame from the queue
        extractionLock.release() # release lock
        
        extractionEmpty.release() # space now available
        print(f'Converting frame {count}')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #convert to grayscale
        grayscaleEmpty.acquire() #wait if grayscale queue full
        
        grayscaleLock.acquire() # acquire lock
        grayscaleQueue.append(gray)
        grayscaleLock.release() # release lock
        
        grayscaleFull.release()
        count += 1
    print(f'Frame conversion complete {count} frames')

#Display the 72 frames from grayscaleQueue
#display them at 24fps
def displayFrames(grayscaleQueue, frameDelay): #consumer (3rd thread)
    count = 0
    while count < 72:
        grayscaleFull.acquire()
        
        grayscaleLock.acquire() # acquire lock
        frame = grayscaleQueue.pop(0)
        grayscaleLock.release() # release lock
        
        grayscaleEmpty.release()
        print(f'Displaying frame {count}')
        cv2.imshow('Video', frame)
        if cv2.waitKey(frameDelay) & 0xFF == ord('q'):
            break
        count += 1
    print(f'{count} frames displayed')
    cv2.destroyAllWindows()

def main():
                                                                     #filename, maxFrames, frameDelay
    extractorThread = threading.Thread(target=extractFrames, args=('clip.mp4', extractionQueue, 72), name='Extractor')
    converterThread = threading.Thread(target=convertFrames, args=(extractionQueue, grayscaleQueue), name='Converter')
    print('Starting')
    extractorThread.start() #start extractor
    converterThread.start() #start converter
    # display on main
    displayFrames(grayscaleQueue, 42)
    extractorThread.join() #wait until extract is done
    converterThread.join() #wait until converter finishes

if __name__ == '__main__':
    main()