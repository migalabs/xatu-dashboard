from creates import getNodesTimestamp, current_timestamp_get
# bar
from bar.blobs_by_slot import (blobs_per_slot_create)
from bar.slots_by_blob_count import (slots_by_blob_count_create)
from bar.first_last_difference import (first_last_difference_create)
# box

# area
from area.blob_hash_repetitions import (blob_hash_repetitions_create)
from area.average_blob_arrival import (average_blob_arrival_create)

from typing import List, Callable

blob_functions = [
    current_timestamp_get,
    blobs_per_slot_create,
    slots_by_blob_count_create,
    first_last_difference_create,
    blob_hash_repetitions_create,
    average_blob_arrival_create
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
