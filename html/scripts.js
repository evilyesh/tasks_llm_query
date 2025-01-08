function showError(message) {
	const errorMessage = document.getElementById('errorMessage');
	errorMessage.textContent = message;
	errorMessage.style.display = 'block';
	setTimeout(() => {
		errorMessage.style.display = 'none';
	}, 5000);
}

function showLoader() {
	document.querySelector('.loader').style.display = 'flex';
}

function hideLoader() {
	document.querySelector('.loader').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', async () => {
	document.querySelector('.loader').style.display = 'none';
	document.querySelector('.form-container').addEventListener('paste', handlePaste);

	showLoader();
	try {
		const response = await fetch('/get_all_notes', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
		});

		if (response.ok) {
			const data = await response.json();
			displayNotes(data.notes);
		} else {
			showError('Failed to load notes');
		}
	} catch (error) {
		showError('Failed to load notes');
	} finally {
		hideLoader();
	}
});

document.getElementById('saveNote').addEventListener('click', async () => {
	const content = document.getElementById('noteContent').value;
	const link = document.getElementById('noteLink').value;
	const folder = document.getElementById('noteFolder').value;
	let imgSrc;

	if (document.querySelector('.form-container img')) {
	   	imgSrc = document.querySelector('.form-container img')?.src; 
	}

	showLoader();
	try {
		const response = await fetch('/save_note', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ content, link, folder, img: imgSrc }),
		});

		if (response.ok) {
			alert('Note saved successfully');
		} else {
			showError('Failed to save note');
		}
	} catch (error) {
		showError('Failed to save note');
	} finally {
		hideLoader();
	}
});

document.getElementById('searchNotes').addEventListener('click', async () => {
	const query = document.getElementById('searchQuery').value;

	showLoader();
	try {
		// '/search_notes'
		const response = await fetch('/search_notes', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ query }),
		});

		if (response.ok) {
			const data = await response.json();
			displayNotes(data.notes);
		} else {
			showError('Failed to search notes');
		}
	} catch (error) {
		showError('Failed to search notes');
	} finally {
		hideLoader();
	}
});

document.getElementById('pasteScreenshot').addEventListener('click', async () => {
	try {
		await pasteImageFromClipboard('.form-container img'); // Use a placeholder selector
	} catch (err) {
		console.error('Failed to read clipboard contents: ', err);
		showError('Failed to paste screenshot');
	}
});

function displayNotes(notes) {
	const notesList = document.getElementById('notesList');
	notesList.innerHTML = '';
	notes.forEach(note => {
		const noteItem = document.createElement('div');
		noteItem.className = 'note-item';
		if (note.img) {
			const imgElement = document.createElement('img');
			imgElement.src = note.img.startsWith('data:image') ? note.img : `/path/to/${note.img}`; // Adjust path if necessary
			imgElement.alt = `Note Image ${note.id}`;
			noteItem.appendChild(imgElement);
		}
		
		const contentElement = document.createElement('div');
		if(note.link){
			note.link = `<a target="_blank" href=${note.link}>${createShortString(escapeHtml(note.link))}<a>`;
		}
		contentElement.innerHTML = `${escapeHtml(note.content? note.content : '')}<br>${escapeHtml(note.content_en? note.content_en : '')}<br>${note.link ? note.link : ''}<br>${escapeHtml(note.folder ? note.folder : '')}`;

		noteItem.appendChild(contentElement);

		const deleteButton = document.createElement('span');
		deleteButton.innerHTML = '×';
		deleteButton.className = 'delete-button';
		deleteButton.addEventListener('click', async () => {
			showLoader();
			try {
				const response = await fetch(`/delete_note/${note.id}`, {
					method: 'DELETE',
					headers: {
						'Content-Type': 'application/json',
					},
				});

				if (response.ok) {
					noteItem.remove();
				} else {
					showError('Failed to delete note');
				}
			} catch (error) {
				showError('Failed to delete note');
			} finally {
				hideLoader();
			}
		});
		contentElement.appendChild(deleteButton);

		notesList.appendChild(noteItem);
	});
}

function createShortString(longString) {
	if (longString.length <= 30) return longString;
	return longString.substring(0, 30) + '...';
	// return '...' + longString.substring(longString.length - 30);
}

async function pasteImageFromClipboard(targetSelector) {
	try {
		const clipboardItems = await navigator.clipboard.read();
		
		for (const item of clipboardItems) { 
			if (!item.types.includes('image/png') && !item.types.includes('image/jpeg')) continue;
			
			for (const type of item.types) {
				if (type.startsWith('image/')) {
					const blob = await item.getType(type);
					const reader = new FileReader();
					reader.onloadend = () => {
						const base64data = reader.result;
						let imgElement;

						if (!document.querySelector(targetSelector)) { // If no image element exists, create one
							imgElement = document.createElement('img');
							imgElement.id = 'noteImage';
							document.querySelector('.form-container').appendChild(imgElement); 
						} else {
							imgElement = document.querySelector(targetSelector);
						}

						imgElement.src = base64data;
					};
					reader.readAsDataURL(blob);
					
					break; // Exit loop after processing the first image
				}
			}
		}
		
	} catch (err) {  
		console.error('Failed to read clipboard contents: ', err); 
		showError('Failed to paste screenshot');
  	}	
}

function handlePaste(event) {
	if ((event.ctrlKey || event.metaKey) && event.key === 'v') {
		event.preventDefault();
		try {
			navigator.clipboard.read().then(data => {  
				for (const item of data.items) {
					if (!item.types.includes('image/png') && !item.types.includes('image/jpeg')) continue;
					
					for (const type of item.types) {
						if (type.startsWith('image/')) {
							item.getType(type).then(blob => {
								const reader = new FileReader();
								reader.onloadend = () => {
									const base64data = reader.result;
									let imgElement;

									if (!document.querySelector('.form-container img')) { // If no image element exists, create one
										imgElement = document.createElement('img');
										imgElement.id = 'noteImage';
										document.querySelector('.form-container').appendChild(imgElement); 
									} else {
										imgElement = document.querySelector('.form-container img');  
									}

									imgElement.src = base64data;
									
								};
								reader.readAsDataURL(blob);
								
							});
							
							break; // Exit loop after processing the first image
						}
					}
				}
			}).catch(err => {   
				console.error('Failed to read clipboard contents: ', err); 
				showError('Failed to paste screenshot');
		   });  
		} catch (err) {
			console.error('Paste failed:', err);
		}	
	}
}
