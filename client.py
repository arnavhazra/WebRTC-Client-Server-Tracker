import asyncio
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.contrib.signaling import TcpSocketSignaling
from multiprocessing import Process, Queue, Value

def process_a(queue, coordinates):
    """
    This process parses the image and determines the current location of the ball as x,y coordinates.
    Args:
        queue (Queue): A queue to get frames from.
        coordinates (Value): A shared value to store the computed coordinates.
    """
    while True:
        frame = queue.get()  # Get the frame from the queue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert the frame to grayscale
        ret, thresh = cv2.threshold(gray, 127, 255, 0)  # Apply threshold to the grayscale image
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # Find contours in the threshold image
        if contours:  # If contours are found
            c = max(contours, key = cv2.contourArea)  # Get the contour with the maximum area
            x, y, _, _ = cv2.boundingRect(c)  # Get the bounding rectangle for the contour
            coordinates.value = x, y  # Update the shared coordinates value
            print("Coordinates are computed:", x, y)  # Print the computed coordinates

async def handle_track(track, queue, channel, coordinates):
    """
    This function handles the received track, puts the frame into the queue, and sends the coordinates.
    Args:
        track (Track): The received track.
        queue (Queue): A queue to put frames into.
        channel (DataChannel): The data channel to send coordinates.
        coordinates (Value): A shared value to get the computed coordinates from.
    """
    while True:
        frame = await track.recv()  # Receive the frame from the track
        queue.put(np.frombuffer(frame.data, np.uint8).reshape(frame.height, frame.width, 3))  # Put the frame into the queue
        print("Frame is received and put into the queue")  # Print a message indicating that the frame is received and put into the queue
        x, y = coordinates.value  # Get the computed coordinates
        channel.send(f"{x},{y}".encode())  # Convert coordinates to bytes before sending
        print("Coordinates are sent:", x, y)  # Print the sent coordinates

async def run(pc, signaling, queue, coordinates):
    """
    This function runs the main logic of the client.
    Args:
        pc (RTCPeerConnection): The RTCPeerConnection object.
        signaling (TcpSocketSignaling): The TcpSocketSignaling object.
        queue (Queue): A queue to put frames into.
        coordinates (Value): A shared value to get the computed coordinates from.
    """
    try:
        channel = pc.createDataChannel("data")  # Create a data channel
        print("Data channel is created")  # Print a message indicating that the data channel is created

        @pc.on("track")
        def on_track(track):
            print("Receiving %s" % track.kind)  # Print a message indicating that a track is being received
            if track.kind == "video":  # If the track is a video track
                asyncio.ensure_future(handle_track(track, queue, channel, coordinates))  # Handle the track

        @pc.on("datachannel")
        def on_datachannel(channel):
            print("Data channel is established")  # Print a message indicating that the data channel is established
            @channel.on("message")
            def on_message(message):
                x, y = coordinates.value  # Get the computed coordinates
                channel.send(f"{x},{y}")  # Send the coordinates
                print("Coordinates are sent:", x, y)  # Print the sent coordinates

        await signaling.connect()  # Connect the signaling
        print("Signaling is connected")  # Print a message indicating that the signaling is connected
        obj = await signaling.receive()  # Receive the offer
        print("Offer is received")  # Print a message indicating that the offer is received
        await pc.setRemoteDescription(RTCSessionDescription(type=obj.type, sdp=obj.sdp))  # Set the received offer as the remote description
        print("Offer is set as remote description")  # Print a message indicating that the offer is set as the remote description
        await pc.setLocalDescription(await pc.createAnswer())  # Create an answer and set it as the local description
        print("Answer is created")  # Print a message indicating that the answer is created
        await signaling.send(pc.localDescription)  # Send the local description
        print("Answer is sent")  # Print a message indicating that the answer is sent
    except Exception as e:
        print(f"Error occurred: {e}")  # Print the error if any

def main():
    """
    The main function of the client.
    """
    signaling = TcpSocketSignaling('localhost', 12345)  # Create a TcpSocketSignaling object
    pc = RTCPeerConnection()  # Create a RTCPeerConnection object
    queue = Queue()  # Create a queue
    coordinates = Value('d', 0.0)  # Create a shared value for coordinates
    p = Process(target=process_a, args=(queue, coordinates))  # Create a process for process_a
    p.start()  # Start the process
    loop = asyncio.get_event_loop()  # Get the event loop
    try:
        loop.run_until_complete(run(pc, signaling, queue, coordinates))  # Run the main logic of the client
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())  # Close the RTCPeerConnection
        loop.run_until_complete(signaling.close())  # Close the TcpSocketSignaling
        p.join()  # Join the process

if __name__ == "__main__":
    main()  # Run the main function