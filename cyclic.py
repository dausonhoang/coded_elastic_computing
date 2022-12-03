def cyclicTAS(N, L, F, n_left):
    """
    IMPLEMENTING THE CYCLIC TAS
    :param N: Number of machines
    :param L: Coding parameter
    :param F: Number of tasks
    :param n_left: index of machine that left
    :return: an array cyclicT[n] representing a pair (start, end) indices of the task assignment to machine n
             cyclicT[n_left] = (-1,-1)
    """
    cyclicT = []
    if n_left == -1:  # no machine left, N machines in total
        num_allocated_tasks = L * F / N
        for n in range(N):
            start = int(n * F / N) % F
            end = int(start + num_allocated_tasks - 1) % F
            cyclicT.append((start, end))
    else:               # one machine left, N-1 machines remain
        num_allocated_tasks = (L * F) / (N - 1)
        for n in range(N):
            if n == n_left:
                start = None
                end = None
            elif n < n_left:
                start = int(n * F / (N - 1)) % F
                end = int(start + num_allocated_tasks - 1) % F
            else:
                start = int((n - 1) * F / (N - 1)) % F
                end = int(start + num_allocated_tasks - 1) % F
            cyclicT.append((start, end))
    return cyclicT


def cyclic_completed_TAS(N, L, F, fraction):
    """
    IMPLEMENTING THE COMPLETED TASKS BY A CYCLIC TAS BY RATIO (0.25, 0.5, 0.75)
    :param N: Number of machines
    :param L: Coding parameter
    :param F: Number of tasks
    :param fraction: 0.25, 0.5, or 0.75
    :return: an array completedT[n] representing a pair (start_completed, end_completed) indices of the task completed at machine n
    """

    cyclicT = cyclicTAS(N, L, F, -1)
    num_completed_tasks = int(fraction*L*F/N)

    completedT = []
    for n in range(N):
        start_completed = cyclicT[n][0]     # assume tasks are carried out from 'start' to 'end'
        end_completed = (start_completed + num_completed_tasks - 1) % F
        completedT.append((start_completed, end_completed))
    return completedT


def main():
    N = 5
    L = 3
    F = 20
    for n_left in range(-1,N):
        T = cyclicTAS(N, L, F, n_left)
        print("n_left = ", n_left, "\n")
        for n in range(N):
            print("     n = ", n, ": [", T[n][0],", ", T[n][1],"]")
        print("-------------------------\n")

if __name__ == '__main__':
    main()
