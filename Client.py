# importing libraries
import socket
def client():
    HOST = '192.168.1.37' # my own local IP address
    #Image
    PORT_image = 21200 # random! (Must be the same with the server)
    #Audio
    PORT_audio = 21300 # random! (Must be the same with the server)

    # Creating the sockets and requesting to connect
    #AF_INET means IP and SOCK_STREAM mean TCP
    client_image = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_image.connect((HOST, PORT_image))
    client_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_audio.connect((HOST, PORT_audio))

    # Opening files
    file_image = open("captured_frame.jpg", "rb")
    file_audio = open("output.wav", "rb")

    # Sending file names
    client_image.send("received_image.jpg".encode())
    client_audio.send("received_audio.wav".encode())

    # Reading and sending files
    data_image = file_image.read()
    client_image.sendall(data_image)
    client_image.send(b"<END>")
    data_audio = file_audio.read()
    client_audio.sendall(data_audio)
    client_audio.send(b"<END>")

    # Closing stuff
    file_image.close()
    client_image.close()
    file_audio.close()
    client_audio.close()
