from flask import Flask, send_from_directory, request, jsonify
import extension

app = Flask(__name__)


@app.route('/')
def home():
	"""Serve the home page."""
	return send_from_directory('html', 'index.html')


@app.route('/html/<path:filename>')
def static_files(filename):
	"""Serve static files from the 'html' directory."""
	return send_from_directory('html', filename)


@app.route('/save_note', methods=['POST'])
def save_note():
	data = request.json
	content = data.get('content')
	link = data.get('link')
	folder = data.get('folder')
	img = data.get('img')

	extension.save_note(content, link, folder, img)

	return jsonify({"status": "success", "message": "Note saved successfully"}), 200


@app.route('/get_all_notes', methods=['GET'])
def get_all_notes():
	notes = extension.get_all_notes()
	return jsonify({"status": "success", "notes": notes}), 200


@app.route('/search_notes', methods=['POST'])
def search_notes():
	query = request.json.get('query')
	relevant_notes = extension.search_notes(query)
	return jsonify({"status": "success", "notes": relevant_notes}), 200


@app.route('/delete_note/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
	success, message = extension.delete_note(note_id)
	if success:
		return jsonify({"status": "success", "message": "Note deleted successfully"}), 200
	else:
		return jsonify({"status": "error", "message": message}), 404


if __name__ == '__main__':
	app.run(debug=True, port=5858)
