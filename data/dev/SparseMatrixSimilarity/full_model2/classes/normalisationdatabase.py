import sqlite3, time

def timeit(func): 
    '''Decorator that reports the execution time.'''
  
    def wrap(*args, **kwargs): 
        start = time.time() 
        result = func(*args, **kwargs) 
        end = time.time() 
          
        print(func.__name__, round(end-start, 20)) 
        return result 
    return wrap 

class NormalisationDataBase(object):

    DB_LOCATION = "/smartsolman/data/src/norma.db"
    # @timeit
    def __init__(self):
        self.connection = sqlite3.connect(NormalisationDataBase.DB_LOCATION)
        self.cur = self.connection.cursor()

    # @timeit
    def isFrenchStopword(self, token):
        sql = "SELECT mot FROM stopwords_fr WHERE mot=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return True

    # @timeit
    def isEnglishStopword(self, token):
        sql = "SELECT mot FROM stopwords_eng WHERE mot=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return True

    # @timeit
    def isSAPterm(self, token):
        sql = "SELECT mot FROM sap WHERE mot=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return True

    # @timeit
    def isUnique(self, token):
        sql = "SELECT mot FROM mots_uniques WHERE mot=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return True

    # @timeit
    def frLemmatisation(self, token):
        sql = "SELECT lemme FROM lemmatisation_fr WHERE mot=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return result[0]

    # @timeit
    def isFrLemma(self, token):
        sql = "SELECT lemme FROM lemmatisation_fr WHERE lemme=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return True

    # @timeit
    def isEngLemma(self, token):
        sql = "SELECT lemme FROM lemmatisation_eng WHERE lemme=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return True

    # @timeit
    def engLemmatisation(self, token):
        sql = "SELECT lemme FROM lemmatisation_eng WHERE mot=?"
        self.cur.execute(sql, (token,))
        result = self.cur.fetchone()
        if result is None:
            return False
        else:
            return result[0]

    # @timeit
    def close(self):
        self.cur.close()
        self.connection.close()

    # @timeit
    def commit(self):
        self.connection.commit()
