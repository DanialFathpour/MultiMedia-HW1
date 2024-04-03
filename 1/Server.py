
# Attention!!!         the server code should be run by cmd and not VScode because it freezes!


# Importing libraries
import socket

def server():
    HOST = '192.168.1.34' # my own local IP address
    # Image
    PORT_image = 21200 # random! (Must be the same with the client)
    # Audio
    PORT_audio = 21300 # random! (Must be the same with the client)

    # Creating the sockets and listening
    #AF_INET means IP and SOCK_STREAM mean TCP
    server_image = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_image.bind((HOST, PORT_image))
    server_image.listen()
    server_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_audio.bind((HOST, PORT_audio))
    server_audio.listen()

    # Accepting the connection from clients
    client_image, addr_image = server_image.accept()
    client_audio, addr_audio = server_audio.accept()

    # Decoding the first chunk of data a.k.a the file name
    file_name_image = client_image.recv(1024).decode()
    file_name_audio = client_audio.recv(1024).decode()

    # Opening files for saving the data
    file_image = open(file_name_image, "wb")
    file_audio = open(file_name_audio, "wb")

    file_bytes_image = b""
    file_bytes_audio = b""

    done_image = False
    done_audio = False

    # Saving the image 
    while not done_image:
        data_image = client_image.recv(1024)
        if file_bytes_image[-5:] == b"<END>":
            done_image = True
        else:
            file_bytes_image += data_image
    file_image.write(file_bytes_image)

    # Saving the audio
    while not done_audio:
        data_audio = client_audio.recv(1024)
        if file_bytes_audio[-5:] == b"<END>":
            done_audio = True
        else:
            file_bytes_audio += data_audio
    file_audio.write(file_bytes_audio)

    # Closing stuff
    file_image.close()
    client_image.close()
    server_image.close()
    file_audio.close()
    client_audio.close()
    server_audio.close()
