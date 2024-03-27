import sys
import SchedIO
import Task

def test(input_path, output_path):
    scheduler = SchedIO.import_file(input_path, output_path)
    scheduler.execute()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        test(input_path, output_path)
        scheduler = SchedIO.import_file(input_path, output_path)
        scheduler.execute()

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
        #new_task = Task.Task(True, 'sporadic', 5, None, 15, 100, 5)
        #new_task = Task.Task(False, 'sporadic', 4, None, 10, None, 15)
        #scheduler.new_task(new_task)

        new_task = Task.Task(True, 'sporadic', 5, None, 15, 100, 5)
        #new_task = Task.Task(True,'sporadic',6,None, 0,100,10)
        scheduler.new_task(new_task)
    else:
        raise Exception(
            'Insufficient arguments. The name of the input and output files are required')
