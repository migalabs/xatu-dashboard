OPT_START_INDEX = 1


def get_options(n_args, args):
    '''
    Get options from the command's arguments.

    Does not validate the existence of an implementation of the flag.
    '''
    option_dict = {}

    for index in range(OPT_START_INDEX, n_args):
        if (args[index][0] == '-'):
            option_dict[args[index]] = []
            for subindex in range(index + 1, n_args):
                if (args[subindex][0] == '-'):
                    break
                option_dict[args[index]].append(args[subindex])
    print('arguments', option_dict)
    return (option_dict)
