import cyclic
import shifted
import zerowaste
import transition_waste_evaluation
import sys


def abandoned_completed_new_tasks_individual(F, TC, TA):
    """
    CALCULATE THE SETS OF ABANDONED COMPLETED & NEW TASKS FOR ONE MACHINE
    :param F: total number of tasks
    :param TC: refers to the tasks COMPLETED at machine n before n_left left
    :param TA: refers to the tasks allocated to machine n after n_left left
    :return:
    """
    start_completed = TC[0]
    end_completed = TC[1]
    start_after = TA[0]
    end_after = TA[1]

    tasks_set_completed = transition_waste_evaluation.to_tasks_set(F, start_completed, end_completed)
    tasks_set_after = transition_waste_evaluation.to_tasks_set(F, start_after, end_after)
    intersection = tasks_set_completed.intersection(tasks_set_after)
    abandoned_completed_tasks = tasks_set_completed.symmetric_difference(intersection)
    new_tasks = tasks_set_after.symmetric_difference(intersection)
    if len(abandoned_completed_tasks) == 0:
        abandoned_completed_tasks = {}
    if len(new_tasks) == 0:
        new_tasks = {}

    return (abandoned_completed_tasks, new_tasks)

def abandoned_completed_tasks_individual(F, TC, TA, category):
    """
    CALCULATE THE SETS OF ABANDONED COMPLETED & NEW TASKS FOR ONE MACHINE
    :param F: total number of tasks
    :param TC: refers to the tasks COMPLETED at machine n before n_left left
    :param TA: refers to the tasks allocated to machine n after n_left left
    :param category: "cyclic", "shifted", or "zw"
    :return:
    """

    if category == "cyclic" or category == "shifted":   # TC are given by the two indices only
        start_completed = TC[0]
        end_completed = TC[1]
        start_after = TA[0]
        end_after = TA[1]
        tasks_set_completed = transition_waste_evaluation.to_tasks_set(F, start_completed, end_completed)
        tasks_set_after = transition_waste_evaluation.to_tasks_set(F, start_after, end_after)
        intersection = tasks_set_completed.intersection(tasks_set_after)
        abandoned_completed_tasks = tasks_set_completed.symmetric_difference(intersection)
    elif category == "zw":  # TC and TA each is a set
        intersection = TC.intersection(TA)
        abandoned_completed_tasks = TC.symmetric_difference(intersection)
    else:
        print("ERROR: invalid category")
        return set()

    if len(abandoned_completed_tasks) == 0:
        abandoned_completed_tasks = {}

    return abandoned_completed_tasks

def abandoned_completed_tasks(N, L, F, n_left, fraction, category):
    """
    RETURN THE SET OF ABANDONED COMPLETED TASKS AT EACH MACHINE WHEN MACHINE N_LEFT LEFT
    :param category: is either "cyclic", "shifted", or "ZW"
    :return: an array of individual abandoned completed tasks for each machine
    """
    if category == "cyclic":
        T_completed = cyclic.cyclic_completed_TAS(N, L, F, fraction)
        T_after = cyclic.cyclicTAS(N, L, F, n_left)
    elif category == "shifted":
        T_completed = cyclic.cyclic_completed_TAS(N, L, F, fraction)
        T_after = shifted.shiftedTAS(N, L, F, n_left)
    elif category == "zw":
        T_completed = zerowaste.zw_completed_TAS(N, L, F, fraction)
        T_after = zerowaste.zwTAS(N, L, F, n_left)
    else:
        print("ERROR: invalid category")

    AC = []        # list of abandoned_completed_tasks for every machine n
    for n in range(N):
        if n == n_left:
            AC.append({})      # for n_left itself, set abandoned = {} to avoid error
        else:
            abandoned_completed_tasks= abandoned_completed_tasks_individual(F, T_completed[n], T_after[n], category)
            AC.append(abandoned_completed_tasks)
    return AC


def average_abandoned_max_abandoned_completed_tasks(N, L, F, fraction, category):
    """
    :return: for each n_left, the average (over N-1 machines) and the max (over all N-1 machines) #abandoned completed tasks
    """
    ave_max = []        # the [n_left] entry of the array gives (ave_abandoned_completed, max_abandoned_completed] for n_left at fraction

    for n_left in range(N):
        AC = abandoned_completed_tasks(N, L, F, n_left, fraction, category)
        sum_abandoned_completed = 0
        max_abandoned_completed = 0
        for n in range(N):
            sum_abandoned_completed = sum_abandoned_completed + len(AC[n])
            if max_abandoned_completed < len(AC[n]):
                max_abandoned_completed = len(AC[n])
        sum_abandoned_completed = sum_abandoned_completed / (N-1)
        ave_max.append((sum_abandoned_completed, max_abandoned_completed))

    return ave_max

def average_average_abandoned_completed_tasks(N, L, F, fraction, category):
    """
    For CPU overhead of transition: average (over n*) of the averages (over all active machines)

    Calculate the AVERAGE (over all n*) of the AVERAGES (over all N-1 machines)
    of #abandoned (wasted) completed tasks
    -Step 1: for EACH n*, compute the #average abandoned completed tasks over all N-1 machines
    -Step 2: sum what are computed in Step 1 for ALL n* and get the average-average by dividing by N
    -Step 3: convert the average-average into a percentage by dividing by fraction*LF/N
    :return: The % of average average #abandoned completed tasks among the COMPLETED ones
             (so, it's dividing by fraction*LF/N)
    """

    average_max = average_abandoned_max_abandoned_completed_tasks(N, L, F, fraction, category)     # Step 1
    average_average_abandoned = 0
    for n_left in range(N):
        average_average_abandoned = average_average_abandoned + average_max[n_left][0]          # Step 2
        #print(f"average_max[{n_left}][0] = {average_max[n_left][0]}")


    average_average_abandoned = average_average_abandoned / N                                   # Step 2
    #print(f"fraction = {fraction}, category = {category}, ave_ave = {average_average_abandoned}")

    num_completed_tasks = fraction*L*F/N
    #print(f"num_completed_tasks = {num_completed_tasks}")
    average_average_abandoned_percentage = average_average_abandoned * 100 / num_completed_tasks    # Step 3
    #print(f"fraction = {fraction}, category = {category}, ave_ave_percentage = {average_average_abandoned_percentage}")
    return average_average_abandoned_percentage

def average_max_abandoned_completed_tasks(N, L, F, fraction, category):
    """
    For actual running time: average (over n*) worst case (over all active machines)

    Calculate the AVERAGE (over all n*) of the MAXES #extra tasks to do (among all N-1 machines) after n* left
    -Step 1: for EACH n*, compute the maximum #extra tasks (same as #abandoned completed?) among all N-1 machines
    -Step 2: sum what are computed in Step 1 for ALL n* and get the average-max by dividing by N
    -Step 3: convert the average-max into a percentage by dividing by LF/(N-1)
    :return: The % of average max #extra tasks over the newly assigned #tasks (so, it's dividing by LF/(N-1))
    """

    average_max = average_abandoned_max_abandoned_completed_tasks(N, L, F, fraction, category) # Step 1
    average_max_abandoned = 0
    for n_left in range(N):
        average_max_abandoned = average_max_abandoned + average_max[n_left][1]              # Step 2

    average_max_abandoned = average_max_abandoned / N                                       # Step 2
    # print(f"fraction = {fraction}, category = {category}, ave_max = {average_max_abandoned}")
    num_assigned_tasks = L * F / (N-1)                                                      # Step 3
    average_max_abandoned_percentage = average_max_abandoned * 100 / num_assigned_tasks     # Step 3
    # print(f"fraction = {fraction}, category = {category}, ave_max_percentage = {average_max_abandoned_percentage}")
    return average_max_abandoned_percentage


def max_max_abandoned_completed_tasks(N, L, F, fraction, category):
    """
    For actual running time: worst (over n*) worst case (over all active machines)

    Calculate the MAX (among all n*) of the MAXES #extra tasks to do (among all N-1 machines) after n* left
    -Step 1: for EACH n*, compute the maximum #extra tasks (same as #abandoned completed?) among all N-1 machines
    -Step 2: choose the max number in Step 1 among ALL n*
    -Step 3: convert the max-max into a percentage by dividing by LF/(N-1)
    :return: The % of max max #extra tasks over the newly assigned #tasks (so, it's dividing by LF/(N-1))
    """

    average_max = average_abandoned_max_abandoned_completed_tasks(N, L, F, fraction, category)  # Step 1
    max_max_abandoned = 0
    for n_left in range(N):
        if max_max_abandoned < average_max[n_left][1]:      # Step 2
            max_max_abandoned = average_max[n_left][1]      # Step 2

    num_assigned_tasks = L * F / (N - 1)                    # Step 3
    max_max_abandoned_percentage = max_max_abandoned * 100 / num_assigned_tasks  # Step 3
    return max_max_abandoned_percentage


def write_to_csv_fixedN(N, L_values, F, fractions):
    """
    This write required results to csv files, N is fixed, L varies
    @L_values: the values of L to be plot
    @fractions: list of fractions used, i.e., [0.1, 0.5, 0.9]
    :return:
    """

    for fraction in fractions:
        # Print the average average wasted completed tasks, correspond to CPU wasted time
        filename_cpu = "cpu-sim-" + str(int(100*fraction)) + ".csv"
        output_file_cpu = open(filename_cpu, "w")
        header_cpu = "L with N = " + str(N) + "," + "Cyclic-ave-ave-" + str(fraction) + "," + "Shifted-ave-ave" + str(fraction) + "\n"
        output_file_cpu.write(header_cpu)
        for L in L_values:
            cyclic_average_average_abandoned = average_average_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
            shifted_average_average_abandoned = average_average_abandoned_completed_tasks(N, L, F, fraction, "shifted")
            line = str(L) + "," + f'{cyclic_average_average_abandoned:.1f}' + "," + f'{shifted_average_average_abandoned:.1f}' + "\n"
            output_file_cpu.write(line)
        output_file_cpu.close()

        # Print the max wasted completed, which correspond to the extra completion time
        filename_completion = "completion-sim-" + str(int(100*fraction)) + ".csv"
        output_file_completion = open(filename_completion, "w")
        header_completion = "L with N = " + str(N) + "," + "Cyclic-ave-max-" + str(fraction) + "," + "Shifted-ave-max/max-max-" + str(fraction)\
                            + "," + "Cyclic-max-max-" + str(fraction) + "\n"
        output_file_completion.write(header_completion)
        for L in L_values:
            cyclic_average_max_abandoned = average_max_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
            shifted_average_max_abandoned = average_max_abandoned_completed_tasks(N, L, F, fraction, "shifted")
            cyclic_max_max_abandoned = max_max_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
            # shifted_max_max_abandoned = max_max_abandoned_completed_tasks(N, L, F, fraction, "shifted")
            line = str(L) + "," + f'{cyclic_average_max_abandoned:.1f}' + "," + f'{shifted_average_max_abandoned:.1f}'\
                   + "," + f'{cyclic_max_max_abandoned:.1f}' + "\n"
            output_file_completion.write(line)
        output_file_completion.close()

def write_to_csv_fixedL(N_values, L, fractions):
    """
    This write required results to csv files
    @N_values: the values of N to be plot
    @fractions: list of fractions used, i.e., [0.1, 0.5, 0.9]
    :return:
    """

    for fraction in fractions:
        # Print the average average wasted completed tasks, correspond to CPU wasted time
        filename_cpu = "L5-cpu-sim-" + str(int(100*fraction)) + ".csv"
        output_file_cpu = open(filename_cpu, "w")
        header_cpu = "N with L = " + str(L) + "," + "Cyclic-ave-ave-" + str(fraction) + "," + "Shifted-ave-ave" + str(fraction) + "\n"
        output_file_cpu.write(header_cpu)
        for N in N_values:
            F = N*(N-1)
            cyclic_average_average_abandoned = average_average_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
            shifted_average_average_abandoned = average_average_abandoned_completed_tasks(N, L, F, fraction, "shifted")
            line = str(N) + "," + f'{cyclic_average_average_abandoned:.1f}' + "," + f'{shifted_average_average_abandoned:.1f}' + "\n"
            output_file_cpu.write(line)
        output_file_cpu.close()

        # Print the max wasted completed, which correspond to the extra completion time
        filename_completion = "L5-completion-sim-" + str(int(100*fraction)) + ".csv"
        output_file_completion = open(filename_completion, "w")
        header_completion = "N with L = " + str(L) + "," + "Cyclic-ave-max-" + str(fraction) + "," + "Shifted-ave-max/max-max-" + str(fraction)\
                            + "," + "Cyclic-max-max-" + str(fraction) + "\n"
        output_file_completion.write(header_completion)
        for N in N_values:
            F = N*(N-1)
            cyclic_average_max_abandoned = average_max_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
            shifted_average_max_abandoned = average_max_abandoned_completed_tasks(N, L, F, fraction, "shifted")
            cyclic_max_max_abandoned = max_max_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
            # shifted_max_max_abandoned = max_max_abandoned_completed_tasks(N, L, F, fraction, "shifted")
            line = str(N) + "," + f'{cyclic_average_max_abandoned:.1f}' + "," + f'{shifted_average_max_abandoned:.1f}'\
                   + "," + f'{cyclic_max_max_abandoned:.1f}' + "\n"
            output_file_completion.write(line)
        output_file_completion.close()


def main():
    N = 10
    L_values = range(3,N)
    F = 10*N*(N-1)
    # fractions = [0.25, 0.5, 0.75]
    fractions = [0.1,0.5,0.9]
    write_to_csv_fixedN(N, L_values, F, fractions)

    L = 5
    N_values = range(L+1,16)
    write_to_csv_fixedL(N_values, L, fractions)

    N = 7
    L = 3
    #F = N*(N-1)
    F = 210
    #
    print(f"N = {N}, L = {L}, F = {F}\n")
    #
    for fraction in [0.1, 0.5, 0.9]:
        print("fraction = ", fraction)
        # cyclic_average_average_abandoned = average_average_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
        # shifted_average_average_abandoned = average_average_abandoned_completed_tasks(N, L, F, fraction, "shifted")
        # print(f"     cyclic_average_average: {cyclic_average_average_abandoned: .1f}")
        # print(f"    shifted_average_average: {shifted_average_average_abandoned: .1f}")

        cyclic_average_max_abandoned = average_max_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
        shifted_average_max_abandoned = average_max_abandoned_completed_tasks(N, L, F, fraction, "shifted")
        zw_average_max_abandoned = average_average_abandoned_completed_tasks(N, L, F, fraction, "zw")
        print(f"     cyclic_average_max: {cyclic_average_max_abandoned: .1f}")
        print(f"    shifted_average_max: {shifted_average_max_abandoned: .1f}")
        print(f"    zw_average_max: {zw_average_max_abandoned: .1f}")

        # cyclic_max_max_abandoned = max_max_abandoned_completed_tasks(N, L, F, fraction, "cyclic")
        # shifted_max_max_abandoned = max_max_abandoned_completed_tasks(N, L, F, fraction, "shifted")
        # print(f"     cyclic_max_max: {cyclic_max_max_abandoned: .1f}")
        # print(f"    shifted_max_max: {shifted_max_max_abandoned: .1f}")

        print("----------------------------------------------")

    #cyclicT_before = cyclic.cyclicTAS(N, L, F, -1)
    #print("Cyclic before = ", cyclicT_before)
    #n_left = 4
    #cyclicT_after = cyclic.cyclicTAS(N, L, F, n_left)
    #print(f"Cyclic after n* = {n_left} left = ", cyclicT_after)
    #
    for n_left in range(N):
        print(f"n_left = {n_left}: ")
        cyclicT_before = cyclic.cyclicTAS(N, L, F, -1)
        cyclicT_after = cyclic.cyclicTAS(N, L, F, n_left)
        shiftedT_after = shifted.shiftedTAS(N, L, F, n_left)
        print("    Cyclic before = ", cyclicT_before)
        print("    Cyclic after = ", cyclicT_after)
        print("    Shifted after = ", shiftedT_after)
        print("--------------------------------\n")
    #
    #
    # for fraction in [0.25, 0.5, 0.75]:
    #     print(f"fraction = {fraction}")
    #     cyclicT_completed = cyclic_completed_TAS(N, L, F, fraction)
    #     print(f"cyclic_completed = {cyclicT_completed}")
    #     for n_left in range(N):
    #         print(f"   n_left = {n_left}")
    #         cyclic_AC_per_nleft = abandoned_completed_tasks(N, L, F, n_left, fraction, "cyclic")
    #         shifted_AC_per_nleft = abandoned_completed_tasks(N, L, F, n_left, fraction, "shifted")
    #         print(f"       cyclicAC = {cyclic_AC_per_nleft}")
    #         print(f"       shiftedAC = {shifted_AC_per_nleft}")
    #     print("------------------------------------")

    #print(cyclic_completed_TAS(N, L, F, 4, 0.25))
    #print(abandoned_completed_new_tasks(N, L, F, 4, 0.25, "cyclic"))

if __name__ == "__main__":
    main()














