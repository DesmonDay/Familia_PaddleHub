# 如何使用

## 如何使用LDA模型

对于LDA模型，你可以直接使用PaddleHub 1.8版本已集成好的模型，具体可以访问：https://www.paddlepaddle.org.cn/hublist?filter=en_category&value=SemanticModel 

网页中包含了详细的使用文档，可自行查看。

## 如何使用SLDA模型

对于SLDA模型，由于目前python版本占用内存较大，使用起来会耗比较多的系统资源，因此未集成到官方的PaddleHub中。后续会进行一定的改进。

对于slda_novel和slda_weibo，这两个模型占用资源情况比较正常；但对于slda_webpage和slda_news这两个模型，由于模型比较大，所以占用的内存也比较大，有可能会让电脑比较卡。

如果你仍然要使用，下面给出具体步骤。

1. 下载对应的模型文件后解压到对应的文件夹，这里对应的模型文件可以到此处下载：
- slda_news(不建议使用): https://bj.bcebos.com/paddlehub/model/nlp/semantic_model/slda_news.tar.gz
- slda_weibo: https://bj.bcebos.com/paddlehub/model/nlp/semantic_model/slda_weibo.tar.gz
- slda_novel: https://bj.bcebos.com/paddlehub/model/nlp/semantic_model/slda_novel.tar.gz
- slda_webpage(不建议使用): https://bj.bcebos.com/paddlehub/model/nlp/semantic_model/slda_webpage.tar.gz

2. 在python中使用，以slda_weibo为例(相当于使用本地下载好的模型文件)

``` python
import paddlehub as hub
model = hub.Module(directory="slda_news")
topic_dist = model.infer_doc_topic_distribution("微博是人们发表言论的地方，我们需要这样的自由天地")
keywords = model.show_topic_keywords(topic_id=10, k=10)
```

## 与C++版本Familia的区别

之所以要集成到PaddleHub中，主要原因是编译C++版本的Familia，许多同学会遇到各种环境依赖导致的问题，所以就提供一个python版本的Familia。（比如我，尽管编译C++版本的Familia没有问题，但是尝试使用其生成的familia.so却无法正常使用，也是因为缺少了相关依赖的关系）

python版本与C++版本的主要区别，一个是由于python本身固有的比较慢的文件读取速度，另一个是内存消耗也比C++大。然后在计算结果对比方面，在使用相同的分词器的情况下，在固定随机输入为相同的前提下，两种版本的结果输出一致；因此两者主要的差异是由于random seed导致的。另一方面，我在python版本中使用的分词器为PaddleHub中的LAC分词器，分词效果更加准确，但这也导致了C++版本Familia的一点差异（如果你仍然要使用C++版本中使用的分词器，可以修改module.py中的self.\_\_tokenizer）。