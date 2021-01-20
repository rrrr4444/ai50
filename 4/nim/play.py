from nim import train, play
import sys

if len(sys.argv) == 2:
    training_rounds = int(sys.argv[1])
else:
    training_rounds = 10000
ai = train(training_rounds)
play(ai)
