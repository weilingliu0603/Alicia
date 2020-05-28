import sqlite3
import flask
m = 0
n=''

app = flask.Flask(__name__)

def get_db():
    db = sqlite3.connect('JPsalonDatabase.db')
    return db
    
@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/admin')
def admin():
    return flask.render_template('admin.html')

@app.route('/action' , methods = ["POST"])
def action():
    data = flask.request.form
    if data['choice'] == "Update member's data":
        return flask.render_template('updatemember.html')
    
    if data['choice'] == "View daily transaction":
        data = flask.request.form
        db = get_db()
        cursor = db.execute('SELECT date,totalAmt FROM Transactions ')
        rows = cursor.fetchall()
        start = str(rows[0][0])
        year,month,day = start.split('-')

        key = day
        value = 0.0
        dates = []
        revenues = []
        for line in rows:
            date = str(line[0])
            year,month,day = date.split('-')
            if day == key:
                value += float(line[1])
            if day != key:
                dates.append(date)
                revenues.append(value)
                value = float(line[1])
                key = day
        dates.append(date)
        revenues.append(value)
        return flask.render_template('viewday.html', revenues = revenues, dates = dates)

    
    if data['choice'] == "View monthly transaction":
        data = flask.request.form
        db = get_db()
        cursor = db.execute('SELECT date,totalAmt FROM Transactions ')
        rows = cursor.fetchall()
        start = str(rows[0][0])
        year,month,day = start.split('-')

        key = month
        value = 0.0
        dates = []
        revenues = []
        dates.append(month+'-'+year)
        for line in rows:
            date = str(line[0])
            year,month,day = date.split('-')
            if month == key:
                value += float(line[1])
            if month != key:
                dates.append(month+'-'+year)
                revenues.append(value)
                value = float(line[1])
                key = month
        dates.append(month+'-'+year)
        revenues.append(value)
        return flask.render_template('viewmonth.html', revenues = revenues, dates = dates)

    if data['choice'] == "View member's transaction history":
        return flask.render_template('viewmember.html')

@app.route('/cuthair')
def cuthair():
    return flask.render_template('cuthair.html')

@app.route('/member')
def member():
    return flask.render_template('member.html')

@app.route('/addmember')
def addmember():
    return flask.render_template('addmember.html')

@app.route('/memberadded', methods = ["POST"])
def memberadded():
    db = get_db()
    
    result = db.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Member'")
    result = result.fetchall()
    m = int(result[0][0]) + 1
    
    data = flask.request.form
    n = data['name']
    g = data['gender']
    e = data['email']
    c = int(data['contact'])
    a = data['address']

    db.execute('INSERT into Member VALUES (?,?,?,?,?,?)',(m,n,g,e,c,a))
    db.commit()
    db.close()
    return flask.render_template('memberadded.html', m = m)

@app.route('/addtrans' , methods = ["POST"])
def addtrans():
    global m,n
    data = flask.request.form
    m = data['ID']
    db = get_db()
    result = db.execute("SELECT fullName FROM MEMBER WHERE memberID = ?",(m))
    result = result.fetchall()
    n = result[0][0]
    return flask.render_template('addtrans.html' , n = n)

@app.route('/transadded', methods = ["POST"])
def transadded():
    import datetime
    global m,n
    db = get_db()
    result = db.execute("SELECT Seq FROM sqlite_sequence WHERE name = 'Transactions'")
    result = result.fetchall()
    no_of_transaction = int(result[0][0]) + 1
    total = 0.0
    purchase = []
    
    I = no_of_transaction
    data = flask.request.form
    d = str(datetime.date.today())

    Cut = data['cut']    #services
    if Cut == 'short':
        total += 35
        purchase.append(('Cut (short length)',35.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Cut (short length)'))
        db.commit()
    if Cut == 'medium':
        total += 40
        purchase.append(('Cut (medium length)',40.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Cut (medium length)'))
        db.commit()
    if Cut == 'long':
        total += 45
        purchase.append(('Cut (long length)',45.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Cut (long length)'))
        db.commit()

    Colour = data['colour']
    if Colour == 'yes':
        total += 100
        purchase.append(('Colour',100.00))

    Highlight = data['highlight']
    if Highlight == 'half':
        total += 150
        purchase.append(('Highlight (half head)',150.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Highlight (half head)'))
        db.commit()
        
    if Highlight == 'full':
        total += 200
        purchase.append(('Highlight (full head)',200.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Highlight (full head)'))
        db.commit()

    Perm = data['perm']
    if Perm == 'yes':
        total += 200
        purchase.append(('Perm',200.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Perm'))
        db.commit()

    Rebonding = data['rebonding']
    if Rebonding == 'yes':
        total += 180
        purchase.append(('Rebonding',180.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Rebonding'))
        db.commit()

    Treatment = data['treatment']
    if Treatment == 'yes':
        total += 80
        purchase.append(('Treatment',80.00))
        db.execute('INSERT into TransDetail VALUES (?,?)',(I,'Treatment'))
        db.commit()

    if m != -1:
        discount = total * 0.1
        total = total * 0.9
    else:
        discount = 0
        

    purchase.append(('',''))
    purchase.append(('Discount',str(discount)))
    purchase.append(('Total payable',str(total)))
    db.execute('INSERT into Transactions VALUES (?,?,?,?,?)',(I,m,n,d,total))
    db.commit()
    
    db.close()
    return flask.render_template('transadded.html' , I = I,
                           m = m, n = n, d = d,
                           purchase = purchase)


@app.route('/updated', methods = ["POST"])
def updated():
    data = flask.request.form
    m = int(data['ID'])
    c = data['contact']
    e = data['email']
    db = get_db()
    if c == '-1':
        db.execute('UPDATE Member SET email = ? WHERE memberID = ?',(e,m))
        db.commit()
    if e == '-1':
        db.execute('UPDATE Member SET contactNo = ? WHERE memberID = ?',(c,m))
        db.commit()

    if c != '-1' and e != '-1':
        db.execute('UPDATE Member SET contactNo = ?, email = ? WHERE memberID = ?',(str(c),str(e),m))
        db.commit()
    return flask.render_template('updated.html', m = m)
    
@app.route('/viewmemberhistory' , methods = ["POST"])
def viewmemberhistory():
    db = get_db()
    data = flask.request.form
    ID = int(data['ID'])
    result = db.execute('SELECT InvoiceNo, date, totalAmt FROM Transactions WHERE memberID = ?',(ID,))
    lst_history = []
    lst_history.append(("Invoice No","Date","Total Amount"))
    for line in result:
        lst_history.append(line)
    db.close()
    return flask.render_template('viewmemberhistory.html', ID=ID , lst_history = lst_history)
    

##@app.route('/viewday', methods = ["POST"])
##def viewdailytrans():
##    db = get_db()
##    date = flask.request.form['date']
##    result = db.execute('SELECT InvoiceNo, memberID, fullName, totalAmt FROM Transactions WHERE date = ?',(date))
##    lst_daily = []
##    lst_daily.append("Invoice No".ljust(16) +"Member ID".ljust(16) +"Full Name".ljust(16) +"Total Amount".ljust(16))
##    for row in result:
##        row = (" "*16).join(row)
##        lst_daily.append(row)
##    db.close()
##    return flask.render_template('viewday.html', date=date, lst_daily=lst_daily)


@app.route('/viewmember')
def viewmember():
    return flask.render_template('viewmember.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
