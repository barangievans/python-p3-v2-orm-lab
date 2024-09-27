# department.py
from __init__ import CURSOR, CONN

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}>"

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS departments;"
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def create(cls, name, location):
        department = cls(name, location)
        department.save()
        return department

    def save(self):
        if self.id is None:
            CURSOR.execute("""INSERT INTO departments (name, location) VALUES (?, ?)""",
                           (self.name, self.location))
            self.id = CURSOR.lastrowid
            Department.all[self.id] = self
        else:
            self.update()

    def update(self):
        CURSOR.execute("""UPDATE departments SET name = ?, location = ? WHERE id = ?""",
                       (self.name, self.location, self.id))

    def delete(self):
        """Delete the instance's corresponding db row and remove it from the cache."""
        CURSOR.execute("DELETE FROM departments WHERE id = ?", (self.id,))
        del Department.all[self.id]  # Remove from cache
        self.id = None  # Reset ID

    @classmethod
    def instance_from_db(cls, row):
        id, name, location = row
        if id in cls.all:
            return cls.all[id]
        department = cls(name, location, id)
        cls.all[id] = department
        return department

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def employees(self):
        from employee import Employee  # Local import to avoid circular dependency
        sql = "SELECT * FROM employees WHERE department_id = ?"
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Employee.instance_from_db(row) for row in rows] if rows else []
