import os
from tqdm import tqdm
import numpy as np

import paddlehub as hub
from paddlehub.module.module import moduleinfo
from paddlehub.common.logger import logger

from slda_webpage.inference_engine import InferenceEngine
from slda_webpage.document import SLDADoc
from slda_webpage.semantic_matching import SemanticMatching, WordAndDis
from slda_webpage.tokenizer import LACTokenizer, SimpleTokenizer
from slda_webpage.config import ModelType
from slda_webpage.vocab import Vocab, WordCount


@moduleinfo(
    name="slda_webpage",
    version="1.0.0",
    summary="This is a PaddleHub Module for SLDA topic model in webpage dataset, where we can infer the topic distribution of document.",
    author="baidu",
    author_email="",
    type="nlp/semantic_model")
class TopicModel(hub.Module):
    def _initialize(self):
        """
        Initialize with the necessary elements.
        """
        self.model_dir = os.path.join(self.directory, 'webpage')
        self.conf_file = 'slda.conf'
        self.__engine = InferenceEngine(self.model_dir, self.conf_file)
        self.vocab_path = os.path.join(self.model_dir, 'vocab_info.txt')
        lac = hub.Module(name="lac")
        # self.__tokenizer = SimpleTokenizer(self.vocab_path)
        self.__tokenizer = LACTokenizer(self.vocab_path, lac)

        self.vocabulary = self.__engine.get_model().get_vocab()
        self.config = self.__engine.get_config()
        self.topic_words = self.__engine.get_model().topic_words()
        self.topic_sum_table = self.__engine.get_model().topic_sum()

        def take_elem(word_count):
                return word_count.count
        for i in range(self.config.num_topics):
            self.topic_words[i].sort(key=take_elem, reverse=True)

        logger.info("Finish Initialization.")

    def infer_doc_topic_distribution(self, document):
        """
        This interface infers the topic distribution of document.
        
        Args:
            document(str): the input document text.

        Returns: 
            results(list): returns the topic distribution of document.
        """
        tokens = self.__tokenizer.tokenize(document)
        if tokens == []:
            return []
        results = []
        sentences = []
        sent = []
        for i in range(len(tokens)):
            sent.append(tokens[i])
            if len(sent) % 5 == 0:
                sentences.append(sent)
                sent = []
        if len(sent) > 0:
            sentences.append(sent)
        
        doc = SLDADoc()
        self.__engine.infer(sentences, doc)
        topics = doc.sparse_topic_dist()
        for topic in topics:
            results.append({"topic id": topic.tid, "distribution": topic.prob})
        return results

    def show_topic_keywords(self, topic_id, k=10):
        """
        This interface returns the k keywords under specific topic.
        
        Args:
            topic_id(int): topic information we want to know.
            k(int): top k keywords.

        Returns:
            results(dict): contains specific topic's keywords and 
                     corresponding probability.
        """
        EPS = 1e-8
        results = {}
        if 0 <= topic_id < self.config.num_topics:
            k = min(k, len(self.topic_words[topic_id]))
            for i in range(k):
                prob = self.topic_words[topic_id][i].count / \
                       (self.topic_sum_table[topic_id] + EPS)
                results[self.vocabulary[self.topic_words[topic_id][i].word_id]] = prob
            return results
        else:
            logger.error("%d is out of range!" % topic_id)

    def cal_doc_keywords_similarity(self, document, top_k=10):
        """
        This interface can be used to find topk keywords of document.
        
        Args:
            document(str): the input document text.
            top_k(int): top k keywords of this document.

        Returns:
            results(list): contains top_k keywords and their corresponding 
                           similarity compared to document.
        """
        tokens = self.__tokenizer.tokenize(document)
        sentences = []
        sent = []
        for i in range(len(tokens)):
            sent.append(tokens[i])
            if len(sent) % 5 == 0:
                sentences.append(sent)
                sent = []
        if len(sent) > 0:
            sentences.append(sent)
        # Do topic inference on documents to obtain topic distribution.
        doc = SLDADoc()
        self.__engine.infer(sentences, doc)
        doc_topic_dist = doc.sparse_topic_dist()
        items = []
        words = set()
        for word in tokens:
            if word in words:
                continue
            words.add(word)
            wd = WordAndDis()
            wd.word = word
            sm = SemanticMatching()
            wd.distance = sm.likelihood_based_similarity(terms=[word],
                                                         doc_topic_dist=doc_topic_dist,
                                                         model=self.__engine.get_model())
            items.append(wd)
        
        def take_elem(word_dis):
            return word_dis.distance

        items.sort(key=take_elem, reverse=True)

        results = []
        size = len(items)
        for i in range(top_k):
            if i >= size:
                break
            results.append({"word": items[i].word, "similarity": items[i].distance})
        return results

    def cal_doc_distance(self, doc_text1, doc_text2):
        """
        This interface calculates the distance between documents.
        
        Args:
            doc_text1(str): the input document text 1.
            doc_text2(str): the input document text 2.
        
        Returns:
            jsd(float): Jensen-Shannon Divergence distance of two documents.
            hd(float): Hellinger Distance of two documents.
        """
        doc1_tokens = self.__tokenizer.tokenize(doc_text1)
        doc2_tokens = self.__tokenizer.tokenize(doc_text2)

        doc1_sents, doc2_sents = [], []
        sent1 = []
        for i in range(len(doc1_tokens)):
            sent1.append(doc1_tokens[i])
            if len(sent1) % 5 == 0:
                doc1_sents.append(sent1)
                sent1 = []
        if len(sent1) > 0:
            doc1_sents.append(sent1)

        sent2 = []
        for i in range(len(doc2_tokens)):
            sent2.append(doc2_tokens[i])
            if len(sent2) % 5 == 0:
                doc2_sents.append(sent2)
                sent2 = []
        if len(sent2) > 0:
            doc2_sents.append(sent2)
        
        # Document topic inference.
        doc1, doc2 = SLDADoc(), SLDADoc()
        self.__engine.infer(doc1_sents, doc1)
        self.__engine.infer(doc2_sents, doc2)

        # To calculate jsd, we need dense document topic distribution.
        dense_dict1 = doc1.dense_topic_dist()
        dense_dict2 = doc2.dense_topic_dist()
        # Calculate the distance between distributions.
        # The smaller the distance, the higher the document semantic similarity.
        sm = SemanticMatching()
        jsd = sm.jensen_shannon_divergence(dense_dict1, dense_dict2)
        hd = sm.hellinger_distance(dense_dict1, dense_dict2)

        return jsd, hd

    def cal_query_doc_similarity(self, query, document):
        """
        This interface calculates the similarity between query and document.
        
        Args:
            query(str): the input query text.
            document(str): the input document text.

        Returns:
            slda_sim(float): likelihood based similarity between query and document 
                            based on SLDA.
        """
        q_tokens = self.__tokenizer.tokenize(query)
        d_tokens = self.__tokenizer.tokenize(document)
        sentences = []
        sent = []
        for i in range(len(d_tokens)):
            sent.append(d_tokens[i])
            if len(sent) % 5 == 0:
                sentences.append(sent)
                sent = []
        if len(sent) > 0:
            sentences.append(sent)

        doc = SLDADoc()
        self.__engine.infer(sentences, doc)
        doc_topic_dist = doc.sparse_topic_dist()
        sm = SemanticMatching()
        slda_sim = sm.likelihood_based_similarity(q_tokens,
                                                  doc_topic_dist,
                                                  self.__engine.get_model())
        return slda_sim