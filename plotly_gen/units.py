from utils import bold


def format_seconds(seconds: float) -> str:
    if (seconds >= 1):
        return (bold(f'{seconds:,.0f}s'))
    return (bold(f'{seconds / 1000:,.0f}ms'))


def format_kilobytes(kilobytes: float) -> str:
    if (kilobytes >= 1000):
        return (bold(f'{kilobytes / 1000:,.1f}mb'))
    return (bold(f'{kilobytes:,.0f}kb'))
