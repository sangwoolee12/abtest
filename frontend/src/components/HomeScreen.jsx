import React from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import chevronDown from '../assets/chevron-down.svg';
import companyLogo1 from '../assets/company-logo-1.svg';
import companyLogo2 from '../assets/company-logo-2.svg';
import companyLogo3 from '../assets/company-logo-3.svg';

const HomeScreenContainer = styled.div`
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 80px;
  min-height: calc(100vh - 120px);
`;

const LeftSection = styled.div`
  max-width: 678px;
  display: flex;
  flex-direction: column;
  gap: 48px;
`;

const HeroTitle = styled.h2`
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 36px;
  line-height: 1.21;
  color: #000000;
  margin: 0;
`;

const HeroDescription = styled.p`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 500;
  font-size: 16px;
  line-height: 1.8;
  color: #878C91;
  margin: 0;
  max-width: 602px;
`;

const CTAButton = styled.button`
  display: flex;
  align-items: center;
  gap: 42px;
  padding: 16px 32px;
  background: #010205;
  border-radius: 70px;
  border: none;
  color: white;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 16px;
  line-height: 1.4;
  letter-spacing: -0.02em;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #1a1a1a;
    transform: translateY(-2px);
  }
`;

const ButtonContent = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ArrowIcon = styled.div`
  width: 24px;
  height: 24px;
  position: relative;
`;

const ArrowLine = styled.div`
  position: absolute;
  top: 12px;
  left: 5px;
  width: 14px;
  height: 2px;
  background: white;
`;

const ArrowHead = styled.div`
  position: absolute;
  top: 5px;
  left: 12px;
  width: 7px;
  height: 14px;
  background: white;
  clip-path: polygon(0 0, 100% 50%, 0 100%);
`;

const RightSection = styled.div`
  position: relative;
  width: 588px;
  height: 547px;
`;

const StatsCard = styled.div`
  position: absolute;
  top: 32px;
  left: 0;
  width: 303px;
  height: 275px;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(84px);
  border-radius: 1000px 20px 20px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 30px;
  padding: 38px 25px;
`;

const StatsNumber = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 84px;
  line-height: 1.5;
  letter-spacing: -0.03em;
  color: #010205;
`;

const StatsDescription = styled.p`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 500;
  font-size: 16px;
  line-height: 1.5;
  color: #5C5D5F;
  text-align: center;
  max-width: 211px;
  margin: 0;
`;

const ChartCard = styled.div`
  position: absolute;
  top: 32px;
  right: 0;
  width: 259px;
  height: 281px;
  background: #F0F0F0;
  backdrop-filter: blur(84px);
  border-radius: 20px;
  position: relative;
`;

const ChartLines = styled.div`
  position: absolute;
  bottom: 24px;
  left: 24px;
  display: flex;
  flex-direction: column;
  gap: 0;
`;

const ChartLine1 = styled.div`
  width: 211px;
  height: 6.65px;
  background: #D9D9D9;
  margin-bottom: 0;
`;

const ChartLine2 = styled.div`
  width: 141px;
  height: 6.65px;
  background: #000000;
`;

const FeatureCard = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 588px;
  height: 216px;
  background: #010205;
  backdrop-filter: blur(84px);
  border-radius: 20px;
  position: relative;
  overflow: hidden;
`;

const FeatureImage = styled.div`
  position: absolute;
  top: -106.92px;
  left: -180.68px;
  width: 503.31px;
  height: 583.71px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
`;

const FeatureContent = styled.div`
  position: absolute;
  top: 48px;
  left: 33px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  z-index: 2;
`;

const FeatureHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 13px;
`;

const FeatureIcon = styled.div`
  width: 54px;
  height: 1px;
  background: white;
`;

const FeatureTitle = styled.h3`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.26;
  letter-spacing: -0.03em;
  color: white;
  margin: 0;
`;

const FeatureDescription = styled.p`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 32px;
  line-height: 1.3;
  letter-spacing: -0.02em;
  color: white;
  margin: 0;
  max-width: 280px;
`;

const ChartBars = styled.div`
  position: absolute;
  top: 51px;
  right: 33px;
  display: flex;
  align-items: flex-end;
  gap: 10px;
`;

const ChartBar = styled.div`
  width: 69px;
  height: ${props => props.height}px;
  background: ${props => props.color};
  border-radius: 4px;
`;

const TrendingCard = styled.div`
  position: absolute;
  top: 0;
  right: 155px;
  width: 108px;
  height: 108px;
  background: #010205;
  border-radius: 683.54px;
  box-shadow: 0px 30.08px 50.58px -6.84px rgba(0, 0, 0, 0.44);
  display: flex;
  align-items: center;
  justify-content: center;
`;

const TrendingIcon = styled.div`
  width: 48px;
  height: 48px;
  position: relative;
`;

const TrendingLine1 = styled.div`
  position: absolute;
  top: 12px;
  left: 2px;
  width: 44px;
  height: 4px;
  background: #A8D67B;
`;

const TrendingLine2 = styled.div`
  position: absolute;
  top: 12px;
  left: 34px;
  width: 12px;
  height: 12px;
  background: #A8D67B;
  border-radius: 50%;
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

const HomeScreen = () => {
  const navigate = useNavigate();

  const handleStartClick = () => {
    navigate('/target');
  };

  return (
    <HomeScreenContainer>
      <BackgroundNoise />
      
      <Header>
        <Logo>
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
        <LeftSection>
          <HeroTitle>
            A/B 마케팅 문구 실험, 클릭률 예측, 이미지 생성까지 한 번에.
          </HeroTitle>
          <HeroDescription>
            사용자의 예측해 가장 효과적인 문구와 이미지를 찾아냅니다.
            데이터 기반의 예측과 자동화된 생성으로 A/B 테스트 과정을 빠르고 간편하게 만듭니다.
          </HeroDescription>
          <CTAButton onClick={handleStartClick}>
            <ButtonContent>
              <span>지금 시작하기</span>
            </ButtonContent>
            <ArrowIcon>
              <ArrowLine />
              <ArrowHead />
            </ArrowIcon>
          </CTAButton>
        </LeftSection>

        <RightSection>
          <StatsCard>
            <StatsNumber>230+</StatsNumber>
            <StatsDescription>
              some big companies that we work with, and trust us very much
            </StatsDescription>
          </StatsCard>
          
          <ChartCard>
            <ChartLines>
              <ChartLine1 />
              <ChartLine2 />
            </ChartLines>
          </ChartCard>
          
          <FeatureCard>
            <FeatureImage />
            <FeatureContent>
              <FeatureHeader>
                <FeatureIcon />
                <FeatureTitle>Drive More Traffic and Sales</FeatureTitle>
              </FeatureHeader>
              <FeatureDescription>
                Drive more traffic and product sales
              </FeatureDescription>
            </FeatureContent>
            <ChartBars>
              <ChartBar height={95} color="#BAE289" />
              <ChartBar height={136} color="#99CF63" />
              <ChartBar height={166} color="#77B248" />
            </ChartBars>
          </FeatureCard>
          
          <TrendingCard>
            <TrendingIcon>
              <TrendingLine1 />
              <TrendingLine2 />
            </TrendingIcon>
          </TrendingCard>
        </RightSection>
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
    </HomeScreenContainer>
  );
};

export default HomeScreen;
