import sys
import cv2
import numpy as np
import pyaudio
import wave
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QTime
import threading
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.HEIGHT = 800 
        self.WIDTH = 600
        self.setWindowTitle("Webcam and Voice Recorder")
        self.setGeometry(100, 100, self.HEIGHT, self.WIDTH)

        # Main window background color and font
        self.setStyleSheet("background-color: #f0f0f0; font-family: Arial;")

        # Video label
        self.video_label = QLabel(self)
        self.video_label.setGeometry(20, 20, self.HEIGHT*2//3, self.WIDTH*2//3)
        self.video_label.setStyleSheet("border: 2px solid black; background-color: white;")

        # Buttons
        self.capture_button = QPushButton(self)
        self.capture_button.setGeometry(self.HEIGHT*3//4, self.WIDTH*1//6, 150, 150)
        self.capture_button.setIcon(QIcon('Image-Capture-icon.png')) 
        self.capture_button.setIconSize(self.capture_button.size())
        self.capture_button.setStyleSheet("background-color: #f0f0f0; color: white; border: none; padding: 5px;")
        self.capture_button.clicked.connect(self.capture_frame)

        self.record_button = QPushButton(self)
        self.record_button.setGeometry(20, self.WIDTH*3//4, 150, 150)
        self.record_button.setIcon(QIcon('audio-icon.png')) 
        self.record_button.setIconSize(self.record_button.size())
        self.record_button.setStyleSheet("background-color: #f0f0f0; color: white; border: none; padding: 0px;border-radius: 75px;")
        self.record_button.clicked.connect(self.start_audio_recording)

        # Timer label
        self.timer_label = QLabel("00:00:00",self)
        self.timer_label.setGeometry(200,500, 300, 50)
        self.timer_label.setStyleSheet("font-size: 30px; color: black;")

        # Webcam capture and timer
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        # Audio recording parameters
        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.audio_sample_rate = 44100
        self.audio_chunk_size = 1024
        self.audio_duration = 30
        self.audio_file = 'recorded_audio.wav'
        self.audio_thread = None
        self.recording_timer = QTimer(self)
        self.recording_timer.timeout.connect(self.update_timer)

        self.start_time = None

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            frame = cv2.flip(frame, 1)
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(self.HEIGHT*2//3, self.WIDTH*2//3, Qt.KeepAspectRatio)
            self.video_label.setPixmap(QPixmap.fromImage(p))

    def capture_frame(self):
        ret, frame = self.capture.read()
        frame = cv2.flip(frame, 1)
        self.capture_button.setEnabled(False)
        QTimer.singleShot(150, self.enable_capture_button)
        if ret:
            cv2.imwrite('captured_frame.jpg', frame)

    def enable_capture_button(self):
        self.capture_button.setEnabled(True)
    def start_audio_recording(self):
        self.audio_thread = threading.Thread(target=self.record_voice)
        self.audio_thread.start()
        self.recording_timer.start(10)
        self.start_time = time.time()

    def record_voice(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.audio_format,
                            channels=self.audio_channels,
                            rate=self.audio_sample_rate,
                            input=True,
                            frames_per_buffer=self.audio_chunk_size)

        frames = []

        print("recording...")
        self.record_button.setEnabled(False)
        for i in range(0, int(self.audio_sample_rate / self.audio_chunk_size * self.audio_duration)):
            data = stream.read(self.audio_chunk_size)
            frames.append(data)

        print("end recording")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        wave_file = wave.open(self.audio_file, 'wb')
        wave_file.setnchannels(self.audio_channels)
        wave_file.setsampwidth(audio.get_sample_size(self.audio_format))
        wave_file.setframerate(self.audio_sample_rate)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()
        self.record_button.setEnabled(True)

    def update_timer(self):
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            m_seconds = int(elapsed_time*100) % 100
            self.timer_label.setText("00:{:02d}:{:02d}".format(int(elapsed_time) , m_seconds))
        else :
            elapsed_time = 0
        if elapsed_time > 30:
            self.start_time = None
            self.timer_label.setText("00:00:00")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_())
