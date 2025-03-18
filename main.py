import argparse




def main():
    parser = argparse.ArgumentParser(description="Simple Snake Game in Python")
    parser.add_argument("--history", help="Displays the history of Snake Game", action="store_true")


    args = parser.parse_args()
    if args.history:
        print("History of the Snake Game:\n"
              "The Snake genre began with the 1976 arcade video game Blockade developed and published by Gremlin Industries.\n"
              "The first home computer version 'Worm' was programmed by Peter Trefonas for the TRS-80 and published in 1978.\n"
              "Fun Fact: The Snake on IBM PC was rendered in a text mode!")

if __name__ == '__main__':
    main()

