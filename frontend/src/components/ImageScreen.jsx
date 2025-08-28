import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';


const ImageScreenContainer = styled.div`
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);

  @media (min-width: 768px) {
    padding: 30px 40px;
  }

  @media (min-width: 1024px) {
    padding: 30px 80px;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
`;

const LogoIcon = styled.div`
  width: 33px;
  height: 33px;
  position: relative;
`;

const LogoSquare1 = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 33px;
  height: 33px;
  background: #99EA48;
  border-radius: 3px 3px 53px 3px;
`;

const LogoSquare2 = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 33px;
  height: 33px;
  background: #99EA48;
  border-radius: 3px 3px 53px 3px;
`;

const LogoSquare3 = styled.div`
  position: absolute;
  top: 11.5px;
  left: 11.5px;
  width: 14px;
  height: 14px;
  background: #191F33;
  border-radius: 3px 3px 53px 3px;
`;

const LogoText = styled.h1`
  font-family: 'Manrope', sans-serif;
  font-weight: 700;
  font-size: 24px;
  line-height: 1.366;
  letter-spacing: -0.05em;
  color: #020407;
  margin: 0;
`;

const MainContent = styled.main`
  padding: 32px 20px;
  min-height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  max-width: 100%;

  @media (min-width: 768px) {
    padding: 60px 40px;
  }

  @media (min-width: 1024px) {
    padding: 80px 188px;
  }
`;

const PageHeader = styled.div`
  text-align: center;
  margin-bottom: 20px;
`;

const PageTitle = styled.h2`
  font-family: 'Apple SD Gothic Neo', sans-serif;
  font-weight: 600;
  font-size: 24px;
  line-height: 1.2;
  color: #000000;
  margin: 0;
  max-width: 100%;

  @media (min-width: 768px) {
    font-size: 32px;
    max-width: 700px;
  }

  @media (min-width: 1024px) {
    font-size: 36px;
  }
`;

const TabContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 18px;
`;

const Tab = styled.div`
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.5;
  color: #6A6A6A;
`;

const FilterBlock = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  margin: 0 auto 18px;

  @media (min-width: 768px) {
    width: 500px;
  }

  @media (min-width: 1024px) {
    width: 612px;
  }
`;

const FilterHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
`;

const FilterTitle = styled.h3`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.5;
  color: #31373D;
  margin: 0;
`;

const ResetButton = styled.button`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.5;
  color: #EA5F38;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin: 0;

  &:hover {
    text-decoration: underline;
  }
`;

const StyleSelector = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 16px 20px;
  min-height: 48px;
  background: #FAFAFA;
  border: 1px solid #ECEDF0;
  border-radius: 12px;
`;

const StyleText = styled.span`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 1.5;
  color: #31373D;
  word-break: break-word;
  text-align: left;
`;

const StyleInput = styled.input`
  width: 100%;
  height: 48px;
  padding: 0 16px;
  background: #FFFFFF;
  border: 1px solid #ECEDF0;
  border-radius: 12px;
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 1.5;
  color: #222222;
  outline: none;

  &::placeholder {
    color: #9AA0A6;
  }

  &:focus {
    border-color: #99EA48;
    box-shadow: 0 0 0 3px rgba(153, 234, 72, 0.1);
  }
`;

const StyleDescription = styled.div`
  margin-top: 3px;
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 400;
  font-size: 12px;
  line-height: 1.4;
  color: #666666;
  text-align: left;
`;

const GenerateButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 32px;
  background: #C3C3C3;
  border: none;
  border-radius: 70px;
  color: #010205;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 16px;
  line-height: 1.4;
  letter-spacing: -0.02em;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 30px auto;

  &:hover {
    background: #B0B0B0;
    transform: translateY(-2px);
  }

  &:disabled {
    background: #E0E0E0;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingSpinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #010205;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ResultsContainer = styled.div`
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  justify-content: center;

  @media (min-width: 768px) {
    max-width: 600px;
    flex-direction: row;
    gap: 24px;
  }

  @media (min-width: 1024px) {
    max-width: 753px;
  }
`;

const ImageCard = styled.div`
  width: 100%;
  background: #FFFFFF;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 32px;

  @media (min-width: 768px) {
    width: 180px;
    padding: 28px;
    gap: 48px;
  }

  @media (min-width: 1024px) {
    width: 235px;
    padding: 32px;
    gap: 56px;
  }
`;

const ImagePlaceholder = styled.div`
  width: 171px;
  height: 193px;
  background: #F0F0F0;
  border-radius: 20px;
  backdrop-filter: blur(84px);
  position: relative;
  margin: 0 auto;
`;

const ImageLines = styled.div`
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 139.31px;
  height: 0;
`;

const LongLine = styled.div`
  width: 139.31px;
  height: 6.65px;
  background: #D9D9D9;
  border-radius: 3.325px;
`;

const ShortLine = styled.div`
  width: 93.09px;
  height: 6.65px;
  background: #000000;
  border-radius: 3.325px;
  margin-top: 10px;
`;

const DownloadButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 32px;
  background: transparent;
  border: 1px solid rgba(155, 155, 156, 0.42);
  border-radius: 70px;
  color: #010205;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 16px;
  line-height: 1.4;
  letter-spacing: -0.02em;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;

  &:hover {
    background: rgba(155, 155, 156, 0.1);
    transform: translateY(-2px);
  }
`;

const RegenerateButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 32px;
  background: transparent;
  border: 1px solid rgba(155, 155, 156, 0.42);
  border-radius: 70px;
  color: #010205;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 16px;
  line-height: 1.4;
  letter-spacing: -0.02em;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: -45px;

  &:hover {
    background: rgba(155, 155, 156, 0.1);
    transform: translateY(-2px);
  }

  &:disabled {
    background: #E0E0E0;
    cursor: not-allowed;
    transform: none;
  }
`;

const ImageScreen = () => {
  const navigate = useNavigate();

  const [isGenerating, setIsGenerating] = useState(false);
  const [regeneratingImages, setRegeneratingImages] = useState([false, false, false]);
  const [imagesGenerated, setImagesGenerated] = useState(false);
  const [generatedImageUrls, setGeneratedImageUrls] = useState([]);
  const [imageStyle, setImageStyle] = useState('');

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleGenerateImages = async () => {
    try {
      // localStorage에서 선택된 마케팅 문구 가져오기
      const selectedOption = localStorage.getItem('selectedOption');
      const selectionLogs = JSON.parse(localStorage.getItem('selectionLogs') || '[]');
      
      if (!selectedOption || selectionLogs.length === 0) {
        alert('먼저 PredictionScreen에서 문구를 선택해주세요.');
        return;
      }
      
      // 가장 최근 선택 로그에서 마케팅 문구 가져오기
      const latestLog = selectionLogs[selectionLogs.length - 1];
      const marketingText = latestLog.marketingText;
      
      if (!marketingText) {
        alert('선택된 마케팅 문구를 찾을 수 없습니다.');
        return;
      }
      
      // 스타일 입력 검증
      if (!imageStyle.trim()) {
        alert('이미지 스타일을 입력해주세요. (예: 밝고 따뜻한 느낌, 파스텔 톤, 미니멀한 디자인)');
        return;
      }
      
      setIsGenerating(true);
      
      // 마케팅 문구와 스타일을 결합하여 이미지 생성
      const combinedPrompt = `마케팅 문구: ${marketingText}\n스타일 요청: ${imageStyle.trim()}`;

      console.log('🔍 이미지 생성 요청:', {
        prompt: combinedPrompt,
        n: 3,
        size: '1024x1024'
      });
      
      // API 호출하여 이미지 생성
      const response = await fetch('/api/generate-images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: combinedPrompt,
          n: 3, // 3개의 이미지 생성
          size: '1024x1024'
        }),
      });
      
      console.log('🔍 API 응답 상태:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔍 API 오류 응답:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('🔍 API 응답 데이터:', data);
      
      if (data.images && data.images.length > 0) {
        console.log('✅ 이미지 생성 성공:', data.images.length, '개');
        setGeneratedImageUrls(data.images);
        setImagesGenerated(true);
      } else {
        console.error('⚠️ 이미지 데이터가 없음:', data);
        throw new Error('이미지 생성에 실패했습니다.');
      }
      
    } catch (error) {
      console.error('이미지 생성 오류:', error);
      alert('이미지 생성 중 오류가 발생했습니다: ' + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async (imageIndex) => {
    try {
      const imageUrl = generatedImageUrls[imageIndex];
      if (!imageUrl) {
        alert('다운로드할 이미지가 없습니다.');
        return;
      }

      // 직접 fetch로 이미지 다운로드
      const response = await fetch(imageUrl, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'image/*'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const blob = await response.blob();
      
      // PNG MIME 타입으로 설정
      const pngBlob = new Blob([blob], { type: 'image/png' });
      
      // 다운로드 링크 생성
      const url = window.URL.createObjectURL(pngBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `generated-image-${imageIndex + 1}.png`;
      link.style.display = 'none';
      
      // 다운로드 실행
      document.body.appendChild(link);
      link.click();
      
      // 정리
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log(`이미지 ${imageIndex + 1} 다운로드 완료`);
      
    } catch (error) {
      console.error('다운로드 오류:', error);
      
      // CORS 오류 시 대체 방법: 새 탭에서 이미지 열기
      try {
        const imageUrl = generatedImageUrls[imageIndex];
        if (imageUrl) {
          const newWindow = window.open(imageUrl, '_blank');
          if (newWindow) {
            alert('이미지를 새 탭에서 열었습니다. 우클릭하여 "이미지를 다른 이름으로 저장"을 선택해주세요.');
          } else {
            alert('팝업이 차단되었습니다. 팝업 차단을 해제하고 다시 시도해주세요.');
          }
        }
      } catch (fallbackError) {
        console.error('대체 방법 오류:', fallbackError);
        alert('다운로드에 실패했습니다. 이미지 URL을 복사하여 브라우저에서 직접 열어보세요.');
      }
    }
  };

  const handleRegenerate = async (imageIndex) => {
    try {
      // localStorage에서 선택된 마케팅 문구 가져오기
      const selectedOption = localStorage.getItem('selectedOption');
      const selectionLogs = JSON.parse(localStorage.getItem('selectionLogs') || '[]');
      
      if (!selectedOption || selectionLogs.length === 0) {
        alert('먼저 PredictionScreen에서 문구를 선택해주세요.');
        return;
      }
      
      // 가장 최근 선택 로그에서 마케팅 문구 가져오기
      const latestLog = selectionLogs[selectionLogs.length - 1];
      const marketingText = latestLog.marketingText;
      
      if (!marketingText) {
        alert('선택된 마케팅 문구를 찾을 수 없습니다.');
        return;
      }
      
      // 스타일 입력 검증
      if (!imageStyle.trim()) {
        alert('이미지 스타일을 입력해주세요. (예: 밝고 따뜻한 느낌, 파스텔 톤, 미니멀한 디자인)');
        return;
      }
      
      // 해당 이미지만 재생성 상태로 설정
      const newRegeneratingImages = [...regeneratingImages];
      newRegeneratingImages[imageIndex] = true;
      setRegeneratingImages(newRegeneratingImages);
      
      // 마케팅 문구와 스타일을 결합하여 이미지 생성
      const combinedPrompt = `마케팅 문구: ${marketingText}\n스타일 요청: ${imageStyle.trim()}`;

      // OpenAI API 호출하여 특정 이미지만 재생성
      const response = await fetch('/api/generate-images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: combinedPrompt,
          n: 1, // 1개의 이미지만 생성
          size: '1024x1024'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.images && data.images.length > 0) {
        // 특정 인덱스의 이미지만 교체
        const newImageUrls = [...generatedImageUrls];
        newImageUrls[imageIndex] = data.images[0];
        setGeneratedImageUrls(newImageUrls);
      } else {
        throw new Error('이미지 재생성에 실패했습니다.');
      }
      
    } catch (error) {
      console.error('이미지 재생성 오류:', error);
      alert('이미지 재생성 중 오류가 발생했습니다: ' + error.message);
    } finally {
      // 해당 이미지의 재생성 상태만 해제
      const newRegeneratingImages = [...regeneratingImages];
      newRegeneratingImages[imageIndex] = false;
      setRegeneratingImages(newRegeneratingImages);
    }
  };

  const handleReset = () => {
    setImagesGenerated(false);
    setIsGenerating(false);
    setImageStyle('');
  };

  return (
    <ImageScreenContainer>
      
      <Header>
        <Logo onClick={handleLogoClick}>
          <LogoIcon>
            <LogoSquare1 />
            <LogoSquare2 />
            <LogoSquare3 />
          </LogoIcon>
          <LogoText>ClickLit</LogoText>
        </Logo>
      </Header>

      <MainContent>
        <PageHeader>
          <PageTitle>어떤 스타일의 이미지를 원하시나요?</PageTitle>
        </PageHeader>

        <TabContainer>
          <Tab>
            Target
          </Tab>
          <Tab>
            Product
          </Tab>
          <Tab>
            Prediction
          </Tab>
          <Tab style={{ fontWeight: '700', color: '#000000' }}>
            Generate Images
          </Tab>
        </TabContainer>

        <FilterBlock>
          <FilterHeader>
            <FilterTitle>선택된 마케팅 문구</FilterTitle>
          </FilterHeader>
          <StyleSelector>
            <StyleText>
              {(() => {
                const selectionLogs = JSON.parse(localStorage.getItem('selectionLogs') || '[]');
                if (selectionLogs.length > 0) {
                  const latestLog = selectionLogs[selectionLogs.length - 1];
                  return latestLog.marketingText || '선택된 문구가 없습니다.';
                }
                return '먼저 PredictionScreen에서 문구를 선택해주세요.';
              })()}
            </StyleText>
          </StyleSelector>
        </FilterBlock>

        <FilterBlock>
          <FilterHeader>
            <FilterTitle>이미지 스타일</FilterTitle>
            <ResetButton onClick={handleReset}>초기화</ResetButton>
          </FilterHeader>
          <StyleInput
            placeholder="예: 밝고 따뜻한 느낌, 파스텔 톤, 미니멀한 디자인, 비즈니스 캐주얼"
            value={imageStyle}
            onChange={(e) => setImageStyle(e.target.value)}
          />
          <StyleDescription>
            색상, 분위기, 디자인 스타일 등을 상세히 설명할수록 더 정확한 이미지가 생성돼요. <br/>
            마케팅 문구는 이미지에 포함되지 않으며, 순수한 스타일만 반영돼요.
          </StyleDescription>
        </FilterBlock>

        <GenerateButton 
          onClick={handleGenerateImages}
          disabled={isGenerating || !imageStyle.trim()}
        >
          {isGenerating ? (
            <>
              <LoadingSpinner />
              생성 중...
            </>
          ) : !imageStyle.trim() ? (
            '스타일을 입력해주세요'
          ) : (
            '이미지 생성하기'
          )}
        </GenerateButton>

        {imagesGenerated && (
          <ResultsContainer>
            {[1, 2, 3].map((index) => (
              <ImageCard key={index}>
                <ImagePlaceholder>
                  {generatedImageUrls[index - 1] ? (
                    <img 
                      src={generatedImageUrls[index - 1]} 
                      alt={`Generated ${index}`}
                      style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '12px' }}
                    />
                  ) : (
                    <ImageLines>
                      <LongLine />
                      <ShortLine />
                    </ImageLines>
                  )}
                </ImagePlaceholder>
                <DownloadButton onClick={() => handleDownload(index - 1)}>
                  다운로드
                </DownloadButton>
                <RegenerateButton 
                  onClick={() => handleRegenerate(index - 1)}
                  disabled={regeneratingImages[index - 1]}
                >
                  {regeneratingImages[index - 1] ? (
                    <>
                      <LoadingSpinner />
                      재생성 중...
                    </>
                  ) : (
                    '재생성'
                  )}
                </RegenerateButton>
              </ImageCard>
            ))}
          </ResultsContainer>
        )}
      </MainContent>


    </ImageScreenContainer>
  );
};

export default ImageScreen;
