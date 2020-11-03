import json, re, datetime, sys, itertools, progressbar, functools
sys.path.append('.')
from classes.messagedelta import MessageDelta
from classes.normalisation2 import Normalisation2
from classes.modeledelta import Modeledelta
from classes.normalisationdatabase import NormalisationDataBase


if __name__ == '__main__':
    
    # object instanciation
    db = NormalisationDataBase()
    delta = MessageDelta()
    norma = Normalisation2(db)
    modelDelta = Modeledelta()
    print()
    print("extraction depuis {}".format(delta.derniere_maj))

    # sauvegarde date et heure avant extraction
    delta.saveDeltaDate()
    
    # extraction from solman since this date
    delta_bow = delta.getMessageDeltaFromSolman()

    # sauvegarde les messages extraits
    delta.saveDeltaMessages(delta_bow)
    print("delta : {} messages".format(len(delta_bow)))

    bar = progressbar.ProgressBar(maxval=len(delta_bow), \
        widgets=[progressbar.Bar('=', 'Normalisation [', ']'), ' ', progressbar.Percentage()] )
    c = 0
    bar.start()

    # normalisation
    delta_doc = {}
    c = 0
    for m, val in delta_bow.items():
        bar.update(c)
        foo = norma.pap_normalize(val['texte'])
        delta_doc[m] = foo
        c += 1
        del foo
    bar.finish()

    # update or add the extraction to the corpus index
    new_docs, new_numbers = modelDelta.appendToIndex(delta_doc)

    # identify unique words
    new_unique = norma.getUniqueWords(corpus_normalized=new_docs, numbers=new_numbers)

    # compute terms frequency
    new_frequence = modelDelta.getFrequency(bow_normalized=new_docs)

    print("Generation modele ...\n")

    # get the corpus without unique words, token below frequency_threshold, without stopwords
    new_corpus = modelDelta.getCorpus(bow_normalized=new_docs, unique=new_unique, frequence=new_frequence)

    # get and save the dictionary from corpus that gensim will use 
    new_dictionary = modelDelta.getGensimDictionary(gensim_corpus=new_corpus)

    # get and save the gensim corpus (doc2bow format => idToken:tokenCount)
    new_gensim_corpus = modelDelta.getGensimCorpus(corpus=new_corpus, dictionary=new_dictionary)

    # compute and save the model
    new_classic_model = modelDelta.getTfidfClassicModel(gensim_corpus=new_gensim_corpus)
    new_custom_model = modelDelta.getTfidfCustomModel(gensim_corpus=new_gensim_corpus, dictionnaire=new_dictionary)

    # generate and save the sparse_matrix from which the cosine distances will be compute
    new_classic_matrix = modelDelta.createClassicSparseMatrix(tfidf_classic=new_classic_model, gensim_corpus=new_gensim_corpus, dictionary=new_dictionary)
    new_custom_matrix = modelDelta.createCustomSparseMatrix(tfidf_custom=new_custom_model, gensim_corpus=new_gensim_corpus, dictionary=new_dictionary)

    print("nouveaux", len(modelDelta.new_messages))
    print("modifiés", len(modelDelta.messages_updated))

    # TODO
    # contrôler que prog s'est correctement exécuté
    # remplacer le modèle par le nouveau