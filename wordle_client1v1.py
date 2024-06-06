# client.py
import socket
import json
import colorama

import echo_protocol1v1 as echo

IP = '127.0.0.1'
PROMPT = 'Guess: '

def print_report(word, report):
    print(" " * len(PROMPT), end="")
    for i in range(len(report)):
        if report[i] == 'green':
            print(f'{colorama.Fore.GREEN}{word[i]}{colorama.Style.RESET_ALL}', end="")
        elif report[i] == 'yellow':
            print(f'{colorama.Fore.YELLOW}{word[i]}{colorama.Style.RESET_ALL}', end="")
        else:
            print(f'{word[i]}', end="")
    print()


if __name__ == "__main__":
    colorama.init()

    name = input("Enter your name: ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, echo.PORT))

    socket_wrapper = echo.SocketWrapper(sock)

    socket_wrapper.send_msg(name)

    word_length = int(socket_wrapper.recv_msg())

    print("Welcome to Wordle!")
    nr_ = '_' * word_length
    print(f"{PROMPT}{nr_}")

    while True:
        guess = input(PROMPT)
        socket_wrapper.send_msg(guess)
        rcvd = socket_wrapper.recv_msg()
        if not rcvd:
            print("Unexpected end of connection, server is down")
            break
        rcvd_deserialized = json.loads(rcvd)
        msg_type = rcvd_deserialized['type']
        player_name = rcvd_deserialized.get('player')


        if msg_type == 'guessed':
            print_report(guess, rcvd_deserialized['value'])
            print("Well Done! You have guessed the word")
            while True:
                rcvd = socket_wrapper.recv_msg()
                rcvd_deserialized = json.loads(rcvd)
                msg_type = rcvd_deserialized['type']
                if msg_type == 'you_won':
                    print("Congrats, you won!")
                    break
                if msg_type == 'you_lost':
                    other_player = rcvd_deserialized['other_player']
                    other_player_guesses = rcvd_deserialized['other_player_guesses']
                    print(f"Better luck next time. {other_player} guessed the word in {other_player_guesses} guesses.")
                    break
            break
        if msg_type == 'out_of_guesses':
            print_report(guess, rcvd_deserialized['value'])
            print("Out of guesses, the game will end")
            break
        if msg_type == 'bad_guess':
            print('Bad guess, try again')

        if msg_type == 'report':
            print_report(guess, rcvd_deserialized['value'])
        if msg_type == 'you_won':
            print("Congrats, you won!")
            break
        if msg_type == 'you_lost':
            other_player = rcvd_deserialized['other_player']
            other_player_guesses = rcvd_deserialized['other_player_guesses']
            print(f"Better luck next time. {other_player} guessed the word in {other_player_guesses} guesses.")
            break
    print("Thanks for playing.")
