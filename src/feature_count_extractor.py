import sys
import nltk
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TreebankWordTokenizer

nltk.download('wordnet')
wordnet_lemmatizer = WordNetLemmatizer()

# a function to lemmatize words, e.g. 'masters degree' --> 'master degree'
def lemmatizing_preprocessor(text):
    text = text.lower()
    text = text.replace('\'', '')  # e.g. master's --> masters, for lemmatizing
    punctuations = "?:!.,;"
    sentence_words = nltk.word_tokenize(text)
    for word in sentence_words:
        if word in punctuations:
            sentence_words.remove(word)

    text = ' '.join([wordnet_lemmatizer.lemmatize(word) for word in sentence_words])
    return text


def load_skills(path):
    file = open(path, "r")
    try:
        contents = file.read()
        skills_dict = ast.literal_eval(contents)
    finally:
        file.close()

    return skills_dict

def load_stopwords_list():
    stopwords_file = open("resources/stopwords.txt", "r")
    try:
        content = stopwords_file.read()
        stopwords = content.split(",")
    finally:
        stopwords_file.close()

    return stopwords


# create a non-lemmatizing count vectorizer with a given vocabulary and n-gram range, uses default 'word' analyzer
def create_nonlemma_vectorizer(vocab, g_min, g_max, stopwords_list):
    vectorizer = CountVectorizer(ngram_range=(g_min, g_max), vocabulary=vocab, analyzer='word', stop_words=stopwords_list)
    return vectorizer


# create a lemmatizing count vectorizer with a given vocabulary and n-gram range
# usese tokenizer that keeps numbers as well
def create_lemmatizing_vectorizer(vocab, g_min, g_max, stopwords_list):
    lemma_vectorizer = CountVectorizer(ngram_range=(g_min, g_max), vocabulary=vocab,
                                       tokenizer=TreebankWordTokenizer().tokenize, stop_words=stopwords_list)
    return lemma_vectorizer


# count skills with given vectorizer and data (list of documents)
# produces a pandas dataframe with counts
def count_skills(vectorizer, doc_list):
    count_vector = vectorizer.fit_transform(doc_list)
    counts = count_vector.getnnz(axis=0)
    feature_names = vectorizer.get_feature_names()
    results = pd.DataFrame({'Skill': feature_names, 'Count': counts})
    results['Frequency'] = results['Count'] / len(doc_list)

    return results

#check command line arguments
if len(sys.argv) != 2:
    print('Wrong number of arguments.')
    exit()

job_title = sys.argv[1]
if job_title not in ('analyst', 'engineer', 'scientist'):
    print('Argument not recognized.')
    exit()

#load data
jobs = pd.read_csv('processed-data/df_filtered.csv')

#take only rows for the given job type
if(job_title == 'analyst'):
    jobs = jobs[ jobs['Job Type'] == 'data analyst' ]
elif(job_title == 'engineer'):
    jobs = jobs[ jobs['Job Type'] == 'data engineer' ]
elif(job_title == 'scientist'):
    jobs = jobs[ jobs['Job Type'] == 'data scientist']

#lemmatize job descriptions to get base form
jobs['description_lemmatized'] = jobs['Job Description'].apply(lemmatizing_preprocessor)
non_lemmatized_data = jobs['Job Description'].to_list()
lemmatized_data = jobs['description_lemmatized'].to_list()

stopwords_list = load_stopwords_list()

# extract education
ed_vocab = load_skills('resources/dict_education.txt')
ed_vectorizer = create_lemmatizing_vectorizer(ed_vocab, 2, 2,stopwords_list)
ed_results = count_skills(ed_vectorizer, lemmatized_data)
ed_results.to_csv('processed-data/'+job_title+'-counts-education.csv')

# extract experience
exp_vocab = load_skills('resources/dict_experience.txt')
exp_vectorizer = create_lemmatizing_vectorizer(exp_vocab, 3, 3,stopwords_list)
exp_results = count_skills(exp_vectorizer, lemmatized_data)
exp_results.to_csv('processed-data/'+job_title+'-counts-experience.csv')

# extract datastore skills
db_vocab = load_skills('resources/dict_skills_datastores.txt')
db_vectorizer = create_nonlemma_vectorizer(db_vocab, 1, 2,stopwords_list)
db_results = count_skills(db_vectorizer, non_lemmatized_data)
db_results.to_csv('processed-data/'+job_title+'-counts-skill-datastores.csv')

# extract cloud providers
cp_vocab = load_skills('resources/dict_skills_cloudproviders.txt')
cp_vectorizer = create_lemmatizing_vectorizer(cp_vocab, 1, 3,stopwords_list)
cp_results = count_skills(cp_vectorizer, non_lemmatized_data)
cp_results.to_csv('processed-data/'+job_title+'-counts-skill-cloudproviders.csv')

# extract data formats
df_vocab = load_skills('resources/dict_skills_dataformats.txt')
df_vectorizer = create_lemmatizing_vectorizer(df_vocab, 1, 1,stopwords_list)
df_results = count_skills(df_vectorizer, non_lemmatized_data)
df_results.to_csv('processed-data/'+job_title+'-counts-skill-dataformats.csv')

# extract data pipelines
dp_vocab = load_skills('resources/dict_skills_datapipelines.txt')
dp_vectorizer = create_lemmatizing_vectorizer(dp_vocab, 1, 2,stopwords_list)
dp_results = count_skills(dp_vectorizer, non_lemmatized_data)
dp_results.to_csv('processed-data/'+job_title+'-counts-skill-datapipelines.csv')

# extract general data analytics skills / keywords
ga_vocab = load_skills('resources/dict_skills_generalanalytics.txt')
ga_vectorizer = create_lemmatizing_vectorizer(ga_vocab, 1, 2,stopwords_list)
ga_results = count_skills(ga_vectorizer, non_lemmatized_data)
ga_results.to_csv('processed-data/'+job_title+'-counts-skill-generalanalytics.csv')

# extract general miscellaneous keywords
gm_vocab = load_skills('resources/dict_skills_generalmisc.txt')
gm_vectorizer = create_lemmatizing_vectorizer(gm_vocab, 2, 2,stopwords_list)
gm_results = count_skills(gm_vectorizer, lemmatized_data)
gm_results.to_csv('processed-data/'+job_title+'-counts-skill-generalmisc.csv')

# extract programming languages
pl_vocab = load_skills('resources/dict_skills_programminglanguages.txt')
pl_vectorizer = create_lemmatizing_vectorizer(pl_vocab, 1, 1,stopwords_list)
pl_results = count_skills(pl_vectorizer, non_lemmatized_data)
pl_results.to_csv('processed-data/'+job_title+'-counts-skill-programminglanguages.csv')
