import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const TargetScreenContainer = styled.div`
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
  width: 612px;

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
  width: 100%;
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
`;

const FilterOptions = styled.div`
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  width: 100%;
  overflow-x: auto;
`;

const FilterOption = styled.div`
  padding: 0 16px;
  height: 48px;
  background: ${props => props.isSelected ? 'rgba(153, 234, 72, 0.9)' : '#FFFFFF'};
  border: 2px solid ${props => props.isSelected ? '#99EA48' : '#ECEDF0'};
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
  width: calc((100% - 60px) / 7);

  &:hover {
    background: ${props => props.isSelected ? 'rgba(153, 234, 72, 0.9)' : '#FAFAFA'};
    border-color: ${props => props.isSelected ? '#8DD43A' : '#D1D5DB'};
  }
`;

const GenderFilterOption = styled.div`
  padding: 0 16px;
  height: 48px;
  background: ${props => props.isSelected ? 'rgba(153, 234, 72, 0.9)' : '#FFFFFF'};
  border: 2px solid ${props => props.isSelected ? '#99EA48' : '#ECEDF0'};
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 0;

  &:hover {
    background: ${props => props.isSelected ? 'rgba(153, 234, 72, 0.9)' : '#FAFAFA'};
    border-color: ${props => props.isSelected ? '#8DD43A' : '#D1D5DB'};
  }
`;

const PersonaSection = styled.div`
  margin-bottom: 10px;
`;

const PersonaToggle = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  margin-bottom: 10px;
`;

const ToggleButton = styled.button`
  padding: 0 5px;
  height: 48px;
  background: ${props => props.isActive ? 'rgba(153, 234, 72, 0.9)' : '#FFFFFF'};
  border: 2px solid ${props => props.isActive ? '#99EA48' : '#ECEDF0'};
  border-radius: 12px;
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #222222;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-width: 0;

  &:hover {
    background: ${props => props.isActive ? 'rgba(153, 234, 72, 0.9)' : '#FAFAFA'};
    border-color: ${props => props.isActive ? '#8DD43A' : '#D1D5DB'};
  }
`;

const PersonaGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 30px;
  margin-bottom: 16px;
`;

const PersonaButton = styled.button`
  padding: 16px;
  background: ${props => props.isSelected ? 'rgba(153, 234, 72, 0.9)' : '#FFFFFF'};
  border: 2px solid ${props => props.isSelected ? '#99EA48' : '#ECEDF0'};
  border-radius: 12px;
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #222222;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;

  &:hover {
    background: ${props => props.isSelected ? 'rgba(153, 234, 72, 0.9)' : '#FAFAFA'};
    border-color: ${props => props.isSelected ? '#8DD43A' : '#D1D5DB'};
  }
`;

const PersonaName = styled.div`
  font-weight: 700;
  margin-bottom: 4px;
`;

const PersonaDetails = styled.div`
  font-size: 12px;
  color: #666666;
  line-height: 1.4;
`;

const FilterOptionText = styled.span`
  font-family: 'Hiragino Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.5;
  color:rgb(62, 64, 67);
  padding: 0 8px;
  white-space: nowrap;
`;

const InterestInput = styled.input`
  width: 100%;
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
  background:rgba(174, 174, 174, 0.76);
  border: none;
  border-radius: 70px;
  color:rgb(0, 0, 0);
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

const TargetScreen = () => {
  const navigate = useNavigate();
  const [selectedAgeGroups, setSelectedAgeGroups] = useState([]);
  const [selectedGenders, setSelectedGenders] = useState([]);
  const [interestInput, setInterestInput] = useState('');
  const [usePersonas, setUsePersonas] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState(null);

  const ageGroups = ['10대', '20대', '30대', '40대', '50대', '60대', '70대 이상'];
  const genders = ['남성', '여성'];
  
  // 8가지 페르소나 정의
  const personas = [
    {
      id: 'p1',
      name: '뷰티/화장품',
      age: '20대',
      gender: '여성',
      interests: '생활, 노하우, 쇼핑',
      categories: '뷰티, 화장품, 스킨케어'
    },
    {
      id: 'p2',
      name: '게임',
      age: '20대',
      gender: '남성',
      interests: '취미, 여가, 여행',
      categories: '게임, 전자제품, 엔터테인먼트'
    },
    {
      id: 'p3',
      name: '패션/잡화',
      age: '30대',
      gender: '여성',
      interests: '생활, 노하우, 쇼핑',
      categories: '패션, 액세서리, 라이프스타일'
    },
    {
      id: 'p4',
      name: '부동산/재테크',
      age: '30대',
      gender: '남성',
      interests: '지식, 동향',
      categories: '부동산, 투자, 금융'
    },
    {
      id: 'p5',
      name: '여행/숙박/항공',
      age: '40대',
      gender: '여성',
      interests: '취미, 여가, 여행',
      categories: '여행, 숙박, 항공'
    },
    {
      id: 'p6',
      name: '스포츠/레저',
      age: '40대',
      gender: '남성',
      interests: '취미, 여가, 여행',
      categories: '스포츠, 아웃도어, 레저'
    },
    {
      id: 'p7',
      name: '식음료/요리',
      age: '50대',
      gender: '여성',
      interests: '생활, 노하우, 쇼핑',
      categories: '식음료, 요리'
    },
    {
      id: 'p8',
      name: '정치/사회',
      age: '50대',
      gender: '남성',
      interests: '지식, 동향',
      categories: '정치, 사회이슈, 뉴스'
    }
  ];

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleAgeGroupToggle = (age) => {
    setSelectedAgeGroups(prev => 
      prev.includes(age) 
        ? prev.filter(a => a !== age)
        : [...prev, age]
    );
  };

  const handleGenderToggle = (gender) => {
    setSelectedGenders(prev => 
      prev.includes(gender) 
        ? prev.filter(g => g !== gender)
        : [...prev, gender]
    );
  };

  const handlePersonaToggle = () => {
    setUsePersonas(!usePersonas);
    if (usePersonas) {
      setSelectedPersona(null);
      setSelectedAgeGroups([]);
      setSelectedGenders([]);
      setInterestInput('');
    }
  };

  const handlePersonaSelect = (persona) => {
    setSelectedPersona(persona);
    setSelectedAgeGroups([persona.age]);
    setSelectedGenders([persona.gender]);
    setInterestInput(persona.interests);
  };

  const handleInterestInputChange = (e) => {
    setInterestInput(e.target.value);
  };

  const handleReset = (type) => {
    switch (type) {
      case 'age':
        setSelectedAgeGroups([]);
        break;
      case 'gender':
        setSelectedGenders([]);
        break;
      case 'interest':
        setInterestInput('');
        break;
      case 'persona':
        setSelectedPersona(null);
        setSelectedAgeGroups([]);
        setSelectedGenders([]);
        setInterestInput('');
        break;
      default:
        break;
    }
  };

  const handleNextStep = () => {
    try {
      const payload = {
        age_groups: selectedAgeGroups,
        genders: selectedGenders,
        interests: interestInput,
        persona: selectedPersona ? {
          id: selectedPersona.id,
          name: selectedPersona.name
        } : null
      };
      localStorage.setItem('target', JSON.stringify(payload));
    } catch (e) {
    }
    navigate('/product');
  };

  const isTargetValid = (selectedAgeGroups.length > 0 && selectedGenders.length > 0 && (interestInput || '').trim().length > 0) || selectedPersona;

  return (
    <TargetScreenContainer>
      
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
          <PageTitle>마케팅하고자 하는 타켓의 정보를 입력해주세요</PageTitle>
        </PageHeader>

        <TabContainer>
          <Tab style={{ fontWeight: '700', color: '#000000' }}>
            Target
          </Tab>
          <Tab>
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
          {/* 페르소나 선택 섹션 */}
          <PersonaSection>
            <FilterHeader>
              <FilterTitle>페르소나 선택</FilterTitle>
              <ResetButton onClick={() => handleReset('persona')}>초기화</ResetButton>
            </FilterHeader>
            
            <PersonaToggle>
              <ToggleButton 
                isActive={!usePersonas} 
                onClick={handlePersonaToggle}
              >
                직접 입력
              </ToggleButton>
              <ToggleButton 
                isActive={usePersonas} 
                onClick={handlePersonaToggle}
              >
                페르소나 선택
              </ToggleButton>
            </PersonaToggle>

            {usePersonas && (
              <PersonaGrid>
                {personas.map((persona) => (
                  <PersonaButton
                    key={persona.id}
                    isSelected={selectedPersona?.id === persona.id}
                    onClick={() => handlePersonaSelect(persona)}
                  >
                    <PersonaName>{persona.name}</PersonaName>
                    <PersonaDetails isSelected={selectedPersona?.id === persona.id}>
                      {persona.age} • {persona.gender}<br/>
                      {persona.interests}<br/>
                      {persona.categories}
                    </PersonaDetails>
                  </PersonaButton>
                ))}
              </PersonaGrid>
            )}
          </PersonaSection>

          {!usePersonas && (
            <>
              <FilterBlock>
                <FilterHeader>
                  <FilterTitle>타겟 연령대 (복수 선택 가능)</FilterTitle>
                  <ResetButton onClick={() => handleReset('age')}>초기화</ResetButton>
                </FilterHeader>
                <FilterOptions>
                  {ageGroups.map((age) => (
                    <FilterOption
                      key={age}
                      isSelected={selectedAgeGroups.includes(age)}
                      onClick={() => handleAgeGroupToggle(age)}
                    >
                      <FilterOptionText>{age}</FilterOptionText>
                    </FilterOption>
                  ))}
                </FilterOptions>
                <Divider />
              </FilterBlock>

              <FilterBlock>
                <FilterHeader>
                  <FilterTitle>타겟 성별 (복수 선택 가능)</FilterTitle>
                  <ResetButton onClick={() => handleReset('gender')}>초기화</ResetButton>
                </FilterHeader>
                <FilterOptions>
                  {genders.map((gender) => (
                    <GenderFilterOption
                      key={gender}
                      isSelected={selectedGenders.includes(gender)}
                      onClick={() => handleGenderToggle(gender)}
                    >
                      <FilterOptionText>{gender}</FilterOptionText>
                    </GenderFilterOption>
                  ))}
                </FilterOptions>
                <Divider />
              </FilterBlock>

              <FilterBlock>
                <FilterHeader>
                  <FilterTitle>타겟 관심사</FilterTitle>
                  <ResetButton onClick={() => handleReset('interest')}>초기화</ResetButton>
                </FilterHeader>
                <InterestInput
                  type="text"
                  placeholder="예: 야구, KBO, 유니폼"
                  value={interestInput}
                  onChange={handleInterestInputChange}
                />
              </FilterBlock>
            </>
          )}

          <ActionButton onClick={handleNextStep} disabled={!isTargetValid}>
            다음 단계
          </ActionButton>
        </FilterContainer>
      </MainContent>

    </TargetScreenContainer>
  );
};

export default TargetScreen;
