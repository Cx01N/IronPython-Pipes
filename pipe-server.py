import clr
import time
import threading
import sys
from System import Environment
clr.AddReference('System.Core')
import System.IO.HandleInheritability
clr.AddReference("System.IO.Pipes")
import System.IO.Pipes
from System.IO.Pipes import PipeDirection, PipeTransmissionMode, PipeOptions, NamedPipeServerStream, PipeAccessRights, PipeAccessRule, PipeSecurity
from System.Security.Principal import SecurityIdentifier, WellKnownSidType
from System.Security.AccessControl import AccessControlType
import System.Collections.Generic

# Create a queue to hold received data
received_queue = System.Collections.Generic.Queue[str]()

# Function to run in the separate thread to handle the named pipe server
def server_thread_function():
    # Create the named pipe server
    pipe_name = "my_pipe"
    security = PipeSecurity()
    
    #security.AddAccessRule(PipeAccessRule(SecurityIdentifier(WellKnownSidType.BuiltinUsersSid, None), PipeAccessRights.FullControl, AccessControlType.Allow))
    #security.AddAccessRule(PipeAccessRule(SecurityIdentifier(WellKnownSidType.CreatorOwnerSid, None), PipeAccessRights.FullControl, AccessControlType.Allow))
    #security.AddAccessRule(PipeAccessRule(SecurityIdentifier(WellKnownSidType.LocalSystemSid, None), PipeAccessRights.FullControl, AccessControlType.Allow))
  
        
    
    # Create a new access rule for anonymous users
    rule = PipeAccessRule('Everyone', PipeAccessRights.ReadWrite, AccessControlType.Allow)
    security.AddAccessRule(rule)
    
    #security.AddAccessRule(PipeAccessRule(SecurityIdentifier(WellKnownSidType.WorldSid, None), PipeAccessRights.ReadWrite, AccessControlType.Allow))
    #security.AddAccessRule(PipeAccessRule(SecurityIdentifier(WellKnownSidType.AuthenticatedUserSid, None), PipeAccessRights.CreateNewInstance | PipeAccessRights.ReadWrite, AccessControlType.Allow))

    #security.AddAccessRule(PipeAccessRule(SecurityIdentifier(WellKnownSidType.AnonymousSid, None), PipeAccessRights.FullControl, AccessControlType.Allow))
    #security.AddAccessRule(PipeAccessRule("Everyone", PipeAccessRights.ReadWrite, AccessControlType.Allow))
    #security.AddAccessRule(PipeAccessRule("Authenticated Users", PipeAccessRights.FullControl, AccessControlType.Allow))
    #security.AddAccessRule(PipeAccessRule("Users", PipeAccessRights.FullControl | PipeAccessRights.CreateNewInstance, AccessControlType.Allow))
    #security.AddAccessRule(PipeAccessRule(SecurityIdentifier(WellKnownSidType.AuthenticatedUserSid, None), PipeAccessRights.FullControl, AccessControlType.Allow))

    pipe_server = NamedPipeServerStream(pipe_name, PipeDirection.InOut, 100, PipeTransmissionMode.Message, 0, 4096, 4096, security)
    
    pipe_server.WaitForConnection()

    while True:
        # Receive data from the client
        pipe_reader = System.IO.StreamReader(pipe_server)
        received_data = pipe_reader.ReadLine()

        # Add the received data to the queue
        received_queue.Enqueue(received_data)

        # Send a response to the client
        pipe_writer = System.IO.StreamWriter(pipe_server)
        pipe_writer.WriteLine("Hello from the server!")
        pipe_writer.Flush()
        
        # Disconnect the client
        #pipe_server.Disconnect()


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

# Create and start the separate thread for the named pipe server
server_thread = KThread(target=server_thread_function)
server_thread.daemon = True
server_thread.start()

# Check the received queue for data
while True:
    if received_queue.Count > 0:
        # Print the received data
        print(received_queue.Peek())
        received_queue.Dequeue()

server_thread.kill()