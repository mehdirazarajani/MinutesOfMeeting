import fasttext.util
import fasttext

if __name__ == '__main__':
    # fasttext.util.download_model('en', if_exists='ignore')  # English
    ft = fasttext.load_model('crawl-300d-2M-subword.bin')
    print(ft.get_dimension())
    print(ft.get_dimension())
    print(ft.get_word_vector('hello').shape)
    print(ft.get_nearest_neighbors('hello'))