import requests, json, marshal, pickle, datetime, re, copy, itertools, progressbar
from collections import defaultdict
from gensim import corpora, models, similarities

class Modeledelta(object):

    # with open("/smartsolman/data/stopwords_v1.2","rb") as f:
    #     STOPWORDS_FR = pickle.load(f)

    # with open("/smartsolman/data/english_stopwords_merge_of_nltk_spacy_gensim","r") as f:
    #     STOPWORDS_ENG = json.load(f)

    # with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model2/full_dico_unique","r") as u:
    #     UNIQUE = json.load(u).keys()

    # with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model2/full_dico","r") as u:
    #     FULL_DICT = json.load(u).keys()

    # with open("/smartsolman/data/src/fautes_orthographe/dev/dict_fautes_orthographes_92.json","r") as f:
    #     CORRECTION_ORTHOGRAPHE = json.load(f)

    with open("/smartsolman/data/dev/SparseMatrixSimilarity/full_model2/docNormalized","r") as f:
        DOC = json.load(f)

    NUMBERS = marshal.load(open("/smartsolman/data/dev/SparseMatrixSimilarity/full_model2/list_numbers", "rb"))
    
    SEUIL_FREQ = 12.0
    TERMS_FREQ = ["b","n","a","l","d","L"]
    DOCS_FREQ = ["n","f","t","p"]
    DOCS_NORM = ["n","c","u","b"]
    
    def __init__(self):
        self.status = "Hold The DOOR !!!"
        self.messages_updated = []
        self.new_messages = []
        self.smartirs = list(map(lambda para: para[0]+para[1]+para[2] ,list(itertools.product(Modeledelta.TERMS_FREQ, Modeledelta.DOCS_FREQ, Modeledelta.DOCS_NORM))))
        self.param = open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model2/parametresSMARTIRS","r").read()

    def getFrequency(self, bow_normalized: dict):
        counting = len(bow_normalized)
        frequency = defaultdict(int)

        bar = progressbar.ProgressBar(maxval=len(bow_normalized), \
            widgets=[progressbar.Bar('=', 'Frequence [', ']'), ' ', progressbar.Percentage()] )
        c = 0
        bar.start()

        for texte in bow_normalized:
            bar.update(c)
            for token in texte:
                frequency[token] += (1 * 100)/counting
                frequency[token] = round(frequency[token], 3) 
            c += 1
        bar.finish()

        with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/frequence","w") as f:
            json.dump(frequency, f)

        return frequency

    def appendToIndex(self, delta_doc: dict):
        doc = copy.deepcopy(Modeledelta.DOC)
        numbers = copy.deepcopy(Modeledelta.NUMBERS)

        assert len(doc) == len(numbers), "ModelFilesIndexError after loading"

        bar = progressbar.ProgressBar(maxval=len(delta_doc), \
            widgets=[progressbar.Bar('=', 'MAJ Index [', ']'), ' ', progressbar.Percentage()] )
        c = 0
        bar.start()

        for n_msg, message in delta_doc.items():
            bar.update(c)
            # si le message existe déjà
            if int(n_msg) in numbers:
                # replace 'message' to docNormalized
                index = numbers.index(int(n_msg))
                doc[index] = message
                self.messages_updated.append(n_msg)
            else:
            # Si est un nouveau message
                # append 'n_msg' to numbers AND append 'message' to docNormalized
                numbers.append(int(n_msg))
                doc.append(message)
                self.new_messages.append(n_msg)
            c += 1
        bar.finish()
        assert len(doc) == len(numbers), "ModelFilesIndexError after delta update"

        # TODO sauvegarder le nouvel index dans ./full_model_buffer
        # docNormalized
        # numbers

        marshal.dump(numbers, open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/list_numbers", 'wb'))

        with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/docNormalized","w") as f:
            json.dump(doc, f)

        return doc, numbers

    def getCorpus(self, bow_normalized, unique, frequence):
        texts = [[token for token in texte 
                    if frequence[token] < self.SEUIL_FREQ 
                    if not token in unique.keys() 
                    if not token in Modeledelta.STOPWORDS_FR 
                    if not token in Modeledelta.STOPWORDS_ENG] 
                for texte in bow_normalized]
        return texts

    def getGensimDictionary(self, gensim_corpus):
        dictionnaire = corpora.Dictionary(gensim_corpus)
        dictionnaire.save('/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/specifiques.dict')
        dictionnaire.save_as_text('/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/gensimDictionary.txt')
        return dictionnaire

    def getGensimCorpus(self, corpus, dictionary):
        gensim_corpus = [dictionary.doc2bow(text) for text in corpus]
        corpora.MmCorpus.serialize('/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/specifiques.mm', gensim_corpus)
        return gensim_corpus

    def getTfidfClassicModel(self, gensim_corpus):
        tfidf_classic = models.TfidfModel(corpus=gensim_corpus, normalize=True) 
        tfidf_classic.save("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/classic_model/tfidf_classic.model")
        return tfidf_classic

    def getTfidfCustomModel(self, gensim_corpus, dictionnaire):
        assert self.param in self.smartirs, "AttributeError: le paramètre smartirs n'existe pas"
        tfidf_custom = models.TfidfModel(corpus=gensim_corpus, dictionary=dictionnaire, smartirs=self.param) 
        tfidf_custom.save("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/custom_model/tfidf_custom.model")
        return tfidf_custom

    def createClassicSparseMatrix(self, tfidf_classic, gensim_corpus, dictionary):
        index_classic = similarities.SparseMatrixSimilarity(tfidf_classic[gensim_corpus], num_features=len(dictionary))
        index_classic.save('/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/classic_model/sparse.index', separately=["index"])

    def createCustomSparseMatrix(self, tfidf_custom, gensim_corpus, dictionary):
        index_custom = similarities.SparseMatrixSimilarity(tfidf_custom[gensim_corpus], num_features=len(dictionary))
        index_custom.save('/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/custom_model/{}/sparse.index'.format(self.param), separately=["index"])
