# WebRTC application - Ball Tracking System

This project consists of two Python programs, a server and a client, that work together to track the position of a bouncing ball in real-time. The server generates a continuous 2D image of a ball bouncing across the screen and transmits these images to the client. The client then processes these images to determine the current location of the ball and sends these coordinates back to the server.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

The project requires Python 3 and the following Python libraries installed:

- asyncio
- cv2 (OpenCV)
- numpy
- aiortc

You can install these packages using pip:

```
pip install asyncio opencv-python numpy aiortc
```

## Running the Programs

To run the server program, navigate to the directory containing the project files and run the following command:

```
python3 server.py
```

To run the client program, open a new terminal, navigate to the same directory, and run the following command:

```
python3 client.py
```

## Project Structure

The project consists of two main Python files:

- `server.py`: This is the server program. It generates a continuous 2D image of a ball bouncing across the screen and transmits these images to the client using the aiortc library. It also receives the ball's coordinates from the client and calculates the error between the received coordinates and the actual coordinates.

- `client.py`: This is the client program. It receives the images from the server, processes these images to determine the current location of the ball, and sends these coordinates back to the server. The image processing is done in a separate process.

## Built With

- [Python](https://www.python.org/) - The programming language used.
- [aiortc](https://github.com/aiortc/aiortc) - The library used for Real-Time Communications (RTC) capabilities.
- [OpenCV](https://opencv.org/) - The library used for image processing tasks.
- [asyncio](https://docs.python.org/3/library/asyncio.html) - The library used for writing single-threaded concurrent code using coroutines, multiplexing I/O access over sockets and other resources, running network clients and servers, and other related primitives.
- [numpy](https://numpy.org/) - The library used for numerical computations.

## Authors

- Arnav Hazra

## Acknowledgments

- Thanks to the aiortc project for providing a Python implementation of RTC.
- Thanks to the OpenCV project for providing a powerful library for image processing tasks.

