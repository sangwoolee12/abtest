import React from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import trendingUpIcon from '../assets/trending-up-1.svg';


const HomeScreenContainer = styled.div`
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
`;

const BackgroundNoise = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('../assets/background.jpeg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
`;

const Header = styled.header`
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 40px;
  padding: 40px 20px;
  min-height: calc(100vh - 120px);
  margin: 0 auto;
  max-width: 100%;

  @media (min-width: 768px) {
    padding: 60px 40px;
    gap: 60px;
  }

  @media (min-width: 1024px) {
    flex-direction: row;
    justify-content: center;
    align-items: center;
    gap: 80px;
    padding: 80px;
  }

  @media (max-width: 1504px) {
    flex-direction: column;
    gap: 60px;
  }
`;

const LeftSection = styled.div`
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: 32px;
  text-align: center;

  @media (min-width: 768px) {
    gap: 40px;
    text-align: left;
  }

  @media (min-width: 1024px) {
    max-width: 678px;
    gap: 48px;
  }

  @media (max-width: 1504px) {
    text-align: center;
    max-width: 100%;
  }
`;

const HeroTitle = styled.h2`
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 28px;
  line-height: 1.21;
  color: #000000;
  margin: 0;

  @media (min-width: 768px) {
    font-size: 36px;
  }

  @media (min-width: 1024px) {
    font-size: 48px;
  }
`;

const HeroDescription = styled.p`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 500;
  font-size: 14px;
  line-height: 1.8;
  color: #878C91;
  margin: 0;
  max-width: 100%;

  @media (min-width: 768px) {
    font-size: 16px;
    max-width: 602px;
  }
`;

const CTAButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
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
  width: fit-content;
  max-width: 300px;
  margin: 0 auto;

  @media (min-width: 768px) {
    margin: 0;
    gap: 42px;
  }

  @media (max-width: 1504px) {
    margin: 0 auto;
  }

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

const RightSection = styled.div`
  position: relative;
  width: 100%;
  height: 400px;
  order: -1;

  @media (min-width: 768px) {
    height: 500px;
    order: 0;
  }

  @media (min-width: 1024px) {
    width: 588px;
    height: 547px;
  }

  @media (max-width: 1504px) {
    width: 100%;
    height: 500px;
    order: 1;
  }
`;

// Top-Left: 라임 그린 트렌드 라인이 있는 검은 원형 아이콘과 연한 회색 1/4 원
const TopLeftCard = styled.div`
  position: absolute;
  top: 20px;
  left: 0;
  width: 45%;
  height: 200px;
  position: relative;

  @media (min-width: 768px) {
    top: 32px;
    height: 250px;
    width: 45%;
  }

  @media (min-width: 1024px) {
    width: 303px;
    height: 275px;
  }
`;

const QuarterCircle = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 280px;
  height: 280px;
  background:rgb(211, 211, 211);
  border-radius: 280px 20px 20px 20px;
`;

const TopRightCard = styled.div`
  position: absolute;
  top: 20px;
  right: 0;
  width: 45%;
  height: 200px;
  background: #F8F8F8;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.1);

  @media (min-width: 768px) {
    top: 32px;
    height: 250px;
    padding: 28px;
    gap: 24px;
    width: 45%;
  }

  @media (min-width: 1024px) {
    width: 280px;
    height: 280px;
    padding: 32px;
  }
`;

const TopRightNumber = styled.div`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 900;
  font-size: 64px;
  line-height: 1.2;
  color: #000000;
  margin: 0;
`;

const TopRightText = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const TopRightLine = styled.p`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.4;
  color: #000000;
  margin: 0;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #E5E5E5;
  border-radius: 4px;
  overflow: hidden;
  margin-top: auto;
`;

const ProgressFill = styled.div`
  width: 70%;
  height: 100%;
  background: #000000;
  border-radius: 4px;
`;

const BottomCard = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 588px;
  height: 216px;
  background: #000000;
  border-radius: 20px;
  padding: 48px 33px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const BottomContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const BottomIcon = styled.div`
  width: 54px;
  height: 1px;
  background: white;
  margin-bottom: 8px;
`;

const BottomText = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const BottomLine = styled.p`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  font-size: 32px;
  line-height: 1.3;
  letter-spacing: -0.02em;
  color: white;
  margin: 0;
`;

const BottomChartBars = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 10px;
`;

const BottomChartBar = styled.div`
  width: 69px;
  height: ${props => props.height}px;
  background: #99EA48;
  border-radius: 4px;
`;

const BlackCircle = styled.div`
  position: absolute;
  top: -25px;
  right: 70px;
  width: 108px;
  height: 108px;
  background: #000000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0px 30.08px 50.58px -6.84px rgba(0, 0, 0, 0.44);
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
          <LogoText>Clicklit!</LogoText>
        </Logo>
      </Header>

      <MainContent>
        <LeftSection>
          <HeroTitle>
            A/B 마케팅 문구 실험, 클릭률 예측, <br />
            이미지 생성까지 한 번에.
          </HeroTitle>
          <HeroDescription>
            사용자의 선택을 예측해 가장 효과적인 문구와 이미지를 찾아내요.
            <br />
            데이터 기반의 예측과 자동화된 생성으로 A/B 테스트 과정을 빠르고 간편하게 만들어요.
          </HeroDescription>
          <CTAButton onClick={handleStartClick}>
            <ButtonContent>
              <span>지금 시작하기</span>
            </ButtonContent>
          </CTAButton>
        </LeftSection>

        <RightSection>
          <TopLeftCard>
            <QuarterCircle />
            <BlackCircle>
              <img 
                src={trendingUpIcon} 
                alt="Trending Up" 
                style={{
                  width: '48px',
                  height: '28px'
                }}
              />
            </BlackCircle>
          </TopLeftCard>
          <TopRightCard>
            <TopRightNumber>3</TopRightNumber>
            <TopRightText>
              <TopRightLine>세 학교(한국외대, 건국대, 숭실대)</TopRightLine>
              <TopRightLine>학생들이 2주간</TopRightLine>
              <TopRightLine>제작한 AI 프로젝트입니다.</TopRightLine>
            </TopRightText>
            <ProgressBar>
              <ProgressFill />
            </ProgressBar>
          </TopRightCard>
          <BottomCard>
            <BottomContent>
              <BottomIcon />
              <BottomText>
                <BottomLine>다양한 A/B 테스트를</BottomLine>
                <BottomLine>진행해보세요</BottomLine>
              </BottomText>
            </BottomContent>
            <BottomChartBars>
              <BottomChartBar height={95} />
              <BottomChartBar height={136} />
              <BottomChartBar height={166} />
            </BottomChartBars>
          </BottomCard>
        </RightSection>
      </MainContent>

    </HomeScreenContainer>
  );
};

export default HomeScreen;
