from flask import Flask, render_template, request, redirect
from database import get_all_records
from config import PRICING  # 导入配置

app = Flask(__name__)

@app.route('/')
def index():
    records = get_all_records()
    return render_template('index.html', records=records, pricing=PRICING)

@app.route('/update_pricing', methods=['POST'])
def update_pricing():

    # 更新配置（实际保存到文件或DB）
    PRICING['small_car']['hourly_rate'] = float(request.form['small_rate'])
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)