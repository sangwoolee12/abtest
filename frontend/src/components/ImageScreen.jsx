import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import chevronDown from '../assets/chevron-down.svg';
import companyLogo1 from '../assets/company-logo-1.svg';
import companyLogo2 from '../assets/company-logo-2.svg';
import companyLogo3 from '../assets/company-logo-3.svg';

const ImageScreenContainer = styled.div`
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
  padding: 80px 188px;
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
  max-width: 700px;
`;

const TabContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 18px;
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

const FilterBlock = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 612px;
  margin: 0 auto 18px;
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
  justify-content: center;
  padding: 0 8px;
  height: 48px;
  background: #FAFAFA;
  border: 1px solid #ECEDF0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #F0F0F0;
  }
`;

const StyleText = styled.span`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 12px;
  line-height: 1.5;
  color: #9B9B9C;
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
  margin: 0 auto;

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
  max-width: 753px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
  justify-content: center;
`;

const ImageCard = styled.div`
  width: 235px;
  background: #FFFFFF;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 56px;
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

const ImageScreen = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Generate Images');
  const [isGenerating, setIsGenerating] = useState(false);
  const [imagesGenerated, setImagesGenerated] = useState(false);

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleTabClick = (tab) => {
    if (tab === 'Target') {
      navigate('/target');
    } else if (tab === 'Product') {
      navigate('/product');
    } else if (tab === 'Generated texts') {
      navigate('/prediction');
    } else {
      setActiveTab(tab);
    }
  };

  const handleGenerateImages = () => {
    setIsGenerating(true);
    
    // 3초 후에 이미지 생성 완료
    setTimeout(() => {
      setIsGenerating(false);
      setImagesGenerated(true);
    }, 3000);
  };

  const handleDownload = (imageIndex) => {
    // 다운로드 기능 (향후 구현)
    alert(`이미지 ${imageIndex + 1} 다운로드 기능은 향후 구현 예정입니다.`);
  };

  const handleReset = () => {
    setImagesGenerated(false);
    setIsGenerating(false);
  };

  return (
    <ImageScreenContainer>
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
          <PageTitle>어떤 스타일의 이미지를 원하시나요?</PageTitle>
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
            isActive={activeTab === 'Generated texts'} 
            onClick={() => handleTabClick('Generated texts')}
          >
            Generated texts
          </Tab>
          <Tab 
            isActive={activeTab === 'Generate Images'} 
            onClick={() => handleTabClick('Generate Images')}
          >
            Generate Images
          </Tab>
        </TabContainer>

        <FilterBlock>
          <FilterHeader>
            <FilterTitle>이미지 스타일</FilterTitle>
            <ResetButton onClick={handleReset}>Reset</ResetButton>
          </FilterHeader>
          <StyleSelector>
            <StyleText>#밝은 #하늘색 #시원한</StyleText>
          </StyleSelector>
        </FilterBlock>

        <GenerateButton 
          onClick={handleGenerateImages}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <LoadingSpinner />
              생성 중...
            </>
          ) : (
            '이미지 생성하기'
          )}
        </GenerateButton>

        {imagesGenerated && (
          <ResultsContainer>
            {[1, 2, 3].map((index) => (
              <ImageCard key={index}>
                <ImagePlaceholder>
                  <ImageLines>
                    <LongLine />
                    <ShortLine />
                  </ImageLines>
                </ImagePlaceholder>
                <DownloadButton onClick={() => handleDownload(index - 1)}>
                  다운로드
                </DownloadButton>
              </ImageCard>
            ))}
          </ResultsContainer>
        )}
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
    </ImageScreenContainer>
  );
};

export default ImageScreen;
