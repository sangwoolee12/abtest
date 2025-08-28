# image_generation.py
import os, base64
import google.genai as genai
from .models import ImageGenerationRequest, ImageGenerationResponse

def generate_images_with_gemini(req: ImageGenerationRequest) -> ImageGenerationResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("Gemini API key not configured")

    client = genai.Client(api_key=api_key)

    prompt = (
        f"professional advertisement image, {req.prompt}, "
        "modern design, high quality, business style, 1024x1024"
    )

    image_urls = []
    
    # 요청된 개수만큼 이미지 생성 (최대 3개)
    max_images = min(req.n, 3)
    
    for i in range(max_images):
        try:
            # 각 이미지마다 약간 다른 프롬프트 생성 (다양성 확보)
            varied_prompt = f"{prompt}, variation {i+1}"
            
            resp = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[varied_prompt],
            )

            if not getattr(resp, "candidates", None):
                print(f"⚠️ 이미지 {i+1} 생성 실패: candidates 없음")
                continue

            cand = resp.candidates[0]
            content = getattr(cand, "content", None)
            if not content or not getattr(content, "parts", None):
                print(f"⚠️ 이미지 {i+1} 생성 실패: content parts 없음")
                continue

            # 이미지 데이터 찾기
            for part in content.parts:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    mime = getattr(inline, "mime_type", "image/png")
                    raw: bytes = inline.data
                    b64 = base64.b64encode(raw).decode("ascii")
                    image_urls.append(f"data:{mime};base64,{b64}")
                    print(f"✅ 이미지 {i+1} 생성 성공")
                    break
                elif getattr(part, "text", None):
                    print(f"📝 이미지 {i+1} 텍스트 응답: {part.text[:120]}...")
            
        except Exception as e:
            print(f"⚠️ 이미지 {i+1} 생성 중 오류: {e}")
            continue

    if not image_urls:
        raise Exception("Gemini 응답에서 이미지 데이터를 찾을 수 없음")

    print(f"🎉 총 {len(image_urls)}개 이미지 생성 완료")
    return ImageGenerationResponse(images=image_urls)