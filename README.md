# MultiMedia-HW1

## Image-Voice Chat


![Video-Voice Chat schematic](part1sch.jpg)

In the first part of this project we have an application that can capture an **image** of the webcam and a **30s audio**, then send it to the destination PC using **`TCP/IP`**.

### prerequisites
for this code to work, you need to install a couple of libraries:
* openCV (cv2)
* socket
* numpy
* pyaudio
* wave
* threading
* pyQT5

for installing any of the libraries above, you should open your termnial (for instance VScode terminal) and enter `pip install <library name>` e.g. `pip install cv2`

### how it works
It shows the webcam and can capture an image using `openCV`. The picture can be edited using *`Gama Correction Method`* (using `numpy`).it also can record a 30s audio using `pyaudio` and then saves them using `wave`. 

The sending and receiving part is done with `server.py` and `client.py` using `socket` library .In these files we make a **`TCP/IP`** server and exchange data with packets on ports 21200 (image) and 21300 (audio). (The chosen port are random :))

we used multithreading because VScode froze. (probably because this code uses multi OS processes)

the UI is done with pyQT.

**Caution:** First you should click `receive` then `send` for it to work properly. (First it should create the server)

## Wireless Communication & Command**
