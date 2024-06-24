import sys
import SchedIO
import Task,subprocess

if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        scheduler = SchedIO.import_file(input_path, output_path)
        '''
        print("Do you want to add some seconds?")
        while True:
            seconds = input()
            if seconds.lower() == "next":
                print("Skipping the execution")
                break  # Exits the loop
            try:
                seconds = int(seconds)
                if 0 <= seconds <= 100:
                    scheduler.add_time(seconds)
                    break  # Exits the loop
                else:
                    raise ValueError("The number of seconds must be between 0 and 100")
            except ValueError:
                print("Invalid value, please try again or type 'Next' to skip the execution:")

        '''
        scheduler.execute()
        

        #scheduler.execute()


        # Chiamata al controller come se fosse da riga di comando
        #command = f'python3 controller.py {input_path} {output_path}'
        #subprocess.run(command, shell=True, check=True)
        '''while(True):
            real_time = input()
            real_time = bool(real_time)
            _type = input()
            _id = input()
            _id = int(_id)
            period = input()
            if period == 'None':
                period = None
            else:
                period = int(period)
            activation = input()
            activation = int(activation)
            deadline = input()
            deadline = int(deadline)
            wcet = input()
            wcet = int(wcet)
            new_task = Task.Task(real_time, _type, _id, period, activation, deadline, wcet)
            scheduler.new_task(new_task)'''

        #new_task = Task.Task(True, 'periodic', 5, 20, 0, 100, 5)
        new_task = Task.Task(True, 'sporadic', 5, None, 15, 100, 5)
        #new_task = Task.Task(False, 'sporadic', 4, None, 10, None, 15)
        #scheduler.new_task(new_task)

        new_task = Task.Task(True, 'sporadic', 11, None, 15, 100, 5)
        #new_task = Task.Task(True,'sporadic',6,None, 0,100,10)
        scheduler.new_task(new_task)
        

        #scheduler.add_time(40)


    else:
        raise Exception(
            'Insufficient arguments. The name of the input and output files are required')
