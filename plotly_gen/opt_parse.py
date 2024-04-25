OPT_START_INDEX = 1


# This function will get options from the command line, even if they
# are not valid, but main will ignore them
def get_options(n_args, args):
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
