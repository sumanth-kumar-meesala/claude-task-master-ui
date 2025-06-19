/**
 * Validation utility functions.
 */

/**
 * Validates an email address.
 * 
 * @param email - Email address to validate
 * @returns True if valid, false otherwise
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validates a URL.
 * 
 * @param url - URL to validate
 * @returns True if valid, false otherwise
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validates a phone number (basic validation).
 * 
 * @param phone - Phone number to validate
 * @returns True if valid, false otherwise
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

/**
 * Validates a password strength.
 * 
 * @param password - Password to validate
 * @returns Object with validation results
 */
export function validatePassword(password: string): {
  isValid: boolean;
  score: number;
  feedback: string[];
} {
  const feedback: string[] = [];
  let score = 0;
  
  if (password.length >= 8) {
    score += 1;
  } else {
    feedback.push('Password must be at least 8 characters long');
  }
  
  if (/[a-z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Password must contain at least one lowercase letter');
  }
  
  if (/[A-Z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Password must contain at least one uppercase letter');
  }
  
  if (/\d/.test(password)) {
    score += 1;
  } else {
    feedback.push('Password must contain at least one number');
  }
  
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Password must contain at least one special character');
  }
  
  return {
    isValid: score >= 4,
    score,
    feedback,
  };
}

/**
 * Validates if a string is not empty or just whitespace.
 * 
 * @param value - String to validate
 * @returns True if not empty, false otherwise
 */
export function isNotEmpty(value: string): boolean {
  return value.trim().length > 0;
}

/**
 * Validates if a value is within a specified range.
 * 
 * @param value - Number to validate
 * @param min - Minimum value
 * @param max - Maximum value
 * @returns True if within range, false otherwise
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}

/**
 * Validates if a string matches a pattern.
 * 
 * @param value - String to validate
 * @param pattern - Regular expression pattern
 * @returns True if matches, false otherwise
 */
export function matchesPattern(value: string, pattern: RegExp): boolean {
  return pattern.test(value);
}

/**
 * Validates if a file has an allowed extension.
 * 
 * @param filename - File name to validate
 * @param allowedExtensions - Array of allowed extensions
 * @returns True if allowed, false otherwise
 */
export function hasAllowedExtension(
  filename: string,
  allowedExtensions: string[]
): boolean {
  const extension = filename.split('.').pop()?.toLowerCase();
  return extension ? allowedExtensions.includes(extension) : false;
}

/**
 * Validates if a file size is within limits.
 * 
 * @param fileSize - File size in bytes
 * @param maxSize - Maximum size in bytes
 * @returns True if within limits, false otherwise
 */
export function isValidFileSize(fileSize: number, maxSize: number): boolean {
  return fileSize <= maxSize;
}

/**
 * Validates a credit card number using Luhn algorithm.
 * 
 * @param cardNumber - Credit card number
 * @returns True if valid, false otherwise
 */
export function isValidCreditCard(cardNumber: string): boolean {
  const cleanNumber = cardNumber.replace(/\D/g, '');
  
  if (cleanNumber.length < 13 || cleanNumber.length > 19) {
    return false;
  }
  
  let sum = 0;
  let isEven = false;
  
  for (let i = cleanNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cleanNumber.charAt(i), 10);
    
    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    
    sum += digit;
    isEven = !isEven;
  }
  
  return sum % 10 === 0;
}

/**
 * Validates a date string.
 * 
 * @param dateString - Date string to validate
 * @returns True if valid date, false otherwise
 */
export function isValidDate(dateString: string): boolean {
  const date = new Date(dateString);
  return !isNaN(date.getTime());
}

/**
 * Validates if a date is in the future.
 * 
 * @param date - Date to validate
 * @returns True if in future, false otherwise
 */
export function isFutureDate(date: Date | string): boolean {
  const dateObj = new Date(date);
  const now = new Date();
  return dateObj > now;
}

/**
 * Validates if a date is in the past.
 * 
 * @param date - Date to validate
 * @returns True if in past, false otherwise
 */
export function isPastDate(date: Date | string): boolean {
  const dateObj = new Date(date);
  const now = new Date();
  return dateObj < now;
}

/**
 * Validates JSON string.
 * 
 * @param jsonString - JSON string to validate
 * @returns True if valid JSON, false otherwise
 */
export function isValidJson(jsonString: string): boolean {
  try {
    JSON.parse(jsonString);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validates if a value is a valid hex color.
 * 
 * @param color - Color string to validate
 * @returns True if valid hex color, false otherwise
 */
export function isValidHexColor(color: string): boolean {
  const hexRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
  return hexRegex.test(color);
}

/**
 * Validates if a string contains only alphanumeric characters.
 * 
 * @param value - String to validate
 * @returns True if alphanumeric, false otherwise
 */
export function isAlphanumeric(value: string): boolean {
  const alphanumericRegex = /^[a-zA-Z0-9]+$/;
  return alphanumericRegex.test(value);
}
