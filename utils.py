
import io
from pptx import Presentation
from pdf2image import convert_from_bytes
from PIL import Image
import openai
import base64
import asyncio

SYSTEM_PROMPT = """
You are a world-class presentation designer reviewing pitch decks.
Evaluate slide layout and design only (not content), based on these:
Emphasis, Balance, Contrast, Proportion, Whitespace, Rhythm, Hierarchy, Unity.
Return simple bullet points in this format:
• [short feedback]
"""

async def process_slide(image: Image.Image, index: int):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    response = await openai.ChatCompletion.acreate(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": f"Slide {index + 1}:"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
            ]}
        ],
        max_tokens=500
    )
    return {
        "slide": index + 1,
        "feedback": response.choices[0].message.content.strip().split("\n")
    }

async def process_presentation(content: bytes, filename: str):
    if filename.endswith(".pdf"):
        slides = convert_from_bytes(content)
    elif filename.endswith(".pptx"):
        slides = convert_ppt_to_images(content)
    else:
        return {"error": "Unsupported file format"}

    results = await asyncio.gather(*(process_slide(slide, i) for i, slide in enumerate(slides[:10])))

    summary_text = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Write an overall design summary for the slides. Format: bullet points."},
            {"role": "user", "content": "\n\n".join(["\n".join(r["feedback"]) for r in results])}
        ],
        max_tokens=300
    )

    return {
        "slides": results,
        "summary": summary_text.choices[0].message.content.strip().split("\n")
    }

def convert_ppt_to_images(content: bytes):
    prs = Presentation(io.BytesIO(content))
    images = []
    for slide in prs.slides:
        img = Image.new("RGB", (1920, 1080), color="white")
        images.append(img)
    return images
