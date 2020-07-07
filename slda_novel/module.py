import os
from tqdm import tqdm
import numpy as np

import paddlehub as hub
from paddlehub.module.module import moduleinfo
from paddlehub.common.logger import logger

from slda_novel.inference_engine import InferenceEngine
from slda_novel.document import SLDADoc
from slda_novel.semantic_matching import SemanticMatching, WordAndDis
from slda_novel.tokenizer import LACTokenizer, SimpleTokenizer
from slda_novel.config import ModelType
from slda_novel.vocab import Vocab, WordCount


@moduleinfo(
    name="slda_news",
    version="1.0.0",
    summary="This is a PaddleHub Module for SLDA model in novel dataset.",
    author="",
    author_email="",
    type="nlp/topic_model")
class TopicModel(hub.Module):
    def _initialize(self):
        """
        Initialize with the necessary elements.
        """
        self.model_dir = os.path.join(self.directory, 'novel')
        self.conf_file = 'slda.conf'
        self.__engine = InferenceEngine(self.model_dir, self.conf_file)
        self.vocab_path = os.path.join(self.model_dir, 'vocab_info.txt')
        lac = hub.Module(name="lac")
        # self.__tokenizer = SimpleTokenizer(self.vocab_path)
        self.__tokenizer = LACTokenizer(self.vocab_path, lac)

    def infer_doc_topic_distribution(self, document):
        """
        This interface infers the topic distribution of document.
        
        Args:
            document(string): the input document text.

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
            results(dict): contains specific topic's keywords and corresponding 
                           probability.
        """
        EPS = 1e-8
        vocabulary = self.__engine.get_model().get_vocab()
        config = self.__engine.get_config()
        topic_words = self.__engine.get_model().topic_words()
        topic_sum_table = self.__engine.get_model().topic_sum()
        for i in range(config.num_topics):
            def take_elem(word_count):
                return word_count.count
            topic_words[i].sort(key=take_elem, reverse=True)
        results = {}
        if 0 <= topic_id < config.num_topics:
            k = min(k, len(topic_words[topic_id]))
            for i in range(k):
                prob = topic_words[topic_id][i].count / \
                       (topic_sum_table[topic_id] + EPS)
                results[vocabulary[topic_words[topic_id][i].word_id]] = prob
            return results
        else:
            logger.error("%d is out of range!" % topic_id)
