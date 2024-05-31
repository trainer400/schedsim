import pandas as pd
import matplotlib.pyplot as plt

def create_graph(output_image):
    # Leggi i dati dal file CSV
    input_csv = 'input/out.csv'
    df = pd.read_csv(input_csv, header=None, names=['time', 'task_id', 'job', 'processor', 'type', 'extra'], delimiter=',')

    # Rimuovi eventuali righe con valori NaN
    df.dropna(inplace=True)

    # Converti le colonne in interi, gestendo le eccezioni
    try:
        df['time'] = pd.to_numeric(df['time'], errors='coerce').fillna(0).astype(int)
        df['task_id'] = pd.to_numeric(df['task_id'], errors='coerce').fillna(0).astype(int)
        df['job'] = pd.to_numeric(df['job'], errors='coerce').fillna(0).astype(int)
    except ValueError as e:
        print("Errore di conversione:", e)
        print("Valori non convertibili:")
        for column in ['time', 'task_id', 'job']:
            non_convertible_values = df[pd.to_numeric(df[column], errors='coerce').isnull()][column]
            print(f"{column}: {non_convertible_values}")
    # Rimuovi eventuali righe con valori NaN
    df.dropna(inplace=True)

    # Converti le colonne in interi, ignorando i valori non convertibili
    df['time'] = pd.to_numeric(df['time'], errors='coerce').fillna(0).astype(int)
    df['task_id'] = pd.to_numeric(df['task_id'], errors='coerce').fillna(0).astype(int)
    df['job'] = pd.to_numeric(df['job'], errors='coerce').fillna(0).astype(int)
    
    # Configura il grafico
    fig, ax = plt.subplots(figsize=(12, 8))  # Aumenta la dimensione della figura per maggiore chiarezza

    # Dizionario per tenere traccia dei task attivi
    active_tasks = {}

    # Disegna le barre orizzontali
    for index, row in df.iterrows():
        time = row['time']
        task_id = row['task_id']
        job = row['job']
        event_type = row['type']

        if event_type == 'A':
            # Arrival: la task arriva nel sistema
            active_tasks[(task_id, job)] = {'arrival': time}
        elif event_type == 'S':
            # Start: la task inizia l'esecuzione
            if (task_id, job) in active_tasks:
                active_tasks[(task_id, job)]['start'] = time
        elif event_type == 'F':
            # Finish: la task termina l'esecuzione
            if (task_id, job) in active_tasks:
                start_time = active_tasks[(task_id, job)]['start']
                duration = time - start_time
                label = f'Task {task_id}'
                ax.broken_barh([(start_time, duration)], (task_id - 0.4, 0.8), facecolors='tab:blue')
                ax.text(start_time + duration / 2, task_id, label, ha='center', va='center', color='white', fontsize=8)
                del active_tasks[(task_id, job)]

    # Configura gli assi
    ax.set_xlabel('Time')
    ax.set_ylabel('Task ID')

    # Imposta una scala più fine per l'asse delle x
    min_time = df['time'].min()
    max_time = df['time'].max()
    ax.set_xticks(range(min_time, max_time + 1, 5))  # Scala di 5 unità

    ax.set_yticks(df['task_id'].unique())
    ax.set_yticklabels([f'Task {task_id}' for task_id in df['task_id'].unique()])
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Salva il grafico
    plt.savefig(output_image)

    # Chiudi la figura per liberare la memoria
    plt.close()