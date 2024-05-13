from creates import current_timestamp_get

# bar
from plots.bar.blobs_by_slot import (bar_blobs_per_slot_create)
from plots.bar.slots_by_blob_count import (bar_slots_by_blob_count_create)
from plots.bar.first_last_difference import (bar_first_last_difference_create)

# box
from plots.box.first_last_difference import (box_first_last_difference_create)
from plots.box.block_size_vs_blobs import (box_block_size_vs_blobs_create)

# area
from plots.area.blob_hash_repetitions import (area_blob_hash_repetitions_create)
from plots.area.average_blob_arrival import (area_average_blob_arrival_create)
from plots.area.blob_size_used_per_blob import (area_blob_size_used_per_blob_create)

# pie
from plots.pie.slots_by_blob_count import (pie_slots_by_blob_count_create)

from typing import List, Callable

blob_functions = [
    current_timestamp_get,                  # 1
    bar_blobs_per_slot_create,              # 2
    bar_slots_by_blob_count_create,         # 3
    pie_slots_by_blob_count_create,         # 4
    bar_first_last_difference_create,       # 5
    box_first_last_difference_create,       # 6
    area_blob_hash_repetitions_create,      # 7
    area_average_blob_arrival_create,       # 8
    area_blob_size_used_per_blob_create,    # 9
    box_block_size_vs_blobs_create          # 10
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
