# Vue 3 + TypeScript + Vite

이 템플릿은 Vue 3와 TypeScript를 Vite에서 개발하는 데 도움이 됩니다. 이 템플릿은 Vue 3의 `<script setup>` SFC를 사용합니다. 자세한 내용은 [script setup 문서](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup)를 참조하세요.

프로젝트 설정 및 IDE 지원에 대한 자세한 내용은 [Vue 문서 TypeScript 가이드](https://vuejs.org/guide/typescript/overview.html#project-setup)에서 확인할 수 있습니다.

## 타이포그래피

이 프로젝트는 [Pretendard](https://github.com/orioncactus/pretendard)를 기본 폰트로 사용합니다. Pretendard는 라틴어와 한글 문자를 모두 지원하는 현대적이고 깔끔한 산세리프 폰트로, 다국어 애플리케이션에 이상적입니다.

### 폰트 설정

폰트는 다음 파일에서 설정됩니다:
- `src/index.css`: Pretendard CSS를 가져오고 기본 font-family로 설정합니다
- `index.html`: 성능 향상을 위해 Pretendard CSS를 미리 로드합니다

폰트 패밀리 스택에는 다양한 시스템에서 일관된 렌더링을 보장하기 위한 대체 폰트가 포함되어 있습니다.

### CSS 가져오기 순서

CSS 파일에서 `@import` 문은 다른 모든 CSS 규칙보다 먼저 와야 합니다. 이 프로젝트에서는 다음 순서로 가져오기를 배치합니다:

1. Pretendard 폰트 CSS (CDN에서)
2. Tailwind CSS
3. 기타 CSS 라이브러리

이 순서는 PostCSS 처리 중에 발생할 수 있는 "@import must precede all other statements" 오류를 방지합니다.

## 코드 포맷팅

이 프로젝트는 코드 포맷팅을 위해 [Prettier](https://prettier.io/)를 사용합니다. Prettier는 프로젝트 전체에서 일관된 코드 스타일을 보장하는 독단적인 코드 포맷터입니다.

### Prettier 설정

Prettier 설정은 `.prettierrc.json`에 다음과 같이 정의되어 있습니다:
- 문장 끝에 세미콜론 사용
- 탭 너비 2칸
- 줄 길이 100자
- 문자열에 작은따옴표 사용
- ES5 후행 쉼표
- 괄호 간격 적용
- Vue 스크립트 및 스타일 태그에 들여쓰기 없음 (추가 줄바꿈 방지)
- LF 줄 끝 문자

### ESLint 통합

Prettier는 ESLint와 통합되어 코드 포맷팅 문제가 ESLint 오류로 보고됩니다. 이 통합은 `.eslintrc.js`에서 구성됩니다.

### 사용 가능한 스크립트

다음 npm 스크립트를 포맷팅에 사용할 수 있습니다:

```bash
# src 디렉토리의 모든 파일 포맷팅
npm run format

# 모든 파일이 올바르게 포맷팅되었는지 확인
npm run format:check

# 특정 파일 포맷팅 (예: main.ts)
npm run format:main
```
