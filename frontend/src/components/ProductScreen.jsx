import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import chevronDown from '../assets/chevron-down.svg';
import companyLogo1 from '../assets/company-logo-1.svg';
import companyLogo2 from '../assets/company-logo-2.svg';
import companyLogo3 from '../assets/company-logo-3.svg';

const ProductScreenContainer = styled.div`
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
`;

const TabContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 30px;
`;

const Tab = styled.div`
  padding: 10px 16px;
  background: ${props => props.isActive ? '#FAFAFA' : 'transparent'};
  border: ${props => props.isActive ? '1px solid #ECEDF0' : 'none'};
  border-radius: 8px;
  cursor: pointer;
  font-family: 'Roboto', sans-serif;
  font-weight: ${props => props.isActive ? '500' : '400'};
  font-size: 16px;
  line-height: 1.5;
  color: ${props => props.isActive ? '#222222' : '#6A6A6A'};
  transition: all 0.3s ease;

  &:hover {
    background: #FAFAFA;
  }
`;

const FilterContainer = styled.div`
  max-width: 850px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
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

const ProductCategorySelector = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px;
  height: 48px;
  background: #FFFFFF;
  border: 1px solid #ECEDF0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #FAFAFA;
  }
`;

const CategoryText = styled.span`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 12px;
  line-height: 1.5;
  color: #555E67;
  padding: 0 8px;
`;

const CalendarIcon = styled.div`
  width: 37px;
  height: 37px;
  background: #EFEFEF;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const CalendarVector = styled.div`
  width: 8px;
  height: 4px;
  background: #555E67;
  border-radius: 2px;
`;

const CategoryDropdown = styled.div`
  margin-top: 8px;
  background: #FFFFFF;
  border: 1px solid #ECEDF0;
  border-radius: 12px;
  overflow: hidden;
`;

const CategoryOption = styled.div`
  padding: 12px 16px;
  font-family: 'Hiragino Sans', sans-serif;
  font-size: 14px;
  color: #222222;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: #FAFAFA;
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
`;

const Divider = styled.div`
  height: 1px;
  background: #ECEDF0;
  width: 100%;
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

const ProductScreen = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Product');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [marketingA, setMarketingA] = useState('');
  const [marketingB, setMarketingB] = useState('');
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);
  const categories = ['음식', '여행', '뷰티', '게임', '패션', '스포츠', '교육'];

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleTabClick = (tab) => {
    if (tab === 'Target') {
      navigate('/target');
    } else {
      setActiveTab(tab);
    }
  };

  const handleCategorySelect = () => {
    setIsCategoryOpen(prev => !prev);
  };

  const handleChooseCategory = (cat) => {
    setSelectedCategory(cat);
    setIsCategoryOpen(false);
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
    try {
      const target = JSON.parse(localStorage.getItem('target') || '{}');
      const payload = {
        ...target,
        category: selectedCategory,
        marketing_a: marketingA,
        marketing_b: marketingB,
      };
      localStorage.setItem('product', JSON.stringify(payload));

      const resp = await fetch(`/api/predict`, {
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
      // no-op
    }
  };

  const isProductValid = (selectedCategory || '').trim().length > 0 && (marketingA || '').trim().length > 0 && (marketingB || '').trim().length > 0;

  return (
    <ProductScreenContainer>
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
          <PageTitle>마케팅하고자 하는 제품의 정보/ 마케팅 문구를 입력해주세요</PageTitle>
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

        <FilterContainer>
          <FilterBlock>
            <FilterHeader>
              <FilterTitle>제품 카테고리</FilterTitle>
              <ResetButton onClick={() => handleReset('category')}>초기화</ResetButton>
            </FilterHeader>
            <ProductCategorySelector onClick={handleCategorySelect}>
              <CategoryText>{selectedCategory || '제품 카테고리를 선택해주세요'}</CategoryText>
              <CalendarIcon>
                <CalendarVector />
              </CalendarIcon>
            </ProductCategorySelector>
            {isCategoryOpen && (
              <CategoryDropdown>
                {categories.map((cat) => (
                  <CategoryOption key={cat} onClick={() => handleChooseCategory(cat)}>
                    {cat}
                  </CategoryOption>
                ))}
              </CategoryDropdown>
            )}
            <Divider />
          </FilterBlock>

          <FilterBlock>
            <FilterHeader>
              <FilterTitle>마케팅 문구</FilterTitle>
              <ResetButton onClick={() => handleReset('marketing')}>초기화</ResetButton>
            </FilterHeader>
            <MarketingOptions>
              <MarketingInputWrapper>
                <MarketingLabel>A안</MarketingLabel>
                <MarketingInput
                  type="text"
                  placeholder="마케팅 문구 A안을 입력하세요"
                  value={marketingA}
                  onChange={handleMarketingAChange}
                />
              </MarketingInputWrapper>
              <MarketingInputWrapper>
                <MarketingLabel>B안</MarketingLabel>
                <MarketingInput
                  type="text"
                  placeholder="마케팅 문구 B안을 입력하세요"
                  value={marketingB}
                  onChange={handleMarketingBChange}
                />
              </MarketingInputWrapper>
            </MarketingOptions>
            <Divider />
          </FilterBlock>

          <ActionButton onClick={handleViewResults} disabled={!isProductValid}>
            결과 보러가기
          </ActionButton>
        </FilterContainer>
      </MainContent>

      <Footer>
        <CompanyLogos>
          <CompanyLogo>
            <img src={companyLogo1} alt="Company 1" style={{ width: '100%', height: 'auto' }} />
          </CompanyLogo>
          <CompanyLogo>
            <img src={companyLogo2} alt="Company 2" style={{ width: '100%', height: 'auto' }} />
          </CompanyLogo>
          <CompanyLogo>
            <img src={companyLogo3} alt="Company 3" style={{ width: '100%', height: 'auto' }} />
          </CompanyLogo>
        </CompanyLogos>
      </Footer>
    </ProductScreenContainer>
  );
};

export default ProductScreen;
