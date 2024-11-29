import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import os


def create_graph(output_image, start_time, end_time, fraction, plot_graph=False):
    try:
        # Convert (start_time, end_time, fraction) to integers
        if start_time is not None:
            start_time = int(start_time)
        if end_time is not None:
            end_time = int(end_time)
        if fraction is not None:
            fraction = int(fraction)

        # Get the temporary directory path and path to temporany CSV file
        temp_dir = tempfile.gettempdir()
        input_csv = os.path.join(temp_dir, 'out.csv')

        # Check if the "out.csv" file exists and is not empty
        if os.path.isfile(input_csv) and os.path.getsize(input_csv) > 0:

            df = pd.read_csv(input_csv, header=0, names=[
                             'time', 'task_id', 'job', 'processor', 'type', 'extra'], delimiter=',')

            # Remove any rows with NaN values, or occur error
            df.dropna(inplace=True)

            # Convert columns to integers, handling exceptions to avoid cast errors
            df['time'] = pd.to_numeric(
                df['time'], errors='coerce').fillna(0).astype(int)
            df['task_id'] = pd.to_numeric(
                df['task_id'], errors='coerce').fillna(0).astype(int)
            df['job'] = pd.to_numeric(
                df['job'], errors='coerce').fillna(0).astype(int)

            # Filter data based on start_time and end_time
            df = df[(df['time'] >= start_time) & (df['time'] <= end_time)]

            # Create a mapping between task IDs and their relative positions
            task_positions = {}
            unique_task_ids = df['task_id'].unique()
            for idx, task_id in enumerate(sorted(unique_task_ids)):
                # Add 1 to avoid starting positions from zero
                task_positions[task_id] = idx + 1

            fig, ax = plt.subplots(figsize=(20, 14))
            active_tasks = {}

            # Draw horizontal bars (divided by type)
            for index, row in df.iterrows():
                time = row['time']
                task_id = row['task_id']
                job = row['job']
                event_type = row['type']

                if event_type == 'F':
                    # FINISH: task finishes execution
                    if (task_id, job) in active_tasks and 'start' in active_tasks[(task_id, job)]:
                        start_time_exec = active_tasks[(task_id, job)]['start']
                        duration = time - start_time_exec
                        label = f'Task {task_id}'
                        ax.broken_barh([(start_time_exec, duration)], (
                            task_positions[task_id] - 0.2, 0.4), facecolors='tab:green', alpha=0.75)
                        ax.text(start_time_exec + duration / 2,
                                task_positions[task_id], label, ha='center', va='center', color='white', fontsize=8)
                        del active_tasks[(task_id, job)]

                    ax.broken_barh(
                        [(time, 0.1)], (task_positions[task_id] - 0.2, 0.4), facecolors='tab:blue')

                elif event_type == 'A':
                    # ARRIVAL: task arrives in the system
                    active_tasks[(task_id, job)] = {'arrival': time}

                    if (task_id, job) in active_tasks and 'start' in active_tasks[(task_id, job)] and active_tasks[(task_id, job)]['start'] == time:
                        start_time_exec = active_tasks[(task_id, job)]['start']
                        duration = time - start_time_exec
                        label = f'Task {task_id}'
                        ax.broken_barh(
                            [(start_time_exec, duration)], (task_positions[task_id] - 0.2, 0.4), facecolors='tab:green')
                        ax.text(start_time_exec + duration / 2,
                                task_positions[task_id], label, ha='center', va='center', color='white', fontsize=8)
                        ax.broken_barh(
                            [(time, 0.1)], (task_positions[task_id] - 0.2, 0.4), facecolors='tab:red')
                    else:
                        ax.broken_barh(
                            [(time, 0.1)], (task_positions[task_id] - 0.2, 0.4), facecolors='tab:red')

                elif event_type == 'S':
                    # START: task starts execution
                    if (task_id, job) in active_tasks:
                        active_tasks[(task_id, job)]['start'] = time
                    else:
                        active_tasks[(task_id, job)] = {'start': time}

                elif event_type == 'D':
                    # DEADLINE: add a narrow orange block
                    ax.broken_barh(
                        [(time, 0.1)], (task_positions[task_id] - 0.2, 0.4), facecolors='tab:orange')

            # Configure the axes
            ax.set_xlabel('Time')
            ax.set_ylabel('Task ID')

            # Set a finer scale for the x-axis and define the limits
            ax.set_xticks(range(start_time, end_time + 1, fraction))
            ax.set_xlim(start_time-1, end_time+1)
            plt.xticks(rotation=90)
            ax.set_yticks(range(1, len(unique_task_ids) + 1))
            ax.set_yticklabels(
                [f'Task {task_id}' for task_id in sorted(unique_task_ids)])
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)

            # Define the legend
            legend_labels = [
                'Red: Arrival',
                'Blue: End',
                'Green: Execution',
                'Orange: Deadline'
            ]
            legend_colors = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange']
            handles = [plt.Line2D([0], [0], color=color, lw=4)
                       for color in legend_colors]
            ax.legend(handles, legend_labels, loc='lower center',
                      bbox_to_anchor=(0.5, -0.1), ncol=4)

            if plot_graph:
                plt.show()
            else:
                # Save the graph
                plt.savefig(output_image, bbox_inches='tight')

                # Close the figure to free memory
                plt.close()

        else:
            # Create a new figure empty (method to manage an empty CSV file)
            plt.figure(figsize=(30, 10))
            plt.plot([], [])
            plt.xlabel('Time')
            plt.ylabel('Task ID')
            plt.xticks(range(start_time, end_time, fraction))
            plt.yticks([])
            plt.grid(True, linestyle='--', linewidth=0.5)
            plt.savefig(output_image)

    except Exception as e:
        print(f"Error while creating the graph: {str(e)}")
