# distutils: language=c
# cython: embedsignature=True
# cython: language_level=3

def gauss_sum(int n):
    """Computes `n(n+1)/2` for natural numbers `n` (slowly)."""
    cdef int sum = 0
    while n > 0:
        sum += n
        n -= 1
    return sum
