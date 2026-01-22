// Building Code MCP 데이터

export const stats = {
  sections: 25707,
  codes: 14,
  provinces: 5,
};

export const codes = {
  national: [
    { id: 'nbc2025', name: 'NBC 2025', fullName: 'National Building Code', sections: 4213 },
    { id: 'nfc2025', name: 'NFC 2025', fullName: 'National Fire Code', sections: 1407 },
    { id: 'npc2025', name: 'NPC 2025', fullName: 'National Plumbing Code', sections: 595 },
    { id: 'necb2025', name: 'NECB 2025', fullName: 'National Energy Code', sections: 777 },
  ],
  provincial: [
    { id: 'obc', name: 'OBC', fullName: 'Ontario Building Code', sections: 3925, province: 'Ontario' },
    { id: 'bcbc', name: 'BCBC 2024', fullName: 'BC Building Code', sections: 2645, province: 'British Columbia' },
    { id: 'abc', name: 'ABC', fullName: 'Alberta Building Code', sections: 4165, province: 'Alberta' },
    { id: 'qcc', name: 'QCC 2020', fullName: 'Quebec Construction Code', sections: 3925, province: 'Quebec' },
  ],
  guides: [
    { id: 'ugp9', name: 'Part 9 Guide', fullName: "User's Guide - NBC Part 9", sections: 1399 },
    { id: 'ugp4', name: 'Part 4 Guide', fullName: "User's Guide - NBC Part 4", sections: 21 },
    { id: 'ugnecb', name: 'NECB Guide', fullName: "User's Guide - NECB", sections: 612 },
  ],
};

export const demoQuestions = [
  {
    category: '구조',
    question: '온타리오에서 목조 건물 최대 층수는?',
    answer: 'OBC 2024 Section 3.2.2.58에 따르면, 캡슐화된 대량 목재 구조(Encapsulated Mass Timber Construction)의 경우 최대 12층까지 허용됩니다.',
    reference: 'OBC Vol.1, Page 245',
  },
  {
    category: '화재 안전',
    question: 'NBC에서 스프링클러 면제 조건은?',
    answer: 'NBC 2025 Section 3.2.5.12에 따르면, 건물 높이가 3층 이하이고 건물 면적이 2000m² 이하인 경우 일부 용도에서 스프링클러를 면제받을 수 있습니다.',
    reference: 'NBC 2025, Page 312',
  },
  {
    category: '에너지',
    question: 'NECB 창문 열관류율 기준은?',
    answer: 'NECB 2025 Table 3.2.2.2에 따르면, Climate Zone 7A (토론토 등)에서 창문의 최대 U-value는 1.9 W/(m²·K)입니다.',
    reference: 'NECB 2025, Page 89',
  },
  {
    category: '접근성',
    question: 'barrier-free 경사로 최대 기울기는?',
    answer: 'NBC 2025 Section 3.8.3.4에 따르면, barrier-free 경사로의 최대 기울기는 1:12 (8.33%)이며, 수평 길이 9m마다 수평 휴식 공간이 필요합니다.',
    reference: 'NBC 2025, Page 421',
  },
];

export const steps = [
  {
    step: 1,
    title: 'PDF 준비',
    description: '공식 웹사이트에서 Building Code PDF를 다운로드하세요. NRC, Ontario, BC 등 각 관할권 사이트에서 무료로 제공됩니다.',
    icon: 'FileText',
  },
  {
    step: 2,
    title: 'MCP 서버 설치',
    description: 'Claude Desktop에 Building Code MCP 서버를 연결하세요. 5분이면 설정 완료됩니다.',
    icon: 'Plug',
  },
  {
    step: 3,
    title: '자연어로 검색',
    description: '"온타리오 주거용 계단 폭"처럼 평소 말하듯 질문하세요. AI가 관련 조항을 찾아 원본 위치를 알려줍니다.',
    icon: 'MessageSquare',
  },
];
