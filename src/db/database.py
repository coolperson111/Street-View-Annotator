import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()


class Database:
    def __init__(self):
        # Fetch database connection details from environment variables
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PWD")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")

        # Establish connection to the database.conn = None
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.cur = self.conn.cursor()
            print("Database connection successful.")
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def insert_annotation(
        self,
        stview_image_path,
        stview_heading,
        stview_latlng,
        tree_latlng,
        stview_pano_id=None,
        tree_species=None,
        tree_height=None,
        tree_diameter=None,
        annotator_name=None,
    ):
        insert_query = sql.SQL(
            """
            INSERT INTO tree_annotations (
                stview_image_path, stview_heading, stview_latlng, tree_latlng, stview_pano_id, tree_species, tree_height, tree_diameter, annotator_name
            ) VALUES (
                %s, %s, ST_GeomFromText(%s), ST_GeomFromText(%s), %s, %s, %s, %s, %s
            )
        """
        )
        try:
            self.cur.execute(
                insert_query,
                (
                    stview_image_path,
                    stview_heading,
                    stview_latlng,
                    tree_latlng,
                    stview_pano_id,
                    tree_species,
                    tree_height,
                    tree_diameter,
                    annotator_name,
                ),
            )
            self.conn.commit()
            print("Annotation inserted successfully.")
        except Exception as e:
            print(f"Error inserting annotation: {e}")
            self.conn.rollback()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")
