/**
 * Utility function to display submitted form data in a toast and console
 * This is used for demonstration purposes in the AppearanceForm component
 */
import { useToast } from '@/core/composables';

export function showSubmittedData(data: Record<string, any>) {
  console.log('Form submitted with data:', data);

  // Format theme for display
  let themeDisplay = data.theme === 'light' ? '라이트' : '다크';

  // Show a toast notification
  const toast = useToast();
  toast.success('화면 설정이 업데이트되었습니다', {
    description: `테마: ${themeDisplay}, 폰트: ${data.font}`,
    position: 'bottom-right',
  });
}
