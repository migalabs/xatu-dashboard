from creates import current_timestamp_get
from typing import List, Callable
import plots.bar as bar
import plots.area as area
import plots.box as box
import plots.pie as pie

blob_functions = [
    current_timestamp_get,                   # 1
    bar.blobs_per_slot_create,               # 2
    bar.slots_by_blob_count_create,          # 3
    pie.slots_by_blob_count_create,          # 4
    bar.first_last_difference_create,        # 5
    box.first_last_difference_create,        # 6
    area.blob_hash_repetitions_create,       # 7
    area.average_blob_arrival_create,        # 8
    area.blob_size_used_per_blob_create,     # 9
    box.block_size_vs_blobs_create,          # 10
]

builder_functions = blob_functions


# Returns an array with the corresponding functions inside the given indexes
# Will return all functions if args are empty
# Note: to use with flag -t
# * "-t 1 2" will select the first and second function, etc
def get_test_functions(args, functions=builder_functions) -> List[Callable]:
    n_args = args.__len__()
    testing_functions = functions.copy()
    testing_functions.extend([])  # add any extras solely for testing purposes

    if (n_args > 0):
        testing_list = []

        for index in range(0, n_args):
            function_index = int(args[index]) - 1

            if (index == n_args or function_index >= len(testing_functions)):
                break

            testing_list.append(testing_functions[function_index])

        return (testing_list)

    return (testing_functions)
