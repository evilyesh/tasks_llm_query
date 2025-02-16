import sqlite3
import requests
import json
import re
from config import OPENAI_API_KEY
from fts import FTS # Import the fts module to use FTS functions

fts = FTS()
fts.db_init()

def chat_with_model(messages, model="gpt-3.5-turbo", api_key=OPENAI_API_KEY):
	url = "http://127.0.0.1:8989/v1/chat/completions"
	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {api_key}"
	}
	data = {
		"model": model,
		"messages": messages
	}
	response = requests.post(url, headers=headers, data=json.dumps(data))
	if response.status_code == 200:
		return response.json()['choices'][0]['message']['content'].strip()
	else:
		raise Exception(f"API request failed with status code {response.status_code}: {response.text}")


def row_to_dict(row):
	return {key: row[key] for key in row.keys()}


def clean_text(text):
	cleaned_text = re.sub(r'[^ \w]', ' ', text)
	return cleaned_text


def generate_summary(text):
	messages = [
		{"role": "system", "content": "You are a helpful assistant that summarizes text."},
		{"role": "user", "content": f"This need for search in text. Summarize the following text in English: '{text}' \n Extract all the significant words from the English text and for each word make all the word forms of this word, add to the text."}
	]
	return chat_with_model(messages)


def generate_keywords(content_en, content=None):
	messages = [
		{"role": "system", "content": "You are a helpful assistant that extract words from text with the word forms. You extract keywords from text, without any other words and symbols! If text is rubbish return empty string! If cant extract words return empty string! If you dont know word do nothing with them."},
		{"role": "user", "content": f"Extract all the significant words from text and for each word make all the word forms of this word. Text: '{content_en}'"}
	]
	keywords = chat_with_model(messages).replace('\n', ' ')
	return ' '.join(set(keywords.split())) + ' '.join(set(content.split()))   # Make keywords unique


def generate_similar(content_en, content=None):
	messages = [
		{"role": "system", "content": "You are a helpful assistant that extract words from text with the word forms and similar words (synonyms). You extract keywords and add similar words from text, add text theme short description, without any other words and symbols! If text is rubbish return #emptystring#! If cant extract words return #emptystring#! If you dont know word do nothing with them. "},
		{"role": "user", "content": f"First, write a general topic of the text. Then write keywords. Then for each word, write similar words (synonyms) by which I can search for this text. Mark general topic as 'gt'. Mark keywords as 'kw'. Mark similar as 'sw'. Text: '{content_en}'"}
	]
	keywords = clean_text(chat_with_model(messages).replace('\n', ' ') or '')
	return ' '.join(set([i if len(i) > 2 else '' for i in keywords.split()]))   # Make keywords unique


def generate_translation(content_en):
	messages = [
		{"role": "system", "content": "You are a helpful assistant that translate text to English. You translate the text according to the meaning. You return only translated text, without any other words and symbols! If text is rubbish return empty string! If you dont know word do nothing with them."},
		{"role": "user", "content": f"Translate text to English. Text: '{content_en}'"}
	]
	keywords = chat_with_model(messages).replace('\n', ' ')
	return ' '.join(set(keywords.split()))  # Make keywords unique


def generate_query_with_synonyms_and_theme(query):
	messages = [
		{"role": "system", "content": "You are a helpful assistant that generates synonyms and a theme for a search query. Return the query with added synonyms and theme. Do not add any other words and symbols!"},
		{"role": "user", "content": f" Do not add any other words and symbols! Word 'theme' no need to write in response! Generate synonyms and a theme for the following query: '{query}'"}
	]
	processed_query = chat_with_model(messages)
	return processed_query


def save_note(content, link, folder, img):
	content_en = generate_translation(content)
	keywords = generate_keywords(clean_text(content_en), content=content)

	# Add record to FTS table
	fts.add_record(content, keywords, link, None, None, folder, content_en, img)


def get_all_notes():
	notes = fts.get_all_records()
	return [row_to_dict(note) for note in notes]


def search_notes(query):
	# Generate query with synonyms and theme
	translation = generate_translation(query)
	processed_query = generate_query_with_synonyms_and_theme(query + ' ' + translation)
	processed_query += f" {query}"

	# Search using FTS
	print(processed_query)
	processed_query = ' OR '.join(clean_text(processed_query).split())
	results = fts.search_texts(processed_query)

	# Convert results to dictionary format
	notes = [row_to_dict(note) for note in results]

	# Evaluate relevance
	relevant_notes = []
	for note in notes:
		messages = [
			{"role": "system", "content": "You are a helpful assistant that evaluates the relevance of a note to a query. Answer only 'yes' or 'no'."},
			{"role": "user", "content": f"Is the following note relevant to the query: '{query}'? Note: '{note['content_en']} {note['link']}'"}
		]
		response = chat_with_model(messages)
		if "yes" in response.lower():
			relevant_notes.append(note)

	return relevant_notes


# New function for deleting a note
def delete_note(note_id):

	try:
		# Delete record from FTS table
		fts.delete_record(note_id)
		return True, ""
	except Exception as e:
		raise e
