from creates import get_current_timestamp
from typing import List, Callable
import plots.bar as bar
import plots.area as area
import plots.box as box
import plots.pie as pie

blob_functions = [
    get_current_timestamp,                      # 1 timestamp
    bar.slots_by_blob_count_create,             # 2 bar_slots-by-blob-count
    pie.slots_by_blob_count_create,             # 3 pie_slots-by-blob-count
    area.average_blob_arrival_create,           # 4 area_avg-blob-arrival
    box.first_last_difference_create,           # 5 box_first-last-timediff
    area.blob_size_used_per_blob_create,        # 6 area_blob-size-used
    box.block_size_vs_blobs_create,             # 7 box_block-size-vs-blobs
    pie.missed_blocks_after_block_with_blobs,   # 8 pie_missed-after-blob-count
    area.blob_hash_repetitions_create,          # 9 area_blob-hash-repetitions
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