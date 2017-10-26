import numpy


def nonlin(x, deriv=False):
    if deriv:
        return x * (1 - x)
    return 1 / (1 + numpy.exp(-x))


X = numpy.array([
    [0, 0, 1],
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 1]])

y = numpy.array([[0, 0, 1, 1]]).T
numpy.random.seed(1)
syn0 = 2 * numpy.random.random((3, 1)) - 1
l1 = None
for _ in range(0, 10000):
    l0 = X
    l1 = nonlin(numpy.dot(l0, syn0))
    l1_error = y - l1
    l1_delta = l1_error * nonlin(l1, True)
    syn0 += numpy.dot(l0.T, l1_delta)

print('Output After Training:')
print(l1)

X = numpy.array([
    [0, 0, 1],
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 1]])

y = numpy.array([
    [0],
    [1],
    [1],
    [0]])

numpy.random.seed(1)
syn0 = 2 * numpy.random.random((3, 4)) - 1
syn1 = 2 * numpy.random.random((4, 1)) - 1
for index in range(0, 10000000000):
    l0 = X
    l1 = nonlin(numpy.dot(l0, syn0))
    l2 = nonlin(numpy.dot(l1, syn1))
    l2_error = y - l2
    if (index % 10000) == 0:
        print('Error: ' + str(numpy.mean(numpy.abs(l2_error))))
    l2_delta = l2_error * nonlin(l2, deriv=True)
    l1_error = l2_delta.dot(syn1.T)
    l1_delta = l1_error * nonlin(l1, deriv=True)
    syn1 += l1.T.dot(l2_delta)
    syn0 += l0.T.dot(l1_delta)
