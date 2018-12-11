files = ['45119-0-vol1.txt', '45312-0-vol2.txt', '46387-0-vol3.txt', '46470-0-vol4.txt']

count_all = 0
for fname in files:
    count_file = 0
    file = open(fname, encoding='utf8', mode='r')
    for line in file:
        count_file += len(line.split(' '))
    print('There is', count_file, 'words in', fname)
    file.close()
    count_all += count_file
print('There is', count_all, 'words in all files.')
