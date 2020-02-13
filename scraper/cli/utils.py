
"""Utils."""


def count_lines(filename):
    """Count file lines."""
    return sum(1 for i in open(filename, 'rb'))
