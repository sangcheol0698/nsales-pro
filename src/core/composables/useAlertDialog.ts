import { type Component, h, ref, render } from 'vue';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/core/components/ui/alert-dialog';

/**
 * AlertDialog 옵션 인터페이스
 */
export interface AlertDialogOptions {
  /**
   * 다이얼로그 제목
   */
  title?: string;
  /**
   * 다이얼로그 설명
   */
  description?: string;
  /**
   * 확인 버튼 텍스트
   * @default "확인"
   */
  confirmText?: string;
  /**
   * 취소 버튼 텍스트
   * @default "취소"
   */
  cancelText?: string;
  /**
   * 확인 버튼 클릭 시 콜백 함수
   */
  onConfirm?: () => void;
  /**
   * 취소 버튼 클릭 시 콜백 함수
   */
  onCancel?: () => void;
}

/**
 * AlertDialog를 프로그래밍 방식으로 사용하기 위한 컴포저블
 * @returns AlertDialog 관련 메소드가 포함된 객체
 */
export function useAlertDialog() {
  // 다이얼로그 표시 여부
  const isOpen = ref(false);
  // 다이얼로그 컨테이너 요소
  let container: HTMLElement | null = null;
  // 현재 다이얼로그 옵션
  let currentOptions: AlertDialogOptions = {};

  /**
   * 다이얼로그 열기
   * @param options - 다이얼로그 옵션
   */
  const open = (options: AlertDialogOptions) => {
    // 옵션 저장
    currentOptions = options;

    // 컨테이너가 없으면 생성
    if (!container) {
      container = document.createElement('div');
      document.body.appendChild(container);
    }

    // 다이얼로그 표시
    isOpen.value = true;

    // 다이얼로그 컴포넌트 렌더링
    renderDialog();
  };

  /**
   * 다이얼로그 닫기
   */
  const close = () => {
    isOpen.value = false;
    
    // 컨테이너가 있으면 제거
    if (container) {
      render(null, container);
      document.body.removeChild(container);
      container = null;
    }
  };

  /**
   * 확인 버튼 클릭 핸들러
   */
  const handleConfirm = () => {
    if (currentOptions.onConfirm) {
      currentOptions.onConfirm();
    }
    close();
  };

  /**
   * 취소 버튼 클릭 핸들러
   */
  const handleCancel = () => {
    if (currentOptions.onCancel) {
      currentOptions.onCancel();
    }
    close();
  };

  /**
   * 다이얼로그 컴포넌트 렌더링
   */
  const renderDialog = () => {
    if (!container) return;

    // AlertDialog 컴포넌트 생성
    const DialogComponent: Component = {
      setup() {
        return () => h(AlertDialog, { open: isOpen.value }, {
          default: () => h(AlertDialogContent, {}, {
            default: () => [
              h(AlertDialogHeader, {}, {
                default: () => [
                  h(AlertDialogTitle, {}, { default: () => currentOptions.title || '' }),
                  currentOptions.description 
                    ? h(AlertDialogDescription, {}, { default: () => currentOptions.description }) 
                    : null
                ]
              }),
              h(AlertDialogFooter, {}, {
                default: () => [
                  h(AlertDialogCancel, { onClick: handleCancel }, { default: () => currentOptions.cancelText || '취소' }),
                  h(AlertDialogAction, { onClick: handleConfirm }, { default: () => currentOptions.confirmText || '확인' })
                ]
              })
            ]
          })
        });
      }
    };

    // 컴포넌트 렌더링
    render(h(DialogComponent), container);
  };

  /**
   * 확인 다이얼로그 표시 (확인 버튼만 있는 다이얼로그)
   * @param title - 다이얼로그 제목
   * @param description - 다이얼로그 설명 (선택적)
   * @param onConfirm - 확인 버튼 클릭 시 콜백 함수 (선택적)
   */
  const alert = (title: string, description?: string, onConfirm?: () => void) => {
    open({
      title,
      description,
      confirmText: '확인',
      onConfirm,
      // 취소 버튼 없음
    });
  };

  /**
   * 확인/취소 다이얼로그 표시
   * @param title - 다이얼로그 제목
   * @param description - 다이얼로그 설명 (선택적)
   * @param onConfirm - 확인 버튼 클릭 시 콜백 함수 (선택적)
   * @param onCancel - 취소 버튼 클릭 시 콜백 함수 (선택적)
   */
  const confirm = (title: string, description?: string, onConfirm?: () => void, onCancel?: () => void) => {
    open({
      title,
      description,
      confirmText: '확인',
      cancelText: '취소',
      onConfirm,
      onCancel,
    });
  };

  return {
    open,
    close,
    alert,
    confirm,
    isOpen,
  };
}