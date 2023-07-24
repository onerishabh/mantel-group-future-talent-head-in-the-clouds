from flask import Flask, redirect, render_template, request, url_for
import utils.contact as contact_helper_fn
import utils.mailing_list as mailing_helper_fn
import utils.ip as ip_helper_fn

app = Flask(__name__)

notes = []


@app.route('/')
def index():
    return render_template('index.html', notes=notes)


@app.route('/add', methods=['POST'])
def add_note():
    note = request.form['note']
    if note:
        notes.append(note)


    # store access details to a table
    browser_details = request.user_agent.string
    ip_address = request.remote_addr
    ip_helper_fn.save_to_ip_list(ip_address, browser_details)

    return redirect(url_for('index'))

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    subscribe = request.form.get('subscribe')

    if subscribe:
        """
            Add this email to a email list being maintained on dynamodb
        """
        mailing_helper_fn.save_to_mailing_list(name, email)

    contact_helper_fn.contact_us(name, email, message)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
