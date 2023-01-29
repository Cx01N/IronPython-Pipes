import os
import clr
import sys
import time
import threading
clr.AddReference('System.Core')
clr.AddReference("System.IO.Pipes")
import System.IO.Pipes
from System.IO.Pipes import PipeDirection, PipeTransmissionMode, PipeOptions, NamedPipeServerStream
import System.Threading
import System.Collections.Generic
from System.Security.Principal import TokenImpersonationLevel

# Create a queue to hold data to be sent through the pipe
send_queue = System.Collections.Generic.Queue[str]()

# Function to run in the separate thread to handle the named pipe connection
def pipe_thread_function():
    # Connect to the named pipe
    pipe_name = "my_pipe"
    host_name = "192.168.223.246"
    #host_name = "WinDev2206Eva"
    os.path.exists(host_name)
    time.sleep(5)
    
    pipe_client = System.IO.Pipes.NamedPipeClientStream(host_name, pipe_name, PipeDirection.InOut, 0, TokenImpersonationLevel.Impersonation)
    #pipe_client = System.IO.Pipes.NamedPipeClientStream(host_name, pipe_name)
    # Connect to the server
    pipe_client.Connect(5)

    while True:
        # Check if there is data in the send queue to send through the pipe
        if send_queue.Count > 0:
            # Send data through the pipe
            pipe_writer = System.IO.StreamWriter(pipe_client)
            pipe_writer.WriteLine(send_queue.Peek())
            pipe_writer.Flush()
            send_queue.Dequeue()

        # Receive data from the pipe
        pipe_reader = System.IO.StreamReader(pipe_client)
        received_data = pipe_reader.ReadLine()

        if received_data:
            # Print the received data
            print(received_data)
        time.sleep(1)
        
        
class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()
  method."""

    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread toinstall our trace.
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
    trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


# Create and start the separate thread for the named pipe connection
pipe_thread = KThread(target=pipe_thread_function)
pipe_thread.daemon = True
pipe_thread.start()

while True:
    # Add data to the send queue to be sent through the pipe
    send_queue.Enqueue("Hello from the client!")
    time.sleep(1)

print('exit')
pipe_thread.kill()

