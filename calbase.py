import re
import datetime
import sqlite3
from collections import defaultdict

class BDB:
    def __init__(self, filename):
        self.datastore = defaultdict(list)

        with open(filename, "r") as f:
            data = f.readlines()

        for line in data:
            m = re.match("(\d\d\d\d)-(\d\d)-(\d\d) (.*)", line).groups()
            birthday = datetime.date(int(m[0]), int(m[1]), int(m[2]))
            name = m[3]
            self.datastore[birthday.month].append((birthday, name))
    
    def get_month(self, year, month):
        entries = {}
        for birthday, name in self.datastore[month]:
            cur_birthday = datetime.date(year, birthday.month, birthday.day).isoformat()
            age = year - birthday.year
            entries[cur_birthday] = "Geburtstag {} ({})".format(name, age)
        return entries

class TDB:
    def __init__(self, filename):
        self.datastore = {}

        with open(filename, "r") as f:
            data = f.readlines()

        for line in data:
            m = re.match("(\d\d\d\d-\d\d-\d\d) (.*)", line).groups()
            self.datastore[m[0]] = m[1]

    def get_month(self, year, month):
        return self.datastore


class DB:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.db.execute("CREATE TABLE IF NOT EXISTS events ( \
                        date TEXT, \
                        desc TEXT)")

    def get_month(self, year, month):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM events WHERE date LIKE ?", ["{}-{:02}%".format(year, month)])
        d = {}
        for row in cur.fetchall():
            d[row[0]] = row[1]
        return d

    def set_day(self, year, month, day, text):
        DAF = "{}-{:02}-{:02}"
        cur = self.db.cursor()  
        cur.execute("DELETE FROM events WHERE date LIKE ?", [DAF.format(year, month, day)])
        if text:
            cur.execute("INSERT INTO events VALUES (?, ?)", (DAF.format(year, month, day), text))
        self.db.commit()

class EntryJoin:
    def __init__(self, *args):
        self.calendars = args 

    def get_month(self, year, month):
        entries = {}
        for c in self.calendars:
            for k, v in c.get_month(year, month).items():
                if k in entries:
                    entries[k] = entries[k] + " / " + v
                else:
                    entries[k] = v

        return entries

    def set_day(self, year, month, day, text):
        self.calendars[0].set_day(year, month, day, text)

if __name__ == "__main__":
    today = datetime.date.today()
    cur_month = today.month
    cur_year = today.year
    selected = today.day

    db = EntryJoin(DB("events.sqlite"), BDB("bdays.txt"))
    events = db.get_month(cur_year, cur_month)
    
    import pprint; pprint.pprint(events)
