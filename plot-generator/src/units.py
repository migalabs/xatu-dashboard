from utils import bold

# -- Functions used for tick formatting --


def format_seconds(seconds: float) -> str:
    if (seconds >= 1):
        return (bold(f'{seconds:,.0f}s'))
    return (bold(f'{seconds / 1000:,.0f}ms'))


def format_kilobytes(kilobytes: float) -> str:
    if (kilobytes >= 1024):
        return (bold(f'{kilobytes / 1024:,.1f}mb'))
    return (bold(f'{kilobytes:,.0f}kb'))
