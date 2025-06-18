/**
 * Formats a phone number by adding hyphens in the appropriate positions.
 * 
 * @param phoneNumber The phone number to format (can be with or without hyphens)
 * @returns The formatted phone number with hyphens
 */
export function formatPhoneNumber(phoneNumber: string | null | undefined): string {
  // Return empty string if phoneNumber is null or undefined
  if (!phoneNumber) {
    return '';
  }
  
  // Remove any existing hyphens or non-digit characters
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  // Format based on the length of the phone number
  if (cleaned.length === 11) {
    // Mobile number format: 010-1234-5678
    return `${cleaned.substring(0, 3)}-${cleaned.substring(3, 7)}-${cleaned.substring(7)}`;
  } else if (cleaned.length === 10) {
    // Some mobile or local number format: 010-123-4567 or 02-1234-5678
    if (cleaned.startsWith('02')) {
      // Seoul area code
      return `${cleaned.substring(0, 2)}-${cleaned.substring(2, 6)}-${cleaned.substring(6)}`;
    } else {
      // Other 10-digit number
      return `${cleaned.substring(0, 3)}-${cleaned.substring(3, 6)}-${cleaned.substring(6)}`;
    }
  } else if (cleaned.length === 9) {
    // Local number with 2-digit area code: 02-123-4567
    if (cleaned.startsWith('02')) {
      return `${cleaned.substring(0, 2)}-${cleaned.substring(2, 5)}-${cleaned.substring(5)}`;
    } else {
      // Other 9-digit number
      return `${cleaned.substring(0, 3)}-${cleaned.substring(3, 6)}-${cleaned.substring(6)}`;
    }
  } else if (cleaned.length === 8) {
    // Just a local number without area code: 1234-5678
    return `${cleaned.substring(0, 4)}-${cleaned.substring(4)}`;
  }
  
  // If the format doesn't match any known pattern, return as is
  return phoneNumber;
}