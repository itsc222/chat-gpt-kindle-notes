import os
import openai
openai.organization = "org-0zjmYYl5jY0K38Kvn3wzK7At"
openai.Model.list()
import polars as pl
import re

#Write function for reading the Kindle notes text file.
def read_txt_file(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            return content

#Write function for writing the Kindle notes text file to the local directory.
def write_txt_file(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"File written successfully: {file_path}")
    except IOError as e:
        print(f"Error writing to the file: {e}")

# Set filepaths for potential location for Kindle Notes
path1 = '/Volumes/KINDLENEW/documents/My Clippings.txt'
path2 = '/Users/ischneid/Desktop/My Clippings.txt'

#Set try/except block for reading the file in multple locations.
try:
    text_content = read_txt_file(path1)
except FileNotFoundError:
    try:
        text_content = read_txt_file(path2)
    except:
        print("I cannot find your clippings file on either your Kindle of the Desktop. Please locate the file and try again.")

#Write the text file to the local directory.
if text_content:
    # Replace 'output_file_path' with the path to the destination .txt file in your workspace directory
    output_file_path = '/Users/ischneid/chat-gpt-kindle-notes/my_clippings.txt'
    write_txt_file(output_file_path, text_content)
     
text_content = read_txt_file('/Users/ischneid/chat-gpt-kindle-notes/my_clippings.txt')

#Initialize main datatable
highlight_data_main = {'title' : [],
               'date' : [],
               'note' : []}

highlight_df_main = pl.DataFrame(highlight_data_main, schema = {
                            'title': str,
                            'date': str,
                            'note' : str
                            })

text_sep = text_content.split('==========')


for note in text_sep:

    split_note = note.split('\n')
    filtered_list = [item for item in split_note if item]

    try:




        highlight_data = {'title' : filtered_list[0],
                    'date' : filtered_list[1],
                    'note' : filtered_list[2]}
        
        highlight_df = pl.DataFrame(highlight_data)

        highlight_df_main.extend(highlight_df)
    
    except IndexError:
        # print("There was an index error")
        pass


def search_notes(term):
    note_df = highlight_df_main.select(['title', 'note'])
    filtered_df = note_df.filter(note_df['note'].str.contains(term))
    
    return filtered_df

def search_author(term):    
    
        note_df = highlight_df_main.select(['title', 'note'])
        filtered_df = note_df.filter(note_df['title'].str.contains(term))
        return filtered_df

def search_both(term):
        notes = search_notes(term)
        data = notes.extend(search_author(term))
        data = data.unique()
        return(data)

    
    #Extract data for query

term = r"Chen et al."
data= (search_both(term))

print(data)

prompt = "Print the quotes most relevant to voicing or heteroglossia"
initial_question = f"You are a research assistant. Read these Kindle Highlights. {data}. Pay attention to the 'notes' column. Only copy-pase the exact content of cells in your responses."

def generate_chat_response():
    # List of messages representing a conversation
    messages = [
    {"role": "system", "content": f"{initial_question}"},
    {"role": "user", "content": f"{prompt}"}
    ]

    # Call the chat completions endpoint
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate chat model here
        messages=messages
    )

    # Extract the assistant's reply from the response
    assistant_reply = response['choices'][0]['message']['content']
    print("Assistant:", assistant_reply)

# Call the function to generate the chat response

# generate_chat_response()

notes = (data['note']).to_list()

# File path to save the data
file_path = "/Users/ischneid/chat-gpt-kindle-notes/selected_clippings.txt"

# Write the list elements to a text file with line breaks
with open(file_path, "w") as file:
    for item in notes:
        file.write(str(item) + "\n" + "\n")