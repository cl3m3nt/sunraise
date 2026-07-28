import itertools
from time import sleep


def get_waiting():
    print("Waiting", end="", flush=True)

    for _ in range(5):
        sleep(1)
        print(".", end="", flush=True)

    print()


def get_infinite_waiting():

    for dots in itertools.cycle([".", "..", "..."]):
        print(f"\rWaiting{dots}", end="", flush=True)
        sleep(0.5)
