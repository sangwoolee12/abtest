import os, base64
import google.genai as genai
from .models import ImageGenerationRequest, ImageGenerationResponse

def generate_images_with_gemini(req: ImageGenerationRequest) -> ImageGenerationResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("Gemini API key not configured")

    client = genai.Client(api_key=api_key)

    # 사용자 프롬프트에서 마케팅 문구와 스타일 정보 추출
    user_prompt = req.prompt.strip()
    
    # 마케팅 문구와 스타일 요청이 모두 포함된 경우만 처리
    if "마케팅 문구:" in user_prompt and "스타일 요청:" in user_prompt:
        # 마케팅 문구와 스타일을 분리
        parts = user_prompt.split("스타일 요청:")
        marketing_part = parts[0].replace("마케팅 문구:", "").strip()
        style_request = parts[1].strip()
        
        if not style_request:
            raise Exception("스타일 요청이 비어있어요. 이미지 스타일을 입력해주세요.")
        
        if not marketing_part:
            raise Exception("마케팅 문구가 비어있어요. 마케팅 문구를 선택해주세요.")
        
        # 마케팅 문구의 뉘앙스를 반영하여 이미지 생성
        prompt = (
            f"Create a professional advertisement image that captures the essence and mood of this marketing message: '{marketing_part}'. "
            f"Style requirements: {style_request}, "
            "modern design, high quality, business style, 1024x1024 resolution. "
            "The image should reflect the emotional tone, target audience, and brand personality conveyed in the marketing text. "
            "IMPORTANT: Generate an image, not text. Return image data only. "
            "Do not include any text or words in the image."
        )
    else:
        # 마케팅 문구나 스타일 요청이 없는 경우 에러 발생
        raise Exception("마케팅 문구와 스타일 요청이 모두 필요합니다.")

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
            image_found = False
            for part in content.parts:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    mime = getattr(inline, "mime_type", "image/png")
                    raw: bytes = inline.data
                    b64 = base64.b64encode(raw).decode("ascii")
                    image_urls.append(f"data:{mime};base64,{b64}")
                    print(f"✅ 이미지 {i+1} 생성 성공")
                    image_found = True
                    break
                elif getattr(part, "text", None):
                    print(f"📝 이미지 {i+1} 텍스트 응답: {part.text[:120]}...")
            
            # 이미지를 찾지 못한 경우 재시도
            if not image_found:
                print(f"⚠️ 이미지 {i+1}에서 이미지 데이터를 찾을 수 없음, 재시도...")
                # 재시도 로직 추가
                try:
                    retry_prompt = f"{prompt}, create image, variation {i+1}, no text response"
                    retry_resp = client.models.generate_content(
                        model="gemini-2.5-flash-image-preview",
                        contents=[retry_prompt],
                    )
                    
                    if getattr(retry_resp, "candidates", None):
                        retry_cand = retry_resp.candidates[0]
                        retry_content = getattr(retry_cand, "content", None)
                        if retry_content and getattr(retry_content, "parts", None):
                            for retry_part in retry_content.parts:
                                retry_inline = getattr(retry_part, "inline_data", None)
                                if retry_inline and getattr(retry_inline, "data", None):
                                    mime = getattr(retry_inline, "mime_type", "image/png")
                                    raw: bytes = retry_inline.data
                                    b64 = base64.b64encode(raw).decode("ascii")
                                    image_urls.append(f"data:{mime};base64,{b64}")
                                    print(f"✅ 이미지 {i+1} 재시도 성공")
                                    image_found = True
                                    break
                except Exception as retry_e:
                    print(f"⚠️ 이미지 {i+1} 재시도 실패: {retry_e}")
                
                if not image_found:
                    print(f"❌ 이미지 {i+1} 최종 실패")
            
        except Exception as e:
            print(f"⚠️ 이미지 {i+1} 생성 중 오류: {e}")
            continue

    if not image_urls:
        raise Exception("Gemini 응답에서 이미지 데이터를 찾을 수 없음")

    print(f"🎉 총 {len(image_urls)}개 이미지 생성 완료")
    return ImageGenerationResponse(images=image_urls)