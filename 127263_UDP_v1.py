import socket
import threading

completed_handshakes = {}

def listen_for_messages(listen_ip, listen_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((listen_ip, listen_port))
        print(f"Listening on {listen_ip}:{listen_port}...")
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            message = data.decode('utf-8')

            # Check if this client has completed the handshake
            if addr not in completed_handshakes or not completed_handshakes[addr]:
                if message == "INIT":
                    print(f"Received INIT from {addr}. Sending ACK.")
                    sock.sendto("ACK".encode('utf-8'), addr)
                    print(f"Sent ACK to {addr}.")
                elif message == "READY":
                    print(f"Handshake completed with {addr}. Communication can proceed.")
                    completed_handshakes[addr] = True
            else:
                print(f"Received message from {addr}: {message}")
    except Exception as e:
        print(f"Listener error: {e}")
    finally:
        sock.close()


def send_message(target_ip, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        while True:
            if (target_ip, target_port) not in completed_handshakes:
                user_input = input("Type 'INIT' to initiate handshake: ")
            else:
                user_input = input("Type a message to send: ")
            
            if user_input.lower() == 'init':
                print(f"Initiating handshake with {target_ip}:{target_port}...")
                
                # "INIT" to initiate handshake
                sock.sendto("INIT".encode('utf-8'), (target_ip, target_port))
                while True:
                    # Wait for "ACK" 
                    data, addr = sock.recvfrom(1024)
                    if data.decode('utf-8') == "ACK" and addr == (target_ip, target_port):
                        print(f"Received ACK from {addr}. Sending READY.")
                        # Send "READY" to complete the handshake
                        sock.sendto("READY".encode('utf-8'), (target_ip, target_port))
                        print("Handshake completed. You can now send messages.")
                        # Mark handshake as complete
                        completed_handshakes[addr] = True
                        break

            elif user_input:  # send message
                if completed_handshakes.get((target_ip, target_port), False):
                    sock.sendto(user_input.encode('utf-8'), (target_ip, target_port))
                    print(f"Sent message: {user_input}")
                else:
                    print("You must complete the handshake before sending messages.")

    except ConnectionResetError as e:
        print(f"Connection error: {e}. Retrying...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    # Input for listening port and sending port
    listen_port = int(input("Enter the port to listen on: "))
    target_port = int(input("Enter the port to send messages to: "))
    target_ip = input("Enter the IP address to send messages to: ")

    #local host
    #listen_ip = target_ip

    # Get the local IP address
    listen_ip = socket.gethostbyname(socket.gethostname())

    # Start the listening thread
    listen_thread = threading.Thread(target=listen_for_messages, args=(listen_ip, listen_port))
    listen_thread.daemon = True
    listen_thread.start()

    # Start sending messages
    send_message(target_ip, target_port)
