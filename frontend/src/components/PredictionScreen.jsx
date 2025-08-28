import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const PredictionScreenContainer = styled.div`
  width: 100%;
  min-height: 100vh;
  position: relative;
  background: #FFFFFF;
`;

const Header = styled.header`
  position: relative;
  z-index: 10;
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
  position: relative;
  z-index: 5;
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
    padding: 80px;
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
  margin: 0 auto;
  max-width: 100%;
  text-align: center;
  width: 100%;

  @media (min-width: 768px) {
    font-size: 32px;
    max-width: 589px;
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
  width: 100%;
  margin: 0 auto 18px;

  @media (min-width: 768px) {
    max-width: 800px;
  }

  @media (min-width: 1024px) {
    max-width: 969px;
  }
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

const SummaryPanel = styled.div`
  width: 100%;
  min-height: 60px;
  background:rgb(255, 255, 255);
  border: 1px solid #DDDDDD;
  border-radius: 12px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 auto 30px;
  flex-wrap: wrap;

  @media (min-width: 768px) {
    max-width: 450px;
    padding: 6px 20px;
  }

  @media (min-width: 1024px) {
    max-width: 500px;
    padding: 6px 24px;
  }
`;

const SummarySection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
`;

const SummaryLabel = styled.span`
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 14px;
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
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;

  @media (min-width: 768px) {
    max-width: 800px;
    gap: 24px;
  }

  @media (min-width: 1024px) {
    max-width: 969px;
    flex-direction: row;
    justify-content: stretch;
  }
`;

const ResultCard = styled.div`
  flex: 1;
  background: #FFFFFF;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
  justify-content: space-between;
  transition: all 0.3s ease;

  @media (min-width: 768px) {
    padding: 28px;
    gap: 32px;
  }

  @media (min-width: 1024px) {
    padding: 32px;
    gap: 40px;
  }
`;

const ResultCardA = styled(ResultCard)`
  border-left: 4px solid rgba(153, 234, 72, 0.9);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0px 8px 20px rgba(153, 234, 72, 0.15);
  }
`;

const ResultCardB = styled(ResultCard)`
  border-left: 4px solid rgba(153, 234, 72, 0.9);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0px 8px 20px rgba(153, 234, 72, 0.15);
  }
`;

const ResultCardC = styled(ResultCard)`
  border-left: 4px solid rgba(153, 234, 72, 0.9);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0px 8px 20px rgba(153, 234, 72, 0.15);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  min-height: 60px;
  align-items: flex-start;
`;

const Badge = styled.div`
  padding: 16px 32px;
  border-radius: 70px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 500;
  font-size: 12px;
  line-height: 1.4;
  letter-spacing: -0.02em;
  color: #010205;
  display: flex;
  align-items: center;
  gap: 10px;
  height: 48px;
  min-width: 140px;

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
      case 'highest':
        return `
          background: linear-gradient(90deg, rgba(255, 200, 20, 0) 0%, rgba(255, 200, 20, 1) 82%);
        `;
      default:
        return 'background: transparent;';
    }
  }}
`;

const ChartContainer = styled.div`
  width: 200px;
  height: 80px;
  margin: 0 auto;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
`;

const ChartBar = styled.div`
  width: ${props => props.height}%;
  height: 30px;
  background: ${props => props.color};
  border: 1px solid #FFFFFF;
  border-radius: 0 4px 4px 0;
  position: relative;
  min-width: 20px;
  max-width: 90%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
`;

const ChartValue = styled.div`
  position: absolute;
  right: -50px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.21;
  color: #222222;
  white-space: nowrap;
`;

const ContentPlaceholder = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 1.6;
  color: #333333;
  text-align: left;
  margin-top: 16px;
  padding: 16px;
  background: #F8F9FA;
  border-radius: 12px;
  border: 1px solid #E9ECEF;
  white-space: pre-wrap;
  word-break: break-word;
`;

const AnalysisSection = styled.div`
  margin-top: 8px;
`;

const AnalysisHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`;

const AnalysisTitle = styled.h4`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 16px;
  color: #010205;
  margin: 0;
`;

const ToggleButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #FFFFFF;
  border: 1px solid #DEE2E6;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 500;
  font-size: 12px;
  color: #6C757D;
  transition: all 0.3s ease;

  &:hover {
    background: #F8F9FA;
    border-color: #ADB5BD;
  }

  svg {
    transition: transform 0.3s ease;
    transform: ${props => props.isExpanded ? 'rotate(180deg)' : 'rotate(0deg)'};
  }
`;

const AnalysisContent = styled.div`
  max-height: ${props => props.isExpanded ? 'none' : '120px'};
  overflow: hidden;
  transition: max-height 0.3s ease;
  position: relative;
  min-height: 120px;
  
  /* 텍스트 넘침 체크를 위한 스크롤바 표시 (숨김) */
  &::-webkit-scrollbar {
    display: none;
  }
`;

const AnalysisOverlay = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(transparent, #F8F9FA);
  display: ${props => props.isExpanded ? 'none' : 'block'};
  pointer-events: none;
`;

const MarketingTextSection = styled.div`
  margin: 12px 0;
  padding: 16px;
  background: #F8F9FA;
  border-radius: 12px;
  border: 1px solid #E9ECEF;
`;

const MarketingTextLabel = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.4;
  color: #495057;
  margin-bottom: 8px;
`;

const MarketingTextContent = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 1.6;
  color: #212529;
  background: #FFFFFF;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #DEE2E6;
  word-break: break-word;
  min-height: 80px;
  max-height: 80px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
`;

const CTRSummary = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 16px;
  line-height: 1.4;
  color: #495057;
  background: #F8F9FA;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #E9ECEF;
  margin-bottom: 12px;
  text-align: center;
`;

const AnalysisText = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 1.6;
  color: #212529;
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

const PredictionScreen = () => {
  const navigate = useNavigate();
  const [result, setResult] = useState({ ctr_a: null, ctr_b: null, ctr_c: null, analysis_a: '', analysis_b: '', analysis_c: '', ai_suggestion: '' });
  const [error, setError] = useState('');
  
  // 토글 상태 관리
  const [expandedAnalysis, setExpandedAnalysis] = useState({
    a: false,
    b: false,
    c: false
  });

  // 텍스트 넘침 체크를 위한 간단한 함수
  const checkTextOverflow = (text) => {
    if (!text) return false;
    // 텍스트 길이로 대략적인 넘침 여부 판단 (한 줄당 약 50자 기준)
    const lines = Math.ceil(text.length / 50);
    return lines > 2; // 120px 높이에 약 2줄 정도 들어감
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  const toggleAnalysis = (option) => {
    setExpandedAnalysis(prev => ({
      ...prev,
      [option]: !prev[option]
    }));
  };

  useEffect(() => {
    try {
      const predRaw = localStorage.getItem('prediction');
      const pred = predRaw ? JSON.parse(predRaw) : null;

      if (pred) {
        setResult(pred);
      } else {
        setError('결과가 생성되지 않았습니다. 이전 페이지에서 다시 시도해 주세요.');
      }
    } catch (e) {
      setError('저장된 값을 불러오지 못했습니다.');
    }
  }, []);



  return (
    <PredictionScreenContainer>

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
          <PageTitle>입력하신 마케팅 문구의 예측 결과입니다</PageTitle>
        </PageHeader>

        <TabContainer>
          <Tab>
            Target
          </Tab>
          <Tab>
            Product
          </Tab>
          <Tab style={{ fontWeight: '700', color: '#000000' }}>
            Prediction
          </Tab>
          <Tab>
            Generate Images
          </Tab>
        </TabContainer>

        <SummaryPanel>
          <SummarySection>
            <SummaryLabel>타겟</SummaryLabel>
            <SummaryValue>
              {(() => {
                const target = JSON.parse(localStorage.getItem('target') || '{}');
                return [...(target.age_groups || []), ...(target.genders || [])].join(', ') || '-';
              })()}
            </SummaryValue>
          </SummarySection>
          <VerticalDivider />
          <SummarySection>
            <SummaryLabel>관심사</SummaryLabel>
            <SummaryValue>
              {(() => {
                const target = JSON.parse(localStorage.getItem('target') || '{}');
                return target.interests || '-';
              })()}
            </SummaryValue>
          </SummarySection>

        </SummaryPanel>

        <ResultsContainer>
          {/* A안 */}
          <ResultCardA>
            <CardHeader>
                {result.ctr_a && result.ctr_b && result.ctr_a > result.ctr_b ? (
                  <Badge variant="highest">
                    👑 최다 CTR 예측
                  </Badge>
                ) : (
                  <div style={{ minHeight: '48px', minWidth: '140px' }}></div>
                )}
              
            </CardHeader>

            <ChartContainer>
              <div style={{ position: 'relative' }}>
                <ChartBar
                  height={result.ctr_a ? result.ctr_a * 900 : 0}
                  color="rgba(153, 234, 72, 0.9)"
                >
                  <ChartValue>
                    {result.ctr_a ? `${(result.ctr_a * 100).toFixed(1)}%` : '-'}
                  </ChartValue>
                </ChartBar>
              </div>
            </ChartContainer>

            {/* A안 마케팅 문구 표시 */}
            <MarketingTextSection>
              <MarketingTextLabel>A안 마케팅 문구</MarketingTextLabel>
              <MarketingTextContent>
                {JSON.parse(localStorage.getItem('product') || '{}').marketing_a || 'A안 마케팅 문구가 없습니다.'}
              </MarketingTextContent>
            </MarketingTextSection>

            <AnalysisSection>
              <AnalysisHeader>
                <AnalysisTitle>상세 분석</AnalysisTitle>
                <ToggleButton 
                  isExpanded={expandedAnalysis.a}
                  onClick={() => toggleAnalysis('a')}
                >
                  {expandedAnalysis.a ? '접기' : '펼치기'}
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </ToggleButton>
              </AnalysisHeader>
              <AnalysisContent isExpanded={expandedAnalysis.a}>
                <ContentPlaceholder>
                  {error ? error : (
                    <>
                      <CTRSummary>
                        <strong>예측 CTR: {result.ctr_a ? `${(result.ctr_a * 100).toFixed(1)}%` : '-'}</strong>
                      </CTRSummary>
                      <AnalysisText>
                        {result.analysis_a || 'A안에 대한 상세한 분석 내용을 확인할 수 있어요.'}
                      </AnalysisText>
                    </>
                  )}
                </ContentPlaceholder>
                {!expandedAnalysis.a && checkTextOverflow(result.analysis_a) && (
                  <AnalysisOverlay isExpanded={expandedAnalysis.a} />
                )}
              </AnalysisContent>
            </AnalysisSection>

            <ActionButton
              onClick={async () => {
                const product = JSON.parse(localStorage.getItem('product') || '{}');
                const target = JSON.parse(localStorage.getItem('target') || '{}');
                const marketingText = product.marketing_a || '';
                
                // 백엔드에 사용자 선택 전송
                try {
                  const response = await fetch('/api/user-choice', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      log_id: result.log_id,
                      user_final_text: marketingText
                    })
                  });
                  
                  if (response.ok) {
                    console.log('사용자 선택이 성공적으로 저장되었습니다.');
                  } else {
                    console.error('사용자 선택 저장 실패:', response.statusText);
                  }
                } catch (error) {
                  console.error('사용자 선택 저장 중 오류:', error);
                }
                
                // 로그 기록
                const logData = {
                  timestamp: new Date().toISOString(),
                  selectedOption: 'A',
                  marketingText: marketingText,
                  ctr: result.ctr_a,
                  target: target,
                  product: product,
                  result: result
                };
                
                // localStorage에 로그 저장
                const existingLogs = JSON.parse(localStorage.getItem('selectionLogs') || '[]');
                existingLogs.push(logData);
                localStorage.setItem('selectionLogs', JSON.stringify(existingLogs));
                
                // 선택 정보 저장
                localStorage.setItem('selectedOption', JSON.stringify({
                  option: 'A',
                  text: marketingText,
                  target: target,
                  product: product
                }));
                
                navigate('/image');
              }}
            >
              A안 선택
            </ActionButton>
          </ResultCardA>

          {/* B안 */}
          <ResultCardB>
            <CardHeader>
                {result.ctr_a && result.ctr_b && result.ctr_b > result.ctr_a ? (
                  <Badge variant="highest">
                    👑 최다 CTR 예측
                  </Badge>
                ) : (
                  <div style={{ minHeight: '48px', minWidth: '140px' }}></div>
                )}
              
            </CardHeader>

            <ChartContainer>
              <div style={{ position: 'relative' }}>
                <ChartBar
                  height={result.ctr_b ? result.ctr_b * 900 : 0}
                  color="rgba(153, 234, 72, 0.9)"
                >
                  <ChartValue>
                    {result.ctr_b ? `${(result.ctr_b * 100).toFixed(1)}%` : '-'}
                  </ChartValue>
                </ChartBar>
              </div>
            </ChartContainer>

              {/* B안 마케팅 문구 표시 */}
              <MarketingTextSection>
                <MarketingTextLabel>B안 마케팅 문구</MarketingTextLabel>
                <MarketingTextContent>
                  {JSON.parse(localStorage.getItem('product') || '{}').marketing_b || 'B안 마케팅 문구가 없습니다.'}
                </MarketingTextContent>
              </MarketingTextSection>

              <AnalysisSection>
              <AnalysisHeader>
                <AnalysisTitle>상세 분석</AnalysisTitle>
                <ToggleButton 
                  isExpanded={expandedAnalysis.b}
                  onClick={() => toggleAnalysis('b')}
                >
                  {expandedAnalysis.b ? '접기' : '펼치기'}
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </ToggleButton>
              </AnalysisHeader>
              <AnalysisContent isExpanded={expandedAnalysis.b}>
                <ContentPlaceholder>
                  {error ? error : (
                    <>
                      <CTRSummary>
                        <strong>예측 CTR: {result.ctr_b ? `${(result.ctr_b * 100).toFixed(1)}%` : '-'}</strong>
                      </CTRSummary>
                      <AnalysisText>
                        {result.analysis_b || 'B안에 대한 상세한 분석 내용을 확인할 수 있어요.'}
                      </AnalysisText>
                    </>
                  )}
                </ContentPlaceholder>
                {!expandedAnalysis.b && checkTextOverflow(result.analysis_b) && (
                  <AnalysisOverlay isExpanded={expandedAnalysis.b} />
                )}
              </AnalysisContent>
            </AnalysisSection>

            <ActionButton
              onClick={async () => {
                const product = JSON.parse(localStorage.getItem('product') || '{}');
                const target = JSON.parse(localStorage.getItem('target') || '{}');
                const marketingText = product.marketing_b || '';
                
                // 백엔드에 사용자 선택 전송
                try {
                  const response = await fetch('/api/user-choice', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      log_id: result.log_id,
                      user_final_text: marketingText
                    })
                  });
                  
                  if (response.ok) {
                    console.log('사용자 선택이 성공적으로 저장되었습니다.');
                  } else {
                    console.error('사용자 선택 저장 실패:', response.statusText);
                  }
                } catch (error) {
                    console.error('사용자 선택 저장 중 오류:', error);
                }
                
                // 로그 기록
                const logData = {
                  timestamp: new Date().toISOString(),
                  selectedOption: 'B',
                  marketingText: marketingText,
                  ctr: result.ctr_b,
                  target: target,
                  product: product,
                  result: result
                };
                
                // localStorage에 로그 저장
                const existingLogs = JSON.parse(localStorage.getItem('selectionLogs') || '[]');
                existingLogs.push(logData);
                localStorage.setItem('selectionLogs', JSON.stringify(existingLogs));
                
                // 선택 정보 저장
                localStorage.setItem('selectedOption', JSON.stringify({
                  option: 'B',
                  text: marketingText,
                  target: target,
                  product: product
                }));
                
                navigate('/image');
              }}
            >
              B안 선택
            </ActionButton>
          </ResultCardB>

          {/* C안 (AI 추천) */}
          <ResultCardC>
            <CardHeader>
                <Badge variant="ai">
                  🦄 AI 추가 생성 문구
                </Badge>
              
            </CardHeader>

            <ChartContainer>
              <div style={{ position: 'relative' }}>
                <ChartBar
                  height={result.ctr_c ? result.ctr_c * 900 : 0}
                  color="#F072F6"
                >
                  <ChartValue>
                    {result.ctr_c ? `${(result.ctr_c * 100).toFixed(1)}%` : '-'}
                  </ChartValue>
                </ChartBar>
              </div>
            </ChartContainer>

            {/* C안 마케팅 문구 표시 */}
            <MarketingTextSection>
              <MarketingTextLabel>C안 마케팅 문구</MarketingTextLabel>
              <MarketingTextContent>
                {result.ai_suggestion || 'AI가 생성한 마케팅 문구가 없습니다.'}
              </MarketingTextContent>
            </MarketingTextSection>

            <AnalysisSection>
              <AnalysisHeader>
                <AnalysisTitle>상세 분석</AnalysisTitle>
                <ToggleButton 
                  isExpanded={expandedAnalysis.c}
                  onClick={() => toggleAnalysis('c')}
                >
                  {expandedAnalysis.c ? '접기' : '펼치기'}
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </ToggleButton>
              </AnalysisHeader>
              <AnalysisContent isExpanded={expandedAnalysis.c}>
                <ContentPlaceholder>
                  {error ? error : (
                    <>
                      <CTRSummary>
                        <strong>예측 CTR: {result.ctr_c ? `${(result.ctr_c * 100).toFixed(1)}%` : '-'}</strong>
                      </CTRSummary>
                      <AnalysisText>
                        {result.analysis_c ? 
                          `${result.analysis_c}` : 
                          'C안에 대한 상세한 분석 내용을 확인할 수 있어요.'
                        }
                      </AnalysisText>
                    </>
                  )}
                </ContentPlaceholder>
                {!expandedAnalysis.c && checkTextOverflow(result.analysis_c) && (
                  <AnalysisOverlay isExpanded={expandedAnalysis.c} />
                )}
              </AnalysisContent>
            </AnalysisSection>

            <ActionButton
              onClick={async () => {
                const product = JSON.parse(localStorage.getItem('product') || '{}');
                const target = JSON.parse(localStorage.getItem('target') || '{}');
                const marketingText = result.ai_suggestion || '';
                
                // 백엔드에 사용자 선택 전송
                try {
                  const response = await fetch('/api/user-choice', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      log_id: result.log_id,
                      user_final_text: marketingText
                    })
                  });
                  
                  if (response.ok) {
                    console.log('사용자 선택이 성공적으로 저장되었습니다.');
                  } else {
                    console.error('사용자 선택 저장 실패:', response.statusText);
                  }
                } catch (error) {
                  console.error('사용자 선택 저장 중 오류:', error);
                }
                
                // 로그 기록
                const logData = {
                  timestamp: new Date().toISOString(),
                  selectedOption: 'C',
                  marketingText: marketingText,
                  ctr: result.ctr_c || 0,
                  target: target,
                  product: product,
                  result: result
                };
                
                // localStorage에 로그 저장
                const existingLogs = JSON.parse(localStorage.getItem('selectionLogs') || '[]');
                existingLogs.push(logData);
                localStorage.setItem('selectionLogs', JSON.stringify(existingLogs));
                
                // 선택 정보 저장
                localStorage.setItem('selectedOption', JSON.stringify({
                  option: 'C',
                  text: marketingText,
                  target: target,
                  product: product
                }));
                
                navigate('/image');
              }}
            >
              C안 선택
            </ActionButton>
          </ResultCardC>
        </ResultsContainer>
      </MainContent>

    </PredictionScreenContainer>
  );
};

export default PredictionScreen;
