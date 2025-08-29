import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const ProductScreenContainer = styled.div`
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
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
  margin: 0;

  @media (min-width: 768px) {
    font-size: 32px;
  }

  @media (min-width: 1024px) {
    font-size: 36px;
  }
`;

const TabContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 30px;
`;

const Tab = styled.div`
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: default;
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.5;
  color: #6A6A6A;
  transition: all 0.3s ease;
`;

const FilterContainer = styled.div`
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;

  @media (min-width: 768px) {
    max-width: 700px;
    gap: 30px;
  }

  @media (min-width: 1024px) {
    max-width: 850px;
  }
`;

const FilterBlock = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 612px;
  margin: 0 auto;
`;

const FilterHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
`;

const FilterTitle = styled.h3`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 700;
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

  &:disabled {
    color: #9AA0A6;
    cursor: not-allowed;
    text-decoration: none;
    opacity: 0.6;
  }
`;

const CategorySelect = styled.select`
  width: 100%;
  height: 48px;
  background: #FFFFFF;
  border: 1px solid #ECEDF0;
  border-radius: 12px;
  padding: 0 16px;
  font-family: 'Hiragino Sans', sans-serif;
  font-size: 14px;
  color: #555E67;
  cursor: pointer;
  transition: all 0.3s ease;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23555E67' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 16px;

  &:hover {
    background-color: #FAFAFA;
    border-color: #D1D5DB;
  }

  &:focus {
    outline: none;
    border-color: #99EA48;
    box-shadow: 0 0 0 3px rgba(153, 234, 72, 0.1);
  }

  &:disabled {
    background-color: #F5F5F5;
    border-color: #E0E0E0;
    color: #9AA0A6;
    cursor: not-allowed;
    opacity: 0.6;
  }

  option {
    padding: 12px 16px;
    font-family: 'Hiragino Sans', sans-serif;
    font-size: 14px;
    color: #222222;
  }
`;

const MarketingOptions = styled.div`
  display: flex;
  flex-direction: row;
  gap: 12px;
`;

const MarketingInputWrapper = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const MarketingLabel = styled.span`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 12px;
  line-height: 1.5;
  color: #31373D;
`;

const MarketingInput = styled.input`
  height: 48px;
  background: #FFFFFF;
  border: 1px solid #ECEDF0;
  border-radius: 12px;
  padding: 0 12px;
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 500;
  font-size: 14px;
  line-height: 1.5;
  color: #222222;

  &::placeholder {
    color: #9AA0A6;
  }

  &:disabled {
    background-color: #F5F5F5;
    border-color: #E0E0E0;
    color: #9AA0A6;
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const Divider = styled.div`
  height: 1px;
  background: #ECEDF0;
  width: 100%;
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

const ActionButton = styled.button`
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
  margin: 0 auto;

  &:hover {
    background: #B0B0B0;
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const ProductScreen = () => {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('');
  const [marketingA, setMarketingA] = useState('');
  const [marketingB, setMarketingB] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const categories = ['뷰티/화장품', '게임', '패션/잡화', '부동산/재테크', '여행/숙박/항공', '스포츠/레저', '식음료/요리', '정치/사회'];

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
  };

  const handleMarketingAChange = (e) => {
    setMarketingA(e.target.value);
  };

  const handleMarketingBChange = (e) => {
    setMarketingB(e.target.value);
  };

  const handleReset = (type) => {
    switch (type) {
      case 'category':
        setSelectedCategory('');
        break;
      case 'marketing':
        setMarketingA('');
        setMarketingB('');
        break;
      default:
        break;
    }
  };

  const handleViewResults = async () => {
    setIsLoading(true);
    try {
      const target = JSON.parse(localStorage.getItem('target') || '{}');
      const payload = {
        ...target,
        category: selectedCategory,
        marketing_a: marketingA,
        marketing_b: marketingB,
      };
      localStorage.setItem('product', JSON.stringify(payload));

      const baseUrl = process.env.REACT_APP_API_BASE_URL || '';
      const apiUrl = baseUrl ? `${baseUrl}/api/predict` : '/api/predict';
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
        } catch (_) {
          detail = `HTTP ${resp.status}`;
        }
        throw new Error(`Request failed: ${resp.status} ${detail}`);
      }
      const data = await resp.json();
      localStorage.setItem('prediction', JSON.stringify(data));
      navigate('/prediction');
    } catch (e) {
      alert((e && e.message) ? e.message : '결과 생성 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const isProductValid = (selectedCategory || '').trim().length > 0 && (marketingA || '').trim().length > 0 && (marketingB || '').trim().length > 0;

  return (
    <ProductScreenContainer>
      
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
          <PageTitle>마케팅하고자 하는 제품의 카테고리/마케팅 문구를 입력해주세요</PageTitle>
        </PageHeader>

        <TabContainer>
          <Tab>
            Target
          </Tab>
          <Tab style={{ fontWeight: '700', color: '#000000' }}>
            Product
          </Tab>
          <Tab>
            Prediction
          </Tab>
          <Tab>
            Generate Images
          </Tab>
        </TabContainer>

        <FilterContainer>
          <FilterBlock>
            <FilterHeader>
              <FilterTitle>제품 카테고리</FilterTitle>
              <ResetButton onClick={() => handleReset('category')} disabled={isLoading}>초기화</ResetButton>
            </FilterHeader>
            <CategorySelect 
              value={selectedCategory} 
              onChange={handleCategoryChange}
              disabled={isLoading}
            >
              <option value="" disabled>제품 카테고리를 선택해주세요</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </CategorySelect>
            <Divider />
          </FilterBlock>

          <FilterBlock>
            <FilterHeader>
              <FilterTitle>마케팅 문구</FilterTitle>
              <ResetButton onClick={() => handleReset('marketing')} disabled={isLoading}>초기화</ResetButton>
            </FilterHeader>
            <MarketingOptions>
              <MarketingInputWrapper>
                <MarketingLabel>A안</MarketingLabel>
                <MarketingInput
                  type="text"
                  placeholder="마케팅 문구 A안을 입력하세요"
                  value={marketingA}
                  onChange={handleMarketingAChange}
                  disabled={isLoading}
                />
              </MarketingInputWrapper>
              <MarketingInputWrapper>
                <MarketingLabel>B안</MarketingLabel>
                <MarketingInput
                  type="text"
                  placeholder="마케팅 문구 B안을 입력하세요"
                  value={marketingB}
                  onChange={handleMarketingBChange}
                  disabled={isLoading}
                />
              </MarketingInputWrapper>
            </MarketingOptions>
            <Divider />
          </FilterBlock>

          <ActionButton onClick={handleViewResults} disabled={!isProductValid || isLoading}>
            {isLoading ? (
              <>
                <LoadingSpinner />
                평가중...
              </>
            ) : (
              '결과 보러가기'
            )}
          </ActionButton>
        </FilterContainer>
      </MainContent>

    </ProductScreenContainer>
  );
};

export default ProductScreen;
