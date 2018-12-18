import twitter #pip install python-twitter
import json
import tltk
tltk.corpus.w2v_load()
api = twitter.Api(consumer_key='n6iKTpsIXeuKk1HLij0tPMMT2',
                  consumer_secret='VGRT2j93HpPik4KGthn0HK8vbhClW3WNwqa64dvb11UMr8oQZz',
                  access_token_key='2370704640-qPoGhhsqwlX1HXfCdTJF4bI8mDuuH8XH0ILsX2T',
                  access_token_secret='ZgcTQj3yaK0ppcRfNtDXUvQEz3T24ZXiTf3Ykhw1NqIxQ')

class ThaiTweet:
    @classmethod        
    def user_timeline(cls,username):
        '''Get twitter username and return twitter timeline.
        '''
        return api.GetUserTimeline(screen_name=username)
    
    def tweet_text(cls,status_item):
        '''Convert Status item to json string.
        Pick only Thai 'text' from json dictionary and return in list.
    
        '''
        twitter_info = json.dumps(status_item._json)
        valid_json_string = '[' + twitter_info + ']'
        data_dictionary = json.loads(valid_json_string)
        if data_dictionary[0]['lang'] == 'th':
            return data_dictionary[0]['text']
        
class ThTwitterAnalysis(ThaiTweet):
    def __init__(self,username):
        self.username = username
        
    def tweet_data(self):
        '''Return list of tweet. None object will be removed from list.
        '''
        data = [self.tweet_text(item) for item in self.user_timeline(self.username)]
        while None in data : data.remove(None)
        return data
        
    #choose sentence to analyze
    def segment_tweet(self,raw_data):
        '''Segment tweet into word and return clean list of words.
        '''
        word_seg = tltk.nlp.word_segment(raw_data)
        return word_seg.replace('<s/>','').split('|')[:-1]
            
    def analyze_tweet_word(self,data_index):
        '''Return list of tuple of word and word existance in corpus.
        
        Arguments:
            data_index = index of tweet to be analyzed
            
        >>>analyze_tweet_word(tweet_data,0)
        => [('อย่า', 'มีคำใน corpus'),
            ('ตื่น', 'มีคำใน corpus'),
            ('ไป', 'มีคำใน corpus'),
            ('!!', 'ไม่ปรากฏคำใน corpus')]
        '''
        if data_index < len(self.tweet_data()):
            raw_data = self.tweet_data()[data_index]
            label_result = {True:'มีคำใน corpus',False:'ไม่ปรากฏคำใน corpus'}
            return [(i,label_result[tltk.corpus.w2v_exist(i)]) for i in self.segment_tweet(raw_data)]
        else:
            print('data_index cannot exceed',len(self.tweet_data())-1)        

class ThTwitterDict(ThTwitterAnalysis):
    def __init__(self,analyzed_tweet):
        self.analyzed_tweet = analyzed_tweet
        
    def save_to_dict(self):
        '''Ask user to input formal Thai word for word 
        that do not exist in tltk corpus.
        Twitter word and fomal Thai word will be saved 
        to twitter_dictionary.txt file.
        '''
        dict_file = open('twitter_dictionary.txt','a+',encoding='utf-8') 
        for item in self.analyzed_tweet:
            if item[1] == 'ไม่ปรากฏคำใน corpus':
                print("Enter formal Thai for",item[0],"(enter 'q' if not necessary)")
                new_word = input(": ")
                if new_word != 'q':
                    dict_file.write('\n')
                    data = (item[0],new_word)
                    dict_file.write(json.dumps(data))
        dict_file.close()
    
    def trans_tweet(self):
        '''Translate twitter language(th) to formal Thai.
        '''
        with open('twitter_dictionary.txt','r',encoding='utf-8') as dict_file:
            dict_data = {}
            for line in dict_file:
                if line != '\n':
                    data = json.loads(line)
                    dict_data[data[0]] = data[1]
        translated_tweet = ''
        for item in self.analyzed_tweet:
            if item[1] == 'มีคำใน corpus' or item[0] == ' ':
                translated_tweet = translated_tweet + item[0]
            elif item[0] in dict_data:
                translated_tweet = translated_tweet + dict_data[item[0]]
            else:
                translated_tweet = translated_tweet + '<' + item[0] +'>'
        return translated_tweet
    
        
        
    