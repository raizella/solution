class Pair:
    
    def __init__(self, w):
        if '|' in w:
            self.word = w.partition('|')[2]
            self.list = []
            self.list += w.partition('|')[0]
            self.list.sort()
        else:
            self.word = w
            self.list = []
            self.list += w
            self.list.sort()

    def getWord(self):
        return self.word

    def getJoined(self):
        return "".join(self.list)

    def getList(self):
        return self.list

    def __repr__(self):
        return repr((self.list, self.word))

    def __eq__(self, key):
        return key.getList() == self.list

    def __getitem__(self, index):
        if index == 0:
            return self.list
        else:
            return self.word
