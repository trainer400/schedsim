import sys

from Visualizer import create_graph

if __name__ == "__main__":
    input_path = 'out.csv'
    output_path = 'out.png'
        
    create_graph(output_path)
    print(input_path)