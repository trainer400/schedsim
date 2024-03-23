import sys
import SchedIO
import Task

if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        scheduler = SchedIO.import_file(input_path, output_path)
        scheduler.execute()
        new_task = Task.Task(True, 'sporadic', 5, None, 15, 100, 5)
        #new_task = Task.Task(True,'sporadic',6,None, 0,100,10)
        scheduler.new_task(new_task)
    else:
        raise Exception(
            'Insufficient arguments. The name of the input and output files are required')
