import re
import jieba
import pickle
from config import input_file, stopwords_file


def load_stop_words():
    # 加载停用词
    stop_words = set()
    with open(stopwords_file, encoding="utf-8") as f1:
        for line in f1.readlines():
            stop_words.add(line.strip())
        stop_words.add(" ")
    return stop_words

def chinese_word_extraction(content_raw):
    '''只保留中文词
    '''
    chinese_pattern = u"([\u4e00-\u9fa5]+)"
    chi_pattern = re.compile(chinese_pattern)
    re_data = chi_pattern.findall(content_raw)
    content_clean  = ' '.join(re_data)
    return content_clean

def pre_processing(line):
    """对一行语料进行预处理，包括去除中文词以外的字符、分词。
    返回一行字符串
    """
    stop_words = load_stop_words()
    line = chinese_word_extraction(line)
    word_list = list(jieba.cut_for_search(line))
    output_line = ""
    for word in word_list:
        if word not in stop_words:
            output_line = output_line + word.strip() + " "
    return output_line

def load_raw_docs(input_file):
    """获取原始文档内容
    """
    doc_f = open(input_file,'r')
    docs = []
    for line in doc_f.readlines():
        docs.append(line)
    doc_f.close()
    return docs

def check_syntax(expression, **variables):
    """检查表达式合法性
    """
    try:
        eval(expression, variables)
    except (SyntaxError, NameError, ZeroDivisionError):
        return False
    else:
        return True

def parse_query(query):
    """解析用户的query表达式
    """
    operators = {'(',')','&','|','-'}
    exps = [] # 保存格式化后的表达式
    words_query = [] # 
    
    cnt = 0
    pre = 0
    for idx in range(len(query)):
        w = query[idx]
        if w in operators:
            if idx>0 and pre<idx:
                exps.append('variables[{0}]'.format(cnt))
                words_query.append(query[pre:idx])
                cnt += 1
            exps.append(w)
            pre = idx+1
    if pre!=len(query):
        exps.append('variables[{0}]'.format(cnt))
        words_query.append(query[pre:])
        cnt+=1
            
    return exps, words_query

def find_docs_by_words(words, word2docs):
    """返回包含words的文档id集合
    """
    if len(words)==0:
        return set()
    for word in words:
        if word not in word2docs.keys():
            return set()
    rst_docs = word2docs[words[0]]
    for word in words[1:]:
        rst_docs &= word2docs[word]
    return rst_docs

def eval_exps(expression, words_query, word2docs):
    """计算符合条件的文档集合
    """
    exps_docs = []
    for item in words_query:
        words = pre_processing(item)
        exps_docs.append(find_docs_by_words(words.split(), word2docs))
    return eval(expression, {"variables":exps_docs})

def show(ids,n,raw_docs):
    """打印搜索结果
    """
    print("搜索结果：")
    print("搜索到满足条件的文档数{0}。".format(len(ids)))
    for i in list(ids)[:n]:
        print('document{0}:'.format(i))
        print(raw_docs[i])
        
lexicon = pickle.load(open('./cache/lexicon.k','rb'))
lexicon_doc = pickle.load(open('./cache/lexicon_doc.k','rb'))
word2docs = pickle.load(open('./cache/word2docs.k', 'rb'))
raw_docs = load_raw_docs(input_file)

def search(query, n=10):
    """
    """
    exps, words_query = parse_query(query)
    islegal = check_syntax(''.join(exps), variables=[set() for i in range(len(exps))])
    if not islegal:
        print('表达式不合法！请重新输入。')
        return 
    ids = eval_exps(''.join(exps), words_query, word2docs)
    show(ids,n,raw_docs)

