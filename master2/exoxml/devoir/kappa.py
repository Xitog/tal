from nltk.metrics.agreement import AnnotationTask
from nltk.metrics import ConfusionMatrix

def kappa(data):
    """Data is a list of list.
       Each element is a list :
       [annotator, element, label]
    """
    task = AnnotationTask(data)
    return task.kappa()

if __name__ == '__main__':
    data = [
        ['1', 0, 'no'],
        ['2', 0, 'yes'],
        ['1', 1, 'no'],
        ['2', 1, 'no'],
        ['1', 2, 'no'],
        ['2', 2, 'no'],
        ['1', 3, 'no'],
        ['2', 3, 'yes'],
        ['1', 4, 'no'],
        ['2', 4, 'yes'],
        ['1', 5, 'yes'],
        ['2', 5, 'no'],
        ['1', 6, 'no'],
        ['2', 6, 'yes'],
        ['1', 7, 'no'],
        ['2', 7, 'yes'],
        ['1', 8, 'no'],
        ['2', 8, 'yes'],
        ['1', 9, 'no'],
        ['2', 9, 'yes']
    ]
    print(kappa(data)) # -0.2121
