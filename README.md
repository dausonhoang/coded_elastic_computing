Simulation of the computation overhead for cyclic & shifted cyclic   
compared to the zero-waste scheme in the paper "Transition Waste Optimization for Coded Elastic Computing"  

The computation overhead can be defined to be the maximum number of completed tasks among the remaining machines n   
that have been wasted due to the transition (Machine n* or n_left leaves), averaged over all n* = 1,2,...,N  

Parameters  
-N: total number of machines  
-L: parameter of the underlying coded computing scheme (length of the erasure code), each task must be carried out by exactly L machines  
-F: total number of tasks  

Run the simulation by running the main() method in `completed_transition_waste_evaluation.py' and tune the parameters if needed
-cyclic & shifted cyclic works for every L < N, F can be set to a multiple of N(N-1), currently, 10*N(N-1) to avoid rounding impact when F/N/(N-1) is small  
-zero-waste scheme currently works with N = 7, L = 3, and F = 210 only (using the Fano plane as an example)  
