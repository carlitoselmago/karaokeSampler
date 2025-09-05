from pythonosc.udp_client import SimpleUDPClient
from time import sleep

ip = "127.0.0.1"
port = 8000

client = SimpleUDPClient(ip, port)  # Create client

client.send_message("/newsong", "new song titleeeee")   # Send float message
#client.send_message("/some/address", [1, 2., "hello"])  # Send message with int, float and string