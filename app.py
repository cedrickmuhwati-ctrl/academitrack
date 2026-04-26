from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from algorithms import (
    bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort,
    linear_search, binary_search, jump_search
)

app = Flask(__name__)
app.secret_key = 'academitrack_secret_key'

# ── Database config ──────────────────────────────────────────────────────────
# Change yourpassword to your actual MySQL root password
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:sedym2006@localhost/academitrack_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Model ────────────────────────────────────────────────────────────────────
class Student(db.Model):
    __tablename__ = 'students'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    student_id  = db.Column(db.String(20),  nullable=False, unique=True)
    age         = db.Column(db.Integer,     nullable=False)
    gpa         = db.Column(db.Float,       nullable=False)
    major       = db.Column(db.String(100), nullable=False)
    enrolled_on = db.Column(db.Date,        nullable=False)
    is_active   = db.Column(db.Boolean,     nullable=False, default=True)

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'student_id':  self.student_id,
            'age':         self.age,
            'gpa':         self.gpa,
            'major':       self.major,
            'enrolled_on': self.enrolled_on.strftime('%Y-%m-%d'),
            'is_active':   'Yes' if self.is_active else 'No',
        }

SORTABLE_FIELDS   = ['name', 'student_id', 'age', 'gpa', 'major', 'enrolled_on']
SORT_ALGORITHMS   = ['Bubble Sort', 'Selection Sort', 'Insertion Sort', 'Merge Sort', 'Quick Sort']
SEARCH_ALGORITHMS = ['Linear Search', 'Binary Search', 'Jump Search']

SORT_MAP = {
    'Bubble Sort':    bubble_sort,
    'Selection Sort': selection_sort,
    'Insertion Sort': insertion_sort,
    'Merge Sort':     merge_sort,
    'Quick Sort':     quick_sort,
}
SEARCH_MAP = {
    'Linear Search': linear_search,
    'Binary Search': binary_search,
    'Jump Search':   jump_search,
}

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# --- Add record ---
@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        try:
            student = Student(
                name        = request.form['name'],
                student_id  = request.form['student_id'],
                age         = int(request.form['age']),
                gpa         = float(request.form['gpa']),
                major       = request.form['major'],
                enrolled_on = datetime.strptime(request.form['enrolled_on'], '%Y-%m-%d').date(),
                is_active   = request.form.get('is_active') == 'on',
            )
            db.session.add(student)
            db.session.commit()
            flash('Record added successfully!', 'success')
            return redirect(url_for('add_record'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')
    return render_template('add_record.html')

# --- Sort & Search ---
@app.route('/sort_search', methods=['GET', 'POST'])
def sort_search():
    records        = []
    search_results = []
    sort_algo      = request.form.get('sort_algo', SORT_ALGORITHMS[0])
    sort_field     = request.form.get('sort_field', 'name')
    sort_order     = request.form.get('sort_order', 'asc')
    search_algo    = request.form.get('search_algo', SEARCH_ALGORITHMS[0])
    search_term    = request.form.get('search_term', '').strip()
    action         = request.form.get('action')
    no_results     = False

    if action == 'sort':
        data    = [s.to_dict() for s in Student.query.all()]
        reverse = (sort_order == 'desc')
        records = SORT_MAP[sort_algo](data, key=sort_field, reverse=reverse)

    elif action == 'search':
        data           = [s.to_dict() for s in Student.query.order_by(Student.name).all()]
        search_results = SEARCH_MAP[search_algo](data, search_term)
        no_results     = len(search_results) == 0

    return render_template(
        'sort_search.html',
        records=records,
        search_results=search_results,
        sort_algo=sort_algo,
        sort_field=sort_field,
        sort_order=sort_order,
        search_algo=search_algo,
        search_term=search_term,
        sort_algorithms=SORT_ALGORITHMS,
        search_algorithms=SEARCH_ALGORITHMS,
        sortable_fields=SORTABLE_FIELDS,
        action=action,
        no_results=no_results,
    )

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # auto-creates the students table
    app.run(debug=True)
