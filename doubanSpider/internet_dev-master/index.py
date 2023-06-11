import os
from flask import Flask, render_template, request, redirect, url_for,send_from_directory
# import pandas as pd
import jieba.analyse
from wordcloud import WordCloud
import sqlite3

app = Flask(__name__,template_folder='templates')
data_file = "./text/account.txt"

# 遍历txt文件
def get_saved_data():
    saved_data = []
    with open(data_file, "r") as file:
        f = file.readlines()
        saved_data = [line.strip().split(",") for line in f]
        print(save_data)
    return saved_data
# 新增账号密码信息的保存
def save_data(name, password):
    with open(data_file, "a") as file:
        file.write(f"{name},{password}\n")
        

# 访问根目录
@app.route("/")
def index():
    saved_data = get_saved_data()
    # print(saved_data)
    return render_template("index.html", data=saved_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    print("ck1")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(username,password)
        data = get_saved_data()
        print(data)
        for line in data:
            x,y = line
            if x == username and y == password: # 输入账号密码与account.txt中某一项匹配
                response = redirect(url_for("main")) # 重定向到main
                response.set_cookie("logged_in", "1") # 设置cookies 状态为1
                return response

        
        return "Invalid username or password"

    return render_template("index.html")

#退出登录
# TODO: 
@app.route("/logout")
def logout():
    response = redirect(url_for("login"))
    response.set_cookie("logged_in", "0")
    return response

@app.route("/signin_info")
def signin_info():
     return render_template("signin.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        data = get_saved_data()
        for line in data:
            x,y = line
            if x == username and y == password:
                return "用户已经存在"
        # TODO：将原本文件所有的数据清空了。 completed
        new_line = username +","+password + "\n"
        with open(data_file, "a") as file:
            #file.seek() 应该不用seek函数来定位了（0 for start 1 for present 2 for end）
            file.writelines(new_line)
        # TODO:弹出警告框“注册成功” 
        response = redirect(url_for("main")) # 重定向到main
        response.set_cookie("logged_in", "1") # 设置cookies 状态为1
        return response
        

@app.route("/main", methods=["GET", "POST"])
def main():
    image_url = 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2892024245.webp'
    if not is_user_logged_in():
        return redirect(url_for("login"))
    
    return render_template("main.html", image_url=image_url)

    # 这里是截取的代码，应该无用
    '''
    if request.method == "POST":
        search_name = request.form.get("search")
        saved_data = get_saved_data()

        for item in saved_data:
            if item[0] == search_name:
                return render_template("main.html", result=item[1])

        return render_template("main.html", result=None)

    return render_template("main.html")
    '''
    

# 提供下载功能 “path” 指定要下载的文件
@app.route("/download/<path>")
def download(path):
    return send_from_directory(os.path.join(app.root_path, "downloads"), path,as_attachment=True)

# 判断cookies
def is_user_logged_in():
    return request.cookies.get("logged_in") == "1"

# TODO: 拉取豆瓣网电影以及评论
# TODO： 词云，为每部电影输出特定的词云（尤其是评论中的），并生成词云图.png可供下载 completed
# TODO： 建立收藏。（即新数据库下的增删）。

@app.route("/mv_info")
def mv_info():
    return render_template("mv.html")



@app.route("/wordcloud_info")
def wordcloud_info():
    return render_template("wordcloud.html")

@app.route("/individual")
def individual():
    db_path = 'individual.db'
    import os
    if os.path.exists(db_path):
        datalist = []
        con = sqlite3.connect("individual.db")
        cur = con.cursor()
        sql = "select * from movieinfo"
        data = cur.execute(sql)
        for item in data:
            datalist.append(item)

        cur.close()
        con.close()

        return render_template("individual.html", movies = datalist)
    else:
        sql = '''    
            create table movieinfo
            (
            id integer primary key autoincrement,
            cname varchar,
            fname varchar,
            score numeric,
            rated numeric,
            instruction text
            );
        
        '''
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()

@app.route("/addlike", methods=["GET", "POST"])
def addlike():
    if request.method == "POST":
        mv_name = request.form.get("moviename")
        print(mv_name)
        sql_mv_name = '"' + mv_name + '"'
        
        datalist = []
        showdatalist = []
        conn = sqlite3.connect('movie.db')
        cursor = conn.cursor()
        
        sql = '''
            select
            cname varchar,
            fname varchar,
            score numeric,
            rated numeric,
            instruction text
            from movieinfo
            where cname = (%s)
        '''%sql_mv_name
        data = cursor.execute(sql)
        for item in data:
            datalist.append(item)
        
        if datalist == []:
            return "后台数据库中没有这部电影"
        
        cursor.close()
        conn.close()
        
        datalist = list(datalist[0])
        
        for index in range(len(datalist)):
            datalist[index] = str(datalist[index])
            
        print(datalist)
        for index in range(len(datalist)):
            datalist[index] = '"' + datalist[index] + '"'
        
        con = sqlite3.connect('individual.db')
        cur = con.cursor()
        
        sql = '''
        insert into movieinfo (
            cname,
            fname,
            score,
            rated,
            instruction
        )values (%s)
        '''%",".join(datalist)
        
        sql2 = "select * from movieinfo"
        
        cur.execute(sql)
        data = cur.execute(sql2)
            
        for item in data:
            showdatalist.append(item)

        con.commit()
        cur.close()
        con.close()

    return render_template("individual.html", movies = showdatalist)

@app.route("/deletelike", methods=["GET", "POST"])
def deletelike():
    if request.method == "POST":
        mv_id = request.form.get("movieid")
        sql_mv_id = '"' + mv_id + '"'
        
        datalist = []
        conn = sqlite3.connect('individual.db')
        cursor = conn.cursor()
        sql = "delete from movieinfo where id = (%s)"%sql_mv_id
        sql2 = "select * from movieinfo"
        
        cursor.execute(sql)
        data = cursor.execute(sql2)
        for item in data:
            datalist.append(item)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        
    
    return render_template("individual.html", movies = datalist)
    

# 词云部分
@app.route("/wordcloud", methods=["GET", "POST"])
def wordcloud():
    if request.method == "POST":
        # 获取用户输入的电影名
        mv_name = request.form.get("username")
        print(mv_name)
        data_list = []
        
        sql_mv_name = '"' + mv_name + '"'
        con = sqlite3.connect("movie.db")
        cur = con.cursor()
        sql = "select cname from movieinfo where cname = (%s)"%sql_mv_name
        
        data = cur.execute(sql)
        print(data)
        for item in data:
            data_list.append(item)
            
        cur.close()
        con.close()

        # 在此需做条件判断，若我们保存的txt或者数据库中有该电影则正常执行，否则弹出警告框，提示“目前库中没有相关电影”
        if data_list != []:
            wordcloud_generate(mv_name)
            img_name = mv_name +".jpg" # 生成的文件一定是jpg
            path = "/download/"+img_name
            response = redirect(path) # 重定向到download
            return response
        else:
            return "目前库中没有相关电影"
            
        
        #mv_name = "中文词云图2"
        # TODO 通过在与电影配套的txt文件中（或数据库）中给定评论的list，再调用以下函数生成词云

        
        
    
# 词云生成
def wordcloud_generate(filename):
    # TODO:选择打开文件的方式，例如txt，xmxl等
    # 保存为列表file
    sql_filename = '"' + filename + '"'
    
    data_list = []
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select comments from movieinfo where cname = (%s)"%sql_filename
    
    data = cur.execute(sql)
    for item in data:
        data_list.append(item)
    
    cur.close()
    con.close()
    
    file = data_list[0][0]
    
    words = jieba.lcut(file)     #精确分词
    newwords = ''.join(words)    #空格拼接
    
    wordcloud = WordCloud(width=400,                  # 设置宽为400px
    height=300,                 # 设置高为300px
    background_color='white',    # 设置背景颜色为白色
    #stopwords=stopwords,         # 设置禁用词，在生成的词云中不会出现set集合中的词
    max_font_size=100,           # 设置最大的字体大小，所有词都不会超过100px
    min_font_size=10,            # 设置最小的字体大小，所有词都不会超过10px
    max_words=20,                # 设置最大的单词个数
    scale=2 ,font_path = "static/other/msyh.ttc")
    
    wordcloud.generate(newwords)
    path = r"downloads/" + filename + ".jpg"
    print(path)
    wordcloud.to_file(path)


if __name__ == "__main__":
    print(app.root_path)
    app.run(debug=True)

