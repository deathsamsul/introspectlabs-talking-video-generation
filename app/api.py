from fastapi import FastAPI, UploadFile, File, Form
import shutil
from generate_avatar import generate_avatar

app = FastAPI()

@app.post("/generate-avatar")
async def generate(
    image: UploadFile = File(...),
    text: str = Form(...),
    emotion: str = Form(...)
):

    image_path = f"samples/{image.filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    output_video = "outputs/avatar_output.mp4"

    generate_avatar(
        image=image_path,
        text=text,
        emotion=emotion,
        output=output_video
    )

    return {
        "status": "success",
        "video_path": output_video
    }