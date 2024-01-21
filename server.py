import asyncio
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCDataChannelParameters
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.contrib.signaling import TcpSocketSignaling

class BallBouncingVideoStreamTrack(VideoStreamTrack):
    """
    A video track that generates a continuous 2D image/frames of a ball bouncing across the screen.
    """
    def __init__(self):
        super().__init__()  # Call the super class constructor
        self.ball_pos = [0, 0]  # Initialize the ball position
        self.ball_vel = [3, 3]  # Initialize the ball velocity

    async def recv(self):
        """
        This method generates a frame with a bouncing ball.
        """
        frame = np.zeros((500, 500, 3), dtype=np.uint8)  # Initialize a black frame

        # update ball position less frequently and use interpolation for smoother animation
        if self.time % 10 == 0:
            self.ball_pos[0] += self.ball_vel[0]  # Update the x-coordinate of the ball position
            self.ball_pos[1] += self.ball_vel[1]  # Update the y-coordinate of the ball position

            # bounce off walls
            if self.ball_pos[0] in [0, 500]:  # If the ball hits the left or right wall
                self.ball_vel[0] *= -1  # Reverse the x-velocity
            if self.ball_pos[1] in [0, 500]:  # If the ball hits the top or bottom wall
                self.ball_vel[1] *= -1  # Reverse the y-velocity

        # draw ball
        cv2.circle(frame, tuple(self.ball_pos), 20, (0, 255, 0), -1)  # Draw the ball on the frame

        return frame  # Return the frame

async def run(pc, signaling, local_video):
    """
    This function runs the main logic of the server.
    Args:
        pc (RTCPeerConnection): The RTCPeerConnection object.
        signaling (TcpSocketSignaling): The TcpSocketSignaling object.
        local_video (BallBouncingVideoStreamTrack): The local video track.
    """
    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)  # Print a message indicating that a track is being received
        if track.kind == "video":  # If the track is a video track
            pc.addTrack(local_video)  # Add the local video track to the peer connection

    @pc.on("datachannel")
    def on_datachannel(channel):
        print("Data channel is established")  # Print a message indicating that the data channel is established
        @channel.on("message")
        def on_message(message):
            try:
                print("Received message:", message)  # Print the received message
                x, y = map(int, message.split(","))  # Parse the received message into x and y coordinates
                print("Ball position:", x, y)  # Print the ball position
                print("Coordinate error:", abs(x - local_video.ball_pos[0]), abs(y - local_video.ball_pos[1]))  # Print the coordinate error
            except Exception as e:
                print(f"Error occurred: {e}")  # Print the error if any

    # Add a data channel before creating the offer
    pc.createDataChannel("data")  # Create a data channel
    print("Data channel is created")  # Print a message indicating that the data channel is created

    await signaling.connect()  # Connect the signaling
    print("Signaling is connected")  # Print a message indicating that the signaling is connected
    await pc.setLocalDescription(await pc.createOffer())  # Create an offer and set it as the local description
    print("Offer is created")  # Print a message indicating that the offer is created
    await signaling.send(pc.localDescription)  # Send the local description
    print("Offer is sent")  # Print a message indicating that the offer is sent

    # Wait for answer
    obj = await signaling.receive()  # Receive the answer
    print("Answer is received")  # Print a message indicating that the answer is received
    await pc.setRemoteDescription(RTCSessionDescription(type=obj.type, sdp=obj.sdp))  # Set the received answer as the remote description
    print("Answer is set as remote description")  # Print a message indicating that the answer is set as the remote description

    # Keep the server running
    while True:
        await asyncio.sleep(1)  # Wait for a second

def main():
    """
    The main function of the server.
    """
    signaling = TcpSocketSignaling('localhost', 12345)  # Create a TcpSocketSignaling object
    pc = RTCPeerConnection()  # Create a RTCPeerConnection object
    local_video = BallBouncingVideoStreamTrack()  # Create a BallBouncingVideoStreamTrack object
    loop = asyncio.get_event_loop()  # Get the event loop
    try:
        loop.run_until_complete(run(pc, signaling, local_video))  # Run the main logic of the server
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())  # Close the RTCPeerConnection
        loop.run_until_complete(signaling.close())  # Close the TcpSocketSignaling

if __name__ == "__main__":
    main()  # Run the main function