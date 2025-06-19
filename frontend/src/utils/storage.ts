/**
 * Local storage utility functions.
 */

/**
 * Safely gets an item from localStorage.
 * 
 * @param key - Storage key
 * @param defaultValue - Default value if key doesn't exist
 * @returns Stored value or default
 */
export function getStorageItem<T>(key: string, defaultValue: T): T {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.warn(`Error reading from localStorage key "${key}":`, error);
    return defaultValue;
  }
}

/**
 * Safely sets an item in localStorage.
 * 
 * @param key - Storage key
 * @param value - Value to store
 * @returns True if successful, false otherwise
 */
export function setStorageItem<T>(key: string, value: T): boolean {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.warn(`Error writing to localStorage key "${key}":`, error);
    return false;
  }
}

/**
 * Safely removes an item from localStorage.
 * 
 * @param key - Storage key
 * @returns True if successful, false otherwise
 */
export function removeStorageItem(key: string): boolean {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.warn(`Error removing from localStorage key "${key}":`, error);
    return false;
  }
}

/**
 * Clears all items from localStorage.
 * 
 * @returns True if successful, false otherwise
 */
export function clearStorage(): boolean {
  try {
    localStorage.clear();
    return true;
  } catch (error) {
    console.warn('Error clearing localStorage:', error);
    return false;
  }
}

/**
 * Gets all keys from localStorage.
 * 
 * @returns Array of storage keys
 */
export function getStorageKeys(): string[] {
  try {
    return Object.keys(localStorage);
  } catch (error) {
    console.warn('Error getting localStorage keys:', error);
    return [];
  }
}

/**
 * Checks if localStorage is available.
 * 
 * @returns True if available, false otherwise
 */
export function isStorageAvailable(): boolean {
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

/**
 * Gets the size of localStorage in bytes.
 * 
 * @returns Size in bytes
 */
export function getStorageSize(): number {
  try {
    let total = 0;
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        total += localStorage[key].length + key.length;
      }
    }
    return total;
  } catch (error) {
    console.warn('Error calculating localStorage size:', error);
    return 0;
  }
}

/**
 * Creates a storage manager for a specific prefix.
 * 
 * @param prefix - Key prefix
 * @returns Storage manager object
 */
export function createStorageManager(prefix: string) {
  const prefixedKey = (key: string) => `${prefix}_${key}`;
  
  return {
    get: <T>(key: string, defaultValue: T): T =>
      getStorageItem(prefixedKey(key), defaultValue),
    
    set: <T>(key: string, value: T): boolean =>
      setStorageItem(prefixedKey(key), value),
    
    remove: (key: string): boolean =>
      removeStorageItem(prefixedKey(key)),
    
    clear: (): boolean => {
      try {
        const keys = getStorageKeys().filter(key => key.startsWith(`${prefix}_`));
        keys.forEach(key => localStorage.removeItem(key));
        return true;
      } catch (error) {
        console.warn(`Error clearing storage with prefix "${prefix}":`, error);
        return false;
      }
    },
    
    keys: (): string[] =>
      getStorageKeys()
        .filter(key => key.startsWith(`${prefix}_`))
        .map(key => key.replace(`${prefix}_`, '')),
  };
}

/**
 * Storage manager for app-specific data.
 */
export const appStorage = createStorageManager('project_overview_agent');

/**
 * Storage keys used by the application.
 */
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed',
  RECENT_PROJECTS: 'recent_projects',
  DRAFT_DATA: 'draft_data',
  API_CACHE: 'api_cache',
} as const;
