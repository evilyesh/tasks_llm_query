import sqlite3


class FTS:
	def __init__(self):
		self.conn = None
		self.cursor = None

	def get_conn(self):
		self.conn = sqlite3.connect('./texts.db')
		self.cursor = self.conn.cursor()

	def db_init(self):
		self.get_conn()
		# Создание виртуальной таблицы FTS
		self.cursor.execute('''
		CREATE VIRTUAL TABLE IF NOT EXISTS texts_fts USING fts5(
			content,
			content_en,
			keywords,
			tokenize='porter'
		);
		''')

		self.conn.commit()
		
		self.cursor.execute('''
		CREATE TABLE IF NOT EXISTS texts(
			id INTEGER PRIMARY KEY,
			content, 
			keywords, 
			link, 
			embedding,
			favicon,
			folder,
			content_en, 
			img
		);
		''')

		self.conn.commit()

		self.conn.close()
		self.conn = None
		self.cursor = None 

	def add_record(self, content, keywords, link, embedding, favicon, folder, content_en, img):
		# Добавляем запись в основную таблицу
		self.get_conn()
		self.cursor.execute('''
		INSERT INTO texts (content, keywords, link, embedding, favicon, folder, content_en, img)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		''', (content, keywords, link, embedding, favicon, folder, content_en, img))

		# Добавляем данные в таблицу FTS
		self.cursor.execute('''
		INSERT INTO texts_fts (content, content_en, keywords)
		VALUES (?, ?, ?)
		''', (content, content_en, keywords))

		self.conn.commit() 
		self.conn.close()
		self.conn = None
		self.cursor = None

	def search_texts(self, query):
		self.get_conn()
		# Выполняем поиск в таблице FTS


		debug_query = '''
		SELECT * FROM texts
		WHERE id IN (
			SELECT rowid FROM texts_fts WHERE texts_fts MATCH ?
		)
		ORDER BY id DESC
		'''.replace('?', repr(query))

		print(debug_query)

		self.cursor.execute('''
		SELECT * FROM texts
		WHERE id IN (
			SELECT rowid FROM texts_fts WHERE texts_fts MATCH ?
		)
		ORDER BY id DESC
		''', (query,))

		# Получение названий полей
		columns = [description[0] for description in self.cursor.description]

		# Получение данных и преобразование в словарь
		results = []
		for row in self.cursor.fetchall():
			results.append(dict(zip(columns, row)))

		self.conn.commit()
		self.conn.close()
		self.conn = None
		self.cursor = None
		return results

	def update_record(self, record_id, content, content_en, keywords):
		self.get_conn()
		# Обновляем запись в основной таблице
		self.cursor.execute('''
		UPDATE texts
		SET content = ?, keywords = ?
		WHERE id = ?
		''', (content, content_en, record_id))

		# Обновляем данные в таблице FTS
		self.cursor.execute('''
		UPDATE texts_fts
		SET content = ?, content_en = ?, keywords = ?
		WHERE rowid = ?
		''', (content, content_en, keywords, record_id))

		self.conn.commit()
		self.conn.close()
		self.conn = None
		self.cursor = None

	def delete_record(self, record_id):
		self.get_conn()
		# Удаляем запись из основной таблицы
		self.cursor.execute('DELETE FROM texts WHERE id = ?', (record_id,))

		# Удаляем данные из таблицы FTS
		self.cursor.execute('DELETE FROM texts_fts WHERE rowid = ?', (record_id,))

		self.conn.commit()
		self.conn.close()
		self.conn = None
		self.cursor = None

	def get_all_records(self):
		self.get_conn()
		# Удаляем запись из основной таблицы
		self.cursor.execute('SELECT * FROM texts ORDER BY id DESC')

		# Получение названий полей
		columns = [description[0] for description in self.cursor.description]

		# Получение данных и преобразование в словарь
		results = []
		for row in self.cursor.fetchall():
			results.append(dict(zip(columns, row)))

		self.conn.commit()
		self.conn.close()
		self.conn = None
		self.cursor = None
		return results


# if __name__ == '__main__':
# 	fts = FTS()
# 	results = fts.search_texts("контроллер")
# 	for row in results:
# 		print(row)
