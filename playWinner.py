from game import replay_genome


config_path = "./config-feedforward.txt"

print("Enter a Tick rate(speed in fps - 250 is average ):")
ticks = input()



replay_genome(config_path , ticks = int(ticks))
