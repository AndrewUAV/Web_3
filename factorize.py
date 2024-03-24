from time import time
from multiprocessing import Process, cpu_count


def factorize(*numbers):
    result = []
    for num in numbers:
        factors = []
        for i in range(1, (num + 1) // 2):
            if num % i == 0:
                factors.append(i)
        result.append(factors)
    return result


def print_factorize(*data_list):

    start = time()
    print('Start factorize')
    factorize(*data_list)
    end = time()
    print('End factorize')
    print(f'Total time of factorize == {end - start} sec')


def print_process_factorize(*data_list):
    res = []
    print('Start factorize process')
    start = time()
    print(f'CPU: {cpu_count()}')
    for num in data_list:
        process = Process(target=factorize, args=(num, ))
        process.start()
        res.append(process)
    [el.join() for el in res]
    end = time()
    print('End factorize process')
    print(f'Total time of process factorize == {end - start} sec')


def main():

    print_factorize(128, 255, 99999, 10651060, 123456789, 234567890)

    print_process_factorize(128, 255, 99999, 10651060, 123456789, 234567890)


if __name__ == "__main__":
    main()