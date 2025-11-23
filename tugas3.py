import random

import numpy as np


# Default data dari kasus TSP lima kota
DEFAULT_CITIES = ['A', 'B', 'C', 'D', 'E']

DEFAULT_DIST_MATRIX = np.array([
    [0, 7, 5, 9, 9],
    [7, 0, 7, 2, 8],
    [5, 7, 0, 4, 3],
    [9, 2, 4, 0, 6],
    [9, 8, 3, 6, 0],
], dtype=float)

DEFAULT_POP_SIZE = 100
DEFAULT_GENERATIONS = 500
DEFAULT_TOURNAMENT_K = 5
DEFAULT_CROSSOVER_RATE = 0.9
DEFAULT_MUTATION_RATE = 0.2
DEFAULT_ELITE_SIZE = 1


def route_distance(route, dist_matrix):
    """Hitung jarak total dari rute TSP."""
    n = len(route)
    return sum(dist_matrix[route[i], route[(i + 1) % n]] for i in range(n))


def create_individual(n):
    ind = list(range(n))
    random.shuffle(ind)
    return ind


def initial_population(size, n):
    return [create_individual(n) for _ in range(size)]


def tournament_selection(population, dist_matrix, tournament_k):
    candidates = random.sample(population, tournament_k)
    return min(candidates, key=lambda ind: route_distance(ind, dist_matrix))


def ordered_crossover(parent1, parent2):
    a, b = sorted(random.sample(range(len(parent1)), 2))
    child = [-1] * len(parent1)
    child[a:b + 1] = parent1[a:b + 1]

    p2_idx = 0
    for i in range(len(parent1)):
        if child[i] != -1:
            continue
        while parent2[p2_idx] in child:
            p2_idx = (p2_idx + 1) % len(parent2)
        child[i] = parent2[p2_idx]
        p2_idx = (p2_idx + 1) % len(parent2)

    return child


def swap_mutation(individual):
    a, b = random.sample(range(len(individual)), 2)
    individual[a], individual[b] = individual[b], individual[a]
    return individual


def solve_tsp_ga(
    pop_size=DEFAULT_POP_SIZE,
    generations=DEFAULT_GENERATIONS,
    crossover_rate=DEFAULT_CROSSOVER_RATE,
    mutation_rate=DEFAULT_MUTATION_RATE,
    tournament_k=DEFAULT_TOURNAMENT_K,
    elite_size=DEFAULT_ELITE_SIZE,
    cities=None,
    dist_matrix=None,
    seed=None,
    verbose=False,
):
    """Jalankan algoritma genetika untuk TSP dan kembalikan ringkasan hasil."""

    cities = list(cities) if cities is not None else list(DEFAULT_CITIES)
    matrix = np.array(dist_matrix if dist_matrix is not None else DEFAULT_DIST_MATRIX, dtype=float)

    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError('Matriks jarak harus berbentuk bujur sangkar')

    if matrix.shape[0] != len(cities):
        raise ValueError('Jumlah kota harus sesuai dengan ukuran matriks jarak')

    if pop_size < 2:
        raise ValueError('Populasi minimal terdiri dari 2 individu')

    if tournament_k < 1 or tournament_k > pop_size:
        raise ValueError('tournament_k berada di rentang 1 hingga ukuran populasi')

    if elite_size < 0 or elite_size > pop_size:
        raise ValueError('elite_size berada di rentang 0 hingga ukuran populasi')

    if not 0 <= crossover_rate <= 1:
        raise ValueError('crossover_rate berada pada rentang 0-1')

    if not 0 <= mutation_rate <= 1:
        raise ValueError('mutation_rate berada pada rentang 0-1')

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    num_cities = len(cities)
    population = initial_population(pop_size, num_cities)

    best = min(population, key=lambda ind: route_distance(ind, matrix))
    best_distance = route_distance(best, matrix)

    history = []

    for generation in range(generations):
        population = sorted(population, key=lambda ind: route_distance(ind, matrix))

        current_best = population[0]
        current_distance = route_distance(current_best, matrix)

        if current_distance < best_distance:
            best = current_best[:]
            best_distance = current_distance

        if verbose and generation % 50 == 0:
            print(f'Gen {generation}: Best Distance = {best_distance:.4f}')

        history.append(
            {
                'generation': generation + 1,
                'distance': current_distance,
                'route_indices': current_best[:],
                'route': [cities[i] for i in current_best],
            }
        )

        new_population = population[:elite_size]

        while len(new_population) < pop_size:
            parent1 = tournament_selection(population, matrix, tournament_k)
            parent2 = tournament_selection(population, matrix, tournament_k)

            if random.random() < crossover_rate:
                child = ordered_crossover(parent1, parent2)
            else:
                child = parent1[:]

            if random.random() < mutation_rate:
                child = swap_mutation(child)

            new_population.append(child)

        population = new_population

    best_route = [cities[i] for i in best]

    return {
        'best_route': best_route,
        'best_distance': best_distance,
        'best_route_indices': best[:],
        'history': history,
        'cities': cities,
        'dist_matrix': matrix.tolist(),
        'params': {
            'pop_size': pop_size,
            'generations': generations,
            'crossover_rate': crossover_rate,
            'mutation_rate': mutation_rate,
            'tournament_k': tournament_k,
            'elite_size': elite_size,
            'seed': seed,
        },
    }


if __name__ == '__main__':
    result = solve_tsp_ga(verbose=True)
    route = ' -> '.join(result['best_route'] + [result['best_route'][0]])
    print('\nRute terbaik:', route)
    print('Jarak total:', result['best_distance'])