# LDA模型 API 说明 
## cal_doc_distance(doc_text1, doc_text2)
用于计算两个输入文档之间的距离，包括Jensen-Shannon divergence(JS散度)、Hellinger Distance(海林格距离)。

**参数**

- doc_text1(str): 输入的第一个文档。
- doc_text2(str): 输入的第二个文档。

**返回**

- jsd(float): 两个文档之间的JS散度。
- hd(float): 两个文档之间的海林格距离。

## cal_doc_keywords_similarity(document, top_k=10)

用于查找输入文档的前k个关键词。

**参数**

- document(str): 输入文档。
- top_k(int): 查找输入文档的前k个关键词。

**返回**

- results(list): 包含每个关键词以及对应的与原文档的相似度。

## cal_query_doc_similarity(query, document)

用于计算短文档与长文档之间的相似度。

**参数**

- query(str): 输入的短文档。
- document(str): 输入的长文档。

**返回**

- lda_sim(float): 返回短文档与长文档之间的相似度。

## infer_doc_topic_distribution(document)

用于推理出文档的主题分布。

**参数**

- document(str): 输入文档。

**返回**

- results(list): 包含主题分布下各个主题ID和对应的概率分布。

## show_topic_keywords(topic_id, k=10)

用于展示出每个主题下对应的关键词，可配合推理主题分布的API使用。

**参数**

- topic_id(int): 主题ID。
- k(int): 需要知道对应主题的前k个关键词。

**返回**

- results(dict): 返回对应文档的前k个关键词，以及各个关键词在文档中的出现概率。
