from sqlalchemy.orm import sessionmaker
import Parser.powerpoint_parser as powerpoint_parser
import Explainer.gpt_explainer as gpt_explainer
import Utils.gather_explanations_to_json as gather_explanations_to_json
import asyncio
from datetime import datetime
import os
import time
from Database.database_orm import *


async def main():
    """
    This function is used to process the PowerPoint presentations in the uploads folder and save the explanations in
    the outputs folder.
    """

    while True:
        engine = create_engine(f'sqlite:///../Database/db/mydatabase.db', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        uploads = session.query(Upload).filter_by(status=UploadStatus.PENDING).all()

        for upload in uploads:
            upload.status = UploadStatus.PROCESSING
            session.commit()
            uid = upload.uid
            filename = upload.filename

            path = f'../Web_api/uploads/{uid}.pptx'

            if not os.path.exists(path):
                print("File not found")
                upload.status = UploadStatus.FAILED
                session.commit()
                session.close()
                break

            print(f'processing {filename}...')

            pptx_object = powerpoint_parser.PowerpointParser(path)

            gpt_object = gpt_explainer.GptExplainer()

            coroutines = [gpt_object.send_slide_text_to_gpt(slide_number, slide_text) for slide_number, slide_text
                          in
                          enumerate(pptx_object.extract_text_from_slide())]

            await asyncio.gather(*coroutines)

            gather_explanations_to_json.save_to_json(gpt_object.get_explanations_slides(), path)

            print(f'{filename} was processed successfully')
            upload.status = UploadStatus.DONE
            upload.finish_time = datetime.now()
            session.commit()
            session.close()

        time.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
