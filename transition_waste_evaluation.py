import cyclic
import shifted


def necessary_change(N, L, F):
    return int(L*F/N/(N-1))


def to_tasks_set(F, start, end):
    """
    TURNING (START, END) TO A SET
    :param F:
    :param start:
    :param end:
    :return:
    """
    if start < end:
        tasks_set = set(range(start, end + 1))
    else:
        tasks_set = set(range(start, F)).union(set(range(end + 1)))
    return tasks_set


def abandoned_new_tasks_individual(F, TB, TA):
    """
    CALCULATE THE SETS OF ABANDONED AND NEW TASKS FOR ONE MACHINE
    :param F: total number of tasks
    :param TB: refers to the tasks allocated to machine n before n_left left
    :param TA: refers to the tasks allocated to machine n after n_left left
    :return:
    """
    start_before = TB[0]
    end_before = TB[1]
    start_after = TA[0]
    end_after = TA[1]

    tasks_set_before = to_tasks_set(F, start_before, end_before)
    tasks_set_after = to_tasks_set(F, start_after, end_after)
    intersection = tasks_set_before.intersection(tasks_set_after)
    abandoned_tasks = tasks_set_before.symmetric_difference(intersection)
    new_tasks = tasks_set_after.symmetric_difference(intersection)
    if len(abandoned_tasks) == 0:
        abandoned_tasks = {}
    if len(new_tasks) == 0:
        new_tasks = {}

    return (abandoned_tasks, new_tasks)

def abandoned_new_tasks(N, L, F, n_left, category):
    """
    RETURN THE SET OF ABANDONED AND NEW TASKS AT EACH MACHINE WHEN MACHINE N_LEFT LEFT
    :param N:
    :param L:
    :param F:
    :param n:
    :param category: is either "cyclic", "shifted", or "ZW"
    :return: an array of individual (abandoned + new)
    """
    if category == "cyclic":
        T_before = cyclic.cyclicTAS(N, L, F, -1)
        T_after = cyclic.cyclicTAS(N, L, F, n_left)
    elif category == "shifted":
        T_before = cyclic.cyclicTAS(N, L, F, -1)        # same as cyclic
        T_after = shifted.shiftedTAS(N, L, F, n_left)   # shifted cyclic
    elif category == "ZW":
        pass
    else:
        print("ERROR: invalid category")

    AN = []
    for n in range(N):
        if n == n_left:
            AN.append(({},{}))      # for n_left itself, set abandoned, new = {} to avoid error
        else:
            abandoned_tasks, new_tasks = abandoned_new_tasks_individual(F, T_before[n], T_after[n])
            AN.append((abandoned_tasks, new_tasks))
    return AN


def transition_waste(N, L, F, category):
    """
    CALCULATE THE TOTAL TRANSITION WASTE (ABANDONED + NEW - NECESSARY)
    OVER ALL MACHINES WHEN N_LEFT LEFT
    :param N:
    :param L:
    :param F:
    :param category: "cyclic", "shifted", or "ZW"
    :return: a 2-d array, first index is n_left, second index is n for a remaining machine
    """
    AN_list = []    # AN_list[n_left] is the list of abandoned and new tasks for each machine n
    for n_left in range(N):
        AN_list.append(abandoned_new_tasks(N, L, F, n_left, category))

    TW_list = []    # TW_list[n_left][n] is the waste (abandoned + new - necessary) for machine n when n_left
    for n_left in range(N):
        TW = []     # transition waste for every machine when n_left
        for n in range(N):
            if n == n_left:
                waste = 0       # consider the waste at machine n_left is zero
            else:
                waste = len(AN_list[n_left][n][0]) + len(AN_list[n_left][n][1]) - necessary_change(N, L, F)
            TW.append(waste)
        TW_list.append(TW)

    return TW_list


def transition_waste_total(N, L, F, category):
    """
    COMPUTE THE TOTAL TRANSITION WASTE ACROSS ALL MACHINES WHEN N_LEFT
    :param N:
    :param L:
    :param F:
    :param category:
    :return:
    """
    TW_list = transition_waste(N, L, F, category)
    TW_total = []
    for n_left in range(N):
        TW_total.append(sum(TW_list[n_left]))

    return TW_total

def test_transition_waste_total(N, L, F, category):
    """
    Verify the total TW against Theorem 2 & 3
    """
    TW_total = transition_waste_total(N, L, F, category)
    for n_left in range(N-L-1):
        if category == "cyclic":
            if n_left < N - L - 1:
                tw_theory = int((n_left * (n_left - 1) + (N - L - n_left - 1) * (N - L - n_left)) * F / N / (N - 1))
            else:
                tw_theory = int(n_left * (n_left - 1) * F / N / (N - 1))
            if TW_total[n_left] != tw_theory:
                print("Error: total TW inconsistent with theory for n_left = ", n_left)
                return False
        elif category == "shifted":
            if (N-L) % 2 == 1:
                tw_theory = int((N-L-1)^2*F/(2*N*(N-1)))
            else:
                tw_theory = int((N-L)*(N-L-2)*F/(2*N*(N-1)))
            if TW_total[n_left] != tw_theory:
                print("Error: total TW inconsistent with theory for n_left = ", n_left, " (", category,")")
                print("theory TW = ", tw_theory, " while the calculated TW = ", TW_total[n_left])
                return False

    return True

def main():
    N = 7
    L = 3
    F = 210
    # print("Abandoned & New Tasks Set for cyclic:")
    # for n_left in range(N):
    #     AN_cyclic = abandoned_new_tasks(N, L, F, n_left, "cyclic")
    #     print("n_left = ", n_left)
    #     print("     AN[n_left] = ", AN_cyclic)
    #     print("-------------------------\n")
    #
    # print("Necessary change = ", necessary_change(N, L, F))
    #
    print("Transition waste for cyclic:")
    # TW_list_cyclic = transition_waste(N, L, F, "cyclic")
    # print(TW_list_cyclic)
    TW_total_cyclic = transition_waste_total(N, L, F, "cyclic")
    print(TW_total_cyclic)
    #
    # print("Abandoned & New Tasks Set for SHIFTED:")
    # for n_left in range(N):
    #     AN_shifted = abandoned_new_tasks(N, L, F, n_left, "shifted")
    #     print("n_left = ", n_left)
    #     print("     AN[n_left] = ", AN_shifted)
    #     print("-------------------------\n")

    print("Transition waste for SHIFTED:")
    # TW_list_shifted = transition_waste(N, L, F, "shifted")
    # print(TW_list_shifted)
    TW_total_shifted = transition_waste_total(N, L, F, "shifted")
    print(TW_total_shifted)

    print(test_transition_waste_total(N, L, F, "cyclic"))
    print(test_transition_waste_total(N, L, F, "shifted"))

    # print("Cyclic original: ", cyclic.cyclicTAS(N, L, F, -1))
    # print("Shifted cyclic: ", shifted.shiftedTAS(N, L, F, 0))

if __name__ == "__main__":
    main()














