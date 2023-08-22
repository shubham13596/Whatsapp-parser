from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
import re
from datetime import datetime
import os

app= Flask(__name__)

@app.route('/', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename and file.filename.endswith('.txt'):
            if not os.path.exists('input'):
                os.makedirs('input')
            if not os.path.exists('output'):
                os.makedirs('output')
            save_location = os.path.join('input', file.filename)
            file.save(save_location)

            parsed_df = parse_whatsapp_file(save_location)
            csv_filename = 'whatsapp_text_parsed.csv'
            parsed_df.to_csv('output/whatsapp_text_parsed.csv', index = False, header = False)
            #csv_file = csv_filename
            #return send_from_directory('output', csv_file)
            return redirect(url_for('download'))
        
    return render_template('index.html')
        
def parse_whatsapp_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        chat_lines = file.readlines()

    # Initialize lists to store data
    timestamps = []
    senders = []
    messages = []
    
    # Regular expression patterns to extract data
    pattern = re.compile(r'(\d{1,2}/\d{1,2}/\d{2},? \d{1,2}:\d{2}) - ([^:]+): (.+)')

    # Iterate through chat lines and extract data
    for line in chat_lines:
        match = pattern.match(line)
        if match:
            timestamp_str, sender, message = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%d/%m/%y, %H:%M')
            
            timestamps.append(timestamp)
            senders.append(sender)
            messages.append(message)

    # Create a DataFrame
    data = {'Timestamp': timestamps, 'Sender': senders, 'Message': messages}
    df = pd.DataFrame(data)

    return df

@app.route('/download')
def download():
    return render_template('download.html', files = os.listdir('output'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('output', filename)

if __name__ == '__main__':
    app.run(debug = True)
    
