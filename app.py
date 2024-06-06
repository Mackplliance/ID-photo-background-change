from flask import Flask, request, render_template, send_file, redirect, url_for
import os

from ai_cutout import rmbg

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 从表单获取数据
        file = request.files['image']
        background_color = request.form['color']
        width = request.form['width']
        height = request.form['height']
        size_opt = request.form['size_opt']

        if file:
            # 保存上传的文件
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # 处理图片
            bg_image_path = rmbg(filepath, background_color, width, height, size_opt)

            # 重定向到结果页面
            return redirect(url_for('result', image_path=bg_image_path))
        return 'No file uploaded'

    # GET 请求时显示上传页面
    return render_template('index.html')


@app.route('/result')
def result():
    image_path = request.args.get('image_path')
    return render_template('result.html', image_path=image_path)


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
