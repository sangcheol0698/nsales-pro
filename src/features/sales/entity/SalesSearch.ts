export interface SalesSearch {
  // 부서 정보
  부서범위: string;
  부서아이디: number;
  부서이름: string;

  // 집계 관련 금액
  매출합계: number;
  매출목표: number;
  달성률: number;
  인건비: number;
  판관비: number;
  제경비: number;
  영업이익: number;
  영업이익률: number;

  // 인원 수
  정직원: number;
  외주: number;
  프리랜서: number;

  // 인건비 집계
  정직원인건비: number;
  외주인건비: number;
  프리랜서인건비: number;

  // 계약 유형별 집계
  SI: number;
  SM: number;

  // 월별 매출액
  sales_01: number;
  sales_02: number;
  sales_03: number;
  sales_04: number;
  sales_05: number;
  sales_06: number;
  sales_07: number;
  sales_08: number;
  sales_09: number;
  sales_10: number;
  sales_11: number;
  sales_12: number;
}