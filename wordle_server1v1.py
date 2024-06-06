# server.py
import socket
import threading
import json
import time
import csv
import random
import echo_protocol1v1 as echo

IP = '127.0.0.1'

connections = []
addrs = []
attempts = {}
names = {}
finish = 0

def load_words(file_path):
    words = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            words.append(row[0])
        return words

def choose_word(words):
    return random.choice(words)

def create_report(expected, actual):
    report = ["none" for _ in range(len(expected))]
    for i in range(len(expected)):
        if expected[i] == actual[i]:
            report[i] = "green"
        elif actual[i] in expected:
            report[i] = "yellow"
    return report

def create_bad_guess_msg(player_name):
    return json.dumps({'type': 'bad_guess', 'player': player_name})

def create_guessed_msg(player_name, expected, actual):
    return json.dumps({'type': 'guessed', 'value': create_report(expected, actual), 'player': player_name})

def create_report_msg(player_name, expected, actual):
    return json.dumps({'type': 'report', 'value': create_report(expected, actual), 'player': player_name})

def create_out_of_guesses_msg(player_name, expected, actual):
    return json.dumps({'type': 'out_of_guesses', 'value': create_report(expected, actual), 'player': player_name})

def create_you_won_msg():
    return json.dumps({'type': 'you_won'})

def create_you_lost_msg(other_player_name, other_player_guesses):
    return json.dumps({'type': 'you_lost', 'other_player': other_player_name, 'other_player_guesses': other_player_guesses})

def handle_client(client_socket, client_address):
    global attempts, finish, names
    print(f"Thread for handling client: {client_address}")
    sock_wrapper = echo.SocketWrapper(client_socket)

    guesses = 0
    max_guesses = 6
    sock_wrapper.send_msg(str(word_length))
    name = sock_wrapper.recv_msg()
    names[client_socket] = name

    while True:
        msg = sock_wrapper.recv_msg()
        guesses += 1
        if not msg:
            print("Unexpected game exit.")
            break

        if len(msg) != len(chosen_word):
            bad_guess = create_bad_guess_msg(name)
            print(f'sending {bad_guess}')
            sock_wrapper.send_msg(bad_guess)
        elif msg == chosen_word:
            finish = 1
            guessed = create_guessed_msg(name, chosen_word, msg)
            print(f'sending {guessed}')
            sock_wrapper.send_msg(guessed)
            attempts[client_socket] = guesses
            break
        elif guesses == max_guesses:
            out_of_guesses = create_out_of_guesses_msg(name, chosen_word, msg)
            print(f'sending {out_of_guesses}')
            sock_wrapper.send_msg(out_of_guesses)
            attempts[client_socket] = guesses
            break
        else:
            report = create_report_msg(name, chosen_word, msg)
            print(f'sending {report}')
            sock_wrapper.send_msg(report)

    while len(attempts) != 2:
        time.sleep(1)

    other_client_socket = [sock for sock in attempts.keys() if sock != client_socket][0]
    other_player_name = names[other_client_socket]
    other_player_guesses = attempts[other_client_socket]

    if attempts[client_socket] <= other_player_guesses:
        sock_wrapper.send_msg(create_you_won_msg())
    else:
        sock_wrapper.send_msg(create_you_lost_msg(other_player_name, other_player_guesses))

    print(f"Done with client {client_address}")

def waiting_for_connection():
    global connections, addrs
    while len(connections) < 2:
        conn, addr = sock.accept()
        connections.append(conn)
        addrs.append(addr)
        print(f"Accepted new client connection: {addr}")
        th = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        th.start()

if __name__ == "__main__":
    print("Welcome to Wordle Server!")
    print("Ready to accept a client connection.")
    words = load_words("words.csv")
    chosen_word = choose_word(words)
    word_length = len(chosen_word)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((IP, echo.PORT))
    sock.listen()
    while True:
        waiting_for_connection()
