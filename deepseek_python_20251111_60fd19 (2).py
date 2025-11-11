#!/usr/bin/env python3
"""
Сайт с фотогалереей на Python с HTML в одном файле
Запуск: python website.py
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import html
import urllib.parse
import json
from datetime import datetime
import os
import base64
import mimetypes

class WebsiteHandler(SimpleHTTPRequestHandler):
    
    # Папка для хранения фотографий
    PHOTOS_DIR = "photos"
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_home_page()
        elif self.path == '/about':
            self.send_about_page()
        elif self.path == '/contact':
            self.send_contact_page()
        elif self.path == '/gallery':
            self.send_gallery_page()
        elif self.path == '/upload':
            self.send_upload_page()
        elif self.path == '/api/time':
            self.send_api_time()
        elif self.path == '/api/photos':
            self.send_api_photos()
        elif self.path.startswith('/photos/'):
            self.serve_photo()
        else:
            # Для статических файлов (CSS, JS)
            if self.path.startswith('/static/'):
                self.serve_static()
            else:
                self.send_error(404)
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/contact':
            self.handle_contact_form()
        elif self.path == '/api/upload':
            self.handle_photo_upload()
        elif self.path.startswith('/api/delete/'):
            self.handle_photo_delete()
        else:
            self.send_error(404)
    
    def serve_static(self):
        """Обслуживание статических файлов"""
        try:
            filepath = self.path[1:]  # убираем первый слеш
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                
                # Определяем MIME тип
                mime_type, _ = mimetypes.guess_type(filepath)
                if not mime_type:
                    if filepath.endswith('.css'):
                        mime_type = 'text/css'
                    elif filepath.endswith('.js'):
                        mime_type = 'application/javascript'
                    else:
                        mime_type = 'text/plain'
                
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.send_header('Content-Length', str(len(file_data)))
                self.end_headers()
                self.wfile.write(file_data)
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, f"Static serve error: {str(e)}")
    
    def send_home_page(self):
        """Главная страница"""
        # Получаем последние 3 фото для превью
        photos = self.get_photos_list()[:3]
        photos_html = self.generate_photos_html(photos, "latest-photos")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Главная - Нам Полгода</title>
            <style>
                {self.get_css_styles()}
            </style>
        </head>
        <body>
            {self.get_navigation()}
            
            <div class="container">
                <header class="hero">
                    <h1>💕 Нам уже полгода вместе! 💕</h1>
                    <p>Этот сайт - наша маленькая фото-история</p>
                </header>
                
                <section class="welcome-section">
                    <div class="welcome-text">
                        <h2>Привет, любимая! 👋</h2>
                        <p>Здесь собраны наши лучшие моменты за эти полгода. Каждая фотография - это история, 
                        которая делает нашу любовь еще крепче.</p>
                        <div class="action-buttons">
                            <a href="/gallery" class="btn btn-primary">📸 Смотреть все фото</a>
                            <a href="/upload" class="btn btn-secondary">➕ Добавить фото</a>
                        </div>
                    </div>
                </section>
                
                <section class="latest-photos">
                    <h2>Последние фотографии</h2>
                    {photos_html if photos else '<p class="no-photos">Пока нет фотографий. Будь первой, кто добавит!</p>'}
                    <div class="text-center">
                        <a href="/gallery" class="btn">Все фотографии →</a>
                    </div>
                </section>
                
                <section class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{len(self.get_photos_list())}</div>
                        <div class="stat-label">Фотографий</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">180+</div>
                        <div class="stat-label">Дней вместе</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">∞</div>
                        <div class="stat-label">Любви</div>
                    </div>
                </section>
            </div>
            
            {self.get_footer()}
            
            <script>
                {self.get_javascript()}
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_gallery_page(self):
        """Страница галереи"""
        photos = self.get_photos_list()
        photos_html = self.generate_photos_html(photos, "gallery-grid")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Галерея - Наши фото</title>
            <style>
                {self.get_css_styles()}
            </style>
        </head>
        <body>
            {self.get_navigation()}
            
            <div class="container">
                <div class="gallery-header">
                    <h1>📸 Наша галерея</h1>
                    <p>Всего фотографий: {len(photos)}</p>
                    <a href="/upload" class="btn btn-primary">➕ Добавить фото</a>
                </div>
                
                {photos_html if photos else '''
                <div class="empty-gallery">
                    <div class="empty-icon">📷</div>
                    <h2>Пока нет фотографий</h2>
                    <p>Добавь первую фотографию и начни нашу историю!</p>
                    <a href="/upload" class="btn btn-primary">Добавить фото</a>
                </div>
                '''}
            </div>
            
            <!-- Модальное окно для просмотра фото -->
            <div id="photoModal" class="modal">
                <span class="close">&times;</span>
                <img class="modal-content" id="modalImage">
                <div class="modal-caption" id="modalCaption"></div>
                <button class="modal-delete btn btn-danger" id="modalDelete">🗑️ Удалить</button>
            </div>
            
            {self.get_footer()}
            
            <script>
                {self.get_javascript()}
                
                // Модальное окно для фотографий
                const modal = document.getElementById('photoModal');
                const modalImg = document.getElementById('modalImage');
                const modalCaption = document.getElementById('modalCaption');
                const modalDelete = document.getElementById('modalDelete');
                const closeBtn = document.querySelector('.close');
                let currentPhotoName = '';
                
                // Открытие модального окна
                document.addEventListener('click', function(e) {{
                    if (e.target.classList.contains('gallery-photo')) {{
                        modal.style.display = 'block';
                        modalImg.src = e.target.src;
                        modalCaption.textContent = e.target.alt;
                        currentPhotoName = e.target.dataset.name;
                    }}
                }});
                
                // Закрытие модального окна
                closeBtn.onclick = function() {{
                    modal.style.display = 'none';
                }}
                
                // Удаление фото
                modalDelete.onclick = function() {{
                    if (confirm('Удалить эту фотографию?')) {{
                        fetch('/api/delete/' + encodeURIComponent(currentPhotoName), {{ method: 'POST' }})
                            .then(response => response.json())
                            .then(data => {{
                                if (data.success) {{
                                    showNotification('Фото удалено!', 'success');
                                    modal.style.display = 'none';
                                    setTimeout(() => location.reload(), 1000);
                                }} else {{
                                    showNotification('Ошибка удаления: ' + data.error, 'error');
                                }}
                            }})
                            .catch(error => {{
                                showNotification('Ошибка сети', 'error');
                            }});
                    }}
                }}
                
                // Закрытие по клику вне изображения
                window.onclick = function(event) {{
                    if (event.target == modal) {{
                        modal.style.display = 'none';
                    }}
                }}
                
                // Закрытие по ESC
                document.addEventListener('keydown', function(event) {{
                    if (event.key === 'Escape') {{
                        modal.style.display = 'none';
                    }}
                }});
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_upload_page(self):
        """Страница загрузки фото"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Добавить фото</title>
            <style>
                {self.get_css_styles()}
            </style>
        </head>
        <body>
            {self.get_navigation()}
            
            <div class="container">
                <div class="upload-container">
                    <h1>➕ Добавить новое фото</h1>
                    
                    <div class="upload-area" id="uploadArea">
                        <div class="upload-icon">📷</div>
                        <h3>Перетащите фото сюда</h3>
                        <p>или</p>
                        <input type="file" id="fileInput" accept="image/*" multiple style="display: none;">
                        <label for="fileInput" class="btn btn-primary">Выбрать файлы</label>
                    </div>
                    
                    <div class="upload-preview" id="uploadPreview"></div>
                    
                    <div class="upload-progress" id="uploadProgress" style="display: none;">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <p id="progressText">Загрузка...</p>
                    </div>
                </div>
            </div>
            
            {self.get_footer()}
            
            <script>
                {self.get_javascript()}
                
                const uploadArea = document.getElementById('uploadArea');
                const fileInput = document.getElementById('fileInput');
                const uploadPreview = document.getElementById('uploadPreview');
                const uploadProgress = document.getElementById('uploadProgress');
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                
                // Обработка перетаскивания
                uploadArea.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                }});
                
                uploadArea.addEventListener('dragleave', () => {{
                    uploadArea.classList.remove('dragover');
                }});
                
                uploadArea.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    handleFiles(e.dataTransfer.files);
                }});
                
                // Клик по области загрузки
                uploadArea.addEventListener('click', () => {{
                    fileInput.click();
                }});
                
                fileInput.addEventListener('change', (e) => {{
                    handleFiles(e.target.files);
                }});
                
                function handleFiles(files) {{
                    if (files.length === 0) return;
                    
                    uploadPreview.innerHTML = '';
                    uploadProgress.style.display = 'block';
                    progressFill.style.width = '0%';
                    
                    let uploadedCount = 0;
                    
                    Array.from(files).forEach((file, index) => {{
                        if (file.type.startsWith('image/')) {{
                            const reader = new FileReader();
                            
                            reader.onload = function(e) {{
                                const preview = document.createElement('div');
                                preview.className = 'photo-preview';
                                preview.innerHTML = `
                                    <img src="${{e.target.result}}" alt="${{file.name}}">
                                    <div class="preview-info">
                                        <span>${{file.name}}</span>
                                        <span class="file-size">(${{Math.round(file.size/1024)}} KB)</span>
                                    </div>
                                `;
                                uploadPreview.appendChild(preview);
                            }};
                            
                            reader.readAsDataURL(file);
                            
                            // Загрузка на сервер
                            uploadFile(file, index, files.length).then(() => {{
                                uploadedCount++;
                                const progress = (uploadedCount / files.length) * 100;
                                progressFill.style.width = progress + '%';
                                progressText.textContent = `Загружено ${{uploadedCount}} из ${{files.length}}`;
                                
                                if (uploadedCount === files.length) {{
                                    setTimeout(() => {{
                                        showNotification('Все фото загружены!', 'success');
                                        setTimeout(() => window.location.href = '/gallery', 1500);
                                    }}, 500);
                                }}
                            }}).catch(error => {{
                                showNotification('Ошибка загрузки: ' + file.name, 'error');
                            }});
                        }} else {{
                            showNotification('Файл ' + file.name + ' не является изображением', 'error');
                        }}
                    }});
                }}
                
                function uploadFile(file) {{
                    return new Promise((resolve, reject) => {{
                        const formData = new FormData();
                        formData.append('photo', file);
                        
                        fetch('/api/upload', {{
                            method: 'POST',
                            body: formData
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                resolve(data);
                            }} else {{
                                reject(new Error(data.error || 'Unknown error'));
                            }}
                        }})
                        .catch(error => {{
                            reject(error);
                        }});
                    }});
                }}
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_about_page(self):
        """Страница "О нас" """
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>О нас - Нам полгода</title>
            <style>
                {self.get_css_styles()}
            </style>
        </head>
        <body>
            {self.get_navigation()}
            
            <div class="container">
                <h1>💑 О нашей паре</h1>
                
                <div class="about-content">
                    <div class="love-story">
                        <h2>Наша история</h2>
                        <p>Уже полгода мы вместе, и каждый день наполнен любовью, смехом и теплыми моментами. 
                        Этот сайт - наша маленькая цифровая память о самых счастливых мгновениях.</p>
                        
                        <h2>Что здесь есть</h2>
                        <ul>
                            <li>📸 Галерея наших фотографий</li>
                            <li>💌 Возможность добавлять новые фото</li>
                            <li>🎨 Красивый и удобный интерфейс</li>
                            <li>📱 Полная адаптивность для всех устройств</li>
                        </ul>
                        
                        <h2>Технологии любви ❤️</h2>
                        <div class="tech-stack">
                            <div class="tech-item">
                                <h4>Python</h4>
                                <p>Серверная магия</p>
                            </div>
                            <div class="tech-item">
                                <h4>HTML/CSS/JS</h4>
                                <p>Красота и функциональность</p>
                            </div>
                            <div class="tech-item">
                                <h4>Любовь</h4>
                                <p>Главный ингредиент</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {self.get_footer()}
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_contact_page(self, message=None, message_type='success'):
        """Страница контактов"""
        message_html = ""
        if message:
            message_class = "success" if message_type == 'success' else "error"
            message_html = f'<div class="message {message_class}">{html.escape(message)}</div>'
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Контакты - Нам полгода</title>
            <style>
                {self.get_css_styles()}
            </style>
        </head>
        <body>
            {self.get_navigation()}
            
            <div class="container">
                <h1>💌 Свяжись со мной</h1>
                
                {message_html}
                
                <div class="contact-container">
                    <div class="contact-form">
                        <h2>Напиши мне сообщение</h2>
                        <form method="POST" action="/contact">
                            <div class="form-group">
                                <label for="name">Твое имя:</label>
                                <input type="text" id="name" name="name" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="message">Сообщение:</label>
                                <textarea id="message" name="message" rows="5" placeholder="Напиши что-нибудь приятное..." required></textarea>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">Отправить 💕</button>
                        </form>
                    </div>
                    
                    <div class="contact-info">
                        <h2>Наши контакты</h2>
                        <div class="contact-item">
                            <strong>💕 Статус:</strong>
                            <p>Влюблены навсегда</p>
                        </div>
                        <div class="contact-item">
                            <strong>📅 Вместе с:</strong>
                            <p>Полгода и counting...</p>
                        </div>
                        <div class="contact-item">
                            <strong>🎯 Цель:</strong>
                            <p>Быть счастливыми вместе</p>
                        </div>
                    </div>
                </div>
            </div>
            
            {self.get_footer()}
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_contact_form(self):
        """Обработка формы обратной связи"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            
            name = html.escape(params.get('name', [''])[0])
            message = html.escape(params.get('message', [''])[0])
            
            if not name or not message:
                self.send_contact_page("Пожалуйста, заполните все поля", "error")
                return
            
            # Сохраняем сообщение в файл
            os.makedirs('messages', exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(f'messages/message_{timestamp}.txt', 'w', encoding='utf-8') as f:
                f.write(f"От: {name}\n")
                f.write(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Сообщение:\n{message}\n")
            
            success_message = f"Спасибо, {name}! Твое сообщение сохранено в мое сердце 💕"
            self.send_contact_page(success_message, 'success')
            
        except Exception as e:
            self.send_contact_page("Произошла ошибка при отправке сообщения", "error")
    
    def handle_photo_upload(self):
        """Обработка загрузки фото"""
        try:
            content_type = self.headers.get('content-type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Invalid content type")
                return
            
            # Создаем папку для фото если не существует
            os.makedirs(self.PHOTOS_DIR, exist_ok=True)
            
            # Читаем данные формы
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Простой парсинг multipart/form-data
            boundary = content_type.split("boundary=")[1].encode()
            parts = post_data.split(b'--' + boundary)
            
            for part in parts:
                if b'name="photo"' in part and b'filename="' in part:
                    # Извлекаем имя файла
                    filename_start = part.find(b'filename="') + 10
                    filename_end = part.find(b'"', filename_start)
                    if filename_start == 9 or filename_end == -1:
                        continue
                    filename = part[filename_start:filename_end].decode('utf-8', errors='ignore')
                    
                    # Извлекаем данные файла
                    file_data_start = part.find(b'\r\n\r\n') + 4
                    file_data_end = part.find(b'\r\n--', file_data_start)
                    if file_data_start == 3 or file_data_end == -1:
                        continue
                    file_data = part[file_data_start:file_data_end]
                    
                    # Проверяем тип файла
                    if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        response = {'success': False, 'error': 'Invalid file type'}
                        self.send_json_response(response, 400)
                        return
                    
                    # Сохраняем файл
                    safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    filepath = os.path.join(self.PHOTOS_DIR, safe_filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(file_data)
                    
                    # Отправляем успешный ответ
                    response = {'success': True, 'filename': safe_filename}
                    self.send_json_response(response)
                    return
            
            response = {'success': False, 'error': 'No photo found'}
            self.send_json_response(response, 400)
            
        except Exception as e:
            response = {'success': False, 'error': f'Upload error: {str(e)}'}
            self.send_json_response(response, 500)
    
    def handle_photo_delete(self):
        """Удаление фото"""
        try:
            filename = urllib.parse.unquote(self.path.split('/api/delete/')[1])
            filepath = os.path.join(self.PHOTOS_DIR, filename)
            
            if os.path.exists(filepath) and os.path.isfile(filepath):
                os.remove(filepath)
                response = {'success': True}
            else:
                response = {'success': False, 'error': 'File not found'}
            
            self.send_json_response(response)
            
        except Exception as e:
            response = {'success': False, 'error': f'Delete error: {str(e)}'}
            self.send_json_response(response, 500)
    
    def serve_photo(self):
        """Отдача фото"""
        try:
            filename = urllib.parse.unquote(self.path.split('/photos/')[1])
            filepath = os.path.join(self.PHOTOS_DIR, filename)
            
            if os.path.exists(filepath) and os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                
                # Определяем MIME тип
                mime_type, _ = mimetypes.guess_type(filepath)
                if not mime_type:
                    mime_type = 'image/jpeg'
                
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.send_header('Content-Length', str(len(file_data)))
                self.send_header('Cache-Control', 'max-age=3600')  # Кэшируем на 1 час
                self.end_headers()
                self.wfile.write(file_data)
            else:
                self.send_error(404, "Photo not found")
                
        except Exception as e:
            self.send_error(500, f"Photo serve error: {str(e)}")
    
    def send_json_response(self, data, status=200):
        """Утилита для отправки JSON ответов"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_api_time(self):
        """API для получения времени"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = {'time': current_time}
        self.send_json_response(response)
    
    def send_api_photos(self):
        """API для получения списка фото"""
        photos = self.get_photos_list()
        response = {'photos': photos}
        self.send_json_response(response)
    
    def get_photos_list(self):
        """Получение списка фото"""
        try:
            if os.path.exists(self.PHOTOS_DIR):
                photos = []
                for filename in os.listdir(self.PHOTOS_DIR):
                    filepath = os.path.join(self.PHOTOS_DIR, filename)
                    if (os.path.isfile(filepath) and 
                        filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))):
                        photos.append({
                            'name': filename,
                            'url': f'/photos/{urllib.parse.quote(filename)}',
                            'upload_time': os.path.getctime(filepath)
                        })
                # Сортируем по времени загрузки (новые сначала)
                photos.sort(key=lambda x: x['upload_time'], reverse=True)
                return photos
            return []
        except Exception as e:
            print(f"Error getting photos list: {e}")
            return []
    
    def generate_photos_html(self, photos, css_class):
        """Генерация HTML для фотографий"""
        if not photos:
            return ""
        
        photos_html = '<div class="' + css_class + '">'
        for photo in photos:
            photos_html += f"""
            <div class="photo-item">
                <img src="{photo['url']}" 
                     alt="Наше фото" 
                     class="gallery-photo"
                     data-name="{photo['name']}"
                     loading="lazy">
                <div class="photo-overlay">
                    <span class="photo-date">{datetime.fromtimestamp(photo['upload_time']).strftime('%d.%m.%Y %H:%M')}</span>
                </div>
            </div>
            """
        photos_html += '</div>'
        return photos_html
    
    def get_navigation(self):
        """Навигационное меню"""
        return """
        <nav class="navbar">
            <div class="nav-container">
                <a href="/" class="nav-logo">💕 Нам полгода</a>
                <ul class="nav-menu">
                    <li><a href="/">Главная</a></li>
                    <li><a href="/gallery">Галерея</a></li>
                    <li><a href="/upload">Добавить фото</a></li>
                    <li><a href="/about">О нас</a></li>
                    <li><a href="/contact">Контакты</a></li>
                </ul>
            </div>
        </nav>
        """
    
    def get_footer(self):
        """Подвал сайта"""
        current_year = datetime.now().year
        return f"""
        <footer class="footer">
            <div class="container">
                <p>&copy; {current_year} Нам полгода 💕</p>
                <p>Сделано с любовью на Python</p>
            </div>
        </footer>
        """
    
    def get_css_styles(self):
        """CSS стили"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            min-height: calc(100vh - 140px);
        }
        
        /* Навигация */
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        
        .nav-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #e91e63;
            text-decoration: none;
        }
        
        .nav-menu {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-menu a {
            color: #333;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-menu a:hover {
            color: #e91e63;
        }
        
        /* Герой секция */
        .hero {
            text-align: center;
            padding: 4rem 2rem;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
        }
        
        .hero h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #e91e63, #9c27b0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .hero p {
            font-size: 1.2rem;
            color: #666;
        }
        
        /* Приветственная секция */
        .welcome-section {
            background: rgba(255, 255, 255, 0.9);
            padding: 3rem;
            border-radius: 20px;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
        }
        
        .welcome-text h2 {
            color: #e91e63;
            margin-bottom: 1rem;
        }
        
        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }
        
        /* Кнопки */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #e91e63, #9c27b0);
            color: white;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.9);
            color: #e91e63;
            border: 2px solid #e91e63;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .text-center {
            text-align: center;
            margin-top: 2rem;
        }
        
        .no-photos {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 2rem;
        }
        
        /* Статистика */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1.5rem;
            margin: 3rem 0;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem 1rem;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #e91e63;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #666;
            font-weight: 500;
        }
        
        /* Галерея */
        .gallery-header {
            text-align: center;
            margin-bottom: 3rem;
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .gallery-header h1 {
            color: #e91e63;
            margin-bottom: 1rem;
        }
        
        .latest-photos, .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .photo-item {
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
            background: white;
            aspect-ratio: 1;
        }
        
        .photo-item:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        
        .gallery-photo {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.3s ease;
        }
        
        .photo-item:hover .gallery-photo {
            transform: scale(1.1);
        }
        
        .photo-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.7));
            color: white;
            padding: 1rem;
            transform: translateY(100%);
            transition: transform 0.3s ease;
        }
        
        .photo-item:hover .photo-overlay {
            transform: translateY(0);
        }
        
        .photo-date {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        /* Пустая галерея */
        .empty-gallery {
            text-align: center;
            padding: 4rem 2rem;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .empty-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        /* Загрузка фото */
        .upload-container {
            background: rgba(255, 255, 255, 0.9);
            padding: 3rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .upload-area {
            border: 3px dashed #e91e63;
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area.dragover {
            background: rgba(233, 30, 99, 0.1);
            border-color: #9c27b0;
        }
        
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        .upload-preview {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .photo-preview {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .photo-preview img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 5px;
            margin-bottom: 0.5rem;
        }
        
        .preview-info {
            font-size: 0.9rem;
            color: #666;
        }
        
        .file-size {
            color: #999;
            font-size: 0.8rem;
        }
        
        /* Прогресс бар */
        .upload-progress {
            margin: 2rem 0;
        }
        
        .progress-bar {
            width: 100%;
            height: 10px;
            background: #eee;
            border-radius: 5px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #e91e63, #9c27b0);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        /* Модальное окно */
        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            animation: fadeIn 0.3s;
        }
        
        .modal-content {
            display: block;
            margin: auto;
            max-width: 90%;
            max-height: 80%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 10px;
        }
        
        .modal-caption {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            text-align: center;
            background: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 5px;
        }
        
        .close {
            position: absolute;
            top: 20px;
            right: 35px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            z-index: 2001;
        }
        
        .close:hover {
            color: #e91e63;
        }
        
        .modal-delete {
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 2001;
        }
        
        /* Сообщения */
        .message {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        /* Формы */
        .contact-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            margin-top: 2rem;
        }
        
        .contact-form, .contact-info {
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
        }
        
        .form-group input:focus,
        .form-group textarea:focus {
            border-color: #e91e63;
            outline: none;
        }
        
        .contact-item {
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }
        
        .contact-item:last-child {
            border-bottom: none;
        }
        
        /* О нас */
        .about-content {
            background: rgba(255, 255, 255, 0.9);
            padding: 3rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .love-story h2 {
            color: #e91e63;
            margin: 2rem 0 1rem 0;
        }
        
        .love-story ul {
            margin: 1rem 0 2rem 2rem;
        }
        
        .love-story li {
            margin-bottom: 0.5rem;
            list-style-type: none;
            position: relative;
            padding-left: 1.5rem;
        }
        
        .love-story li:before {
            content: "•";
            color: #e91e63;
            font-size: 1.5rem;
            position: absolute;
            left: 0;
            top: -0.3rem;
        }
        
        .tech-stack {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .tech-item {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* Подвал */
        .footer {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
            backdrop-filter: blur(10px);
        }
        
        /* Анимации */
        @keyframes fadeIn {
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }
        
        /* Адаптивность */
        @media (max-width: 768px) {
            .nav-container {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-menu {
                gap: 1rem;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .contact-container {
                grid-template-columns: 1fr;
            }
            
            .latest-photos, .gallery-grid {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }
            
            .action-buttons {
                flex-direction: column;
                align-items: center;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .modal-content {
                max-width: 95%;
                max-height: 70%;
            }
            
            .modal-delete {
                bottom: 10px;
                right: 10px;
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 10px;
            }
            
            .hero {
                padding: 2rem 1rem;
            }
            
            .welcome-section, .about-content, .upload-container {
                padding: 1.5rem;
            }
            
            .latest-photos, .gallery-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def get_javascript(self):
        """JavaScript код"""
        return """
        function showNotification(message, type = 'success') {
            // Создаем элемент уведомления
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                z-index: 3000;
                font-weight: 500;
                animation: slideInRight 0.3s ease, fadeOut 0.3s ease 2.7s;
                max-width: 300px;
                word-wrap: break-word;
            `;
            
            if (type === 'success') {
                notification.style.background = '#27ae60';
            } else {
                notification.style.background = '#e74c3c';
            }
            
            document.body.appendChild(notification);
            
            // Удаляем уведомление через 3 секунды
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        }
        
        // Анимации для уведомлений
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes fadeOut {
                from {
                    opacity: 1;
                }
                to {
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Предотвращение отправки формы при нажатии Enter
        document.addEventListener('DOMContentLoaded', function() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                        e.preventDefault();
                    }
                });
            });
        });
        """
    
    def log_message(self, format, *args):
        """Переопределяем метод логирования для тишины"""
        pass

def main():
    """Запуск веб-сервера"""
    port = 8000
    server_address = ('', port)
    
    # Создаем необходимые папки
    os.makedirs('photos', exist_ok=True)
    os.makedirs('messages', exist_ok=True)
    
    print("🎉 Запуск сайта 'Нам полгода'")
    print(f"🌐 Сервер доступен по адресу: http://localhost:{port}")
    print("💕 Сайт создан с любовью!")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print()
    print("📁 Структура:")
    print("   📸 photos/ - папка для фотографий")
    print("   💌 messages/ - папка для сообщений")
    print()
    
    try:
        httpd = HTTPServer(server_address, WebsiteHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == '__main__':
    main()