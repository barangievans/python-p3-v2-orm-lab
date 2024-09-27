# employee.py
from __init__ import CURSOR, CONN

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}>"

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def save(self):
        if self.id is None:
            CURSOR.execute("""INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)""",
                           (self.name, self.job_title, self.department_id))
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()

    def update(self):
        CURSOR.execute("""UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?""",
                       (self.name, self.job_title, self.department_id, self.id))

    @classmethod
    def instance_from_db(cls, row):
        id, name, job_title, department_id = row
        if id in cls.all:
            return cls.all[id]
        employee = cls(name, job_title, department_id, id)
        cls.all[id] = employee
        return employee

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
