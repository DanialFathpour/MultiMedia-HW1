import sys
import cv2
import numpy as np
import pyaudio
import wave
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QSize
import time
import threading
from Server import server  #import server from server code for recieve
from Client import client  #import client from client code for sending 

#warning
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #Set window parameters----------
        self.HEIGHT = 600 
        self.WIDTH = 800
        self.setWindowTitle("Webcam and Voice Recorder")
        self.setGeometry(100, 100, self.WIDTH, self.HEIGHT)

        # Main window background color and font---------
        self.setStyleSheet("background-color: #f0f0f0; font-family: Arial;")

        # Video label-----------
        self.video_label = QLabel(self)
        self.video_label.setGeometry(20, 20, self.WIDTH*2//3, self.HEIGHT*2//3)
        self.video_label.setStyleSheet("border: 2px solid black; background-color: white;")

        # Buttons--------------
        self.capture_button = QPushButton(self)
        self.capture_button.setGeometry(self.WIDTH*3//4, self.HEIGHT*1//6, 150, 150)
        self.capture_button.setIcon(QIcon('Image-Capture-icon.png')) 
        self.capture_button.setIconSize(self.capture_button.size())
        self.capture_button.setStyleSheet("background-color: #f0f0f0; color: white; border: none; padding: 5px;")
        self.capture_button.clicked.connect(self.capture_frame)

        self.record_button = QPushButton(self)
        self.record_button.setGeometry(20, self.HEIGHT*3//4, 150, 150)
        self.record_button.setIcon(QIcon('audio-icon.png')) 
        self.record_button.setIconSize(self.record_button.size())
        self.record_button.setStyleSheet("background-color: #f0f0f0; color: white; border: none; padding: 0px;border-radius: 75px;")
        self.record_button.clicked.connect(self.start_audio_recording)


        # Show and play buttons---------------
        self.show_frame_button = QPushButton("Show Frame", self)
        self.show_frame_button.setGeometry(self.WIDTH*3//4, self.HEIGHT*1//6 + 200, 230, 150)
        self.show_frame_button.setIcon(QIcon('show.png')) 
        self.show_frame_button.setIconSize(QSize(150, 150))
        self.show_frame_button.setStyleSheet("background-color: #f0f0f0; color: white; border: none; padding: 0px;border-radius: 25px;")
        self.show_frame_button.clicked.connect(self.show_captured_frame)

        self.play_audio_button = QPushButton("Play Audio", self)
        self.play_audio_button.setGeometry(400, 485, 150, 70)
        self.play_audio_button.setIcon(QIcon('play.png')) 
        self.play_audio_button.setIconSize(self.play_audio_button.size())
        self.play_audio_button.setStyleSheet("background-color: #f0f0f0; color: white; border: none; padding: 0px;border-radius: 75px;")
        self.play_audio_button.clicked.connect(self.play_recorded_audio)


        # Timer label for recording---------------------------
        self.timer_label = QLabel("00:00:00",self)
        self.timer_label.setGeometry(200,500, 150, 50)
        self.timer_label.setStyleSheet("font-size: 30px; color: black;")

        # Webcam capture and timer-------------------------
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        # Audio parameters------------------------------
        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.audio_sample_rate = 44100
        self.audio_chunk_size = 1024
        self.audio_duration = 30
        self.audio_file = 'recorded_audio.wav'
        self.audio_thread = None
        self.play_audio_thread = None
        self.recording_timer = QTimer(self)
        self.recording_timer.timeout.connect(self.update_timer)

        self.start_time = None

        #send button--------------------------
        self.send_button = QPushButton("Send", self)
        self.send_button.setGeometry(600, 485, 150, 35)
        self.send_button.setStyleSheet("background-color: #3a8721; color: white; border: none; padding: 0px;border-radius:10px;font-size: 20px")
        self.send_button.clicked.connect(self.send_data)  # Connect the button click to the send_data function

        #recieve button--------------------------
        self.recieve_button = QPushButton("Recieve", self)
        self.recieve_button.setGeometry(600, 485 + 50, 150, 35)
        self.recieve_button.setStyleSheet("background-color: #cc4221; color: white; border: none; padding: 0px;border-radius:10px;font-size: 20px")
        self.recieve_button.clicked.connect(self.recieve_data)  # Connect the button click to the send_data function

    #updating frames and displaying them-----------------------
    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(self.WIDTH*2//3, self.HEIGHT*2//3, Qt.KeepAspectRatio)
            self.video_label.setPixmap(QPixmap.fromImage(p))

    #function for capture a snapshot---------------------------
    def capture_frame(self):
        ret, frame = self.capture.read()

        #disabling the button for 150 miliseconds making capture animation
        self.capture_button.setEnabled(False)
        QTimer.singleShot(150, self.enable_capture_button)

        if ret:
            
            #create trackbars for enabling and changing light intensity using "gamma correction method" --- 
            cv2.namedWindow('Preview (Press q to select and exit)')
            cv2.createTrackbar('Level ', 'Preview (Press q to select and exit)', 10, 50, self.adjust_gamma)
            cv2.createTrackbar('Enable ', 'Preview (Press q to select and exit)', 0, 1, self.enable_gamma_correction)

            #preview loop press "q" to select and exit
            while True:

                #set the gamma value between 0 and 5
                gamma_value = cv2.getTrackbarPos('Level ', 'Preview (Press q to select and exit)')/10

                #enabling the gamma correction
                enable_gamma = cv2.getTrackbarPos('Enable ', 'Preview (Press q to select and exit)')
                if enable_gamma:
                    adjusted_frame = self.apply_gamma_correction(frame, gamma_value)
                else:
                    adjusted_frame = frame

                #showing the adjusted frame
                cv2.imshow('Preview (Press q to select and exit)', adjusted_frame)

                #Press "q" key to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            #save and write the captured image
            cv2.imwrite('captured_frame.jpg', adjusted_frame)
            cv2.destroyAllWindows()

    # Apply gamma correction-----------------------
    def apply_gamma_correction(self, frame, gamma=1.0):
        gamma_corrected = np.power(frame / 255.0, gamma)
        gamma_corrected = (gamma_corrected * 255).astype(np.uint8)
        return gamma_corrected

    # Callback function for adjusting gamma correction-------------
    def adjust_gamma(self, gamma_value):
        pass

    # Callback function for enabling/disabling gamma correction--------------
    def enable_gamma_correction(self, enable_gamma):
        pass


    #helper function for enabling capture button after a delay---------------
    def enable_capture_button(self):
        self.capture_button.setEnabled(True)
    
    #start recording audio--------------------
    def start_audio_recording(self):
        #use multithreading for audio recording
        self.audio_thread = threading.Thread(target=self.record_voice)
        self.audio_thread.start()
        self.recording_timer.start(10)
        self.start_time = time.time()

    #show the captured frame in a seprate window-----------------
    def show_captured_frame(self):
        captured_frame = cv2.imread('captured_frame.jpg')
        cv2.imshow('Captured Frame', captured_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    #start playing the recorded audio in a seprate thread----------------
    def play_recorded_audio(self):
        if self.play_audio_thread is None or not self.play_audio_thread.is_alive():
            self.play_audio_thread = threading.Thread(target=self.play_audio)
            self.play_audio_thread.start()

    #play the recorded audio-----------
    def play_audio(self):
        wave_file = wave.open(self.audio_file, 'rb')
        audio_data = wave_file.readframes(-1)
        wave_file.close()

        audio = pyaudio.PyAudio()
        stream = audio.open(format=audio.get_format_from_width(wave_file.getsampwidth()),
                            channels=wave_file.getnchannels(),
                            rate=wave_file.getframerate(),
                            output=True)
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
        audio.terminate()
    
    #record audio-----------
    def record_voice(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.audio_format,
                            channels=self.audio_channels,
                            rate=self.audio_sample_rate,
                            input=True,
                            frames_per_buffer=self.audio_chunk_size)

        frames = []

        #disabling record button during the recording
        self.record_button.setEnabled(False)

        #recording ...
        for i in range(0, int(self.audio_sample_rate / self.audio_chunk_size * self.audio_duration)):
            data = stream.read(self.audio_chunk_size)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wave_file = wave.open(self.audio_file, 'wb')
        wave_file.setnchannels(self.audio_channels)
        wave_file.setsampwidth(audio.get_sample_size(self.audio_format))
        wave_file.setframerate(self.audio_sample_rate)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        #enabling record button after recording
        self.record_button.setEnabled(True)

    #update record timer--------------------
    def update_timer(self):
        if self.start_time:
            #calculating elapsed time as seconds
            elapsed_time = time.time() - self.start_time

            #calculating seconds/100
            m_seconds = int(elapsed_time*100) % 100

            #update the timer
            self.timer_label.setText("00:{:02d}:{:02d}".format(int(elapsed_time) , m_seconds))

        else :
            elapsed_time = 0

        #restart the timer
        if elapsed_time > 30:
            self.start_time = None
            self.timer_label.setText("00:00:00")

    #Send the data ----------
    def send_data(self):
        client()

    #Recieve the data ---------
    def recieve_data(self):
        server()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
