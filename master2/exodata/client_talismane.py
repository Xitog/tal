# inspired from:
# https://github.com/joliciel-informatique/talismane/blob/master/talismane_examples/src/main/java/com/joliciel/talismane/examples/TalismaneClient.java

from socket import socket, AF_INET, SOCK_STREAM

def open_sock():
    # open connection
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('localhost', 7272))
    return sock

def send_receive(sock, cmd, debug=False):
    # send data
    cmd += '\f\f\f'
    if debug:
        print('Sending input to server:', cmd)
    sock.send(cmd.encode(encoding='utf-8'))
    
    # receive data
    chunks = []
    done = False
    while not done:
        chunk = sock.recv(2048)
        if chunk == b'':
            done = True
        chunks.append(chunk)
    res = b''.join(chunks)
    if debug:
        print('Server:', res)

    # close socket
    #if sock != GLOBAL_SOCK:
    sock.close()

    # return data
    return res.decode(encoding='utf-8')

def console():
    # info
    print('Enter your sentence. Let it empty to run the analysis.')

    # open connection
    sock = open_sock()

    # getting input from user
    cmd = ''
    from_user = 'a'
    while len(from_user) > 0:
        from_user = input('>>> ')
        print('Client:', from_user, len(from_user))
        cmd += from_user + '\n'
    
    # send and receive data
    return send_receive(sock, cmd)

# model
class Word:

    def __init__(self, num, form, lemma, pos, pos_lexicon, morphinfo, f7, f8, f9, f10):
        self.num = num
        self.form = form
        self.lemma = lemma
        self.pos = pos
        self.pos_lexicon = pos_lexicon
        # Morpho-syntaxic information
        self.number = None
        self.gender = None
        self.person = None
        self.possessor_number = None
        self.tense = None
        informations = morphinfo.split('|')
        for info in informations:
            #print('>>>', info)
            infos = info.split('=')
            if len(infos) > 1:
                typ, val = infos[0], infos[1]
                if typ == 'n':
                    self.number = 'plural' if val == 'p' else 'singular'
                elif typ == 'g':
                    self.gender = 'male' if val == 'm' else 'female'
                elif typ == 'p':
                    self.person = val
                elif typ == 'poss':
                    self.possessor_number = 'plural' if val == 'p' else 'singular'
                elif typ == 't':
                    self.tense = val
        self.f7 = f7
        self.f8 = f8
        self.f9 = f9
        self.f10 = f10

    def __str__(self):
        return self.num + '. ' + self.form + ' / ' + self.lemma + ' (' + self.pos + ')'

    def __repr__(self):
        return str(self)

# raw data to object model
# The token number (starting at 1 for the first token)
# The original word form (or _ for an empty token)
# The lemma found in the lexicon (or _ when unknown)
# The part-of-speech tag
# The grammatical category found in the lexicon
# The additional morpho-syntaxic information found in the lexicon.
#     g=m|f: gender = male or female
#     n=p|s: number = plural or singluar
#     p=1|2|3|12|23|123: person = 1st, 2nd, 3rd (or a combination thereof if several can apply)
#     poss=p|s: possessor number = plural or singular
#     t=pst|past|imp|fut|cond: tense = present, past, imperfect, future or conditional. Verb mood is not included, since it is already in the postag.
# The token number of this token's governor (or 0 when the governor is the root)
# The label of the dependency governing this token
#res = console()

def from_res_to_words(res):
    lines = res.split('\n')
    #print('Number of lines:', len(lines))
    words = []
    for lin in lines:
        elems = lin.split('\t')
        if len(elems) == 10:
            words.append(Word(*elems))
        #else:
        #    print(len(lin),':', lin)
    return words

#GLOBAL_SOCK = None

def process_string(string, sock=None, debug=False):
    global GLOBAL_SOCK
    if sock is None:
        #if GLOBAL_SOCK is None:
        #    GLOBAL_SOCK = open_sock()
        #sock = GLOBAL_SOCK
        sock = open_sock()
    res = send_receive(sock, string)
    if debug:
        print(res)
    return from_res_to_words(res)

if __name__ == '__main__':
    #words = process_string('Bonjour le monde !', debug=True)
    cmd = None
    while cmd != 'exit':
        cmd = input('enter sentence: ')
        if cmd != 'exit':
            words = process_string(cmd, debug=True)
            for word in words:
                print('   ', word)
