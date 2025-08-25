import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import chevronDown from '../assets/chevron-down.svg';
import companyLogo1 from '../assets/company-logo-1.svg';
import companyLogo2 from '../assets/company-logo-2.svg';
import companyLogo3 from '../assets/company-logo-3.svg';

const PredictionScreenContainer = styled.div`
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  position: relative;
  overflow: hidden;
`;

const BackgroundNoise = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(%23noise)" opacity="0.1"/></svg>');
  backdrop-filter: blur(64px);
  z-index: 1;
`;

const Header = styled.header`
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 80px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
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

const Navigation = styled.nav`
  display: flex;
  align-items: center;
  gap: 74px;
`;

const NavItems = styled.div`
  display: flex;
  align-items: center;
  gap: 33px;
`;

const NavItem = styled.div`
  display: flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.26;
  color: #020407;
`;

const NavItemText = styled.span``;

const ChevronIcon = styled.img`
  width: 20px;
  height: 20px;
`;

const ContactButton = styled.button`
  width: 134px;
  height: 45px;
  border: 1px solid #EA5F38;
  border-radius: 1000px;
  background: transparent;
  color: #EA5F38;
  font-family: 'HK Grotesk', sans-serif;
  font-weight: 600;
  font-size: 16px;
  line-height: 1.2;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #EA5F38;
    color: white;
  }
`;

const MainContent = styled.main`
  position: relative;
  z-index: 5;
  padding: 80px;
  min-height: calc(100vh - 120px);
`;

const PageHeader = styled.div`
  text-align: center;
  margin-bottom: 20px;
`;

const PageTitle = styled.h2`
  font-family: 'Apple SD Gothic Neo', sans-serif;
  font-weight: 600;
  font-size: 36px;
  line-height: 1.2;
  color: #000000;
  margin: 0;
  max-width: 589px;
  text-align: center;
`;

const TabContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 18px;
`;

const Tab = styled.div`
  padding: 10px 16px;
  background: ${props => (props.isActive ? '#FAFAFA' : 'transparent')};
  border: ${props => (props.isActive ? '1px solid #ECEDF0' : 'none')};
  border-radius: 8px;
  cursor: pointer;
  font-family: 'Roboto', sans-serif;
  font-weight: ${props => (props.isActive ? '500' : '400')};
  font-size: 16px;
  line-height: 1.5;
  color: ${props => (props.isActive ? '#222222' : '#6A6A6A')};
  transition: all 0.3s ease;

  &:hover {
    background: #FAFAFA;
  }
`;

const SummaryPanel = styled.div`
  width: 612px;
  height: 48px;
  background: #FFFFFF;
  border: 1px solid #DDDDDD;
  border-radius: 12px;
  padding: 1px 33px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 0 auto 18px;
`;

const SummarySection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2.25px;
  flex: 1;
`;

const SummaryLabel = styled.span`
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 12px;
  line-height: 1.333;
  color: #222222;
`;

const SummaryValue = styled.span`
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 1.172;
  color: #6A6A6A;
`;

const VerticalDivider = styled.div`
  width: 1px;
  height: 32px;
  background: #DDDDDD;
`;

const ResultsContainer = styled.div`
  max-width: 969px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
  justify-content: stretch;
`;

const ResultCard = styled.div`
  flex: 1;
  background: #FFFFFF;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 56px;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
`;

const CardTitle = styled.span`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 500;
  font-size: 14px;
  line-height: 1.6;
  color: #878C91;
`;

const Badge = styled.div`
  padding: 16px 32px;
  border-radius: 70px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 400;
  font-size: 12px;
  line-height: 1.4;
  letter-spacing: -0.02em;
  color: #010205;
  display: flex;
  align-items: center;
  gap: 10px;

  ${props => {
    switch (props.variant) {
      case 'ctr':
        return `
          background: linear-gradient(90deg, rgba(255, 200, 20, 0) 0%, rgba(255, 200, 20, 1) 82%);
        `;
      case 'ai':
        return `
          background: linear-gradient(90deg, rgba(255, 255, 255, 1) 0%, rgba(240, 122, 246, 1) 94%);
        `;
      default:
        return 'background: transparent;';
    }
  }}
`;

const BadgeIcon = styled.div`
  width: 15px;
  height: 15px;
  border-radius: 50%;

  ${props => {
    switch (props.variant) {
      case 'ctr':
        return 'background: #FFC814;';
      case 'ai':
        return 'background: linear-gradient(180deg, rgba(234, 55, 251, 1) 27%, rgba(241, 210, 244, 1) 100%);';
      default:
        return 'background: transparent;';
    }
  }}
`;

const ChartContainer = styled.div`
  width: 160px;
  height: 201.03px;
  margin: 0 auto;
  position: relative;
  display: flex;
  align-items: end;
  justify-content: center;
  padding-bottom: 20px;
`;

const ChartBar = styled.div`
  width: 40px;
  height: ${props => props.height}%;
  background: ${props => props.color};
  border: 1px solid #FFFFFF;
  border-radius: 4px 4px 0 0;
  position: relative;
  min-height: 20px;
  max-height: 80%;
`;

const ChartLabel = styled.div`
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 12px;
  line-height: 1.21;
  color: #EA5F38;
  white-space: nowrap;
`;

const ChartValue = styled.div`
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.21;
  color: #222222;
  white-space: nowrap;
`;

const ContentPlaceholder = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 26px;
  line-height: 1.5;
  letter-spacing: -0.03em;
  color: #010205;
  text-align: center;
  margin-top: 24px;
`;

const ActionButton = styled.button`
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
  margin: 0 auto;

  &:hover {
    background: rgba(155, 155, 156, 0.1);
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const GeneratedImage = styled.div`
  margin-top: 16px;
  text-align: center;
`;

const GeneratedImageImg = styled.img`
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const ArrowIcon = styled.div`
  width: 24px;
  height: 24px;
  position: relative;
`;

const ArrowHorizontal = styled.div`
  position: absolute;
  top: 12px;
  left: 5px;
  width: 14px;
  height: 0;
  border-top: 2px solid #000000;
`;

const ArrowVertical = styled.div`
  position: absolute;
  top: 5px;
  left: 12px;
  width: 0;
  height: 14px;
  border-left: 2px solid #000000;
`;

const Footer = styled.footer`
  position: relative;
  z-index: 5;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 64px;
  padding: 40px 80px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
`;

const CompanyLogos = styled.div`
  display: flex;
  gap: 27.93px;
  align-items: center;
`;

const CompanyLogo = styled.div`
  width: 108.3px;
  height: 33.32px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const PredictionScreen = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Prediction');
  const [summaryTarget, setSummaryTarget] = useState({ age_groups: [], genders: [], interests: '' });
  const [result, setResult] = useState({ ctr_a: null, ctr_b: null, analysis_a: '', analysis_b: '', ai_suggestion: '' });
  const [error, setError] = useState('');
  const [highestCtrOption, setHighestCtrOption] = useState(null);
  const [generatedImages, setGeneratedImages] = useState({});
  const [imageLoading, setImageLoading] = useState({});

  // --- 이미지 생성 = 최종 선택 잠금 로직 ---
  const [choiceLocked, setChoiceLocked] = useState(false);
  const [chosenOption, setChosenOption] = useState(''); // 'A' | 'B' | 'C'
  const [chosenText, setChosenText] = useState('');

  const logId = result?.log_id || '';
  const lockKey = logId ? `choice_lock_${logId}` : '';

  useEffect(() => {
    if (!logId) return; // 예측 응답 아직 없음
    try {
      const saved = localStorage.getItem(lockKey);
      if (saved) {
        const { locked, option, text } = JSON.parse(saved);
        setChoiceLocked(!!locked);
        if (option) setChosenOption(option);
        if (text) setChosenText(text);
      }
    } catch (e) {
      console.error(e);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [logId]);

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleTabClick = (tab) => {
    if (tab === 'Target') {
      navigate('/target');
    } else if (tab === 'Product') {
      navigate('/product');
    } else {
      setActiveTab(tab);
    }
  };

  const handleGenerateImage = async (option) => {
    // 이미 다른 옵션으로 확정되었으면 막기
    if (choiceLocked && chosenOption !== option) return;

    // 0) 클릭 즉시 문구/타겟 로드 & 잠금 선적용 (다른 시안/더블클릭 방지)
    const product = JSON.parse(localStorage.getItem('product') || '{}');
    const target = JSON.parse(localStorage.getItem('target') || '{}');
    const marketingText =
      option === 'A' ? (product.marketing_a || '') :
      option === 'B' ? (product.marketing_b || '') :
      (result.ai_suggestion || '');

    // 클릭 즉시 잠금 + 로딩 on
    setChoiceLocked(true);
    setChosenOption(option);
    setChosenText(marketingText);
    if (lockKey) {
      localStorage.setItem(lockKey, JSON.stringify({ locked: true, option, text: marketingText }));
    }
    setImageLoading(prev => ({ ...prev, [option]: true }));

    try {
      // 1) 사용자 최종 선택 즉시 기록
      if (logId && marketingText) {
        await fetch('/api/log-user-choice', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ log_id: logId, user_final_text: marketingText }),
        });
      }

      // 2) 이미지 생성
      const payload = {
        marketing_text: marketingText,
        product_category: product.category || null,
        target_audience: [...(target.age_groups || []), ...(target.genders || [])].join(', ')
      };
      const baseUrl = process.env.REACT_APP_API_BASE_URL || '';
      const apiUrl = baseUrl ? `${baseUrl}/api/generate-image` : '/api/generate-image';
      const resp = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        let detail = '';
        try {
          const errJson = await resp.json();
          detail = errJson?.detail || JSON.stringify(errJson);
        } catch (_) {}
        throw new Error(`Image generation failed: ${resp.status} ${detail}`);
      }

      const data = await resp.json();
      setGeneratedImages(prev => ({ ...prev, [option]: data }));
    } catch (e) {
      // 실패 시 잠금 해제하여 재시도 가능하게
      setChoiceLocked(false);
      setChosenOption('');
      setChosenText('');
      if (lockKey) localStorage.removeItem(lockKey);
      alert((e && e.message) ? e.message : '이미지 생성 중 오류가 발생했습니다.');
    } finally {
      setImageLoading(prev => ({ ...prev, [option]: false }));
    }
  };

  const handleDownloadImage = async (option) => {
    try {
      const imageData = generatedImages[option];
      if (!imageData || !imageData.image_url) {
        alert('다운로드할 이미지가 없습니다.');
        return;
      }

      const response = await fetch(imageData.image_url);
      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const filename = `marketing_${option}_${Date.now()}.png`;
      link.download = filename;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('다운로드 중 오류가 발생했습니다.');
    }
  };

  useEffect(() => {
    try {
      const targetRaw = localStorage.getItem('target');
      const predRaw = localStorage.getItem('prediction');
      const target = targetRaw ? JSON.parse(targetRaw) : {};
      const pred = predRaw ? JSON.parse(predRaw) : null;

      setSummaryTarget({
        age_groups: target.age_groups || [],
        genders: target.genders || [],
        interests: target.interests || '',
      });

      if (pred) {
        setResult(pred);
        if (pred.ctr_a && pred.ctr_b) {
          setHighestCtrOption(pred.ctr_a > pred.ctr_b ? 'A' : 'B');
        }
      } else {
        setError('결과가 생성되지 않았습니다. 이전 페이지에서 다시 시도해 주세요.');
      }
    } catch (e) {
      setError('저장된 값을 불러오지 못했습니다.');
    }
  }, []);

  return (
    <PredictionScreenContainer>
      <BackgroundNoise />

      <Header>
        <Logo onClick={handleLogoClick}>
          <LogoIcon>
            <LogoSquare1 />
            <LogoSquare2 />
            <LogoSquare3 />
          </LogoIcon>
          <LogoText>로고</LogoText>
        </Logo>

        <Navigation>
          <NavItems>
            <NavItem>
              <NavItemText>Service</NavItemText>
              <ChevronIcon src={chevronDown} alt="dropdown" />
            </NavItem>
            <NavItem>
              <NavItemText>Agency</NavItemText>
              <ChevronIcon src={chevronDown} alt="dropdown" />
            </NavItem>
            <NavItem>
              <NavItemText>Case study</NavItemText>
              <ChevronIcon src={chevronDown} alt="dropdown" />
            </NavItem>
            <NavItem>
              <NavItemText>Resources</NavItemText>
              <ChevronIcon src={chevronDown} alt="dropdown" />
            </NavItem>
          </NavItems>
          <ContactButton>Contact Us</ContactButton>
        </Navigation>
      </Header>

      <MainContent>
        <PageHeader>
          <PageTitle>입력하신 마케팅 문구의 예측 결과입니다</PageTitle>
        </PageHeader>

        <TabContainer>
          <Tab
            isActive={activeTab === 'Target'}
            onClick={() => handleTabClick('Target')}
          >
            Target
          </Tab>
          <Tab
            isActive={activeTab === 'Product'}
            onClick={() => handleTabClick('Product')}
          >
            Product
          </Tab>
          <Tab
            isActive={activeTab === 'Prediction'}
            onClick={() => handleTabClick('Prediction')}
          >
            Prediction
          </Tab>
          <Tab
            isActive={activeTab === 'Generate Images'}
            onClick={() => handleTabClick('Generate Images')}
          >
            Generate Images
          </Tab>
        </TabContainer>

        <SummaryPanel>
          <SummarySection>
            <SummaryLabel>타겟</SummaryLabel>
            <SummaryValue>
              {[...summaryTarget.age_groups, ...summaryTarget.genders].join(', ') || '-'}
            </SummaryValue>
          </SummarySection>
          <VerticalDivider />
          <SummarySection>
            <SummaryLabel>관심사</SummaryLabel>
            <SummaryValue>{summaryTarget.interests || '-'}</SummaryValue>
          </SummarySection>
        </SummaryPanel>

        <ResultsContainer>
          {/* A안 */}
          <ResultCard>
            <CardHeader>
              {highestCtrOption === 'A' && (
                <Badge variant="ctr">
                  <BadgeIcon variant="ctr" />
                  최다 CTR 예측
                </Badge>
              )}
              {highestCtrOption !== 'A' && <div></div>}
              <CardTitle>A안</CardTitle>
            </CardHeader>

            <ChartContainer>
              <div style={{ position: 'relative' }}>
                <ChartBar
                  height={result.ctr_a ? result.ctr_a * 100 : 0}
                  color="#EA5F38"
                >
                  <ChartValue>
                    {result.ctr_a ? `${(result.ctr_a * 100).toFixed(1)}%` : '-'}
                  </ChartValue>
                </ChartBar>
                <ChartLabel>A안</ChartLabel>
              </div>
            </ChartContainer>

            <ContentPlaceholder>{error ? error : (result.analysis_a || '')}</ContentPlaceholder>

            {generatedImages.A && (
              <GeneratedImage>
                <GeneratedImageImg
                  src={generatedImages.A.image_url}
                  alt="Generated A안 image"
                />
              </GeneratedImage>
            )}

            <ActionButton
              onClick={
                generatedImages.A
                  ? () => handleDownloadImage('A')
                  : () => handleGenerateImage('A')
              }
              disabled={imageLoading.A || choiceLocked && chosenOption !== 'A'}
            >
              {imageLoading.A
                ? '생성 중...'
                : generatedImages.A
                ? '다운로드'
                : '이미지 생성하기'}
              <ArrowIcon>
                <ArrowHorizontal />
                <ArrowVertical />
              </ArrowIcon>
            </ActionButton>
          </ResultCard>

          {/* B안 */}
          <ResultCard>
            <CardHeader>
              {highestCtrOption === 'B' && (
                <Badge variant="ctr">
                  <BadgeIcon variant="ctr" />
                  최다 CTR 예측
                </Badge>
              )}
              {highestCtrOption !== 'B' && <div></div>}
              <CardTitle>B안</CardTitle>
            </CardHeader>

            <ChartContainer>
              <div style={{ position: 'relative' }}>
                <ChartBar
                  height={result.ctr_b ? result.ctr_b * 100 : 0}
                  color="#EA5F38"
                >
                  <ChartValue>
                    {result.ctr_b ? `${(result.ctr_b * 100).toFixed(1)}%` : '-'}
                  </ChartValue>
                </ChartBar>
                <ChartLabel>B안</ChartLabel>
              </div>
            </ChartContainer>

            <ContentPlaceholder>{error ? error : (result.analysis_b || '')}</ContentPlaceholder>

            {generatedImages.B && (
              <GeneratedImage>
                <GeneratedImageImg
                  src={generatedImages.B.image_url}
                  alt="Generated B안 image"
                />
              </GeneratedImage>
            )}

            <ActionButton
              onClick={
                generatedImages.B
                  ? () => handleDownloadImage('B')
                  : () => handleGenerateImage('B')
              }
              disabled={imageLoading.B || choiceLocked && chosenOption !== 'B'}
            >
              {imageLoading.B
                ? '생성 중...'
                : generatedImages.B
                ? '다운로드'
                : '이미지 생성하기'}
              <ArrowIcon>
                <ArrowHorizontal />
                <ArrowVertical />
              </ArrowIcon>
            </ActionButton>
          </ResultCard>

          {/* C안 (AI 추천) */}
          <ResultCard>
            <CardHeader>
              <Badge variant="ai">
                <BadgeIcon variant="ai" />
                AI 추가 생성 문구
              </Badge>
              <CardTitle>C안</CardTitle>
            </CardHeader>

            <ChartContainer>
              <div style={{ position: 'relative' }}>
                <ChartBar
                  height={
                    result.ctr_a && result.ctr_b
                      ? Math.max(result.ctr_a, result.ctr_b) * 100
                      : 0
                  }
                  color="#F072F6"
                >
                  <ChartValue>AI 추천</ChartValue>
                </ChartBar>
                <ChartLabel>C안</ChartLabel>
              </div>
            </ChartContainer>

            <ContentPlaceholder>{error ? error : (result.ai_suggestion || '')}</ContentPlaceholder>

            {generatedImages.C && (
              <GeneratedImage>
                <GeneratedImageImg
                  src={generatedImages.C.image_url}
                  alt="Generated C안 image"
                />
              </GeneratedImage>
            )}

            <ActionButton
              onClick={
                generatedImages.C
                  ? () => handleDownloadImage('C')
                  : () => handleGenerateImage('C')
              }
              disabled={imageLoading.C || choiceLocked && chosenOption !== 'C'}
            >
              {imageLoading.C
                ? '생성 중...'
                : generatedImages.C
                ? '다운로드'
                : '이미지 생성하기'}
              <ArrowIcon>
                <ArrowHorizontal />
                <ArrowVertical />
              </ArrowIcon>
            </ActionButton>
          </ResultCard>
        </ResultsContainer>
      </MainContent>

      <Footer>
        <CompanyLogos>
          <CompanyLogo>
            <img
              src={companyLogo1}
              alt="Company 1"
              style={{ width: '100%', height: 'auto' }}
            />
          </CompanyLogo>
          <CompanyLogo>
            <img
              src={companyLogo2}
              alt="Company 2"
              style={{ width: '100%', height: 'auto' }}
            />
          </CompanyLogo>
          <CompanyLogo>
            <img
              src={companyLogo3}
              alt="Company 3"
              style={{ width: '100%', height: 'auto' }}
            />
          </CompanyLogo>
        </CompanyLogos>
      </Footer>
    </PredictionScreenContainer>
  );
};

export default PredictionScreen;
