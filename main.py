import random
import json
import os

import streamlit as st
import streamlit.components.v1 as stc
import openai

# html関連を当て込む文字列
css = '''<style>
@import url(https://fonts.googleapis.com/css?family=Montserrat);
* {
  margin: 0;
  padding: 0;
  font-family: "Montserrat", sans-serif;
  /*   outline: 1px solid white; */
}

body {
  background: #fff;
  height: 100vh;
  width: 100%;
  display: flex;
  padding-top: 1rem;
}
.base-container {
  width: 100%;
}
.friend-text-div {
  display: flex;
  margin-left: 0.5rem;
}

.friend-text-div > img {
  height: 2rem;
  align-self: flex-end;
}

.friend-text-container {
  width: 15em;
  display: flex;
  flex-direction: column;
}

.friend-text {
  background: #fff;
  border-style: solid;
  border-color: #EFEFEF;
  border-radius: 0.5rem;
  color: #383838;
  height: fit-content;
  width: fit-content;
  padding: 0.5rem 1rem;
  margin: 0.12rem 0.5rem;
}

.my-text-div {
  display: flex;
  justify-content: flex-end;
}

.my-text-div > img {
  height: 2rem;
  align-self: flex-end;
}

.my-text-container {
  width: 15em;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.my-text {
  background: #EFEFEF;
  background-attachment: fixed;
  color: #383838;
  border-radius: 0.5rem 0.2rem 0.2rem 0.5rem;
  height: fit-content;
  width: fit-content;
  padding: 0.5rem 1rem;
  margin: 0.12rem 0.5rem;
}

.my-text-container > div:first-child {
  border-radius: 0.5rem 1rem 0.2rem 0.5rem;
}
.my-text-container > div:last-child {
  border-radius: 0.5rem 0.2rem 1rem 0.5rem;
}
.friend-text-container > div:first-child {
  border-radius: 1rem 0.5rem 0.2rem 0.5rem;
}
.friend-text-container > div:last-child {
  border-radius: 0.5rem 0.2rem 0.5rem 1rem;
}
</style>'''

html = f'''
<html>
<head>
{css}
</head>
<body>
<divs/>
<body>
</body>
</html>
'''

div_base = '''
<div class="base-container">
<conversation/>
</div>
'''

div_friend = '''
  <div class="friend-text-div">
    <img src='https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraight&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light'
/>
    <div class="friend-text-container">
      <div class="friend-text"><txt/></div>
    </div>
  </div>
'''

div_my = '''
  <div class="my-text-div">
    <div class="my-text-container">
      <div class="my-text"><txt/></div>
    </div>
    <img src='https://avataaars.io/?avatarStyle=Circle&topType=LongHairMiaWallace&accessoriesType=Round&hairColor=Blonde&facialHairType=Blank&clotheType=ShirtCrewNeck&clotheColor=Gray02&eyeType=Happy&eyebrowType=Default&mouthType=Default&skinColor=Light'
/>
  </div>
'''
    
def create_conversation_div(comments, speaker1, speaker2):
    """会話のhtmlを作成する"""
    person_divs = []
    # 会話のjsonをイテレートして処理
    for comment in comments:
        if comment['speaker'] == speaker1:
            person_divs.append(div_friend.replace('<txt/>', comment['comment']))
        elif comment['speaker'] == speaker2:
            person_divs.append(div_my.replace('<txt/>', comment['comment']))
        else:
            person_divs.append(div_my.replace('<txt/>', comment['comment']))
    # 結合
    person_txt = ''.join(person_divs) + '\n'
    # はめ込み
    divs = div_base.replace('<conversation/>', person_txt)
    return html.replace('<divs/>', divs)

def get_openai_apikey():
    """openaiのAPIキーを取得"""
    path = r'E:\secrets\openai_apikey.txt'
    if os.path.exists(path): # localhost
        with open(path, 'r') as f:
            return f.read().replace('\n', '')
    else: # streamlit server
        return st.secrets.OpenaiApiKey.key

def get_chatgpt_content(keyword, speaker1, speaker2):
    """chatGPTからウィキペディアの記事の要約をチャット形式でjsonで出力"""
    openai.api_key = get_openai_apikey()

    content = '''# 指示
ウィキペディアから「{0}」を検索して、その内容を{1}と{2}という二人の女性が質問と回答を繰り返す対話形式で説明してください。
挨拶は不要です。敬語は不要です。ですます調は不要です。二人は親友のように会話します。
会話は読者が楽しめるようにできるだけ面白くしてください。出力はjson形式にしてください。

# json形式
[
    {{"speaker": 女性, "comment": 会話内容}},
    {{"speaker": 女性, "comment": 会話内容}},
    {{"speaker": 女性, "comment": 会話内容}},
    {{"speaker": 女性, "comment": 会話内容}}        
]

# 出力
'''.format(keyword, speaker1, speaker2)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content},
        ]
    )
    jsontxt = response["choices"][0]["message"]["content"]
    return json.loads(jsontxt)

def get_random_wiki_article():
    """csvからウィキペディアの記事をランダムに抽出"""
    with open('articles.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines = lines[1:] # remove the header
    line = random.choice(lines).strip()
    return dict(title=line.split(',')[1], url=line.split(',')[2])

def main():
    # 変数初期化
    if 'visibility' not in st.session_state:
        st.session_state['visibility'] = 'hidden'
    if 'disabled' not in st.session_state:
        st.session_state['disabled'] = False
    if 'placeholder' not in st.session_state:
        st.session_state['placeholder'] = "Wikipediaを検索 👇"

    st.title('📚WikiSum')
    st.text('チャット形式でWikipediaを1分で読もう。')

    # 検索ワード
    keyword_input = st.text_input(
        '',
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder=st.session_state.placeholder,
    )
    keyword = str(keyword_input)

    # 検索ボタン
    search_btn_ph = st.empty()
    search_btn = search_btn_ph.button('検索', disabled=False, key='1')

    # ランダムに記事を選ぶボタン
    random_btn_ph = st.empty()
    random_btn = random_btn_ph.button('ランダム', disabled=False, key='2')

    # 処理待ちの表示
    text_wait = st.empty()

    if search_btn or random_btn:
        # 検索文字列が空ならキャンセル
        if search_btn and keyword.strip() == '':
            return

        # 処理中なのでボタンを無効化
        search_btn_ph.button('検索', disabled=True, key='3')
        random_btn_ph.button('ランダム', disabled=True, key='4')
        text_wait.markdown('**処理中...**')

        # ランダムに記事を選ぶ
        if random_btn:
            keyword = get_random_wiki_article()['title']

        # 処理
        try:
            speaker1 = '明日香'
            speaker2 = '麻衣'
            comments = get_chatgpt_content(keyword, speaker1, speaker2)
            divs = create_conversation_div(comments, speaker1, speaker2)
            divs = divs.replace('\n\n', '\n')
            st.subheader(keyword)
            stc.html(divs, height=800, scrolling=True)
        except:
            st.error('エラー！もう一度試してください。')
        finally:
            # 処理が終わったのでボタンを有効化
            search_btn_ph.button('検索', disabled=False, key='5')
            random_btn_ph.button('ランダム', disabled=False, key='6')
            text_wait.empty()
            st.write('もう一度検索する場合、検索かランダムボタンを2回押してください')
        
if __name__ == '__main__':
    main()
