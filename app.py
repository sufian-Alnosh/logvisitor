from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from sqlalchemy import inspect

app = Flask(__name__)

# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
db = SQLAlchemy(app)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    device = db.Column(db.String(100))
    access_time = db.Column(db.DateTime, default=datetime.utcnow)

# التأكد من تنفيذ drop table داخل سياق التطبيق
with app.app_context():
    inspector = inspect(db.engine)
    # حذف الجدول إذا كان موجودًا باستخدام inspect
    if inspector.has_table('visitor'):
        db.drop_all()
        print("Table visitor dropped successfully.")
    
    # إعادة إنشاء الجدول
    db.create_all()

def get_location(ip):
    token = "597d93e989f6ec"  # استبدل "YOUR_API_TOKEN" بالتوكن الخاص بك
    response = requests.get(f'https://ipinfo.io/{ip}/json?token={token}')
    data = response.json()
    country = data.get('country', 'Unknown')
    city = data.get('city', 'Unknown')
    return country, city

@app.route('/')
def index():
    ip_address = request.remote_addr
    country, city = get_location(ip_address)
    device = request.user_agent.string
    new_visitor = Visitor(
        ip_address=ip_address, 
        country=country, 
        city=city, 
        device=device
    )
    db.session.add(new_visitor)
    db.session.commit()
    return render_template('index.html')

@app.route('/visitors')
def visitors():
    all_visitors = Visitor.query.all()
    return render_template('visitors.html', visitors=all_visitors)

if __name__ == '__main__':
    app.run(debug=True)



