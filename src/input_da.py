import tensorflow as tf
import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer as TFIDFVec
from sklearn.feature_extraction.text import CountVectorizer as TFVec
from sklearn.metrics.pairwise import cosine_similarity


VERBOSE = True

def get_input_fn(mode=None):
    """Creates an input function that loads the dataset and prepares it for use."""

    def _input_fn(mode=None, params=None):
        """
        Returns:
            An (one-shot) iterator containing (data, label) tuples
        """
        with tf.device('/cpu:0'):
            if mode == 'train':
                dataset = None
            elif mode == 'eval' or mode == 'predict':
                dataset = None
            else:
                raise ValueError('_input_fn received invalid MODE')
        return dataset

    return _input_fn





def get_input_fn_nli(mode=None):
    """Creates an input function that loads the dataset and prepares it for use."""

    def _input_fn(mode=None, params=None):
        """
        Returns:
            An (one-shot) iterator containing (data, label) tuples
        """
        with tf.device('/cpu:0'):
            if mode == 'train':
                ds_gen = load_nli("example_train.")
            elif mode == 'eval' or mode == 'predict':
                ds_gen = load_nli("example_dev.csv")
            else:
                raise ValueError('_input_fn received invalid MODE')

            #TODO: lookup tf.<data.type> and shape for these textdata/ask Ben
            dataset = tf.data.Dataset.from_generator(
                generator = ds_gen,
                output_types = (tf.int64, tf.int64),
                output_shapes = (tf.TensorShape([]), tf.TensorShape([None]))
            )

        return dataset.make_one_shot_iterator().get_next()

    return _input_fn

def load_nli(file):
    """
    yields the data of next claim in order: claim, evidences, label
    :param file:
    :return:
    """

    with open(file, "r") as read_file:
        data = json.load(read_file)

    claims,evidences,documents,labels = get_claim_evidence_pairs(data)

    tf_vec = TFVec(stop_words="english", max_features=5000).fit(documents)
    tfidf_vec = TFIDFVec(stop_words="english", max_features=5000).fit(documents)
    # TODO: store it, so can be called during testing
    del documents
    tf_claims = tf_vec.transform(claims)
    tf_evidences = tf_vec.transform(evidences)
    tfidf_claims = tfidf_vec.transform(claims)
    tfidf_evidences = tfidf_vec.transform(evidences)
    tfidf_sims = cosine_similarity(tfidf_claims,tfidf_evidences)
    del tfidf_claims, tfidf_evidences


    for tf_claim, tf_evidence,tfidf_sim,label  in zip(tf_claims,tf_evidences, tfidf_sims,labels):
        # see paper: p. 3 A_simple_but_tough_to_beat_baseline
        yield tf_claim, tfidf_sim, tf_evidence, label

def get_claim_evidence_pairs(dict, mode="concat", concat_evidence=True):
    print("\nclaim\n", dict["claim"], "\n\nevidence\n", dict["evidence"])

    claim_list, evidence_list, label_list, document_list = [], [], [], []
    for claim_set in dict:
        # get evidence
        concat = ""
        for evidence in claim_set["evidence"]:
            concat += evidence
        if concat_evidence:
            evidence_list.append(concat)
        else:
            evidence_list.append(claim_set["evidence"])
        # get claim
        claim_list.append(claim_set["claim"])
        # get whole document
        concat += claim_set["claim"]
        document_list.append(concat)
        # get labels
        label_list = claim_set["label"]

    return claim_list, evidence_list, document_list, label_list




#TODO: how to integrate word embedding transform

def get_input_fn_fever(mode=None):
    """Creates an input function that loads the dataset and prepares it for use."""

    def _input_fn(mode=None, params=None):
        """
        Returns:
            An (one-shot) iterator containing (data, label) tuples
        """
        with tf.device('/cpu:0'):
            if mode == 'train':
                ds_gen = load_fever_chunk("example_train.csv",chunk_size=2)
            elif mode == 'eval' or mode == 'predict':
                ds_gen = load_fever_chunk("example_dev.csv", chunk_size=2)
            else:
                raise ValueError('_input_fn received invalid MODE')

            #TODO: lookup tf.<data.type> and shape for these textdata/ask Ben
            dataset = tf.data.Dataset.from_generator(
                generator = ds_gen,
                output_types = (tf.int64, tf.int64),
                output_shapes = (tf.TensorShape([]), tf.TensorShape([None]))
            )

        return dataset.make_one_shot_iterator().get_next()

    return _input_fn

def load_fever_chunk(file,chunk_size=1000):
    """
    Fever specific data set loading by chunks
    :param file:
    :param chunk_size:
    :return:
    """
    #TODO: Treat special case: len(file) not dividable by chunk_size

    # pd.read_csv('pandas_dataframe_importing_csv/example.csv', na_values=sentinels, skiprows=3)
    # pd.read_csv('pandas_dataframe_importing_csv/example.csv', na_values=sentinels, skipfooter=2)

    for begin,end in []:
        df = pd.read_csv(file, skiprows=begin, skipfooter=end)




if __name__ == "__main__":
    a = load_nli(file="/workData/Uni/NLP/project/fever-nli/data/example_train.csv")
    print(a)