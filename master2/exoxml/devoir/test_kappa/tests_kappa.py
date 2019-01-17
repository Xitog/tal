from nltk.metrics.agreement import AnnotationTask
from nltk.metrics import ConfusionMatrix
# Here we have four items, each labeled by two different annotators. In two cases, the annotators agree. In two cases they don't.
toy_data = [
    # annotators, element, label
    ['1', 5723, 'ORG'],
    ['2', 5723, 'ORG'],
    ['1', 55829, 'LOC'],
    ['2', 55829, 'LOC'],
    ['1', 259742, 'PER'],
    ['2', 259742, 'LOC'],
    ['1', 269340, 'PER'],
    ['2', 269340, 'LOC']
]
task = AnnotationTask(data=toy_data)
print(task.kappa())
print(task.alpha())
# 16h52 : Yes ! ça marche !

# L'annotateur est remplacé par une division en deux variables
# L'élément est remplacé par la position dans la liste
toy1 = ['ORG','LOC','PER','PER']
toy2 = ['ORG','LOC','LOC','LOC']
cm = ConfusionMatrix(toy1,toy2)
print(cm)

# multilabel pour une classe (un but)
# only 2 utilisateurs

rater1 = ['no', 'no', 'no', 'no', 'no', 'yes', 'no', 'no', 'no', 'no']
rater2 = ['yes', 'no', 'no', 'yes', 'yes', 'no', 'yes', 'yes', 'yes', 'yes']

if len(rater1) != len(rater2):
    raise Exception('Not good')
nb = 0
toy_data = []
while nb < len(rater1):
    toy_data.append(['1', nb, rater1[nb]])
    toy_data.append(['2', nb, rater2[nb]])
    nb += 1
print(toy_data)
task = AnnotationTask(data=toy_data)
print(task.kappa()) # -0.2121 YES ! J'ai la même chose que l'article
print(task.alpha())

