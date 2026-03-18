import http.server
import socketserver
import os
import json
import io
import re
from validators import validate_image_file
from file_handler import save_file, delete_file
from database import DatabaseManager

db = DatabaseManager()


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            '/': 'index.html',
            '/upload': 'upload.html',
            '/images-list': 'images.html'
        }

        if self.path in routes:
            self.serve_template(routes[self.path])
        elif self.path.startswith('/static/'):
            self.serve_static(self.path)
        elif self.path.startswith('/api/images'):
            self.handle_get_images()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/api/images/'):
            self.handle_delete_image()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_upload(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Expected multipart/form-data")
                return

            form_data = self.rfile.read(int(self.headers['Content-Length']))
            filename = self._extract_filename(form_data)
            file_like = io.BytesIO(form_data)

            is_valid, message = validate_image_file(file_like, filename)

            if not is_valid:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': message
                }).encode('utf-8'))
                return

            file_bytes = self._extract_file_bytes(form_data)
            saved_name = save_file(file_bytes, filename)

            ext = filename.lower().split('.')[-1]
            db.save_metadata(
                filename=saved_name,
                original_name=filename,
                size=len(file_bytes),
                file_type=ext
            )

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': saved_name,
                'url': f'https://group6-image-hosting-server.com/{saved_name}'
            }).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))

    def handle_get_images(self):
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            page = int(params.get('page', [1])[0])

            images, total = db.get_all_images(page=page)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'images': [dict(img) for img in images],
                'total': total,
                'page': page
            }, default=str).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))

    def handle_delete_image(self):
        try:
            image_id = int(self.path.split('/')[-1])
            filename = db.delete_image(image_id)

            if filename:
                delete_file(filename)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': f'Image {filename} deleted successfully'
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Image not found'
                }).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))

    def _extract_filename(self, form_data):
        try:
            decoded = form_data.decode('utf-8', errors='ignore')
            match = re.search(r'filename="([^"]+)"', decoded)
            if match:
                return match.group(1)
        except Exception:
            pass
        return "unknown"

    def _extract_file_bytes(self, form_data):
        boundary = form_data.split(b'\r\n')[0]
        parts = form_data.split(boundary)

        for part in parts:
            if b'Content-Type:' in part or b'filename=' in part:
                header_end = part.find(b'\r\n\r\n')
                if header_end != -1:
                    file_content = part[header_end + 4:]
                    if file_content.endswith(b'\r\n'):
                        file_content = file_content[:-2]
                    return file_content
        return b''

    def serve_template(self, filename):
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'templates', filename)
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def serve_static(self, path):
        try:
            file_path = path[len('/static/'):]
            static_path = os.path.join(os.path.dirname(__file__), 'static', file_path)
            with open(static_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', self.get_content_type(file_path))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def get_content_type(self, file_path):
        if file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith('.png'):
            return 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            return 'image/jpeg'
        else:
            return 'application/octet-stream'


def run_server(port=8000):
    port = int(os.environ.get('PORT', port))
    db.connect()
    try:
        with socketserver.TCPServer(("", port), ImageServerHandler) as httpd:
            print(f"🚀 Server running on port {port} ...")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:
            print(f"❌ Port {port} is already in use. Please stop the server | lsof -ti :{port} | xargs kill -9")
        else:
            print(f"❌ Error starting server: {e}")
    finally:
        db.disconnect()


if __name__ == "__main__":
    run_server()