from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
from datetime import datetime
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbjungle


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/memos', methods=['POST'])
def memo_post():
    currentTime = datetime.now()
    currentTime_string = currentTime.strftime("%Y/%m/%d %H:%M%p %a")
    # 1. 클라이언트로부터 데이터를 받기
    title_receive = request.form['title_give']
    text_receive = request.form['content_give']
    color_receive = request.form['color_give']
    # 3. mongoDB에 데이터 넣기
    last_id = db.memos.find_one(sort=[("_id", -1)])

    if last_id is None:
        last_id = 0
    else:
        last_id = last_id['_id']

    doc = {
        '_id': last_id + 1,
        'title': title_receive,
        'text': text_receive,
        'likes': 0,
        'time': currentTime_string,
        'color': color_receive,
    }
    db.memos.insert_one(doc)
    print('완료: ', title_receive, text_receive, currentTime_string)
    return jsonify({'result': 'success', 'msg': '포스팅 성공!'})


@app.route('/memos', methods=['GET'])
def memos_get():
    result = list(db.memos.find({}).sort('likes', -1))
    return jsonify({'result': 'success', 'msg': '이 요청은 GET!', 'memos': result})


@ app.route('/memos/edit', methods=['POST'])
def edit_memo():
    data_id = request.form['id']
    new_title = request.form['editTitle_give']
    new_text = request.form['editText_give']
    db.memos.update_one({'_id': int(data_id)}, {
        '$set': {'title': new_title, 'text': new_text}})

    return jsonify({'result': 'success', 'msg': '수정 완료!'})


@ app.route('/memos/like', methods=['POST'])
def like_memo():

    data_id = request.form['id']
    memo = db.memos.find_one({'_id': int(data_id)})

    new_likes = memo['likes'] + 1

    result = db.memos.update_one({'_id': int(data_id)}, {
        '$set': {'likes': new_likes}})

    if result.modified_count == 1:
        return jsonify({'result': 'success', "msg": '좋아요 완료!'})
    else:
        return jsonify({'result': 'failure'})


@app.route('/memos/delete', methods=['DELETE'])
def memos_delete():
    data_id = request.form['id']

    result = db.memos.delete_one({'_id': int(data_id)})

    if result.deleted_count == 1:
        return jsonify({'result': 'success', 'msg': '삭제 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
