from neat import Population
import io
from contextlib import redirect_stdout
class CompleteExtinctionException(Exception):
    pass
from flask_socketio import SocketIO
from flask import request
import sys
sys.path.append('./util')
from util import StringDataEmitter         

EVENT_NAME = "stdout"

class ReportingPopulation(Population):
    def __init__(self, config, socket : SocketIO, graphics = True):
        super().__init__(config)
        self.socket = socket
        self.graphics = graphics
    def run(self, fitness_function,n=None):
        """
        Runs NEAT's genetic algorithm for at most n generations.  If n
        is None, run until solution is found or extinction occurs.

        The user-provided fitness_function must take only two arguments:
            1. The population as a list of (genome id, genome) tuples.
            2. The current configuration object.

        The return value of the fitness function is ignored, but it must assign
        a Python float to the `fitness` member of each genome.

        The fitness function is free to maintain external state, perform
        evaluations in parallel, etc.

        It is assumed that fitness_function does not modify the list of genomes,
        the genomes themselves (apart from updating the fitness member),
        or the configuration object.
        """
        socket = self.socket
        if self.config.no_fitness_termination and (n is None):
            raise RuntimeError("Cannot have no generational limit with no fitness termination")

        k = 0

        emitter = StringDataEmitter(EVENT_NAME)
        while n is None or k < n:

            def run_loop(k):
                k += 1

                self.reporters.start_generation(self.generation)

                # Evaluate all genomes using the user-provided function.
                fitness_function(list(self.population.items()), self.config)

                # Gather and report statistics.
                best = None
                for g in self.population.values():
                    if g.fitness is None:
                        raise RuntimeError("Fitness not assigned to genome {}".format(g.key))

                    if best is None or g.fitness > best.fitness:
                        best = g
                self.reporters.post_evaluate(self.config, self.population, self.species, best)

                # Track the best genome ever seen.
                if self.best_genome is None or best.fitness > self.best_genome.fitness:
                    self.best_genome = best

                if not self.config.no_fitness_termination:
                    # End if the fitness threshold is reached.
                    fv = self.fitness_criterion(g.fitness for g in self.population.values())
                    if fv >= self.config.fitness_threshold:
                        self.reporters.found_solution(self.config, self.generation, best)
                        return None

                # Create the next generation from the current generation.
                self.population = self.reproduction.reproduce(self.config, self.species,
                                                              self.config.pop_size, self.generation)

                # Check for complete extinction.
                if not self.species.species:
                    self.reporters.complete_extinction()

                    # If requested by the user, create a completely new population,
                    # otherwise raise an exception.
                    if self.config.reset_on_extinction:
                        self.population = self.reproduction.create_new(self.config.genome_type,
                                                                       self.config.genome_config,
                                                                       self.config.pop_size)
                    else:
                        raise CompleteExtinctionException()

                # Divide the new population into species.
                self.species.speciate(self.config, self.population, self.generation)

                self.reporters.end_generation(self.config, self.population, self.species)

                self.generation += 1
                return k

            f = io.StringIO()

   
            if not self.graphics:
                with redirect_stdout(f):
                    k = run_loop(k)

                    
                    if k is None:
                        break
                    
                print(f"Generation {k} finished, EMTTING TO STDOUT")

                emitter.update_text(f.getvalue())
                emitter.emit_data(socket)# give screen data to client

            else:
                k = run_loop(k)
                if k is None:
                        break
                
            

            #print(f.getvalue(), len(f.getvalue()))

        if self.config.no_fitness_termination:
            self.reporters.found_solution(self.config, self.generation, self.best_genome)

        return self.best_genome