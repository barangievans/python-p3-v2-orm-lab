# review.py
from __init__ import CURSOR, CONN
from department import Department

class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key."""
        if self.id is None:  # New review
            CURSOR.execute("""INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)""",
                           (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid  # Get the ID of the newly created row
            Review.all[self.id] = self  # Cache the instance
        else:
            # If the review already exists, update it
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save the object to the database. Return the new instance."""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        id, year, summary, employee_id = row
        if id in cls.all:
            return cls.all[id]  # Return the cached instance
        review = cls(year, summary, employee_id, id)
        cls.all[id] = review  # Cache the instance
        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        CURSOR.execute("""UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?""",
                       (self.year, self.summary, self.employee_id, self.id))

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute."""
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        del Review.all[self.id]  # Remove from cache
        self.id = None  # Reset ID

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row."""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
