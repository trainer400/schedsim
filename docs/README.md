# SchedSim

SchedSim is a collection of tools to test task scheduling algorithm (both real-time and non real-time).
The software is currently under development by [HEAPLab](https://heaplab.deib.polimi.it) students and researchers.

## Contributors

- Santarossa Noah
- Romano Luca
- Matteo Pignataro

## Introduction

The goal of this project is to add two new functionalities to the existing Schedsim, which simulates
various task scheduling techniques. Our work involves implementing a data structure to support the
insertion of new tasks and the extension of the total time in an ongoing execution. Additionally, we
are developing a graphical user interface (GUI) that supports all available operations and provides a
visual representation of the existing tasks.

## Schedsim

The algorithm implements the following scheduling algorithms: FIFO, SJF, HRRN, SRTF, RR. These
are divided into Non-Preemptive (FIFO, SJF, HRRN) and Preemptive (SRTF, RR) categories. In
Non-Preemptive scheduling, once a task begins its execution, it will not be interrupted until it finishes.
In Preemptive scheduling, tasks can start execution, pause to allow another task to execute, and then
resume. Additionally, the algorithm supports tasks that can be either periodic or sporadic, with or
without deadlines.

## Algorithm

The algorithm processes each time instant, from the start to the end of the simulation period, and
determines which task should be executed at each instant. To make this decision, the algorithm
maintains the following lists:

- Arrival Events: Tasks that are ready to start their execution. These tasks enter this list when their activation time is greater than or equal to the current time;
- Finish Events: Tasks that are completing their execution;
- Deadline Events: Tasks that have missed their deadline;
- Start Events: All tasks that are eligible to be executed;

### Non Preemptive

In Non-Preemptive algorithms, for each time instant, if no task is currently executing, the events in
the Arrival Events list are sorted according to the chosen scheduling algorithm. The algorithm then
selects the first task in the list to be fully executed without interruption.

### Preemptive

In Preemptive algorithms, tasks can be started, interrupted, and then resumed. In SRTF, at each
time instant, the task within the Start Events list that has the shortest remaining execution time is
selected for execution. In RR, at each quantum time instant, the task to be executed is switched in a
cyclic manner, following a repeated round of the tasks in the Start Events list.

## Adding functionalities

The scope of the project is to add the following functionalities:

- Adding Tasks and Time: Support the insertion of tasks after the execution has started, without
  the need to recalculate everything, and provide the ability to extend the simulation’s end time;
- Graphical Interface: Implement a GUI that allows users to interact with the scheduling algorithm and provides a visual representation of the tasks being executed throughout the simulation;

Here we present the web software architecture scheme, showcasing how the user interface connects
and interacts with various system components. The following diagram highlights the seamless communication between the frontend and backend.

TODO: ADD DIAGRAM

### Adding task and time

To support the addition of a new task after the execution has started, various solutions have been
considered. For periodic tasks, it is impossible to add a task without recalculating everything from the
beginning, as the start time of each periodic task is tied to the start time of the scheduling. Therefore,
the optimizations described below focus on the addition of sporadic tasks.

### Basic solution

The basic solution involves saving a copy of the four lists (_Arrival Events_, _Finish Events_, _Deadline Events_, _Start Events_) at each time instant. When a new task is added, the algorithm would return to
the state corresponding to the start time of the new task and continue the execution from that point.
However, this solution is not optimal because saving a copy of the four lists at each time instant is
computationally expensive. Therefore, a more efficient solution is needed-one that does not require
saving the state of the lists at every time instant, but only at certain intervals.

### Balanced binary search tree solution

An alternative solution is to use a Balanced Binary Search Tree (BBST) to save a copy of the four
lists only at time instants when a new task begins execution. With this data structure, fewer copies of
the lists are needed, and when a new task is added, the time to restart the execution can be found in
O(log(total time)). However, this solution is less effective when tasks have short durations, or when
the quantum value in Round Robin scheduling is low, leading to frequent updates of the BBST and,
consequently, too many copies of the lists.

**Example**:<br/>
Time = 10<br/>
We suppose that at the following time instants {2, 3, 5, 7, 9}, the tasks in ”execution” change, and the tree is updated before continuing execution.
Now, consider a new task that starts at time 4. The system finds the largest element in the BBST
(Balanced Binary Search Tree) that is smaller than or equal to 4, which is 3.
The system updates the BBST structure, restores the state from time 3, and resumes the simulation
from that point until the end.
If we consider round-robin execution, the tree size remains constant at one, as the tree is updated with
each time slice.

TODO: add graph

### SQRT decomposition solution

Taking the previous solutions into consideration, we opted for a data structure that saves a copy of the four lists at regular intervals. We chose an approach based on the _Square Root Decomposition Algorithm_. In this method, a copy of the four lists is saved every sqrt(time duration). When a new sporadic task arrives, the algorithm uses the most recent saved state prior to the task’s start time and then simulates the execution from that point to the end.

**Example**:<br/>
Time = 10<br/>
Size = sqrt(10) -> 3 (rounded to the nearest integer)
events_list = {events[0], events[3], events[6], events[9]}, where each events list contains four items
At time 4, a new task is introduced.
The most recent saved state before time 4 is at time 3.
The system restores the state at time 3 and resumes the simulation from there until the end.

TODO: add graph

### Implementation

When the algorithm starts executing, the interval size is calculated as the square root of the total execution time of the simulation, determining how often the states of the lists will be saved. The algorithm then simulates the tasks from the input file, saving the state of the four lists starting at time 0 and at each interval determined by the size. For example, if the total duration is 10, the size will be 3, and the positions that will be saved are 0, 3, 6, and 9. When a new task arrives, if it is sporadic, the time instant at which the execution will be restarted is calculated. This time is the latest saved time instant that is smaller than or equal to the start time of the new task. The execution is then restarted from that time instant and proceeds as before. If additional time is added to the total duration, the list containing the arrival events needs to be updated. The new arrival events are calculated similarly to the initial ones and saved from the previous end time up to the new end time, which is equal to the previous end time plus the added time.

### Test implementation correctness

To test the correctness of the implementation, we created a script that generates two input files. The second file contains a subset of the information from the first one, with a shorter time duration and fewer tasks. The missing tasks in the second file are then added, and the total time is extended to match that of the first file. This approach is used to verify the correct functioning of the method for adding tasks and time. After execution, the two output files are compared, and our implementation consistently passed the test, producing identical files each time.

## Graphical interface

The goal of this project is to create a new user interface (UI) that allows for easy access to and utilization of the newly implemented functionalities. We have developed a web-based UI that can be launched using the **ConnectionHandler.py** script.

### Running the application

To run the application, follow these steps:

1. Open the Schedsim3 folder on your device;
2. Navigate to the visualizer directory using your terminal or command prompt;
3. Compile and run the Connection Handler.py file using Python. This will start the server that hosts the web interface;
4. Open a web browser and go to the URL http://127.0.0.1:5001/ to access the user interface;
5. Interact with the ”Schedsim3” GUI to utilize the scheduling features and visualize task execution;

The homepage of the UI looks like this:

TODO: add graph

We have created several buttons linked to the key features of Schedsim.

### Start button

This button allows you to execute the code using the **execute** function of the **Scheduler** class. The function utilizes the **self.scheduler** instance to start and terminate the execution. If **self.scheduler** is not present, the function throws an exception and quits.

### New task button

This button allows you to create a new task using the new task function of the Scheduler class, which
requires several parameters defined in the Task class. There are two types of tasks:

- **Sporadic**: Requires the parameters (real time, task type, task id, activation, deadline, wcet);
- **Periodic**: Requires the parameters (real time, task type, task id, period, deadline, wcet);

There are several controls:

- **Task ID Check**: Verify that task id is a positive integer. This ensures that only valid tasks are processed;
- **WCET Check**: Confirm that wcet (Worst-Case Execution Time) is a positive integer. This check ensures that the execution time provided is valid and non-zero;
- **Period and Activation Check**: For periodic tasks, ensure period is a positive integer. For sporadic tasks, ensure activation is non-negative. This prevents invalid or nonsensical timing values from being used;
- **Deadline Check**: Ensure deadline is a positive integer. This ensures that deadlines are set correctly and are valid;
- **WCET vs Period Check**: For periodic tasks, ensure wcet is less than or equal to period. This ensures that the execution time fits within the period allocated for the task;
- **Deadline vs WCET Check**: Ensure deadline is greater than wcet. This guarantees that the task has enough time to complete before its deadline;

TODO: add graph

### Add time button

This button allows you to use the **add_time** function of the **Scheduler** class. This function requires a numerical input, which adds the specified amount of time to the **scheduler.end** parameter. When this function is activated, the scheduler implicitly calls the **start** function.

TODO: add graph

### Print graph button

This button allows you to use the **create_graph** function, which automatically prints the graph with default parameters: fraction set to one, and start and end set to the respective parameters of the **scheduler** instance. An additional functionality allows you to define the following parameters (**start**, **end**, **fraction**) to print the graph for a specific interval (usually the most significant). The fraction is a number in the range (1,5), while the start and end are allowed only in the range [**scheduler.start**, **scheduler.end**]. The graph displays four types of data:

- Red for the **arrival** of tasks;
- Blue for the **completion** of tasks;
- Green for the **execution** of tasks;
- Orange for the **deadline** of tasks;

TODO: add graphs

### Select and upload XML file button

This button allows you to select and upload an XML file from your device to the temporary directory of the project. Controls are in place to prevent uploading files that are not in XML format.

### Create XML button

This button allows you to create a new XML file based on the input parameters (**start**, **end**, **scheduler algorithm**). The **RR** algorithm also requires an additional parameter, **quantum**, which defines the time to assign to each task during each cycle.

TODO: add graph

Through the dynamic **Add New Task** button, you can add as many tasks as needed, following the same concept as the **New Task** functionality. The **Submit All Tasks** button finalizes the creation of the XML file, which you can then download using the **Download XML** button. To verify the validity and relationships among the tasks, we use the checks detailed in Section 3.2.3.

TODO: correct section reference with MD

### Download CSV button

This button allows you to download the output of the execution in CSV format. You can only download the file if you have executed the code beforehand.

TODO: add graph

### Download XML button

This button allows you to download the created XML file. You can only download the file if it was previously created using the Create XML button.

TODO: add graph

## Support file

For use well the GUI we have develop many support file.

### SchedulerController

This class manages the interaction between the frontend and backend using an instance of a scheduler.<br/>
Its functions are:

- **Initialization**: Sets up the scheduler, temporary directories, and initializes start and end times;
- **Load XML file**: Loads an XML file to initialize the scheduler with simulation parameters;
- **Execute scheduler**: Runs the scheduler and finalizes its execution;
- **Create task**: Adds a new task to the scheduler, supporting both sporadic and periodic tasks;
- **Add new time**: Extends the simulation time by a specified amount;
- **Print graph**: Generates and saves a graph representing task execution over a specified time range;
- **Create XML**: Creates an XML file representing the simulation configuration, including tasks, scheduler, and hardware;

### Visualizer

The **create_graph** method produces a timeline visualization of task events. It uses Pandas to handle and process numerical data from a CSV file, including managing missing values and converting data types. The method filters the data according to **start_time** and **end_time**, and utilizes Matplotlib to generate a graphical representation. The graph illustrates task arrivals, executions, completions, and deadlines with distinct colors. If the data is missing or empty, an empty graph is generated. The resulting plot is saved as the image file `out.png`.

### Style

The **style.css** file defines the visual presentation of the web page elements. It includes rules for layout, color schemes, fonts, and other stylistic aspects to ensure a cohesive and aesthetically pleasing
user interface.

### Script

The **script.js** file contains JavaScript code that handles various interactions and dynamic behaviors on the web page. It manages event listeners for user actions such as button clicks and form submissions, communicates with the server via AJAX, and updates the user interface based on server responses. This script is essential for enabling interactive features and ensuring smooth functionality.

### Dynamic form

The **dynamic_form.js** file manages the dynamic behavior of the form used for creating XML files. It adjusts the visibility of form fields based on user selections (e.g., task type or scheduling algorithm) to present only relevant options. This script ensures that the form adapts in realtime to user input, improving usability and streamlining the process of configuring XML files.

## Conclusion

With our project, users can now easily interact with the Schedsim Simulator through the web interface we developed, allowing them to visualize a graphical representation of the results. Additionally, the system supports the addition of new tasks and the extension of the total duration without requiring a full recalculation.

## References

1. HEAPLab, Schedsim GitHub Repository, https://github.com/HEAPLab/schedsim, 28 April 2022.
2. Noah Santarossa e Luca Romanò, Schedsim3 https://github.com/NoahSantarossa/schedsim3, 5 September 2024. GitHub Repository,
3. GeeksforGeeks, Binary Search Tree (BST) Data Structure, https://www.geeksforgeeks.org/binary-search-tree-data-structure/, Accessed September 2024.
4. GeeksforGeeks, Square Root (Sqrt) Decomposition Algorithm, https://www.geeksforgeeks.org/square-root-sqrt-decomposition-algorithm/, Accessed September 2024.
5. GeeksforGeeks, Python Lists, https://www.geeksforgeeks.org/python-lists/, Accessed September 2024.
6. GeeksforGeeks, Process Schedulers in Operating System, https://www.geeksforgeeks.org/process-schedulers-in-operating-system/, Accessed September 2024.
