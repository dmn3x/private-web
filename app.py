import re

from flask import Flask, render_template, request

from tugas2 import DEFAULT_CAPACITY, DEFAULT_ITEMS, genetic_algorithm
from tugas3 import (
    DEFAULT_CITIES as TSP_DEFAULT_CITIES,
    DEFAULT_DIST_MATRIX as TSP_DISTANCE_MATRIX,
    DEFAULT_CROSSOVER_RATE as TSP_DEFAULT_CROSSOVER,
    DEFAULT_ELITE_SIZE as TSP_DEFAULT_ELITE,
    DEFAULT_GENERATIONS as TSP_DEFAULT_GENERATIONS,
    DEFAULT_MUTATION_RATE as TSP_DEFAULT_MUTATION,
    DEFAULT_POP_SIZE as TSP_DEFAULT_POP,
    DEFAULT_TOURNAMENT_K as TSP_DEFAULT_TOURNAMENT,
    solve_tsp_ga,
)
from tugas4 import anfis

ITEMS_HELP_TEXT = (
    "Masukkan satu item per baris dengan format: Nama, Berat, Nilai. "
    "Gunakan koma sebagai pemisah dan titik untuk angka desimal."
)
ITEMS_PLACEHOLDER = "Laptop, 2.5, 500\nMouse, 0.1, 40\nTas, 1.5, 150"

app = Flask(__name__)


def _items_dict_to_text(items):
    """Ubah dict item menjadi teks siap diedit di form."""
    return "\n".join(f"{name},{data['weight']},{data['value']}" for name, data in items.items())


def _parse_items(raw_text):
    """Konversi teks form menjadi dict item."""
    items = {}
    for idx, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(',')]
        if len(parts) != 3:
            raise ValueError(f"Format baris {idx} harus 'Nama, berat, nilai'")
        name, weight, value = parts
        if not name:
            name = f"Item{idx}"
        try:
            weight = float(weight)
            value = float(value)
        except ValueError as exc:
            raise ValueError(f"Berat dan nilai harus angka pada baris {idx}") from exc
        items[name] = {"weight": weight, "value": value}

    if not items:
        raise ValueError("Minimal ada satu item untuk dihitung")

    return items


def _cities_to_text(cities):
    return "\n".join(cities)


def _matrix_to_text(matrix):
    def _format_cell(value):
        value = float(value)
        if value.is_integer():
            return str(int(value))
        return (f"{value:.2f}").rstrip('0').rstrip('.')

    rows = []
    for row in matrix:
        row_list = list(row)
        rows.append(" ".join(_format_cell(cell) for cell in row_list))
    return "\n".join(rows)


def _parse_cities(raw_text):
    names = []
    for line in raw_text.splitlines():
        segments = [segment.strip() for segment in line.split(',') if segment.strip()]
        names.extend(segments)

    if not names:
        raise ValueError('Daftar kota tidak boleh kosong')

    return names


def _parse_distance_matrix(raw_text, expected_size):
    rows = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if len(rows) != expected_size:
        raise ValueError('Jumlah baris matriks jarak harus sama dengan jumlah kota')

    matrix = []
    for r_idx, row_text in enumerate(rows, start=1):
        tokens = [token for token in re.split(r'[\s,;]+', row_text) if token]
        if len(tokens) != expected_size:
            raise ValueError(f'Baris {r_idx} matriks harus memiliki {expected_size} nilai')
        values = []
        for c_idx, token in enumerate(tokens, start=1):
            try:
                value = float(token)
            except ValueError as exc:
                raise ValueError(f'Nilai matriks pada baris {r_idx}, kolom {c_idx} harus berupa angka') from exc
            if value < 0:
                raise ValueError('Jarak tidak boleh negatif')
            values.append(value)
        matrix.append(values)

    return matrix

# Route Home - Halaman utama Tugas 1 dengan empat kartu materi
@app.route('/')
def home():
    return render_template('index.html', title="Soft Computing", active_page="home")


@app.route('/tugas1')
def tugas1():
    return render_template('tugas1.html', title="Pengenalan Soft Computing", active_page="tugas1")


@app.route('/tugas2', methods=['GET', 'POST'])
def tugas2_view():
    default_items_text = _items_dict_to_text(DEFAULT_ITEMS)
    elitism_default = 'on' if request.method == 'GET' else 'off'

    form_state = {
        "items_text": request.form.get('items', default_items_text) or default_items_text,
        "capacity": request.form.get('capacity', str(DEFAULT_CAPACITY)),
        "pop_size": request.form.get('pop_size', '10'),
        "generations": request.form.get('generations', '10'),
        "crossover_rate": request.form.get('crossover_rate', '0.8'),
        "mutation_rate": request.form.get('mutation_rate', '0.1'),
        "elitism": request.form.get('elitism', elitism_default),
    }

    result = None
    error = None
    error_field = None

    if request.method == 'POST':
        try:
            items = _parse_items(form_state['items_text'])
        except ValueError as exc:
            error = str(exc)
            error_field = 'items'

        if not error:
            try:
                capacity = float(form_state['capacity'])
                if capacity <= 0:
                    raise ValueError('Kapasitas harus lebih besar dari 0')

                pop_size = int(form_state['pop_size'])
                generations = int(form_state['generations'])
                crossover_rate = float(form_state['crossover_rate'])
                mutation_rate = float(form_state['mutation_rate'])
                elitism = form_state['elitism'] == 'on'

                if pop_size < 2:
                    raise ValueError('Populasi minimal 2 kromosom')
                if generations < 1:
                    raise ValueError('Generasi minimal 1')
                if not 0 <= crossover_rate <= 1:
                    raise ValueError('Crossover rate berada pada rentang 0-1')
                if not 0 <= mutation_rate <= 1:
                    raise ValueError('Mutation rate berada pada rentang 0-1')
            except ValueError as exc:
                error = str(exc)

        if not error:
            result = genetic_algorithm(
                pop_size=pop_size,
                generations=generations,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                elitism=elitism,
                items=items,
                capacity=capacity,
            )

    return render_template(
        'tugas2.html',
        title="Tugas 2",
        active_page="tugas2",
        form_state=form_state,
        result=result,
        error=error,
        error_field=error_field,
        items_help_text=ITEMS_HELP_TEXT,
    )


@app.route('/tugas3', methods=['GET', 'POST'])
def tugas3_view():
    default_city_text = _cities_to_text(TSP_DEFAULT_CITIES)
    default_matrix_text = _matrix_to_text(TSP_DISTANCE_MATRIX)

    form_state = {
        'pop_size': request.form.get('pop_size', str(TSP_DEFAULT_POP)),
        'generations': request.form.get('generations', str(TSP_DEFAULT_GENERATIONS)),
        'crossover_rate': request.form.get('crossover_rate', str(TSP_DEFAULT_CROSSOVER)),
        'mutation_rate': request.form.get('mutation_rate', str(TSP_DEFAULT_MUTATION)),
        'tournament_k': request.form.get('tournament_k', str(TSP_DEFAULT_TOURNAMENT)),
        'elite_size': request.form.get('elite_size', str(TSP_DEFAULT_ELITE)),
        'seed': request.form.get('seed', ''),
        'city_text': request.form.get('cities', default_city_text) or default_city_text,
        'matrix_text': request.form.get('matrix', default_matrix_text) or default_matrix_text,
    }

    error = None
    result = None
    current_cities = list(TSP_DEFAULT_CITIES)
    current_matrix = TSP_DISTANCE_MATRIX.tolist()

    if request.method == 'POST':
        try:
            pop_size = int(form_state['pop_size'])
            generations = int(form_state['generations'])
            tournament_k = int(form_state['tournament_k'])
            elite_size = int(form_state['elite_size'])
            crossover_rate = float(form_state['crossover_rate'])
            mutation_rate = float(form_state['mutation_rate'])

            seed_text = form_state['seed'].strip()
            seed = int(seed_text) if seed_text else None

            cities = _parse_cities(form_state['city_text'])
            matrix = _parse_distance_matrix(form_state['matrix_text'], len(cities))

            current_cities = cities
            current_matrix = matrix

            result = solve_tsp_ga(
                pop_size=pop_size,
                generations=generations,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                tournament_k=tournament_k,
                elite_size=elite_size,
                cities=cities,
                dist_matrix=matrix,
                seed=seed,
            )
        except ValueError as exc:
            error = str(exc)
        except Exception as exc:
            error = f'Gagal menjalankan algoritma: {exc}'

    return render_template(
        'tugas3.html',
        title="Tugas 3",
        active_page="tugas3",
        form_state=form_state,
        error=error,
        result=result,
        cities=current_cities,
        dist_matrix=current_matrix,
        distance_rows=list(zip(current_cities, current_matrix)),
    )


@app.route('/tugas4', methods=['GET', 'POST'])
def tugas4_view():
    form_state = {
        'x': request.form.get('x', '3'),
        'y': request.form.get('y', '4'),
    }

    result = None
    error = None

    if request.method == 'POST':
        try:
            x = float(form_state['x'])
            y = float(form_state['y'])

            result = anfis(x, y)
            result['x'] = x
            result['y'] = y
        except ValueError as exc:
            error = f'Input harus berupa angka: {exc}'
        except Exception as exc:
            error = f'Gagal menjalankan ANFIS: {exc}'

    return render_template(
        'tugas4.html',
        title="Tugas 4",
        active_page="tugas4",
        form_state=form_state,
        result=result,
        error=error,
    )

# Menjalankan aplikasi Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
