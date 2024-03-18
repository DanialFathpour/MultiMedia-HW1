# Importing necessary libraries
import sys
import cv2
import pyaudio 
import wave 
import keyboard 
# if the libraries are not included properly, try installing them by "pip install <library name>" command in vscode terminal

# Creating a VideoCapture object to access the camera
cap = cv2.VideoCapture(0)  # 0 means webcam

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow("This is your webcam", frame)

    # Press the "c" key to capture a frame
    if cv2.waitKey(1) & 0xFF == ord("c"):
        # Save the captured frame to disk
        cv2.imwrite("captured_frame.jpg", frame)
        print("Frame captured and saved as 'captured_frame.jpg'")
        break

# When everything done, release the capture and destroy all windows
cap.release()
cv2.destroyAllWindows()


# Configuring parameters
duration = 30  # seconds
chunk = 1024
format = pyaudio.paInt16
channels = 1
sample_rate = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

print("press 'r' to start recording")
while True:
    if keyboard.is_pressed('r'):
        # Open stream
        stream = p.open(format=format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk)

        frames = []

        print("Recording...")

        for i in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)

        print("Recording finished")

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recording
        wf = wave.open('output.wav', 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print("The recording has been saved as 'output.wav'")
        break
    
    