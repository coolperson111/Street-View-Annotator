import getpass
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()


class Database:
    def __init__(self):
        # Database connection URL
        DB_URL = os.getenv("DATABASE_URL")

        # Establish connection to the database
        try:
            self.conn = psycopg2.connect(DB_URL)
            self.cur = self.conn.cursor()
            print("Database connection successful.")
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def get_or_create_streetview_image(
        self, pano_id, image_path, stview_lat, stview_lng
    ):
        # Check if the pano_id already exists in streetview_images
        check_query = sql.SQL(
            "SELECT image_id FROM streetview_images WHERE pano_id = %s"
        )
        insert_query = sql.SQL(
            "INSERT INTO streetview_images (pano_id, image_path, lat, lng) VALUES (%s, %s, %s, %s) RETURNING image_id"
        )

        try:
            self.cur.execute(check_query, (pano_id,))
            result = self.cur.fetchone()

            if result:
                image_id = result[0]
            else:
                self.cur.execute(
                    insert_query, (pano_id, image_path, stview_lat, stview_lng)
                )
                image_id = self.cur.fetchone()[0]
                self.conn.commit()

            return image_id

        except Exception as e:
            print(f"Error in get_or_create_streetview_image: {e}")
            self.conn.rollback()
            return None

    def insert_annotation(
        self,
        image_path,
        pano_id,
        stview_lat,
        stview_lng,
        tree_lat,
        tree_lng,
        lat_offset=None,
        lng_offset=None,
        image_x=None,
        image_y=None,
        height=None,
        diameter=None,
    ):
        image_id = self.get_or_create_streetview_image(
            pano_id, image_path, stview_lat, stview_lng
        )

        user = getpass.getuser()

        if image_id is None:
            print("Error: Could not obtain image_id for the annotation.")
            return

        insert_query = sql.SQL(
            """
            INSERT INTO tree_details (
                image_id, lat, lng, lat_offset, lng_offset, image_x, image_y, annotator_name, height, diameter
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
        )
        try:
            self.cur.execute(
                insert_query,
                (
                    image_id,
                    tree_lat,
                    tree_lng,
                    lat_offset,
                    lng_offset,
                    image_x,
                    image_y,
                    user,
                    height,
                    diameter,
                ),
            )
            self.conn.commit()
            print("Annotation inserted successfully.")
        except Exception as e:
            print(e)
            self.conn.rollback()

    def load_saved(self):

        query = sql.SQL("SELECT lat, lng, lat_offset, lng_offset FROM tree_details;")

        try:
            self.cur.execute(query)
            return self.cur.fetchall()
        except Exception as e:
            print(f"Error in load_saved: {e}")
            return []

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
