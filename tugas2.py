import random

# 1. Data Masalah Knapsack
# -----------------------------
DEFAULT_ITEMS = {
    'Laptop': {'weight': 2.5, 'value': 500},
    'Mouse': {'weight': 0.1, 'value': 40},
    'Keyboard': {'weight': 0.8, 'value': 120},
    'Monitor': {'weight': 3.2, 'value': 350},
    'Charger': {'weight': 0.5, 'value': 80},
}

DEFAULT_CAPACITY = 15

# 2. Fungsi bantu
# -----------------------------
def decode(chromosome, items, item_list):
    """Kembalikan list item, total berat, total nilai"""
    total_weight = 0
    total_value = 0
    chosen_items = []
    for gene, name in zip(chromosome, item_list):
        if gene == 1:
            total_weight += items[name]['weight']
            total_value += items[name]['value']
            chosen_items.append(name)
    return chosen_items, total_weight, total_value

def fitness(chromosome, items, item_list, capacity):
    """Fungsi fitness dengan penalti berat"""
    _, total_weight, total_value = decode(chromosome, items, item_list)
    if total_weight <= capacity:
        return total_value
    else:
        # Penalti berat berlebih (bisa diganti dengan 0 atau pengurangan)
        return 0

def roulette_selection(population, fitnesses):
    """Seleksi roulette wheel"""
    total_fit = sum(fitnesses)
    
    # Jika fitness nol, pilih acak
    if total_fit == 0:
        return random.choice(population)
    
    pick = random.uniform(0, total_fit)
    current = 0
    for chrom, fit in zip(population, fitnesses):
        current += fit
        if current >= pick:
            return chrom

def crossover(p1, p2):
    """Single-point crossover"""
    if len(p1) != len(p2):
        raise ValueError("Parent length mismatch")

    point = random.randint(1, len(p1) - 1)
    child1 = p1[:point] + p2[point:]
    child2 = p2[:point] + p1[point:]
    return child1, child2

def mutate(chromosome, mutation_rate=0.1):
    """Flip bit dengan probabilitas mutation_rate"""
    return [1 - g if random.random() < mutation_rate else g for g in chromosome]

# 3. Algoritma Genetika Utama
# -----------------------------
def genetic_algorithm(
    pop_size=10,
    generations=10,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elitism=True,
    items=None,
    capacity=None,
    seed=None,
    verbose=False,
):
    """Jalankan algoritma genetika dan kembalikan ringkasan hasil."""

    items = items or DEFAULT_ITEMS
    capacity = capacity if capacity is not None else DEFAULT_CAPACITY
    item_list = list(items.keys())

    if not item_list:
        raise ValueError("Daftar item tidak boleh kosong")

    if seed is not None:
        random.seed(seed)

    n_items = len(item_list)
    # Inisialisasi populasi acak
    population = [[random.randint(0, 1) for _ in range(n_items)] for _ in range(pop_size)]

    history = []

    for gen in range(generations):
        # Hitung fitness
        fitnesses = [fitness(ch, items, item_list, capacity) for ch in population]

        # Catat individu terbaik
        best_index = fitnesses.index(max(fitnesses))
        best_chrom = population[best_index]
        best_fit = fitnesses[best_index]
        best_items, w, v = decode(best_chrom, items, item_list)

        history.append(
            {
                "generation": gen + 1,
                "chromosome": best_chrom[:],
                "items": best_items,
                "weight": w,
                "value": v,
                "fitness": best_fit,
            }
        )

        if verbose:
            print(f'Generasi {gen+1}:')
            print(f'Terbaik: {best_chrom} | Item: {best_items} | Berat: {w} | Nilai: {v} | Fitness: {best_fit}')
            print("-" * 65)

        # Buat generasi baru
        new_population = []

        # Elitism: pertahankan individu terbaik
        if elitism:
            new_population.append(best_chrom)

        # Reproduksi
        while len(new_population) < pop_size:
            # Seleksi orang tua
            parent1 = roulette_selection(population, fitnesses)
            parent2 = roulette_selection(population, fitnesses)

            # Crossover
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1[:], parent2[:]

            # Mutasi
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)

            # Tambah ke populasi baru
            new_population.extend([child1, child2])

        # Batasi ukuran populasi
        population = new_population[:pop_size]

    # Ambil hasil akhir
    fitnesses = [fitness(ch, items, item_list, capacity) for ch in population]
    best_index = fitnesses.index(max(fitnesses))
    best_chrom = population[best_index]
    best_items, w, v = decode(best_chrom, items, item_list)
    best_fit = fitnesses[best_index]
    summary = {
        "best_chromosome": best_chrom[:],
        "best_items": best_items,
        "best_weight": w,
        "best_value": v,
        "best_fitness": best_fit,
        "history": history,
        "items": items,
        "capacity": capacity,
    }

    if verbose:
        print(f"\n{'=' * 20} HASIL AKHIR {'=' * 20}")
        print(f'Kromosom terbaik: {best_chrom}')
        print(f'Item terpilih: {best_items}')
        print(f'Total berat: {w} kg')
        print(f'Total nilai: ${v}')
        print(f'Fitness akhir: {best_fit}')
        print('=' * 50)

    return summary


# 4. Jalankan Program
# -----------------------------
if __name__ == '__main__':
    genetic_algorithm(
        pop_size=8,
        generations=8,
        crossover_rate=0.8,
        mutation_rate=0.1,
        seed=42,
        verbose=True,
    )