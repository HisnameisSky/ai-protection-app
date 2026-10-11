import io
import json
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import numpy as np
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/redaction", tags=["Redaction Service"])

class RedactionItem(BaseModel):
    text: str
    category: str
    box_2d: List[int]  # [ymin, xmin, ymax, xmax] (0〜1000の相対座標)
    reason: str

class RedactionPayload(BaseModel):
    targets: List[RedactionItem]

@router.post("/image")
async def redact_image(
    file: UploadFile = File(...),
    targets_json: str = Form(...)
):
    """
    画像ファイルに対して、指定された相対座標（box_2d）に基づき黒塗り（マスク）を施す
    """
    try:
        # JSONパースのエラーハンドリング
        try:
            targets_data = json.loads(targets_json)
            targets = targets_data.get("targets", [])
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format in targets_json.")

        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = image.size
        draw = ImageDraw.Draw(image)

        for target in targets:
            box = target.get("box_2d")
            if box and len(box) == 4:
                ymin, xmin, ymax, xmax = box
                
                # 0〜1000の範囲にクランプ（はみ出し・異常値防止）
                ymin = max(0, min(1000, ymin))
                xmin = max(0, min(1000, xmin))
                ymax = max(0, min(1000, ymax))
                xmax = max(0, min(1000, xmax))

                # 相対座標（0〜1000）を実際のピクセル座標に変換
                x0 = int((xmin / 1000.0) * width)
                y0 = int((ymin / 1000.0) * height)
                x1 = int((xmax / 1000.0) * width)
                y1 = int((ymax / 1000.0) * height)

                # 反転防止
                if x0 > x1: x0, x1 = x1, x0
                if y0 > y1: y0, y1 = y1, y0

                # 黒塗り矩形を描画
                draw.rectangle([x0, y0, x1, y1], fill="black")

        output_buf = io.BytesIO()
        image.save(output_buf, format="PNG")
        output_buf.seek(0)

        return StreamingResponse(
            output_buf,
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="redacted_{file.filename}"'}
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image redaction failed: {str(e)}")


@router.post("/pdf")
async def redact_pdf(
    file: UploadFile = File(...),
    targets_json: str = Form(...)
):
    """
    PDFファイルに対して、指定された座標に基づき各ページの指定領域を黒塗り（Redaction）処理する
    """
    try:
        try:
            targets_data = json.loads(targets_json)
            targets = targets_data.get("targets", [])
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format in targets_json.")

        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            page_rect = page.rect
            width = page_rect.width
            height = page_rect.height

            for target in targets:
                box = target.get("box_2d")
                if box and len(box) == 4:
                    ymin, xmin, ymax, xmax = box

                    ymin = max(0, min(1000, ymin))
                    xmin = max(0, min(1000, xmin))
                    ymax = max(0, min(1000, ymax))
                    xmax = max(0, min(1000, xmax))

                    x0 = (xmin / 1000.0) * width
                    y0 = (ymin / 1000.0) * height
                    x1 = (xmax / 1000.0) * width
                    y1 = (ymax / 1000.0) * height

                    if x0 > x1: x0, x1 = x1, x0
                    if y0 > y1: y0, y1 = y1, y0

                    rect = fitz.Rect(x0, y0, x1, y1)
                    # PyMuPDFの公式レダクション機能を使用してテキストと背景を完全に消去
                    page.add_redact_annot(rect, fill=(0, 0, 0))

            page.apply_redactions()

        output_buf = io.BytesIO()
        doc.save(output_buf)
        doc.close()
        output_buf.seek(0)

        return StreamingResponse(
            output_buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="redacted_{file.filename}"'}
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF redaction failed: {str(e)}")