def shiftedTAS(N, L, F, n_left):
    """
    IMPLEMENTING THE SHIFTED CYCLIC TAS
    :param N: Number of machines
    :param L: Coding parameter
    :param F: Number of tasks
    :param n_left: index of machine that left
    :return: an array shiftedT[n] representing a pair (start, end) indices of the task assignment to machine n
             shiftedT[n_left] = (-1,-1)
    """
    # only use this function when one machine left
    assert n_left != -1, "ERROR: n_left = -1"

    # formula slightly different from the paper due to labelling n_left from 0->N-1 instead
    delta = ((N - n_left - 1) - int((N + L - 2) / 2)) * (F / (N * (N - 1)))
    shiftedT = []
    num_allocated_tasks = (L * F) / (N - 1)
    for n in range(N):
        if n == n_left:
            start = None
            end = None
        elif n < n_left:
            start = int(delta + n * F / (N - 1)) % F
            end = int(start + num_allocated_tasks - 1) % F
        else:
            start = int(delta + (n - 1) * F / (N - 1)) % F
            end = int(start + num_allocated_tasks - 1) % F
        shiftedT.append((start, end))

    return shiftedT

def main():
    N = 5
    L = 3
    F = 20
    for n_left in range(N):
        T = shiftedTAS(N, L, F, n_left)
        print("n_left = ", n_left, "\n")
        for n in range(N):
            print("     n = ", n, ": [", T[n][0],", ", T[n][1],"]")
        print("-------------------------\n")



if __name__ == '__main__':
    main()
