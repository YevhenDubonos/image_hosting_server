import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT')
            )
            print("✅ Connected to PostgreSQL")
        except Exception as e:
            print(f"❌ Connection error: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("🛑 Disconnected from PostgreSQL")

    def save_metadata(self, filename, original_name, size, file_type):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                """, (filename, original_name, size, file_type))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False

    def get_all_images(self, page=1, per_page=10):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT * FROM images
                    ORDER BY upload_time DESC
                    LIMIT %s OFFSET %s
                """, (per_page, offset))
                images = cursor.fetchall()

                cursor.execute("SELECT COUNT(*) FROM images")
                total = cursor.fetchone()['count']

                return images, total
        except Exception as e:
            print(f"❌ Retrieval error: {e}")
            return [], 0

    def delete_image(self, image_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT filename FROM images WHERE id = %s", (image_id,))
                result = cursor.fetchone()
                if not result:
                    return False

                filename = result[0]
                cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))
                self.connection.commit()
                return filename
        except Exception as e:
            print(f"❌ Delete error: {e}")
            return False
