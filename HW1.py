import sys
import cv2
import numpy as np
import pyaudio
import wave
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt
import threading


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Webcam and Voice Recorder")
        self.setGeometry(100, 100, 800, 600)

        self.video_label = QLabel(self)
        self.video_label.setGeometry(50, 50, 640, 480)

        self.capture_button = QPushButton("Capture Frame", self)
        self.capture_button.setGeometry(50, 550, 150, 30)
        self.capture_button.clicked.connect(self.capture_frame)

        self.goto_audio_button = QPushButton("Go to Audio", self)
        self.goto_audio_button.setGeometry(225, 550, 150, 30)
        self.goto_audio_button.clicked.connect(self.switch_to_audio_page)
        self.goto_audio_button.hide()

        self.record_button = QPushButton(self)
        self.record_button.setGeometry(250, 250, 150, 150)
        self.record_button.setIcon(QIcon('audio-icon.png')) 
        self.record_button.setIconSize(self.record_button.size())
        self.record_button.clicked.connect(self.start_audio_recording)
        self.record_button.hide()

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.audio_sample_rate = 44100
        self.audio_chunk_size = 1024
        self.audio_duration = 30
        self.audio_file = 'recorded_audio.wav'
        self.audio_thread = None

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.video_label.setPixmap(QPixmap.fromImage(p))

    def capture_frame(self):
        ret, frame = self.capture.read()
        if ret:
            cv2.imwrite('captured_frame.jpg', frame)
            self.goto_audio_button.show()

    def switch_to_audio_page(self):
        self.capture_button.hide()
        self.goto_audio_button.hide()
        self.record_button.show()
        self.video_label.hide()
        self.video_label.clear()  # Clear the webcam display

    def start_audio_recording(self):
        self.audio_thread = threading.Thread(target=self.record_voice)
        self.audio_thread.start()

    def record_voice(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.audio_format,
                            channels=self.audio_channels,
                            rate=self.audio_sample_rate,
                            input=True,
                            frames_per_buffer=self.audio_chunk_size)

        frames = []

        print("recording...")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
