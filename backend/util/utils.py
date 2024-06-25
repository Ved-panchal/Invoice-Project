from fastapi.responses import JSONResponse
from bson import ObjectId

class Utils:
    def convert_objectid(self, doc):
        try:
            if isinstance(doc, dict):
                return {key: self.convert_objectid(value) for key, value in doc.items()}
            elif isinstance(doc, list):
                return [self.convert_objectid(item) for item in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            else:
                return doc
        except Exception as e:
            raise Exception(f'Error converting object_id\nDetails: {e}\nPlease contact administrator.')

    def upload_files_to_queue(self, queue_manager, filenames: list[str], user_id: str):
        try:
            queue_manager.call(filenames, user_id)
            # await queue_manager.call(filenames, user_id)
            print("message: ", "File uploaded successfully")
            return JSONResponse(content={"message": "File uploaded successfully"})
        except Exception as e:
            return JSONResponse(content={"message": "File upload failed", "error": str(e)})