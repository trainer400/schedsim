import pandas as pd
import matplotlib.pyplot as plt
import os

def create_graph(output_image, start_time=None, end_time=None):
    try:
        # Leggi i dati dal file CSV
        input_csv = 'input/out.csv'

        # Verifica se il file out.csv esiste e ha dimensione maggiore di 0
        if os.path.isfile(input_csv) and os.path.getsize(input_csv) > 0:
            df = pd.read_csv(input_csv, header=None, names=['time', 'task_id', 'job', 'processor', 'type', 'extra'], delimiter=',')

            # Rimuovi eventuali righe con valori NaN
            df.dropna(inplace=True)

            # Filtra i dati in base all'intervallo di tempo specificato
            if start_time is not None:
                df = df[df['time'] >= start_time]
            if end_time is not None:
                df = df[df['time'] <= end_time]

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
            
            # Crea una mappatura tra gli ID delle task e le loro posizioni relative
            task_positions = {}
            unique_task_ids = df['task_id'].unique()
            for idx, task_id in enumerate(sorted(unique_task_ids)):
                task_positions[task_id] = idx + 1  # Aggiungi 1 per evitare posizioni di partenza da zero

            # Configura il grafico
            fig, ax = plt.subplots(figsize=(20, 14))  # Aumenta la dimensione della figura

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
                        ax.broken_barh([(start_time, duration)], (task_positions[task_id] - 0.2, 0.4), facecolors='tab:blue')
                        ax.text(start_time + duration / 2, task_positions[task_id], label, ha='center', va='center', color='white', fontsize=8)
                        del active_tasks[(task_id, job)]

            # Configura gli assi
            ax.set_xlabel('Time')
            ax.set_ylabel('Task ID')

            # Imposta una scala più fine per l'asse delle x
            min_time = df['time'].min()
            max_time = df['time'].max()
            ax.set_xticks(range(min_time, max_time + 1, 5))  # Scala di 5 unità

            # Imposta la griglia più fitta sull'asse y
            ax.set_yticks(range(1, len(unique_task_ids) + 1))
            ax.set_yticklabels([f'Task {task_id}' for task_id in sorted(unique_task_ids)])

            ax.grid(True, which='both', linestyle='--', linewidth=0.5)

            # Salva il grafico
            plt.savefig(output_image)

            # Chiudi la figura per liberare la memoria
            plt.close()

        else:
            # Crea una nuova figura
            plt.figure(figsize=(30, 10))  # Imposta le dimensioni della figura

            # Disegna un grafico vuoto con un asse x da 0 a 100 e un asse y senza valori
            plt.plot([], [])  # Crea un grafico vuoto
            plt.xlabel('Time')  # Etichetta dell'asse x
            plt.ylabel('Task ID')  # Etichetta dell'asse y
            plt.xticks(range(0, 101, 5))  # Imposta i tick sull'asse x da 0 a 100 con passo 5
            plt.yticks([])  # Rimuove i valori dall'asse y
            plt.grid(True, linestyle='--', linewidth=0.5)  # Aggiungi una griglia con linee tratteggiate

            # Salva il grafico vuoto
            plt.savefig(output_image)

    except Exception as e:
        print(f"Errore durante la creazione del grafico: {str(e)}")
